# Ảnh GPU cho dịch vụ REST (task T38). Không có bản CPU: mô hình đọc là Qwen2.5-7B lượng tử hóa
# NF4 qua bitsandbytes, và bitsandbytes cần CUDA.
#
# Chạy bằng một lệnh:
#
#     docker compose up --build
#
# Lần đầu sẽ tải trọng số Qwen2.5-7B (~15 GB) từ Hugging Face vào volume `hf-cache`; các lần sau
# dùng lại. Trọng số KHÔNG nướng vào ảnh — ảnh 15 GB không đẩy đi đâu được, và giấy phép của mô
# hình là của Alibaba chứ không phải của repo này.
#
# Ảnh nền là bản runtime của PyTorch có sẵn CUDA 12.4 và Python 3.11 (mục 3 CLAUDE.md), nên
# bước cài phụ thuộc không phải tải lại torch. uv thấy torch đã có và bỏ qua.

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HUB_DISABLE_PROGRESS_BARS=1 \
    TRANSFORMERS_VERBOSITY=error \
    HF_HOME=/cache/huggingface \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --no-cache-dir uv

# Phụ thuộc trước, mã nguồn sau: đổi một dòng trong scripts/ thì không cài lại thư viện.
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv pip install --system --no-cache -e .

COPY scripts ./scripts
COPY configs ./configs
COPY models ./models

# Thư mục cache có sẵn để mount volume vào; chạy không mount thì vẫn tải được, chỉ mất khi xóa.
RUN mkdir -p /cache/huggingface

EXPOSE 8000

# start-period rộng vì nạp 7B NF4 mất khoảng một phút trên T4, lâu hơn nếu còn phải tải trọng số.
# Kiểm bằng chính /health: chỉ "ok" khi mô hình đã nạp, không phải chỉ khi cổng mở.
HEALTHCHECK --interval=30s --timeout=5s --start-period=600s --retries=3 \
    CMD python -c "import json,sys,urllib.request; \
r=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)); \
sys.exit(0 if r.get('status') == 'ok' else 1)"

CMD ["python", "scripts/serve.py", "--host", "0.0.0.0", "--port", "8000", \
     "--bundle", "models/e03_chunk_aware.pkl"]
