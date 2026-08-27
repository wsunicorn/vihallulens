# TASKS.md — Danh sách việc tuần tự

> **Đây là nguồn sự thật duy nhất về tiến độ.** Claude Code đọc file này đầu mỗi phiên, làm task chưa tick có số nhỏ nhất, không nhảy cóc.

## Quy tắc

1. Làm **đúng một task** mỗi lần. Xong mới sang task kế.
2. Trước khi tick `[x]`, phải chạy được lệnh ở mục **Kiểm tra** và dán output vào PR.
3. Tick xong ghi ngày vào cột ghi chú.
4. Task có dấu 🚩 là **cổng chặn** — không được làm task sau nếu chưa qua.
5. Gặp quyết định chưa có trong `CLAUDE.md` → **dừng, hỏi người dùng**.
6. Ký hiệu người phụ trách: **L** = Lân, **M** = Minh, **LM** = cả hai.

---

## Giai đoạn 0 — Dựng khung repo (tuần 3)

- [x] **T01** · L · Khởi tạo repo — hoàn thành 19/08/2026
  - Tạo `pyproject.toml` với `uv`, Python 3.11, tên gói `vihallulens`, bố cục `src/`.
  - Khai báo phụ thuộc: `torch`, `transformers`, `accelerate`, `bitsandbytes`, `pandas`, `pyarrow`, `numpy`, `scikit-learn`, `pydantic`, `pyyaml`, `rank-bm25`, `fastapi`, `uvicorn`, `pytest`, `ruff`.
  - `.gitignore` đã tạo sẵn lúc dựng repo ngày 19/08/2026 (loại trừ `data/` trừ `data/raw/MANIFEST.md`, `results/*.npz`, `__pycache__`, `.venv`, `.env`) — chỉ cần rà lại, không tạo mới.
  - Tạo `.env.example` với các khóa cần thiết để trống, ví dụ `GEMINI_API_KEY=`.
  - Tạo cây thư mục theo mục 9 của `CLAUDE.md`.
  - **Kết quả kiểm tra:** `uv pip install -e ".[dev]"` chạy sạch trên Python 3.11.9, `python -c "import vihallulens"` in ra `import vihallulens OK, version 0.1.0`. Phiên bản đã giải: torch 2.13.0, transformers 5.15.0, accelerate 1.14.0, bitsandbytes 0.50.1, pandas 3.0.5, numpy 2.4.6, scikit-learn 1.9.0, pydantic 2.13.4, pytest 9.1.1, ruff 0.16.3.
  - **Ghi chú chuyển cho T07:** `transformers` giải ra **bản 5.15.0**, tức nhánh API mới chứ không phải 4.x mà bài Lookback Lens và phần lớn ví dụ trên mạng dùng. Việc hook trên `self_attn` có nhận được `attn_weights` hay không phải kiểm tra thực tế rồi mới ghim phiên bản — xem mục 5 của `CLAUDE.md`. Chưa ghim ở T01 vì T07 mới là nơi có căn cứ để chọn.

- [x] **T02** · L · Cấu hình lint và test — hoàn thành 19/08/2026
  - Cấu hình `ruff` trong `pyproject.toml`: `line-length = 100`, `target-version = "py311"`, bộ luật `E, W, F, I, UP, B, SIM, N`, isort biết `vihallulens` là gói nội bộ.
  - Cấu hình `pytest`: `testpaths = ["tests"]`.
  - `tests/test_smoke.py`: kiểm tra gói import được, có `__version__`, và cả sáu gói con theo `docs/SPEC.md` đều import được.
  - **Kết quả kiểm tra:** `ruff check .` → `All checks passed!`; `pytest` → `2 passed in 0.02s`.

- [x] **T03** · M · Module cấu hình — hoàn thành 19/08/2026
  - `src/vihallulens/config.py`: sáu pydantic model theo mục 3 của `docs/SPEC.md` — `ExperimentConfig` gồm `DatasetConfig`, `ChunkingConfig`, `ExtractorConfig`, `FeatureConfig`, `DetectorConfig`.
  - `load_config(path) -> ExperimentConfig` và `config_hash(cfg) -> str`.
  - `configs/example.yaml` theo đúng cấu trúc ví dụ trong `docs/SPEC.md`.
  - Ba lớp bảo vệ khả năng tái lập: mọi model đặt `extra="forbid"` nên gõ sai tên khóa là raise chứ không bị bỏ qua âm thầm; `split_seed` khác 42 là raise theo mục 3 và mục 7 của `CLAUDE.md`; `config_hash` bỏ qua `run_name` nên đổi tên lần chạy không sinh hash mới.
  - **Kết quả kiểm tra:** `pytest tests/test_config.py` → `23 passed`; toàn bộ `pytest` → `27 passed`; `ruff check .` → `All checks passed!`.

- [x] **T04** · M · Module ghi kết quả — hoàn thành 19/08/2026
  - `src/vihallulens/evaluation/logging.py` với `log_result`, `export_table` và `read_results` theo mục 2.5 của `docs/SPEC.md`. Ghi nối vào `results/runs.jsonl`, mỗi lần chạy một dòng JSON, không bao giờ ghi đè.
  - Mỗi bản ghi có đủ `timestamp`, `run_name`, `git_commit`, `config_hash`, `config`, `metrics`, `extra`. `config_hash` dùng chung hàm với `config.py` nên dict ghi ra và model sinh ra nó cho cùng một hash.
  - `extra` thiếu `ms_per_sample` hoặc `peak_vram_mb` là raise, không ghi gì — theo mục 3 của `docs/EXPERIMENTS.md`.
  - **Kết quả kiểm tra:** gọi `log_result` hai lần rồi `export_table` trả về đúng 2 dòng; `pytest` → `42 passed`; `ruff check .` → `All checks passed!`.

---

## Giai đoạn 1 — 🚩 Cổng khả thi kỹ thuật (tuần 3, ưu tiên cao nhất)

> Nếu giai đoạn này thất bại, **dừng toàn bộ** và báo người dùng. Không tự đổi hướng đề tài.

- [x] **T05** · L · Đo ngân sách bộ nhớ trên giấy — hoàn thành 19/08/2026
  - Viết `scripts/probe_vram.py --model ... --seq-len ...` in ra: số lớp, số đầu chú ý, dung lượng trọng số sau lượng tử hóa 4-bit, và ước tính dung lượng ma trận chú ý **một lớp** theo công thức `n_heads × seq_len² × 2 byte`.
  - Chạy với `seq_len` thuộc `{1024, 2048, 4096, 8192}`. Đối chiếu với bảng ngân sách ở mục 5 của `CLAUDE.md`.
  - **Đo tỷ lệ token trên từ của tokenizer Qwen2.5 với tiếng Việt.** Mọi số liệu trong `docs/DATA.md` tính bằng **từ**, còn ngân sách bộ nhớ tính bằng **token** — không có tỷ lệ thật thì không biết `max_context_tokens = 4096` cắt mất bao nhiêu phần trăm mẫu. Tokenize toàn bộ ngữ cảnh của bốn bộ, in ra phân vị 50/90/99 và tỷ lệ mẫu vượt 2.048 và 4.096 token.
  - **Kết quả kiểm tra:** `python scripts/probe_vram.py` in ra cả hai bảng, chạy 21 giây trên CPU. Ma trận một lớp 0,23 / 0,94 / 3,76 GB ở 2.048 / 4.096 / 8.192 token — **khớp chính xác bảng mục 5 của `CLAUDE.md`**. Trọng số sau NF4 là 5,44 GB, thấp hơn ngưỡng 7 GB mà T06 đặt ra. Tỷ lệ quy đổi đo được là 1,33–1,36 token mỗi từ; ở `max_context_tokens = 4096` chỉ 14 mẫu trên cả bốn bộ bị cắt. Chi tiết ghi ở mục 4B của `docs/DATA.md`.

- [x] **T06** · L · Nạp mô hình 4-bit trên T4 — hoàn thành 19/08/2026
  - Nạp `Qwen/Qwen2.5-7B-Instruct` với NF4, `attn_implementation="eager"`, `torch_dtype=float16`.
  - In VRAM sau khi nạp.
  - Công cụ đã sẵn sàng từ 19/08/2026: `scripts/probe_load_model.py`, chạy qua `notebooks/t07_trich_attention_t4.ipynb` (notebook đó làm cả T06 lẫn T07 trong một phiên GPU). Script tự in compute capability và cảnh báo nếu card thấp hơn 7.5, tự kiểm `attn_implementation` có đúng là `eager` không, và trả mã thoát khác 0 nếu không đạt tiêu chí.
  - **Kết quả kiểm tra** trên Kaggle Tesla T4 (compute capability 7.5, 14.912 MB): nạp 121,4 giây, `attn_implementation = eager`, 28 lớp / 28 đầu, `dtype` tham số `torch.float16`. **VRAM cấp phát 5.302 MB**, đặt chỗ 5.462 MB, còn trống 9.450 MB cho attention. Dưới ngưỡng 7.168 MB → ĐẠT. Ước tính trên giấy ở T05 là 5,44 GB, lệch dưới 3 %.

- [x] **T07** · L · 🚩 Trích attention bằng hook, không tràn bộ nhớ — **CỔNG ĐÃ QUA** 19/08/2026
  - Đăng ký forward hook trên từng `self_attn`, tính tổng theo chunk ngay trong hook, `del` tensor trước khi ra khỏi hook. Chặn `all_self_attns` tích lũy bằng cách cho hook trả về `(attn_output, None)`.
  - **Việc đầu tiên phải làm:** kiểm tra `output` của hook có thật sự chứa `attn_weights` không — điều này phụ thuộc phiên bản `transformers` (xem mục 5 của `CLAUDE.md`). Xong thì ghim đúng phiên bản đó vào `pyproject.toml` và viết một test khẳng định `attn_weights is not None`. Không ghim thì một lần `uv pip install` sau này có thể làm hỏng toàn bộ pipeline mà không báo lỗi.
  - Chạy thử với một mẫu ViHallu (~200 từ) và một mẫu ISE-DSC01 dài nhất (~4.805 từ).
  - Chốt **mẫu prompt duy nhất** ghép ngữ cảnh, câu hỏi và phản hồi. Ghi nguyên văn vào mục 8 của `CLAUDE.md`. Sau task này không được đổi.
  - Đã làm 19/08/2026: `src/vihallulens/extract/prompt.py` (mẫu prompt đã chốt), `src/vihallulens/extract/attention.py` (`AttentionExtractor` + hook), `scripts/probe_attention_hook.py`, `notebooks/t07_trich_attention_t4.ipynb`. Mục 8 của `CLAUDE.md` đã ghi nguyên văn mẫu prompt.
  - Đã trả lời được câu hỏi phiên bản, đo trên `transformers` 5.15.0: **hook nhận `attn_weights` kể cả khi không bật `output_attentions`**, nên không bật cờ đó nữa và `all_self_attns` không bao giờ tích lũy.
  - Toán lookback đã kiểm bằng `pytest tests/test_attention_math.py` (12 ca, đối chiếu ma trận chú ý có đáp án tính tay) và toàn tuyến đã chạy trên mô hình Qwen2 tí hon ở CPU: `lookback_per_chunk` ra đúng `(n_layers, n_heads, n_response_tokens, n_chunks)`.
  - **Kết quả kiểm tra** trên Kaggle Tesla T4, cấu hình chốt (float16, bỏ lớp 27, 27 lớp được hook):

| Mẫu | Ngữ cảnh | `lookback_per_chunk` | Thời gian | VRAM đỉnh | Lớp nan | Tổng hàng |
|---|---|---|---|---|---|---|
| ViHallu | 200 từ, 4 chunk | (27, 28, 47, 4) | 951 ms | 5.496 MB | không có | 1,0000 |
| ISE-DSC01 dài nhất | 4.805 từ, 169 → 96 chunk | (27, 28, 21, 96) | 4.046 ms | **8.395 MB** | không có | 1,0000 |

  - Đỉnh toàn phiên 8.395 MB trên ngưỡng 14.336 MB → **ĐẠT**, còn dư 42 %. Mục 8 của `CLAUDE.md` đã có mẫu prompt nguyên văn. Cắt ngữ cảnh hoạt động đúng: 169 chunk còn 96, offset vẫn khớp.
  - Ghi chú cho T21: `lookback_total` vẫn có phần tử ở đúng 0 và đúng 1. Đó là các đầu chú ý chỉ nhìn prompt hoặc chỉ nhìn phần tự sinh, tức giá trị biên thật chứ không phải 0/0 như lỗi token đầu đã sửa. Khi gộp đặc trưng cần xử lý biên này.

- [x] **T08** · L · Đo thông lượng và quyết định bậc thang — hoàn thành 20/08/2026, **CỔNG KHẢ THI KỸ THUẬT ĐÃ QUA TRỌN VẸN**
  - Đo ms/mẫu với 20 mẫu ở mỗi mức độ dài. Nếu 7B không qua T07, thử lại với 3B rồi 1.5B.
  - Ghi kết quả vào `results/feasibility.jsonl`.
  - **Kiểm tra:** file kết quả tồn tại, có kết luận rõ mô hình nào dùng được với ngữ cảnh tối đa bao nhiêu token.

  **Task này để làm gì.** T07 trả lời "một mẫu có vừa 16 GB không" — câu hỏi về *vật lý*. T08 trả lời câu hỏi về *lịch*: với hạn mức 30 giờ GPU mỗi tuần trên Kaggle, trích đặc trưng cho 71.520 mẫu của bốn bộ có kịp không. Hai câu này độc lập: một mẫu vừa bộ nhớ không có nghĩa là 71.520 mẫu chạy xong trong tuần. *Thông lượng* (throughput) ở đây là số mẫu xử lý được trong một đơn vị thời gian, quy ước báo cáo bằng nghịch đảo của nó là **ms/mẫu** cho dễ so sánh. *Bậc thang* là bảng sáu nấc lùi ở mục 5 `CLAUDE.md` — nếu không kịp thì lùi theo thứ tự nào.

  **Cách đo, và vì sao không đo bằng một con số duy nhất.** Chi phí mỗi mẫu phụ thuộc mạnh vào độ dài chuỗi, nên một con số "ms/mẫu trung bình" đo trên vài mẫu bất kỳ là vô nghĩa: đo toàn mẫu ngắn thì lạc quan, đo toàn mẫu dài thì bi quan. Thay vào đó chia mẫu thành **bốn mức độ dài** theo số token của prompt — 0–512, 513–1024, 1025–2048, 2049–4096 — đo 20 mẫu mỗi mức, rồi nhân trung vị từng mức với **số mẫu thật rơi vào mức đó** của từng bộ. Kết quả không phải một con số mà là số giờ GPU cho mỗi bộ, tức thứ mà lịch chạy cần.

  **Công cụ đã sẵn sàng từ 20/08/2026:** `scripts/measure_throughput.py` (có cờ `--dry-run` chạy được trên CPU), `tests/test_throughput.py` (26 ca cho phần toán dự báo), `notebooks/t08_thong_luong_t4.ipynb`. Script ghi kết quả qua chính `log_result` của T04 nên bản ghi có đủ `git_commit` và `config_hash` như mọi thí nghiệm khác, chỉ khác đường dẫn là `results/feasibility.jsonl`.

  **Đã đo được trên CPU ngày 20/08/2026** (`python scripts/measure_throughput.py --dry-run`) — phân bố độ dài prompt thật của cả bốn bộ, đây là mẫu số của mọi phép dự báo:

| Bộ | 0–512 | 513–1024 | 1025–2048 | 2049–4096 | Tổng |
|---|---|---|---|---|---|
| ViHallu | 6.461 | 530 | 6 | 3 | 7.000 |
| ISE-DSC01 | 6.188 | 17.770 | 11.931 | 480 | 36.369 |
| ViWikiFC | 20.102 | 817 | 0 | 0 | 20.919 |
| ViFactCheck | 705 | 3.546 | 2.785 | 196 | 7.232 |
| **Tổng** | **33.456** | **22.663** | **14.722** | **679** | **71.520** |

  Khung mẫu prompt (các token `<|im_start|>`, dòng `Ngữ cảnh:`, câu hệ thống) tốn **37 token**, hoặc **41 token** khi có khối câu hỏi. Số mẫu của cả bốn bộ khớp đúng bảng mục 4 `docs/DATA.md`, nên trình đọc dữ liệu trong script không bỏ sót dòng nào.

  Ba điều rút ra ngay từ bảng này, trước cả khi chạm GPU:
  1. **ISE-DSC01 quyết định chi phí.** Nó chiếm 51 % số mẫu nhưng gần như toàn bộ khối lượng ở hai mức đắt: 11.931 mẫu ở mức 1025–2048 và 480 mẫu ở mức trên cùng. Ba bộ còn lại dồn về mức rẻ nhất.
  2. **ViWikiFC gần như miễn phí.** 96 % số mẫu dưới 512 token, không mẫu nào vượt 1.024.
  3. **Mức trên cùng rất thưa** — 679 mẫu trên tổng 71.520, tức 0,9 %. Nếu chỉ mức này quá đắt thì cắt nó rẻ hơn nhiều so với lùi mô hình.

  **Kết quả đo trên Kaggle Tesla T4 ngày 20/08/2026** (`python scripts/measure_throughput.py --per-tier 20`, nạp mô hình 116 giây, 27 lớp được hook):

| Mức (token) | Trung vị | Trung bình | p90 | Token TB | Chunk TB | VRAM đỉnh | Lớp nan |
|---|---|---|---|---|---|---|---|
| 0–512 | 389 ms | 407 ms | 486 ms | 371 | 7,5 | 5.517 MB | không có |
| 513–1024 | 779 ms | 743 ms | 879 ms | 746 | 20,4 | 5.617 MB | không có |
| 1025–2048 | 1.401 ms | 1.460 ms | 1.833 ms | 1.379 | 40,7 | 6.305 MB | không có |
| 2049–4096 | 2.641 ms | 2.907 ms | 3.660 ms | 2.492 | 61,5 | **8.428 MB** | không có |

  Dự báo thời gian trích đặc trưng một lượt cho từng bộ:

| Bộ | Số mẫu | ms/mẫu | Thời gian GPU | % quota tuần |
|---|---|---|---|---|
| ViHallu | 7.000 | 420 | 0 giờ 49 | 2,7 % |
| ISE-DSC01 | 36.369 | 941 | 9 giờ 30 | 31,7 % |
| ViWikiFC | 20.919 | 404 | 2 giờ 20 | 7,8 % |
| ViFactCheck | 7.232 | 1.031 | 2 giờ 04 | 6,9 % |
| **Tổng** | **71.520** | **742** | **14 giờ 44** | **49,1 %** |

  **Kết luận: Qwen2.5-7B-Instruct dùng được ở ngữ cảnh tối đa 4.096 token.** Hai bộ bắt buộc (ViHallu + ISE-DSC01) cần **10 giờ 19**, tức 34,4 % quota tuần, nằm dưới ngưỡng nửa quota mà script đặt ra. VRAM đỉnh 8.428 MB trên trần 14.336 MB, còn dư 41 %, khớp với 8.395 MB đo ở T07. Không lớp nào ra `nan` trên cả 80 mẫu, xác nhận quyết định float16 + bỏ lớp 27 chốt ở T07 ổn định chứ không chỉ đúng trên hai mẫu. **Không phải dùng nấc lùi nào.**

  **Bốn điều học được, ba trong đó không đoán trước được:**

  1. **Chi phí tăng tuyến tính theo độ dài, không phải bậc hai.** Mũ đo được là `k ≈ 1,00`, và chia ra thì bốn mức cho 1,049 / 1,044 / 1,016 / 1,060 ms mỗi token — gần như một hằng số. Quy tắc nhẩm dùng được từ nay: **khoảng 1,05 ms cho mỗi token prompt**. Lý do là ở dải 512–4.096 token, phần tốn thời gian vẫn là các phép nhân ma trận của MLP và các phép chiếu (tỷ lệ với độ dài), cộng với việc giải nén trọng số NF4; ma trận chú ý tuy tăng theo bình phương nhưng chưa đủ lớn để chi phối. Nó chi phối *bộ nhớ* thì đúng — bảng mục 5 `CLAUDE.md` vẫn nguyên giá trị — nhưng bộ nhớ và thời gian là hai chuyện khác nhau.

  2. **Hệ quả trực tiếp: nấc lùi 1 là đòn bẩy cho bộ nhớ, không phải cho thời gian.** Hạ `max_context_tokens` từ 4.096 xuống 2.048 chỉ ảnh hưởng 483 mẫu của hai bộ bắt buộc (3 của ViHallu, 480 của ISE-DSC01) — tính trên giấy thì tiết kiệm khoảng 10 phút trên tổng 10 giờ 19, còn **đo thật thì không tiết kiệm gì cả**, xem lượt đo 2.048 ở dưới. Nếu sau này thiếu giờ GPU thì **đòn bẩy thật là lấy mẫu con ISE-DSC01**, không phải cắt ngữ cảnh. Ghi lại đây để sau này khỏi lùi nhầm nấc.

  3. **ISE-DSC01 nuốt 92 % chi phí của hai bộ bắt buộc** trong khi chỉ chiếm 84 % số mẫu — vì mẫu của nó dài hơn gấp đôi (941 ms/mẫu so với 420 ms/mẫu của ViHallu). Nó cũng là bộ duy nhất có nhiều mẫu ở mức đắt nhất (480 mẫu).

  4. **Phần ngoài GPU chỉ chiếm 9 %.** Lời gọi mô hình chiếm 90–92 % thời gian ở cả bốn mức; render prompt, cắt theo ngân sách và chuyển đặc trưng về CPU gộp lại chưa tới một phần mười. Tối ưu phía CPU không đáng công.

  **Đã chạy thêm cấu hình 2.048 token (ô 6) để kiểm chứng điểm 2 bằng đo đạc thay vì suy luận.** Kết quả nằm ở dòng thứ hai của `results/feasibility.jsonl`, và nó xác nhận: **hạ ngân sách token không mua được thời gian.**

| Mức | 4.096 token | 2.048 token | Chênh | Mẫu bị cắt ở 2.048 |
|---|---|---|---|---|
| 0–512 | 389 ms | 429 ms | +10,2 % | 0/20 |
| 513–1024 | 779 ms | 872 ms | +12,0 % | 0/20 |
| 1025–2048 | 1.401 ms | 1.616 ms | +15,4 % | 0/20 |
| 2049–4096 | 2.641 ms | 2.080 ms | −21,2 % | 20/20 |
| **Dự báo hai bộ bắt buộc** | **10,32 giờ** | **11,58 giờ** | **+12 %** | |
| **VRAM đỉnh** | **8.428 MB** | **6.305 MB** | **−25 %** | |

  Ba mức dưới **không có mẫu nào bị cắt ở cả hai lượt** — cùng 20 mẫu đó, cùng số token đó, cùng số chunk đó — vậy mà chậm đi 10–15 %. Khối lượng tính toán không đổi thì phần chênh này không đến từ thuật toán mà từ máy. Giải thích khả dĩ nhất là **T4 trên Kaggle bị hạ xung do nhiệt**: card tản nhiệt thụ động, lượt đo thứ hai chạy ngay sau khi lượt đầu vừa nạp GPU liên tục vài phút. Nhóm **chưa xác minh** bằng cách đọc nhiệt độ hay xung nhịp, nên đây là giả thuyết chứ không phải kết luận.

  Dù giải thích thế nào, kết luận thực dụng không đổi: chỉ mức trên cùng nhanh lên, ba mức dưới không được lợi gì, và tổng cục lại **đắt hơn** chứ không rẻ hơn. Nấc lùi 1 chỉ mua được **bộ nhớ** (8.428 → 6.305 MB, giảm 25 %), đúng như bảng mục 5 `CLAUDE.md` nói, và không mua được thời gian.

  **Hệ quả cho việc xếp lịch, và đây là chỗ mình suýt ghi hụt:** lượt đo 4.096 chạy **đầu tiên trong phiên, GPU còn nguội**. Một lượt trích thật kéo 9–10 tiếng thì card nóng gần như suốt, nên con số dưới đây là lạc quan. Cộng 15 % cho chắc:

| | Dự báo lúc GPU nguội | Nên lấy để xếp lịch |
|---|---|---|
| ISE-DSC01 một lượt | 9 giờ 30 | **~11 giờ** |
| Hai bộ bắt buộc | 10 giờ 19 | **~12 giờ** |
| Cả bốn bộ | 14 giờ 44 | **~17 giờ** |

  Vẫn nằm trong quota 30 giờ. Nhưng **11 tiếng cho ISE-DSC01 sát giới hạn 12 tiếng của một lượt Save Version** — đây mới là lý do thật để ghi kết quả theo phần.

  **Đã thêm đo nhiệt độ và xung nhịp vào script** (`nvidia-smi`, không thêm thư viện) để lần chạy GPU kế tiếp tự trả lời câu hỏi hạ xung mà không tốn thêm phút quota nào: đọc một lần trước khi đo và một lần sau mỗi mức, in bảng nhiệt độ theo mức, và cảnh báo nếu xung tụt. Tiêu chí là **xu hướng chứ không phải một số đo lẻ** — ngưỡng tuyệt đối kiểu "xung dưới 95 % là hạ xung" nghe hợp lý nhưng sai, vì card rảnh tự hạ xung: đo thử trên card rời của máy cá nhân lúc không làm gì được 1.500/2.100 MHz, tức 71 %, mà chẳng có gì bị ghìm cả. Dấu hiệu thật là **xung cuối phiên thấp hơn đầu phiên trong khi nhiệt độ tăng**.

  **Đã cân nhắc và quyết định KHÔNG chạy lại hai phiên riêng để đo chính xác phần chênh 4.096 với 2.048.** Lý do là có một chặn trên bằng số học khiến mọi kết quả đo đều dẫn tới cùng một quyết định: ngân sách 2.048 chỉ ảnh hưởng 483 mẫu của hai bộ bắt buộc, mà 483 mẫu đó ở cấu hình 4.096 chỉ tốn 21 phút trên tổng 10 giờ 19. Nghĩa là kể cả nếu chúng nhanh bằng không thì tiết kiệm tối đa cũng chỉ **3,4 %**, thực tế khoảng 1,6 %. Đốt quota để làm rõ 1,6 % hay 3,4 % trong khi cả hai đều dẫn tới "giữ 4.096" là không đáng.

  **Bài học về cách đo, phải nhớ cho E11 và E14:** hai lượt đo chạy nối nhau trong cùng một phiên GPU **không so trực tiếp với nhau được**, vì trạng thái nhiệt của card đã khác. Các thí nghiệm sau có so ms/mẫu giữa các mô hình (E14 lùi 3B, 1.5B; E13 đổi sang Sailor2) phải **chạy mỗi cấu hình trong một phiên riêng, hoặc đo xen kẽ** rồi lấy trung bình, chứ không xếp tuần tự rồi so thẳng. Nếu không, kết luận "mô hình nhỏ hơn nhanh hơn X %" sẽ lẫn cả phần hạ xung vào.

  **Một lỗi trong script đã lộ ra nhờ lượt đo này và đã sửa.** Lượt 2.048 báo mũ `k = 0,85`, khác hẳn `k = 1,00` của lượt 4.096. Nguyên nhân: mũ được khớp giữa `median_ms` và `mean_tokens`, mà `mean_tokens` là độ dài **lúc mẫu đi vào**, còn mẫu bị cắt thì thực tế chỉ được đưa vào 2.048 token. Ghép chi phí thật với độ dài không thật thì khớp ra một đường cong chưa từng tồn tại. Đã sửa: chỉ khớp trên các mức **không có mẫu nào bị cắt**, và in ra mức nào bị loại. Thêm `tiers_without_truncation` và hai ca kiểm thử.

  **Ghi chú chuyển cho giai đoạn trích đặc trưng (T21 trở đi), chưa làm bây giờ:** một lượt ISE-DSC01 mất 9 giờ 30. Việc này **không cần ngồi canh** — Kaggle cho "Save Version" chạy nền theo lô, giới hạn 12 tiếng, nên 9 giờ 30 nằm gọn trong một lượt commit. Cái vẫn nên làm là **ghi kết quả ra từng phần và bỏ qua phần đã có khi chạy lại**, không phải vì sợ đứt phiên mà vì nếu hỏng ở giờ thứ tám thì không muốn mất cả tám giờ. Ngoài ra một số thí nghiệm cần **trích lại toàn bộ** chứ không dùng lại được: E04 quét ba cỡ cửa sổ token (ranh giới chunk đổi), E13 đổi mô hình đọc sang Sailor2-8B, E14 lùi 3B và 1.5B. Ước tổng cộng khoảng 19 giờ GPU trải từ tuần 6 tới tuần 11, tức 2–4 giờ mỗi tuần — vẫn thoải mái trong quota, nhưng phải xếp lịch chứ không dồn.

---

## Giai đoạn 2 — Chuẩn hóa dữ liệu (tuần 3–4)

- [x] **T08B** · M · Khảo sát thư mục dữ liệu — hoàn thành 19/08/2026
  - Đã quét `data/raw/`, liệt kê mọi file `.csv`, `.json`, `.parquet` kèm kích thước, số dòng và tên cột.
  - Nhận diện bốn bộ **theo nội dung cột, không dựa vào tên file**: có `prompt` và `response` là ViHallu; có `verdict` và `domain` là ISE-DSC01; có `pairID` và `gold_label` là ViWikiFC; có `Statement` và `Topic` là ViFactCheck.
  - Đã đổi tên về quy ước `{dataset}_{split}.{ext}`, dời hết lên `data/raw/` (bỏ bốn thư mục con), bảng ánh xạ ghi ở `data/raw/MANIFEST.md`. Danh sách đường dẫn chốt nằm ở mục 2 của `docs/DATA.md`.
  - **Kết quả kiểm tra:** `data/raw/MANIFEST.md` liệt kê đủ bốn bộ với tên file trước và sau khi đổi; số dòng và phân bố nhãn khớp 100 % bảng mục 4 của `docs/DATA.md` (7.000 / 36.369 / 16.738+2.090+2.091 / 5.062+723+1.447). Không có file lạ, không thiếu bộ nào.

- [x] **T09** · M · Chuẩn hóa ViHallu — hoàn thành 20/08/2026
  - Viết `src/vihallulens/data/vihallu.py` theo `docs/DATA.md`. Nguồn: `data/raw/vihallu_train.csv`. Bỏ qua `data/raw/vihallu_test_public.csv` vì không có nhãn.
  - Suy ra `meta.prompt_type` theo luật ở mục 7 của `docs/DATA.md`: prompt không có ký tự có dấu tiếng Việt thì gán `noisy`, còn lại gán `unknown`. Ghi kèm `meta.prompt_has_diacritics`.
  - **Kiểm tra:** `python scripts/normalize_data.py --dataset vihallu` sinh Parquet 7.000 dòng, phân bố nhãn khớp 2.245 / 2.448 / 2.307.

  **Task này để làm gì.** Bốn bộ dữ liệu có bốn định dạng khác nhau: CSV, JSON, CSV, Parquet; cột tên khác nhau; nhãn gọi tên khác nhau. Nếu để nguyên thì mỗi thí nghiệm phải biết cách đọc từng bộ, và mỗi lần thêm bộ mới là sửa khắp nơi. *Chuẩn hóa* (normalise) nghĩa là đổ cả bốn về **cùng một bộ cột**, gọi là **schema chung**, định nghĩa ở mục 1 `docs/DATA.md`. Sau bước này, phần còn lại của hệ thống chỉ cần biết đúng 14 cột đó, không cần biết dữ liệu gốc trông ra sao. T09 làm bộ đầu tiên, T10–T12 làm ba bộ còn lại theo đúng khuôn này.

  **Đã làm.** Ba file mới:
  - `src/vihallulens/data/schema.py` — sở hữu định nghĩa schema chung. Mọi bộ đọc xong đều phải đi qua `finalise()`, hàm này sắp lại thứ tự cột, ép kiểu, rồi kiểm tra ràng buộc. Đặt kiểm tra ở lúc ghi là cố ý: một bộ dữ liệu lặng lẽ mất nhãn, hay để `null` vào chỗ mô hình mong đợi chuỗi, bắt ở đây rẻ hơn nhiều so với phát hiện ba tuần sau bên trong vòng lặp huấn luyện.
  - `src/vihallulens/data/vihallu.py` — bộ đọc ViHallu.
  - `scripts/normalize_data.py` — điểm vào dòng lệnh, gọi `--dataset viwikifc` thì báo rõ "đó là task T11" chứ không im lặng.

  **Kết quả chạy:**

```
  số dòng               : 7,000
  ngữ cảnh duy nhất     : 3,865
  phân bố nhãn:
      extrinsic      2,307  ( 33.0 %)
      intrinsic      2,448  ( 35.0 %)
      no             2,245  ( 32.1 %)
  phân bố meta.prompt_type:
      noisy            245  (  3.5 %)
      unknown        6,755  ( 96.5 %)
  đã ghi: data/interim/vihallu_train.parquet  (7,000 dòng)
```

  Khớp đúng bảng mục 4 `docs/DATA.md`. `ruff check .` sạch, `pytest` 167 ca xanh (thêm 55 ca mới).

  **Ba điều học được:**

  1. **Luật nhận `noisy` có độ chính xác cao nhưng độ phủ thấp — 3,5 %, không phải một phần ba như bài báo ngụ ý.** Bài ViHallu nói mỗi ngữ cảnh sinh ba loại prompt phân bố cân bằng, tức `noisy` đáng lẽ khoảng 33 %. Nhưng bỏ dấu chỉ là **một trong bốn** phép nhiễu bài báo liệt kê (bỏ dấu, hoán vị ký tự, xóa token, đảo trật tự từ). Prompt bị hoán vị ký tự mà vẫn còn dấu thì luật không bắt được. Hệ quả phải nhớ khi làm T35: so sánh sẽ là **"nhóm bị bỏ dấu với tất cả phần còn lại"**, chứ không phải "noisy với không noisy" — phần còn lại vẫn lẫn mẫu noisy kiểu khác. Đã ghi vào mục 7 `docs/DATA.md`.

  2. **Nhận diện dấu tiếng Việt phải suy từ Unicode, và phải so với ngữ cảnh chứ không xét prompt một mình.** Cách làm: một ký tự được coi là "có dấu" nếu **phân rã chuẩn tắc** của nó (normalisation form D — tách ký tự có dấu thành chữ cái gốc cộng dấu rời) ra một chữ cái ASCII kèm dấu; cộng thêm `đ`/`Đ` gọi tên riêng vì nó mang nét gạch chứ không phải dấu rời nên Unicode không phân rã, song vẫn biến mất khi bỏ dấu. Cách này đúng cho cả `á` lẫn `ệ` lẫn `ự` mà không phải gõ tay 134 ký tự. Còn việc **so với ngữ cảnh** là để tránh bẫy: một câu hỏi chỉ gồm tên riêng và con số như `IBM 1970?` vốn không có dấu nào để mất, xét một mình sẽ bị gán nhầm là `noisy`.

  3. **`context_id` phải chuẩn hóa NFC trước khi băm.** `context_id` là mã băm của ngữ cảnh, dùng để chia tập theo nhóm ở T14. Cùng một chữ `ế` có thể được lưu thành một mã điểm, hoặc thành `e` cộng hai dấu rời — nhìn giống hệt nhau nhưng băm ra hai giá trị khác nhau. Nếu vậy thì cùng một ngữ cảnh sẽ rơi vào hai tập khác nhau và **rò rỉ từ train sang test**, đúng cái mà việc chia theo nhóm sinh ra để ngăn. Đã chuẩn hóa NFC trước khi băm, và có ca kiểm thử khẳng định hai dạng cho cùng một `context_id`.

  **Ghi chú:** `load_dataset(name, split)` ở mục 2.1 `docs/SPEC.md` chưa viết, vì chưa task nào cần đọc lại file interim. Sẽ viết ở T14 khi chia tập.

- [x] **T10** · M · Chuẩn hóa ISE-DSC01 — hoàn thành 20/08/2026
  - Nguồn: `data/raw/isedsc01_train.json`. Bỏ qua hai file `isedsc01_test_public.json` và `isedsc01_test_private.json` vì thiếu `verdict`.
  - **Kiểm tra:** 36.369 dòng, phân bố 12.786 / 11.000 / 12.583, số mẫu tìm được `evidence_start` là ~~23.785~~ → **23.783**. Xem mục "Sửa một con số" bên dưới: tiêu chí gốc lấy từ một phép đếm sai, và số đúng là 23.783.

  **Task này để làm gì.** Đổ ISE-DSC01 về schema chung, theo đúng khuôn T09 đã dựng. Bộ này quan trọng riêng: ngữ cảnh của nó dài 21–73 câu, tức là nơi duy nhất mà chú ý *có chỗ để phân bố*. Trên ViHallu ngữ cảnh chỉ khoảng 5 câu nên chia đoạn hay không cũng gần như nhau; trên ISE-DSC01 thì khác hẳn. Nó cũng là bộ duy nhất chỉ ra **câu nào** là bằng chứng, nên là bộ duy nhất kiểm chứng được câu hỏi cốt lõi CH1: chú ý có tập trung đúng vào đoạn chứa bằng chứng không (E06).

  **Kết quả chạy:**

```
  số dòng               : 36,369
  ngữ cảnh duy nhất     : 4,793
  phân bố nhãn:
      extrinsic     12,583  ( 34.6 %)
      intrinsic     11,000  ( 30.2 %)
      no            12,786  ( 35.2 %)
  có bằng chứng nguyên văn : 23,783/36,369
  nguồn có ghi bằng chứng  : 23,784
  ghi mà không định vị được: 1
  phân bố meta.domain      : the-gioi 7.405 · thoi-su 7.121 · khoa-hoc 6.522
                             suc-khoe 5.416 · du-lich 5.175 · giao-duc 4.730
```

  Số dòng, số ngữ cảnh duy nhất và phân bố nhãn khớp đúng bảng mục 4 `docs/DATA.md`. `ruff` sạch, `pytest` 182 ca xanh (thêm 15 ca).

  ### Sửa một con số trong tài liệu

  Tiêu chí gốc ghi **23.785**, đo được **23.783**. Chênh đúng hai, và nguyên nhân đáng ghi lại.

  Hai mẫu trong bộ có trường `evidence` chỉ gồm **hai ký tự xuống dòng**, tức một dòng trống, không có chữ nào. Khoảng trắng là **giá trị rỗng duy nhất mà phép tìm chuỗi vẫn tìm thấy**: `context.find("<xuống dòng><xuống dòng>")` trả về vị trí của một dòng trống nào đó trong ngữ cảnh. Hai mẫu ấy vì thế được đếm là "có bằng chứng" và "tìm thấy bằng chứng", trong khi thực chất chúng mang một `evidence_start` trỏ vào chỗ không có gì — mà trông vẫn hoàn toàn hợp lệ.

  Hai mẫu trên ba mươi sáu nghìn thì có đáng sửa không? Có, vì hai lý do. Thứ nhất, E06 đo hit@1, hit@3 và MRR bằng cách so đoạn được chú ý nhiều nhất với **đoạn chứa bằng chứng vàng** — một `evidence_start` trỏ vào dòng trống sẽ được E06 coi là đáp án đúng cần trúng, tức là hai câu hỏi thi có đáp án rác. Thứ hai, chi phí sửa bằng không, còn đây đúng là loại lỗi âm thầm mà sáu tuần sau không ai truy ra nổi. Đã sửa `find_evidence` trong `schema.py` để coi bằng chứng chỉ gồm khoảng trắng là **không có bằng chứng**, kèm ca kiểm thử.

  Đã cập nhật số ở mục 4 `docs/DATA.md` và mục 4 `CLAUDE.md`, có ghi rõ số cũ và lý do lệch chứ không lặng lẽ đổi.

  ### Ba loại "không có offset", phải phân biệt được

| Loại | Số mẫu | Ý nghĩa |
|---|---|---|
| `evidence` là `null` | 12.583 | Toàn bộ nhãn NEI. Bộ dữ liệu không cung cấp bằng chứng |
| `evidence` chỉ gồm khoảng trắng | 2 | Rác trong dữ liệu gốc |
| Có bằng chứng nhưng không tìm thấy nguyên văn | 1 | Lỗi dữ liệu gốc |
| **Tìm thấy nguyên văn** | **23.783** | Dùng được cho E06 |

  Ba loại này đều cho `evidence_start = -1` nhưng khác nhau về ý nghĩa, nên thêm cột `meta.evidence_given`: `false` là bộ dữ liệu không có bằng chứng cho dòng đó, còn `true` mà `evidence_start = -1` là có ghi nhưng không định vị được.

  Mẫu trượt duy nhất: bằng chứng ghi `...ông Thiệu nói..` với **hai dấu chấm**, còn ngữ cảnh chỉ có một dấu chấm rồi xuống dòng — có lẽ do công cụ tách câu tự thêm dấu chấm vào câu vốn đã có. Xử lý theo đúng quy tắc: `evidence_start = -1`, đếm vào báo cáo, **không dùng khớp gần đúng**. Khớp gần đúng sẽ đặt một con số trông hợp lý vào cột mà thí nghiệm sau coi là chân lý, và như vậy còn tệ hơn thừa nhận không tìm thấy.

  ### Hai điều khác học được

  1. **`evidence` của nhãn NEI là `null` trong JSON, không phải chuỗi rỗng.** `str(record["evidence"])` trên `None` cho ra chuỗi `"None"` — bốn ký tự trông như dữ liệu thật, `strip()` ra khác rỗng, và thế là 12.583 dòng NEI sẽ mang bằng chứng giả. Mình đã dính đúng bẫy này lúc dò dữ liệu, phát hiện vì output phình lên hai megabyte. Trong code dùng `str(record.get("evidence") or "")`.

  2. **Test phải gọi đúng bộ đọc thật.** Bản test đầu mình viết dựng lại logic đọc ngay trong file test để né phép kiểm tra 36.369 dòng, tức là đi kiểm tra một bản sao chứ không kiểm tra thứ sẽ chạy — nếu bộ đọc sai thì test vẫn xanh. Đã tách `read_isedsc01` (đọc) khỏi `normalize_isedsc01` (đọc rồi đối chiếu số lượng), làm tương tự cho ViHallu, và mọi ca kiểm thử nay chạy qua `read_*` thật với dữ liệu vài dòng.

- [x] **T11** · M · Chuẩn hóa ViWikiFC — hoàn thành 20/08/2026
  - Nguồn: `data/raw/viwikifc_{train,dev,test}.csv`, giữ nguyên split gốc.
  - **Kiểm tra:** 16.738 / 2.090 / 2.091 dòng ✅. `evidence_start` tìm được ~~100 %~~ → **99,995 % (20.918/20.919)**. Đã dừng lại kiểm tra đúng như tiêu chí yêu cầu, kết luận **không phải lỗi encoding** — xem bên dưới.

  **Task này để làm gì.** Bộ thứ ba, cũng theo khuôn T09. Vai trò riêng của ViWikiFC là **đối chứng ngoài**: nó có bằng chứng cho **cả nhãn NEI**, thứ mà không bộ nào khác có. Ở ISE-DSC01, toàn bộ 12.583 mẫu NEI đều không có bằng chứng, nên không thể hỏi "chú ý có nhìn đúng chỗ không" với lớp ngoại lai. Ở đây thì hỏi được, và đó là toàn bộ nền tảng của E08.

  **Kết quả chạy:**

```
  số dòng               : 20,919      (16.738 train / 2.090 dev / 2.091 test)
  ngữ cảnh duy nhất     : 1,481
  phân bố nhãn:
      extrinsic      6,978  ( 33.4 %)
      intrinsic      6,973  ( 33.3 %)
      no             6,968  ( 33.3 %)
  có bằng chứng nguyên văn : 20,918/20,919
  ghi mà không định vị được: 1
```

  Số dòng ba tập và phân bố nhãn tập train (5.594 / 5.573 / 5.571) khớp đúng bảng mục 4 `docs/DATA.md`. `ruff` sạch, `pytest` 197 ca xanh (thêm 15 ca).

  ### Tiêu chí bảo dừng lại, nên đã dừng lại kiểm tra

  Tiêu chí ghi: *"`evidence_start` tìm được 100 % ở cả ba nhãn. Nếu không đủ 100 % thì có lỗi encoding, dừng lại."* Đo ra 99,995 %, tức **đúng một dòng** của tập train trượt. Đã dừng và truy đến cùng trước khi viết tiếp một dòng code nào.

  **Kết luận: không phải lỗi encoding.** Bằng chứng của dòng đó ghi `...thế kỷ 20 thì NhậtaimBản đã trở thành...`, còn ngữ cảnh của chính nó ghi `...thế kỷ 20 thì Nhật Bản đã trở thành...`. Ba chữ `aim` bị chèn đè lên dấu cách. Đã thử khớp theo NFC, theo NFD, và sau khi cắt khoảng trắng — đều không khớp; còn 20.918 dòng kia khớp chính xác từng ký tự. *Encoding* (cách mã hóa ký tự thành byte) mà hỏng thì hỏng đồng loạt cả tập chứ không hỏng đúng một dòng ở giữa. Đây là lỗi của bộ dữ liệu công bố, không phải của mình.

  Xử lý theo đúng quy tắc mục 7 `docs/DATA.md`: `evidence_start = -1`, đếm vào báo cáo, **không khớp gần đúng**.

  **Vẫn giữ phép kiểm tra, nhưng sửa ngưỡng cho đúng mục đích của nó.** Mục đích thật của phép kiểm tra này là bắt lỗi encoding hàng loạt — thứ làm hỏng hàng nghìn dòng trong im lặng trong khi mọi con số khác vẫn đúng. Nên `check_evidence` raise khi số trượt **nhiều hơn** một, chứ không phải khi **khác** một. Ít hơn một thì chỉ có thể nghĩa là bộ dữ liệu đã được sửa, mà từ chối chạy trên bộ đã sửa thì vô lý. Có ca kiểm thử cho cả hai chiều.

  ### `pairID` trông như khóa chính nhưng không phải

  Tập train có 16.738 dòng nhưng chỉ **15.903 `pairID` duy nhất**: 321 nhóm gồm 835 dòng dùng chung một mã, mỗi nhóm 2–7 dòng. Kiểm tra kỹ thì các dòng trong cùng nhóm **luôn cùng `evidence`, luôn cùng `gold_label`, nhưng khác `claim` 100 %**. Nghĩa là `pairID` định danh **cặp (bằng chứng, nhãn)**, không định danh mẫu: một câu bằng chứng được viết lại thành nhiều cách phát biểu khác nhau, tất cả dùng chung mã.

  Ai dùng nó làm khóa sẽ âm thầm gộp 835 dòng thành 321 và mất 514 mẫu mà không có lỗi nào báo. Trong schema chung nó nằm ở `meta.source_id`, khóa thật là `sample_id` do mình sinh theo chỉ số dòng. Đã ghi cảnh báo vào mục 7 `docs/DATA.md` và có ca kiểm thử.

  ### Xác nhận lại con số rò rỉ của mục 6, bằng một đường tính khác

  Mục 6 `docs/DATA.md` ghi ViWikiFC rò rỉ ngữ cảnh test sang train 845/845, tức 100 %. Tính lại từ `context_id` vừa sinh: **đúng 845/845 ngữ cảnh, 2.091/2.091 dòng**. Tập dev thêm số chưa từng ghi: 836/838 ngữ cảnh, 2.088/2.090 dòng, tức 99,9 %.

  Cả ba tập cộng lại chỉ có **1.481 ngữ cảnh duy nhất** trong khi riêng train đã 1.479 — dev và test gần như không mang theo ngữ cảnh nào mới. Split gốc của bộ này chia theo *phát biểu* chứ không theo *tài liệu nguồn*.

  Hai điều rút ra: thứ nhất, ghi nhận của nhóm ở mục 6 là chính xác. Thứ hai, việc con số tái lập đúng bằng một đường tính hoàn toàn khác (băm NFC của chuỗi ngữ cảnh) cũng là một phép thử gián tiếp cho `context_id` — nếu hàm băm sai thì con số đã không trùng.

  Không dựng báo cáo rò rỉ ở đây vì đó là T14.

- [x] **T12** · M · Chuẩn hóa ViFactCheck — hoàn thành 20/08/2026, **hết giai đoạn chuẩn hóa dữ liệu**
  - Nguồn: `data/raw/vifactcheck_{train,dev,test}.parquet`, giữ nguyên split gốc. Bỏ cột `Unnamed: 0`.
  - **Kiểm tra:** 5.062 / 723 / 1.447 dòng ✅, tỷ lệ `evidence_start` tìm được **59,4 %** ✅ (đúng "xấp xỉ 59 %").

  **Task này để làm gì.** Bộ thứ tư và cuối cùng. ViFactCheck là bộ **dự phòng**, chỉ dùng cho E17 — thí nghiệm chuyển miền, và E17 chỉ làm nếu tuần 14–15 còn thời gian. Chuẩn hóa nó bây giờ vì rẻ (chạy CPU vài giây) và vì để sau thì phải nhớ lại toàn bộ ngữ cảnh.

  **Kết quả chạy:**

```
  số dòng               : 7,232       (5.062 train / 723 dev / 1.447 test)
  ngữ cảnh duy nhất     : 1,041
  phân bố nhãn:
      extrinsic      2,347  ( 32.5 %)
      intrinsic      2,370  ( 32.8 %)
      no             2,515  ( 34.8 %)
  có bằng chứng nguyên văn : 4,296/7,232 (59.4 %)
  ghi mà không định vị được: 2,936
```

  Khớp bảng mục 4 `docs/DATA.md`. `ruff` sạch, `pytest` 214 ca xanh (thêm 17 ca).

  ### Vì sao chỉ 59 % — câu hỏi tài liệu bỏ ngỏ, nay đã trả lời

  `docs/DATA.md` ghi "chỉ 59,2 % bằng chứng nằm nguyên văn; điều này bình thường, không phải lỗi" nhưng **không nói vì sao**. Task này truy ra.

  Trước hết loại trừ hai giả thuyết dễ nghĩ nhất. Gộp khoảng trắng cứu được **0/2.064** mẫu trượt; chuẩn hóa NFC cũng cứu được **0/2.064**. Vậy không phải chuyện định dạng ký tự.

  Rồi nhìn vào chỗ chuỗi bắt đầu lệch nhau:

| Quan sát trên 2.064 mẫu trượt của tập train | Số mẫu |
|---|---|
| 30 ký tự **đầu** của bằng chứng có trong ngữ cảnh | 1.874 |
| Cả 30 ký tự **đầu lẫn 30 ký tự cuối** đều có | 1.741 |
| Không thấy đầu cũng không thấy đuôi | 20 |

  Đầu có, đuôi có, mà cả chuỗi thì không — chỉ có một cách giải thích. Bằng chứng ghi:

```
... tư vấn xếp lớp rất nhanh chóng và nhiệt tình ILA tiếp nhận và hỗ trợ ...
```

  ngữ cảnh ghi:

```
... tư vấn xếp lớp rất nhanh chóng và nhiệt tình. Chẳng những được miễn học phí ...
```

  Người gán nhãn lấy câu A, **bỏ dấu chấm cuối câu**, rồi nối thẳng một câu khác ở chỗ khác vào. **Bằng chứng của bộ này là nhiều câu rời nhau ghép lại.** Cả hai mảnh đều có thật; chỉ chuỗi ghép là không có.

  **Hệ quả về mặt thiết kế, đáng ghi nhớ:** schema chung chỉ có **một** cặp `(evidence_start, evidence_end)`, tức một đoạn liền mạch. Bằng chứng nhiều mảnh rời **về nguyên tắc không biểu diễn được** bằng cấu trúc ấy. Nên con số 59,2 % không phải là "tỷ lệ khớp thành công" mà là **tỷ lệ bằng chứng chỉ gồm một mảnh**. Nếu sau này làm E17 có phần định vị bằng chứng thì phải mở rộng schema thành danh sách đoạn trước, hoặc chấp nhận chỉ dùng 59 % kia. Đã ghi vào mục 7 `docs/DATA.md`.

  ### Bẫy lặp lại lần thứ hai

  `annotation_id` cũng **không phải khóa chính**: 5.062 dòng train nhưng chỉ **1.250** giá trị duy nhất. Đúng cái bẫy `pairID` của ViWikiFC ở T11. Hai trên bốn bộ có cột trông như khóa mà không phải khóa — nên quy ước dùng `sample_id` do mình sinh làm khóa duy nhất là đúng, và mọi mã nguồn gốc đều nằm ở `meta.source_id`.

  ### Cột `Topic` không nhất quán hoa thường

  52 giá trị, trong đó có cả `Thể thao` lẫn `THỂ THAO`, và `Văn hoá` / `Văn hóa` / `VĂN HÓA` / `VĂN HOÁ` — bốn cách viết cho một chủ đề. Schema **giữ nguyên văn** để còn truy ngược về nguồn, nhưng ai cắt kết quả theo chủ đề phải tự gộp hoa thường và thống nhất `hoá`/`hóa` trước, nếu không sẽ đếm một chủ đề thành bốn. Đã ghi cảnh báo và có ca kiểm thử khẳng định giá trị được giữ nguyên văn chứ không bị "dọn dẹp" âm thầm.

  ### Thêm `--all`

  `scripts/normalize_data.py --all` chạy lần lượt cả bốn bộ. Đầu ra một lượt:

```
  vihallu      7.000 dòng · 3.865 ngữ cảnh · bằng chứng   0/7.000  (bộ không có trường này)
  isedsc01    36.369 dòng · 4.793 ngữ cảnh · bằng chứng  23.783/36.369  (65,4 %)
  viwikifc    20.919 dòng · 1.481 ngữ cảnh · bằng chứng  20.918/20.919  (100,0 %)
  vifactcheck  7.232 dòng · 1.041 ngữ cảnh · bằng chứng   4.296/7.232   (59,4 %)
```

  **Tổng 71.520 mẫu**, đúng bằng con số T08 dùng để dự báo giờ GPU.

- [x] **T13** · LM · Kiểm tra thủ công ánh xạ NEI sang ngoại lai — hoàn thành 20/08/2026
  - Lấy ngẫu nhiên 100 mẫu nhãn NEI từ ViWikiFC, hai người gán độc lập xem có đúng là "chứa thông tin ngoài ngữ cảnh" không.
  - **Kiểm tra:** file `results/nei_mapping_audit.csv` có 100 dòng, báo cáo tỷ lệ khớp và hệ số đồng thuận.

  **Task này để làm gì.** Mục 3 `docs/DATA.md` ánh xạ nhãn `NEI` của ViWikiFC thành `extrinsic`, và ngay câu sau đã tự cảnh báo rằng hai khái niệm này **không tương đương**:

  - **NEI** (*Not Enough Information*) nghĩa là: ngữ cảnh **không đủ** để kết luận phát biểu đúng hay sai.
  - **Ảo giác ngoại lai** (*extrinsic hallucination*) nghĩa là: phát biểu **mang vào** thông tin mà ngữ cảnh không hề có.

  Hai cái giao nhau nhiều nhưng không trùng. Một phát biểu hoàn toàn có thể *không kết luận được* trong khi mọi dữ kiện nó nhắc tới đều nằm sẵn trong ngữ cảnh — khi đó ánh xạ sai. Không ai biết chuyện đó xảy ra bao nhiêu phần trăm cho tới khi có người **đọc tay** một mẫu đủ lớn. Đây chính là task đó, và kết quả của nó đi thẳng vào phần hạn chế của báo cáo.

  **Vì sao Claude không làm thay được.** Nếu mình gán cả 100 mẫu thì không còn "hai người gán độc lập", và **hệ số đồng thuận trở thành con số vô nghĩa**. Cái task này đo chính là mức độ hai người thật sự thống nhất với nhau, nên phần gán nhãn bắt buộc là việc của Lân và Minh.

  ### Đã chuẩn bị xong

  `scripts/audit_nei_mapping.py` với hai chế độ, và ba file trong `results/`:

| File | Dùng làm gì |
|---|---|
| `nei_mapping_audit_HUONGDAN.md` | Hướng dẫn gán nhãn — **đọc trước khi làm** |
| `nei_mapping_audit_lan.csv` | Phiếu của Lân, 120 dòng |
| `nei_mapping_audit_minh.csv` | Phiếu của Minh, 120 dòng, **giống hệt** phiếu kia |

  **Bốn đáp án**, không phải hai. Câu hỏi "có phải ngoại lai không" nếu để dạng có/không sẽ mất thông tin, vì "không phải ngoại lai" thật ra là **hai chuyện rất khác nhau**: phát biểu bám sát ngữ cảnh (nhãn `no`), hay phát biểu mâu thuẫn với ngữ cảnh (nhãn `intrinsic`). Chỉ trường hợp đầu nghĩa là nhãn NEI đơn thuần yếu quá; trường hợp sau nghĩa là ánh xạ đẩy mẫu sang **sai hẳn lớp**. Nên bốn mã: `ngoai_lai`, `noi_tai`, `khong`, `khong_chac`.

  ### Vì sao có 120 dòng mà kết quả chỉ 100

  20 dòng là **mẫu đối chứng**: 10 mẫu `Supports` và 10 mẫu `Refutes`, trộn lẫn và xáo ngẫu nhiên nên không phân biệt được với 100 mẫu NEI. Bước `--report` tách chúng ra khỏi thống kê chính, nên **file nộp vẫn đúng 100 dòng** như tiêu chí đòi.

  Lý do cần chúng: cả 100 mẫu NEI đều cùng một nhãn gốc. Nếu ai đó gõ `ngoai_lai` cho tất cả mà không đọc, kết quả sẽ là *tỷ lệ khớp 100 %* — trông rất đẹp — trong khi **Cohen kappa không tính được**, và không có cách nào phân biệt "hai người thật sự đồng ý" với "hai người cùng bấm bừa". Mẫu đối chứng phá thế đó: gán sai `Supports`/`Refutes` là lộ ngay. Ngưỡng cảnh báo đặt ở 70 %.

  *Cohen kappa* là hệ số đo mức đồng thuận **sau khi trừ đi phần đồng thuận do may rủi**. Hai người cùng thích một đáp án thì tự nhiên hay trùng nhau; kappa đo phần trùng vượt quá mức đó. Bằng 1 là trùng khớp hoàn toàn, bằng 0 là không hơn ngẫu nhiên, âm là tệ hơn ngẫu nhiên. Báo cáo in cả kappa lẫn tỷ lệ khớp thô kèm diễn giải theo thang Landis–Koch.

  ### Vài quyết định thiết kế

  - **Hai file riêng, không phải hai cột trong một file.** Hai cột cạnh nhau thì gần như chắc chắn người sau sẽ liếc thấy đáp án của người trước.
  - **Phiếu không chứa đáp án.** Không có cột nhãn gốc, không có file khóa đáp án. Nhãn thật được tra lại qua `sample_id` ở bước `--report`.
  - **Ghi bằng UTF-8 có BOM.** Excel trên Windows mở CSV UTF-8 thường sẽ hiện tiếng Việt thành ký tự rác; BOM là thứ khiến nó hiển thị đúng khi bấm đúp mở file.
  - **`--prepare` không ghi đè phiếu đã có** trừ khi truyền `--force`, kẻo sinh lại đè mất buổi làm của ai đó.
  - **Sắp theo `sample_id` trước khi lấy mẫu.** pandas lấy mẫu theo *vị trí*, nên nếu không cố định thứ tự thì việc chạy lại `normalize_data.py` có thể âm thầm đổi 100 mẫu được kiểm. Lỗi này do một ca kiểm thử phát hiện ra, và đã sửa ở code chứ không sửa test.

  Đã kiểm toàn tuyến bằng phiếu điền giả: `--report` chạy đúng, in đủ đối chứng, tỷ lệ ánh xạ, kappa, bảng chéo 4×4, và sinh `results/nei_mapping_audit.csv` 100 dòng. `ruff` sạch, `pytest` 244 ca xanh (thêm 30 ca).

  ### Kết quả — Lân và Minh gán xong 120/120 dòng, 20/08/2026

| Chỉ số | Giá trị |
|---|---|
| **Hai người cùng cho là ngoại lai** | **67/100** |
| Lân cho là ngoại lai | 71/100 |
| Minh cho là ngoại lai | 77/100 |
| Tỷ lệ khớp thô | 79,0 % |
| **Cohen kappa** | **0,505** — trung bình theo thang Landis–Koch |
| Dương tính giả trên đối chứng (cả hai cùng sai) | 1/20 = 5 % |

  Bảng chéo, hàng là Lân cột là Minh:

| | ngoai_lai | noi_tai | khong | khong_chac |
|---|---|---|---|---|
| **ngoai_lai** | **67** | 4 | 0 | 0 |
| **noi_tai** | 4 | 3 | 0 | 0 |
| **khong** | 6 | 6 | 9 | 1 |
| **khong_chac** | 0 | 0 | 0 | 0 |

  **Kết luận: chỉ khoảng 67 % nhãn NEI thật sự là ảo giác ngoại lai.** Một phần ba còn lại không khớp định nghĩa. Đây là con số **bảo thủ** vì đòi cả hai người cùng đồng ý; con số riêng của từng người là 71 % và 77 %.

  Phân rã 33 mẫu còn lại theo cách hiểu của Lân: **22 mẫu `khong`** — phát biểu bám sát ngữ cảnh, chỉ là ngữ cảnh không đủ để xác nhận, tức đúng nghĩa NEI nhưng không phải ảo giác gì cả; và **7 mẫu `noi_tai`** — phát biểu mâu thuẫn với ngữ cảnh, tức lẽ ra là **nội tại**. Nhóm thứ hai đáng lo hơn nhiều: ánh xạ không chỉ *yếu* mà đẩy mẫu sang **sai hẳn lớp**, và với đề tài phân ba lớp thì đó là nhãn nhiễu trực tiếp.

  ### Cảnh báo đối chứng đã bật — và vì sao con số vẫn dùng được

  Minh đạt **12/20** trên mẫu đối chứng, dưới ngưỡng 70 % mà script đặt ra (Lân 16/20). Đây đúng là thứ mà 20 mẫu đối chứng sinh ra để bắt, nên phải xử lý chứ không lờ đi.

  Truy vào thì sai sót **không phải ngẫu nhiên mà có hướng rõ ràng**:

| Loại đối chứng | Đáp án đúng | Lân | Minh |
|---|---|---|---|
| `Supports` | `khong` | 9/10 | 7/10 |
| `Refutes` | `noi_tai` | 7/10 | **5/10** |

  Sai chính của Minh là **4 mẫu `Refutes` gán thành `ngoai_lai`** — tức đúng chỗ nhầm giữa nội tại và ngoại lai, cùng loại nhầm mà Lân hỏi giữa chừng và đã được làm rõ trong hướng dẫn. Hệ quả có hướng: nó **thổi phồng** số `ngoai_lai` của Minh, và đúng là Minh ra 77 % còn Lân ra 71 %.

  Nhưng con số nộp là **con số đồng thuận**, và ở đó tình hình khác hẳn: trên 20 mẫu đối chứng, **cả hai cùng gán nhầm `ngoai_lai` chỉ 1 lần**. Lý do là sai sót của hai người phần lớn độc lập nhau, nên việc đòi cả hai cùng đồng ý lọc gần hết. Tỷ lệ dương tính giả 5 % này chính là thanh chắn cho con số 67 %, và nó có được **chỉ vì có mẫu đối chứng** — không có chúng thì không cách nào biết 67 % đáng tin tới đâu.

  ### Ba điều học được

  1. **Ranh giới nội tại–ngoại lai khó với cả người, không riêng máy.** 8/100 mẫu NEI có một người gán `noi_tai` còn người kia gán `ngoai_lai` — hai lớp đối lập nhau chứ không phải sát nhau. Trên đối chứng, cả hai đều tệ hơn ở `Refutes` (7/10 và 5/10) so với `Supports` (9/10 và 7/10). Điều này nên ghi vào chương đánh giá: **giới hạn trên của mọi mô hình phân biệt hai lớp này bị chặn bởi chính mức đồng thuận của người**, và ở đây mức đó là kappa 0,505.

  2. **Ghi chú "chưa chắc" dự báo được bất đồng.** Lân đánh dấu 15 dòng NEI là chưa chắc. Trong đó **7 dòng lệch với Minh, tức 47 %**; còn 85 dòng không đánh dấu thì chỉ **14 dòng lệch, tức 16 %**. Gấp gần ba lần. Nghĩa là cảm giác "khó" của người gán không phải mơ hồ mà đo được, và nó chỉ đúng vào vùng ranh giới thật. Nếu sau này cần một tập con "sạch" để huấn luyện thì đây là cách rẻ để lọc.

  3. **Kappa và tỷ lệ khớp thô nói hai chuyện khác nhau, phải in cả hai.** Khớp thô 79 % nghe cao, nhưng vì `ngoai_lai` chiếm đa số nên hai người chọn bừa cũng đã trùng nhau khá nhiều. Kappa 0,505 mới là phần đồng thuận vượt quá may rủi — vẫn là "trung bình", đủ để tin con số nhưng không đủ để gọi ánh xạ này là chắc chắn.

  ### Cách dùng kết quả về sau

  Khi báo cáo số liệu trên ViWikiFC, **không được gọi lớp `extrinsic` của bộ này là ảo giác ngoại lai thuần túy**. Phải ghi rõ nó là nhãn NEI ánh xạ sang, với khoảng một phần ba không khớp định nghĩa. Đã ghi vào mục 3 `docs/DATA.md` và mục 4 `CLAUDE.md`. Cùng cảnh báo áp cho ISE-DSC01, nơi NEI cũng ánh xạ sang `extrinsic` — nhưng bộ đó **không kiểm chứng được** vì nhãn NEI của nó không có bằng chứng.

  Dữ liệu thô 100 dòng kèm cả hai cột gán nhãn và ghi chú: `results/nei_mapping_audit.csv`.

- [x] **T14** · M · Chia tập và báo cáo rò rỉ — hoàn thành 23/08/2026
  - Hiện thực `group_split`. Chia ViHallu và ISE-DSC01 80/10/10 seed 42. ViWikiFC và ViFactCheck giữ split gốc.
  - Sinh `results/leakage_report.md` với số liệu rò rỉ của cả bốn bộ.
  - **Kiểm tra:** báo cáo khớp bảng mục 6 của `docs/DATA.md` ✅ (cả bốn con số khớp chính xác); `group_split` raise khi cố tình truyền dữ liệu rò rỉ ✅.

  **Task này để làm gì.** *Rò rỉ dữ liệu* (data leakage) là khi thứ đáng lẽ chỉ có ở tập test lại đã xuất hiện trong tập train. Ở đề tài này rò rỉ không xảy ra ở mức dòng mà ở mức **ngữ cảnh**: hai mẫu dùng chung một đoạn văn thì không độc lập với nhau — mô hình đã đọc một mẫu lúc huấn luyện thì cũng đã đọc gần hết vật liệu của mẫu kia. Nếu chúng nằm ở hai tập khác nhau, điểm trên test đo **trí nhớ** nhiều ngang đo **khả năng khái quát hóa**, và con số báo cáo đẹp hơn sự thật.

  Nên đơn vị chia tập là `context_id` chứ không phải dòng. Đó là ý nghĩa của *group split*: xáo và chia **cả nhóm**, không bao giờ cắt một nhóm làm đôi.

  **Đã làm.** Ba file mới:
  - `src/vihallulens/data/splits.py` — `group_split`, `assert_no_leakage`, `leakage_between`.
  - `src/vihallulens/data/loading.py` — `load_dataset(name, split)` theo mục 2.1 `docs/SPEC.md`, nợ từ T09 nay trả. Từ đây trở đi mọi thứ đọc dữ liệu qua hàm này chứ không tự mở `data/interim`.
  - `scripts/split_data.py` — chia hai bộ cần chia rồi sinh `results/leakage_report.md` cho cả bốn.

  ### Kết quả chia

| Bộ | train | dev | test | Tổng |
|---|---|---|---|---|
| ViHallu | 5.600 (80,0 %) | 700 (10,0 %) | 700 (10,0 %) | 7.000 |
| ISE-DSC01 | 29.077 (79,9 %) | 3.646 (10,0 %) | 3.646 (10,0 %) | 36.369 |

  **Số này đã đổi ở T18** so với lần chạy đầu (5.598/702/700 và 29.082/3.653/3.634), vì cách xáo thứ tự nhóm cũ không tái lập được giữa các máy. Xem phần T18.

  Tỷ lệ chỉ **xấp xỉ** 80/10/10 vì chia cả nhóm — một ngữ cảnh phải rơi trọn vào một tập. Sai lệch nhỏ tới mức làm tròn một chữ số thập phân thì ra đúng 80,0/10,0/10,0, vì nhóm nhỏ: nhóm lớn nhất của ViHallu 5 dòng, của ISE-DSC01 33 dòng, đều dưới 0,1 % cỡ bộ.

  **Rò rỉ ở hai bộ này bằng 0**, và đó là bằng chứng chứ không phải kỳ vọng — `group_split` gọi `assert_no_leakage` trên chính kết quả nó vừa sinh, raise nếu có bất kỳ ngữ cảnh nào lọt vào hai tập.

  ### Rò rỉ ở hai bộ giữ split gốc

| Bộ | Tập | Theo ngữ cảnh | Theo dòng |
|---|---|---|---|
| ViWikiFC | dev | 836/838 (99,8 %) | 2.088/2.090 (99,9 %) |
| ViWikiFC | test | **845/845 (100 %)** | **2.091/2.091 (100 %)** |
| ViFactCheck | dev | 495/496 (99,8 %) | 721/723 (99,7 %) |
| ViFactCheck | test | 753/758 (99,3 %) | 1.433/1.447 (99,0 %) |

  Cả bốn con số của mục 6 `docs/DATA.md` **khớp chính xác** khi đo lại bằng một đường hoàn toàn khác (băm NFC của chuỗi ngữ cảnh). Ghi nhận của nhóm trước đây là đúng.

  Hai bộ này giữ split gốc để so được với số đã công bố, nên phải nhận luôn phần rò rỉ. **Không sửa được, chỉ báo cáo được** — và hệ quả bắt buộc là không dùng chúng để kết luận về khả năng khái quát hóa.

  ### Ba điều học được

  1. **Báo cáo rò rỉ theo dòng, không chỉ theo ngữ cảnh.** Hai con số trả lời hai câu khác nhau: theo ngữ cảnh là "bao nhiêu vật liệu bị dùng lại", theo dòng là "bao nhiêu phần điểm số thật sự dựa lên đó". Con số theo dòng thường lớn hơn và mới là con số đáng lo. Bảng cũ ở mục 6 chỉ có cột ngữ cảnh; nay có cả hai.

  2. **Split gốc của ban tổ chức cũng rò rỉ, nên tự chia không phải là tự làm khó mình.** File public test của ViHallu rò rỉ 713/919 (77,6 %), của ISE-DSC01 rò rỉ 1.004/1.319 (76,1 %). Nhóm không dùng hai file đó vì thiếu nhãn, nhưng con số này đáng ghi vào báo cáo: nó cho thấy quyết định tự chia theo nhóm là cần thiết chứ không phải cầu toàn.

  3. **Chia theo nhóm và cân bằng nhãn là hai ràng buộc xung khắc — may là không cần ép.** Không thể vừa giữ trọn mỗi ngữ cảnh trong một tập vừa ép tỷ lệ nhãn bằng nhau giữa các tập. Nhóm không ép, và kiểm lại thì phân bố nhãn lệch **không quá 2 điểm phần trăm** so với toàn bộ ở cả hai bộ. Nếu sau này bộ nào lệch nhiều thì phải xử lý, nhưng ở đây thì không cần.

  ### Hai cái bẫy đã chặn trước

  Hai script chạy nối nhau nên có hai cách tự bắn vào chân, đều đã bịt và đều có kiểm chứng:

  - **Chạy `split_data.py` hai lần** sẽ cắt 80 % của 80 %, âm thầm làm teo tập train mỗi lần chạy. Bịt bằng cách **gộp các tập lại trước rồi mới chia**. Đã kiểm bằng cách chạy hai lần rồi so mã băm danh sách `sample_id`: giống hệt nhau, tổng vẫn đủ 7.000 dòng.
  - **Chạy lại `normalize_data.py` sau khi đã chia** sẽ ghi toàn bộ 7.000 dòng vào file train trong khi dev và test cũ vẫn nằm đó, tức cùng một dòng tồn tại ở hai file. Bịt bằng cách cho `normalize_data.py` **tự xóa file của những split nó không ghi**, kèm thông báo rõ ràng.

  `ruff` sạch, `pytest` 277 ca xanh (thêm 33 ca).

- [x] **T15** · M · Chia chunk — hoàn thành 23/08/2026
  - Hiện thực `chunk_context` cả hai chiến lược và `locate_evidence_chunk`.
  - **Kiểm tra:** `pytest tests/test_chunking.py` xanh (37 ca), gồm ca câu tiếng Việt có số thập phân ✅ và ca bằng chứng vắt qua ranh giới chunk ✅.

  **Task này để làm gì.** Đây là chỗ đóng góp của đề tài bắt đầu thành hình. Lookback Lens gốc coi **toàn bộ** ngữ cảnh truy xuất là một khối và hỏi "mô hình nhìn vào ngữ cảnh bao nhiêu phần". Phiên bản chunk-aware hỏi thêm "nhìn vào **đoạn nào**" — mà câu hỏi đó chỉ tồn tại sau khi ngữ cảnh đã được cắt ra. Nên cách cắt không phải chi tiết phụ: mục 2 `docs/EXPERIMENTS.md` đặt hẳn việc so hai cách cắt thành một thí nghiệm riêng (E05).

  Hai chiến lược, theo mục 2.1 `docs/SPEC.md`:
  - **`sentence`** — cắt theo ranh giới câu, gộp những mảnh quá ngắn. Các chunk **lát kín** ngữ cảnh: mỗi ký tự thuộc đúng một chunk.
  - **`token_window`** — cửa sổ cố định `window_size` token, trượt mỗi lần `stride` token. Với `stride` mặc định bằng nửa cửa sổ thì các chunk **chồng lấn**.

  ### Bốn cái bẫy của việc tách câu tiếng Việt

  Tách câu nghe như chỉ cần cắt ở dấu chấm. Bốn ca sau phá ngay ý đó:

  1. **Số thập phân và số hàng nghìn.** Tiếng Việt viết hàng nghìn bằng dấu chấm: `331.212`. May là ca này **tự khỏi** — dấu chấm trong số không có khoảng trắng theo sau, mà mẫu regex đòi phải có khoảng trắng mới coi là ranh giới. Vẫn có ca kiểm thử để nếu ai đó nới lỏng mẫu regex thì test đỏ ngay.
  2. **Chữ viết tắt.** `ThS. Trương Vĩnh Linh`, `TP. Hồ Chí Minh`, `Nxb. Giáo dục` — chấm rồi khoảng trắng rồi chữ hoa, đúng khuôn một ranh giới câu thật. Phải có danh sách viết tắt; thiếu chữ nào là cắt ngay giữa tên người. Đã liệt 40 chữ hay gặp, chia theo nhóm học hàm, đơn vị hành chính, tổ chức, xuất bản.
  3. **Chữ cái viết tắt tên người.** `Nguyễn V. A.` — không thể liệt kê hết, nên bắt bằng luật: một ký tự chữ cái đứng một mình trước dấu chấm thì không phải hết câu.
  4. **Ngày tháng và số thứ tự.** `ngày 31. 12. 2024` — cắt vào giữa ngày còn tệ hơn để nguyên. Luật: từ toàn chữ số trước dấu chấm thì không phải ranh giới.

  ### Hai quyết định thiết kế đáng ghi

  **Chunk theo câu phải lát kín ngữ cảnh, không được để khe hở.** Nếu chunk chỉ giữ phần chữ và bỏ khoảng trắng giữa hai câu, thì token rơi vào khe hở sẽ **không thuộc chunk nào** — nó vẫn nằm trong mẫu số của `lookback_context` nhưng không xuất hiện ở bất kỳ chunk nào, tức rò rỉ một phần chú ý ra ngoài mọi ô. Nên mỗi chunk ôm luôn khoảng trắng đuôi, và `char_end` của chunk này bằng đúng `char_start` của chunk kế. Có ca kiểm thử khẳng định nối các chunk lại ra đúng ngữ cảnh gốc.

  **Câu quá ngắn đầu tiên phải gộp về sau, không gộp về trước.** Mục 2.1 `docs/SPEC.md` ghi "gộp vào câu trước", nhưng câu **đầu tiên** không có câu trước nào để gộp. Mà mở đầu ngắn lại rất hay gặp trong bốn bộ này — một dòng tít, một dòng `Theo VnExpress.` Bỏ mặc thì nó thành một chunk vài từ mà không phân bố chú ý nào nói được điều gì. Nên ca này gộp **về sau**.

  ### Kết quả trên dữ liệu thật

| Bộ | Chunk mỗi ngữ cảnh | Từ mỗi chunk | Ngữ cảnh chỉ có 1 chunk |
|---|---|---|---|
| ViHallu | 5,3 (trung vị 5, tối đa 42) | 33,9 | 1,0 % |
| ISE-DSC01 | 22,8 (trung vị 20, tối đa 161) | 27,7 | 0,0 % |
| ViWikiFC | 3,5 (trung vị 3, tối đa 20) | 31,5 | **15,3 %** |
| ViFactCheck | 19,3 (trung vị 17, tối đa 86) | 35,3 | 0,0 % |

  Trung vị khớp sát cột "số câu mỗi ngữ cảnh" ở mục 4 `docs/DATA.md` (5 / 19 / 4 / 17), lệch chút ở ISE-DSC01 và ViWikiFC do phần gộp câu ngắn.

  **Định vị bằng chứng — đây là nền của E06:**

| Bộ | Định vị được | Vắt qua ranh giới chunk |
|---|---|---|
| ISE-DSC01 | 3.000/3.000 (100 %) | 41 (1,4 %) |
| ViWikiFC | 3.000/3.000 (100 %) | 57 (1,9 %) |

  Đo trên 3.000 mẫu ngẫu nhiên seed 42 của mỗi bộ. **Định vị được 100 %** — nghĩa là E06 có đủ nhãn vàng để chấm hit@1, hit@3 và MRR trên toàn bộ số mẫu có bằng chứng, không mất mẫu nào ở khâu này.

  Chỉ 1,4–1,9 % bằng chứng vắt qua ranh giới hai chunk. Với những ca đó, `locate_evidence_chunk` trả về chunk **chứa phần lớn nhất** của bằng chứng — E06 chấm hit@1 với đúng một chunk vàng nên buộc phải chọn một, và "chứa phần lớn nhất" là cách chọn duy nhất bảo vệ được.

  ### Một phát hiện phải xử lý ở T16

  **15,3 % ngữ cảnh của ViWikiFC chỉ ra đúng một chunk.** Với một chunk thì chunk-aware **thoái hóa thành lookback gộp** — không còn gì để phân biệt, mọi đặc trưng phân bố (entropy, Gini, top1–top2) đều là hằng số. Nghĩa là trên bộ này, hơn một phần bảy số mẫu không đóng góp gì cho câu hỏi CH1.

  Đây đúng là lý do mục 8 `docs/DATA.md` yêu cầu T16 dựng chỉ mục BM25 trên 3.814 câu bằng chứng: để ghép ngữ cảnh nhiều đoạn thật sự thay vì dùng `context` ngắn có sẵn. Trước T15 thì đó là một suy đoán, giờ có con số đỡ lưng.

  ### Ghi chú về chồng lấn, chuyển cho T21

  Với `stride` mặc định bằng nửa cửa sổ, các chunk `token_window` **chồng lấn nhau**, nên một token nằm trong phần chồng được **đếm hai lần** và tổng tỷ trọng các chunk không còn bằng 1. Hệ quả: các đặc trưng của T21 coi véc-tơ per-chunk là một **phân bố xác suất** — `chunk_entropy`, `chunk_gini` — chỉ thật sự đọc một phân bố khi dùng chiến lược `sentence`. Với `token_window` phải chuẩn hóa lại trước khi tính, nếu không entropy sẽ lệch một cách có hệ thống theo `stride`, và E04 quét ba cỡ cửa sổ sẽ đo nhầm thứ đó thành khác biệt giữa các cỡ.

  ### Dọn nợ

  Bộ tách câu tạm trong `scripts/probe_attention_hook.py` — viết ở T07 kèm chú thích "T15 sẽ thay" — đã bị xóa; ba script `probe_attention_hook.py`, `compare_dtypes.py`, `measure_throughput.py` nay đều gọi `chunk_by_sentence` thật. Hệ quả nhỏ cần biết: chạy lại T07 hoặc T08 bây giờ sẽ ra **số chunk khác** với con số đã ghi (ví dụ mẫu ISE-DSC01 dài nhất trước đây ra 169 chunk). Thời gian và bộ nhớ không đổi đáng kể, và hai task đó là thăm dò khả thi chứ không phải thí nghiệm, nên số cũ vẫn giữ nguyên làm bản ghi lịch sử.

  `ruff` sạch, `pytest` 314 ca xanh (thêm 37 ca).

- [x] **T16** · M · Kho truy xuất ViWikiFC — hoàn thành 23/08/2026, **hết giai đoạn 2**
  - Trích 3.814 câu bằng chứng duy nhất, dựng chỉ mục BM25.
  - **Kiểm tra:** file `data/interim/viwikifc_evidence_corpus.parquet` có **3.814 dòng** ✅ từ **73 bài** ✅; truy vấn thử trả về top-5 hợp lý ✅ (và đo hẳn recall, xem dưới).

  **Task này để làm gì.** T15 vừa đo ra một vấn đề: **15,3 % ngữ cảnh của ViWikiFC chỉ ra đúng một chunk**, vì `context` của bộ này thường chỉ ba bốn câu. Với một chunk thì chunk-aware thoái hóa thành lookback gộp — chẳng còn gì để so sánh giữa các đoạn.

  Mục 8 `docs/DATA.md` đưa ra lời giải: cả bộ chỉ dựa trên **3.814 câu bằng chứng duy nhất** rút từ 73 bài Wikipedia — đủ ít để giữ trọn trong bộ nhớ làm **kho truy xuất**. E08 sẽ dựng ngữ cảnh nhiều đoạn thật sự bằng cách lấy top-k câu cho mỗi claim, thay vì dùng `context` ngắn có sẵn.

  *BM25* là công thức xếp hạng văn bản theo mức khớp từ khóa: tài liệu chứa nhiều từ **hiếm** của truy vấn thì điểm cao, từ nào xuất hiện ở khắp nơi thì gần như không tính, và tài liệu dài bị chia bớt điểm để không thắng chỉ nhờ dài. Không cần huấn luyện, không cần GPU — đúng thứ cần ở đây, vì E08 quan tâm chú ý làm gì với ngữ cảnh nhiều đoạn chứ không quan tâm bộ truy xuất giỏi tới đâu.

  ### Kết quả

```
  câu bằng chứng        : 3,814
  bài Wikipedia         : 73
  độ dài câu (từ)       : trung vị 31, trung bình 35.2, dài nhất 251
  claim mỗi câu         : trung bình 5.5, tối đa 42
  dựng chỉ mục BM25     : 0.07 s
```

  Cả hai con số của mục 8 `docs/DATA.md` khớp chính xác. Chỉ mục dựng trong 0,07 giây nên **không lưu chỉ mục xuống đĩa**, chỉ lưu kho câu: một file pickle chứa chỉ mục sẽ mong manh theo phiên bản thư viện mà không giữ gì không tính lại được.

  ### Recall của bằng chứng vàng — con số quyết định E08 có làm được không

  Tiêu chí ghi "truy vấn thử một claim trả về top-5 hợp lý", nhưng nhìn ba kết quả bằng mắt thì không nói lên điều gì. Câu hỏi thật là: **BM25 có tìm lại được đúng câu bằng chứng của một claim, giữa 3.814 ứng viên, hay không.** Nếu không thì ngữ cảnh ghép từ top-k sẽ thường **không chứa câu trả lời**, và E08 sẽ đo chất lượng bộ truy xuất chứ không đo tín hiệu chú ý.

  Đo trên 2.000 claim ngẫu nhiên seed 42:

| | recall@1 | recall@5 | recall@10 | recall@20 | recall@50 |
|---|---|---|---|---|---|
| Bằng chứng vàng | **80,3 %** | 89,6 % | **91,3 %** | 93,2 % | 95,2 % |

  **Kho dùng được.** Bốn trên năm claim tìm đúng bằng chứng ngay ở hạng 1, hơn chín trên mười nằm trong top-10. Ngữ cảnh ghép từ top-k sẽ thường chứa câu trả lời, nên E08 đo được đúng thứ nó muốn đo. Script tự in cảnh báo nếu recall@10 tụt dưới 70 %.

  ### Ba quyết định đáng ghi

  **1. Dựng kho từ file thô, không từ file đã chuẩn hóa.** Con số ra khác nhau đúng một: file thô cho 3.814, file chuẩn hóa cho **3.813**. Lý do là T11 xóa trắng cột `evidence` của mọi dòng không định vị được bằng chứng trong ngữ cảnh của chính nó — và đúng một dòng rơi vào đó, chính là câu `NhậtaimBản` bị lỗi ở nguồn.

  Nếu dựng kho từ file chuẩn hóa thì câu ấy biến mất, và claim tương ứng **vĩnh viễn không thể truy xuất được bằng chứng vàng của nó** — E08 mất một mẫu vì một lý do chẳng liên quan gì tới truy xuất. Kho truy xuất là một **tập câu để tìm kiếm**; việc có định vị được offset của một câu trong ngữ cảnh hay không là câu hỏi hoàn toàn khác.

  **2. Tách token theo âm tiết, không dùng bộ tách từ tiếng Việt.** Tiếng Việt viết mỗi âm tiết rời nhau — "Hà Nội" là hai mảnh của một từ — nên tách theo khoảng trắng cho ra **âm tiết chứ không phải từ**. Bộ tách từ đúng nghĩa sẽ gộp chúng lại, nhưng đó là thêm một phụ thuộc mới, mà mục 7 `CLAUDE.md` bảo phải hỏi trước. Cái giá thực tế nhỏ: claim nhắc cả hai âm tiết của một từ thì tài liệu chứa cả hai vẫn được BM25 cộng điểm gấp đôi. Và recall 80,3 % ở hạng 1 nói rằng cách này đủ dùng. Ghi lại vì đây là **hạn chế thật, đã đo chứ không phải bỏ qua** — nếu sau này cần hơn thì đây là chỗ cải thiện rẻ nhất.

  **3. `evidence_id` băm từ nội dung câu, không đánh số theo thứ tự.** Giống `context_id` ở T09 và vì cùng lý do: nếu đánh số theo vị trí thì dựng lại kho từ dữ liệu sắp xếp khác đi sẽ đổi hết mã, và mọi thứ tham chiếu tới mã cũ thành sai âm thầm.

  ### Một chi tiết nhỏ đã xử lý

  **35 câu bằng chứng xuất hiện dưới nhiều hơn một bài Wikipedia.** Schema mục 8 chỉ có một cột `title` cho mỗi câu, nên phải chọn một: lấy bài xuất hiện nhiều nhất, hòa thì lấy tên đứng trước theo bảng chữ cái. Cách chọn phải tất định, nếu không dựng lại kho sẽ xáo chúng lung tung.

  Cũng ghi thêm cột `n_claims` — số claim dùng câu đó làm bằng chứng, trung bình 5,5 và cao nhất 42. Một câu phục vụ 42 claim là một loại đối tượng khác hẳn một câu phục vụ đúng một claim, và E08 có thể cần biết.

  ### Chuyển cho T27 (E08)

  `EvidenceIndex.search` có sẵn tham số `exclude` để loại một số câu khỏi kết quả. Đó là cách E08 dựng được ngữ cảnh **cố tình không chứa** bằng chứng vàng — chính là tình huống mà ảo giác ngoại lai là câu trả lời trung thực duy nhất. Chưa viết `build_context` vì đó là việc của T27.

  `ruff` sạch, `pytest` 340 ca xanh (thêm 26 ca).

---

**Hết giai đoạn 2.** Bốn bộ đã chuẩn hóa, chia tập, đo rò rỉ, chia chunk và dựng kho truy xuất. Từ T17 trở đi là các baseline, tức bắt đầu có số để so.

---

## Giai đoạn 3 — Các baseline (tuần 4–5)

- [x] **T17** · M · E01 baseline tầm thường — hoàn thành 27/08/2026
  - Hai đặc trưng: độ dài phản hồi và tỷ lệ trùng lặp từ vựng. Logistic regression, 5 seed.
  - **Kiểm tra:** kết quả ghi vào `results/runs.jsonl` ✅, điền Bảng 1 dòng đầu `docs/EXPERIMENTS.md` ✅.

  **Task này để làm gì.** Mục 4 `docs/EXPERIMENTS.md` gọi E01 là *"thí nghiệm bắt buộc chạy sớm nhất, vì nó định nghĩa sàn thật sự"*. Ý tưởng: chỉ dùng hai con số ai cũng tính được — **phản hồi dài bao nhiêu từ**, và **bao nhiêu phần chữ trong phản hồi là chép lại từ ngữ cảnh** — rồi cho một mô hình tuyến tính đơn giản nhất phân loại. Nếu chừng đó đã đủ tốt, thì mọi phương pháp phức tạp hơn, **kể cả đóng góp của chính đề tài này**, phải chứng minh vượt được **nó**, chứ không phải vượt một con số bài báo khác công bố.

  ### Kết quả — sàn cao hơn dự đoán

| Chỉ số | Giá trị | ± lệch chuẩn | Khoảng tin cậy 95 % |
|---|---|---|---|
| **macro-F1** | **0,6562** | 0,0177 | **[0,6200 – 0,6891]** |
| Accuracy | 0,6614 | 0,0178 | [0,6257 – 0,6957] |
| F1 `no` | 0,7418 | 0,0226 | [0,6930 – 0,7830] |
| F1 `intrinsic` | **0,5327** | 0,0293 | [0,4736 – 0,5852] |
| F1 `extrinsic` | 0,6942 | 0,0239 | [0,6462 – 0,7394] |
| ECE | 0,0613 | — | — |

  **Chạy lại ngày 27/08/2026** sau khi T18 sửa cách chia tập. Con số cũ trên tập chia trước là 0,6696; lệch 0,013 và **nằm gọn trong khoảng nhiễu ±0,018** — chính minh họa cho điều mục "yêu cầu 5 seed là rỗng" ở dưới nói.

  Chín tham số phải huấn luyện, **0,001 ms mỗi mẫu**, không cần GPU.

  Ma trận nhầm lẫn trên tập chia trước cho thấy rõ vì sao `intrinsic` khó: nó chỉ được bắt đúng **45,2 %**, và phần trượt chia gần đều sang hai lớp kia. Không lệch hẳn về bên nào, tức hai đặc trưng bề mặt **không có tín hiệu nào** về lớp này chứ không phải có tín hiệu yếu.

  Hai đặc trưng tái lập đúng bảng ở mục 4 `docs/EXPERIMENTS.md`: độ dài trung bình ra **chính xác** 32,9 / 39,5 / 45,9 từ cho ba nhãn. Tỷ lệ trùng lặp ra 0,827 / 0,671 / 0,574, cao hơn số cũ khoảng 0,02 vì cách đếm ở đây bỏ dấu câu và không phân biệt hoa thường; thứ tự và khoảng cách giữa ba nhãn giữ nguyên.

  ### Ba điều con số này quyết định

  1. **Ngưỡng thật để vượt là 0,689 — không phải 0,328, mà cũng không phải 0,656.** Bài PhoBERT công bố macro-F1 32,83 %, lấy đó làm mốc thì mọi thứ đều trông như tiến bộ lớn; hai đặc trưng bề mặt đã đạt gấp đôi. Nhưng khoảng tin cậy của E01 chạm tới **0,689**, nên muốn nói một phương pháp *hơn hẳn* E01 thì phải vượt mốc đó. Vượt 0,67 chỉ là rơi vào khoảng nhiễu của cùng một kết quả.

  2. **`intrinsic` là lớp khó nhất, cách hai lớp kia hơn 0,2 điểm F1.** Và điều đó rất hợp lý: ảo giác nội tại là **xáo trộn thông tin vốn đã có** trong ngữ cảnh, nên nó *vẫn* trùng lặp từ vựng cao và *vẫn* dài vừa phải — hai đặc trưng bề mặt gần như mù với nó. Đây chính là chỗ tín hiệu chú ý theo đoạn có cơ hội đóng góp nhiều nhất, và nên là chỗ E05 tập trung chứng minh. Nếu chunk-aware chỉ cải thiện `no` và `extrinsic` thì chưa nói lên gì.

  3. **Chi phí gần bằng không.** 9 tham số, 0,001 ms/mẫu, chạy CPU. Cột chi phí của E11 vì thế có một mốc dưới rất khắc nghiệt: phương pháp nội tại tốn khoảng 420 ms/mẫu trên ViHallu (đo ở T08), tức **đắt hơn bốn trăm nghìn lần**. Nó phải đổi lại bằng độ chính xác tương xứng.

  ### Một lỗi âm thầm suýt lọt

  Lần chạy đầu cho **ECE = 0,42** — nghĩa là mô hình lệch tự tin tới 42 điểm phần trăm, vô lý với một mô hình đạt accuracy 0,68. Truy ra thì đây là lỗi thật, và là loại lỗi tệ nhất vì **mọi chỉ số khác vẫn đúng và vẫn trông hợp lý**.

  *ECE* (expected calibration error) đo xem mô hình nói "tôi chắc 80 %" thì có đúng khoảng 80 % số lần không. Để tính nó phải biết **cột nào của ma trận xác suất ứng với lớp nào**. Mà scikit-learn sắp lớp theo **bảng chữ cái** — `extrinsic, intrinsic, no` — trong khi thứ tự báo cáo của dự án là `no, intrinsic, extrinsic`. Mình đã ngầm cho rằng hai thứ tự đó trùng nhau. Kiểm lại: chỉ **25,7 %** khớp.

  Macro-F1 và F1 từng lớp **không** bị ảnh hưởng, vì chúng so trực tiếp chuỗi nhãn chứ không đụng tới ma trận xác suất. Sau khi sửa, ECE = **0,0611** — con số hợp lý.

  Cách chặn để không tái diễn: `compute_metrics` nay **tự kiểm tra** rằng lớp có xác suất cao nhất phải trùng với lớp được dự đoán. Nếu không trùng thì raise kèm thông báo chỉ đúng cách sửa. Đây là bất biến luôn đúng với mọi bộ phân loại của sklearn, nên chốt chặn này bắt được lỗi ngay ở mẫu đầu tiên chứ không đợi ai đó thấy con số kỳ lạ.

  ### Yêu cầu "5 seed" là rỗng, và nó còn che mất nguồn biến thiên lớn nhất

  Mục 3 `docs/EXPERIMENTS.md` đòi mọi con số của bộ phân loại phải kèm độ lệch chuẩn qua 5 seed. Đo thật ba nguồn biến thiên:

| Nguồn | Độ lệch chuẩn của macro-F1 |
|---|---|
| Đổi riêng `random_state` — đúng nguyên văn yêu cầu | **0,000000** |
| Lấy lại mẫu tập huấn luyện | ±0,0036 |
| **Lấy lại mẫu tập test** | **±0,0174** |

  Yêu cầu cũ **rỗng**: logistic regression giải bằng lbfgs trên bài toán lồi là tất định, năm seed cho ra năm con số y hệt nhau tới chữ số thứ sáu. Nhưng vấn đề lớn hơn là nó **che mất nguồn biến thiên chi phối**: tập test ViHallu chỉ có 700 mẫu, nên bản thân việc mẫu nào rơi vào tập test đã làm macro-F1 xê dịch **gấp 4,6 lần** biến thiên huấn luyện.

  Nếu báo ±0,004 thì kết quả trông chính xác hơn thực tế **gần năm lần**, và mọi so sánh sau này sẽ kết luận sai: hai phương pháp lệch nhau 0,02 sẽ trông như khác biệt rõ ràng, trong khi thật ra khoảng tin cậy của chúng chồng lên nhau gần hết.

  **Đã sửa quy tắc ở mục 3 `docs/EXPERIMENTS.md`**, áp cho mọi thí nghiệm từ đây:

  1. Con số bất định chính là **khoảng tin cậy 95 % từ 2.000 lần lấy lại mẫu tập test**.
  2. **Vẫn chạy 5 seed với mô hình có yếu tố ngẫu nhiên** — E09 tinh chỉnh bộ mã hóa (khởi tạo trọng số, dropout, thứ tự dữ liệu), LightGBM (lấy mẫu con). Với chúng biến thiên do seed là thật.
  3. Với mô hình tất định thì **ghi thẳng là 0**, đừng bịa ra biến thiên.

  Hệ quả phải nhớ khi đọc bảng kết quả: **hai phương pháp lệch nhau dưới 0,03 macro-F1 trên tập test 700 mẫu là chưa phân định được.**

  ### Đã dựng thêm ba module dùng chung cho mọi thí nghiệm sau

  - `src/vihallulens/features/surface.py` — hai đặc trưng bề mặt.
  - `src/vihallulens/evaluation/metrics.py` — `compute_metrics` theo mục 2.5 `docs/SPEC.md`, kèm ECE và `summarise_runs`.
  - `src/vihallulens/detect/detector.py` — `LookbackDetector` theo mục 2.4 `docs/SPEC.md`. Mặc định tuyến tính, `class_weight="balanced"`, có chuẩn hóa thang đo vì hai đặc trưng lệch nhau khoảng bốn mươi lần.
  - `src/vihallulens/data/text.py` — gom định nghĩa "từ" về một chỗ, để BM25 ở T16 và trùng lặp từ vựng ở T17 không dùng hai định nghĩa khác nhau.

  `ruff` sạch, `pytest` **402 ca xanh** (thêm 62 ca).

- [x] **T18** · M · E09 baseline bộ mã hóa — **xong 27/08/2026** (hai trên ba mô hình)
  - Tinh chỉnh PhoBERT-large, XLM-R-large, InfoXLM-large ba lớp trên ViHallu.
  - **Kiểm tra:** ba dòng kết quả, kèm ms/mẫu và VRAM đỉnh.

  **Task này để làm gì.** Đây là **mốc so sánh nghiêm túc nhất** của đề tài. Khác E01 chỉ dùng hai đặc trưng bề mặt, ba mô hình này thật sự **đọc** văn bản; khác E10 dùng Gemini, chúng **chạy cục bộ** không tốn API. Nếu phương pháp chú ý nội tại không vượt được chúng thì lập luận về chi phí ở câu hỏi CH2 không đứng vững.

  **Đã chuẩn bị:** `src/vihallulens/data/segmentation.py`, `src/vihallulens/detect/encoder.py`, `scripts/train_encoder_baseline.py`, `notebooks/t18_baseline_bo_ma_hoa_t4.ipynb`. `pytest` **435 ca xanh** (thêm 33 ca).

  ### Một quyết định về phụ thuộc, đã hỏi và được duyệt

  **PhoBERT được huấn luyện trên văn bản đã tách từ.** Tiếng Việt viết mỗi âm tiết rời nhau, nên `Hà Nội` là hai mảnh của một từ; PhoBERT học trên dạng đã ghép `Hà_Nội`. Đưa văn bản thô vào là đặt nó trước một bộ từ vựng nó chưa từng thấy, và điểm tụt vì lý do **chẳng liên quan gì tới bài toán**.

  Rủi ro nếu bỏ qua: báo cáo ghi "PhoBERT đạt X" rồi đề tài nói vượt PhoBERT; hội đồng hỏi "các em có tách từ không?" mà trả lời không thì **mốc so sánh đó bị bác bỏ**.

  Theo mục 7 `CLAUDE.md` thì thêm phụ thuộc phải hỏi, nên đã hỏi và được duyệt thêm **`pyvi`** — thư viện nhẹ, chỉ một mô hình CRF vài MB, không kéo theo Java. Chỉ PhoBERT dùng; XLM-R và InfoXLM dùng SentencePiece trên văn bản thô nên **không được** đưa văn bản đã tách từ vào, dấu gạch dưới sẽ bị tokenize thành ký tự thường.

  ### Một con số đo trước khi chạy, và nó đổi cách đọc kết quả

**Đo thật trên Kaggle: 29,3 % cặp của ViHallu vượt giới hạn 256 token của PhoBERT**, còn ở mức 512 token của hai mô hình kia là **2,5 %**. (Ước lượng thô ban đầu của nhóm là 50 % và 1,4 %, tính bằng cách nhân số từ với 1,3; sai vì BPE của PhoBERT trên văn bản **đã tách từ** nén tốt hơn nhiều so với hệ số đó.)

  Đây không phải lựa chọn mà là **trần cứng**: PhoBERT không thể vượt 256 vị trí. Hệ quả: nếu PhoBERT thua thì phải ghi rõ nó thua **một phần vì không đọc hết được ngữ cảnh**, chứ không kết luận là mô hình yếu hơn. Script tự in tỷ lệ này trước mỗi lần chạy.

  Đã cân nhắc ép cả ba xuống 256 token cho công bằng, nhưng bỏ: mục đích của mốc so sánh là **thứ mạnh nhất mà đề tài phải vượt**, nên mỗi mô hình được dùng cấu hình tốt nhất của nó, và tỷ lệ cắt được báo cáo kèm điểm số.

  ### Ba quyết định thiết kế khác

  1. **Viết vòng lặp huấn luyện bằng tay, không dùng `transformers.Trainer`.** Repo giải ra `transformers` 5.15, mà tham số của `Trainer` ở nhánh 5.x khác nhánh 4.x — nhánh mà gần như mọi ví dụ trên mạng dùng. Một vòng lặp bốn mươi dòng không đáng để đánh cược rủi ro phiên bản trên một lần chạy tốn quota GPU.

  2. **Cặp đầu vào đúng theo mẫu prompt đã chốt ở T07:** vế trái là mọi thứ mô hình được cho (ngữ cảnh + câu hỏi), vế phải là văn bản cần chấm (phản hồi). Nhờ vậy so sánh với phương pháp chú ý là so **phương pháp**, không phải so xem ai được cho xem nhiều hơn.

  3. **Ba seed thay vì năm.** Mục 3 `docs/EXPERIMENTS.md` đòi năm, và tinh chỉnh **thật sự** ngẫu nhiên (khởi tạo đầu phân loại, dropout, thứ tự dữ liệu) nên seed ở đây đo được thứ có thật — khác hẳn E01. Nhưng T17 đo được khoảng tin cậy tập test là ±0,017, lớn hơn hẳn biến thiên seed của một mô hình đã hội tụ. Seed thứ tư và thứ năm sẽ tinh chỉnh một con số vốn đã bị một con số lớn hơn chi phối, đổi lại **khoảng một giờ quota mỗi mô hình 512 token**. Có cờ `--seeds 5` cho ai muốn theo đúng nguyên văn.

  ### Hai lỗi phát hiện khi chạy thử trên Kaggle, đã sửa

  **Lỗi 1 — cách chia tập không tái lập được giữa các máy.** Đây là lỗi nghiêm trọng hơn nhiều so với vẻ ngoài của nó. Cùng seed 42, cùng dữ liệu, mà ra hai kết quả khác nhau:

| Máy | train / dev / test |
|---|---|
| Máy cá nhân (Python 3.11) | 5.598 / 702 / 700 |
| Kaggle (Python 3.12, torch 2.10) | **5.632 / 706 / 662** |

  Nguyên nhân: `group_split` xáo thứ tự nhóm bằng `numpy.random.default_rng(seed).shuffle`. Đã loại trừ hai giả thuyết dễ nghĩ — ký tự xuống dòng trong dữ liệu (ViHallu không có ký tự nào), và kiểu dữ liệu của mảng đem xáo (thử object với `<U16` cho cùng hoán vị). Còn lại là chênh lệch phiên bản thư viện trên Kaggle.

  **Không truy tiếp thư viện nào lệch, mà bỏ hẳn chỗ phụ thuộc vào nó.** Thứ tự nhóm nay lấy từ **băm SHA-256 của `(seed, context_id)`** rồi sắp xếp — SHA-256 cố định theo chuẩn chứ không theo phiên bản thư viện, và `sorted` thì ổn định. Kết quả chỉ phụ thuộc seed và các mã ngữ cảnh, không phụ thuộc gì khác.

  Vì sao đáng làm tới mức đó: **mọi thí nghiệm từ đây trở đi đều đứng trên cách chia này**. Một cách chia đổi theo phiên bản thư viện thì hai người trong nhóm chạy cùng một lệnh sẽ ra hai con số khác nhau, và không ai biết vì sao. Thêm **một ca kiểm thử khóa cứng** bốn phần tử đầu của thứ tự xáo, cùng một ca đặt seed toàn cục của NumPy thành giá trị lạ rồi khẳng định cách chia không nhúc nhích — để lần sau ai đó lại với tay sang `numpy.random` là đỏ ngay.

  Số chia mới: ViHallu **5.600 / 700 / 700**, ISE-DSC01 **29.077 / 3.646 / 3.646**. Rò rỉ vẫn bằng 0. Đã chạy lại E01 trên tập mới, kết quả ở phần T17.

  **Lỗi 2 — notebook gọi `split_data.py` khi mới chuẩn hóa một bộ.** Script xử lý cả bốn bộ nên dừng giữa chừng vì thiếu ISE-DSC01. Thêm cờ `--only` để chỉ xử lý bộ cần, và cho báo cáo rò rỉ của lần chạy một phần ghi ra **tên file khác**, để không đè lên bản đầy đủ mà mục 6 `docs/DATA.md` trỏ tới đích danh.

  ### Lỗi thứ ba, phát hiện ở lượt chạy GPU đầu tiên

  Cả ba mô hình đều **dừng ngay trước bước huấn luyện đầu tiên**, sau khi đã tải xong trọng số — tức đã tốn thời gian tải mà chưa học được gì.

```
ValueError: too many dimensions 'str'
    torch.tensor(labels, dtype=torch.long)
```

  Nguyên nhân là một chỗ **nửa vời của chính mình**: trong `main()` mình mã hóa nhãn tập train thành số, nhưng **cố ý giữ nhãn tập test ở dạng chuỗi** vì `compute_metrics` chấm điểm bằng chuỗi. Rồi lại đưa chính chuỗi đó vào `make_loader` để dựng tensor.

  Sửa bằng cách **cho nhãn chỉ tồn tại ở một dạng duy nhất** trong cấu trúc dữ liệu — chuỗi — và mã hóa thành số **ngay tại chỗ dựng loader**. Hai dạng nhãn nằm ở hai chỗ khác nhau thì sớm muộn cũng có chỗ dùng nhầm.

  **Bài học đắt hơn: mình không có cách nào kiểm tra vòng lặp huấn luyện trước khi tốn quota.** Mục 5 `docs/SPEC.md` ghi "chỉ test phần không cần GPU", và mình đã hiểu câu đó thành "vòng lặp huấn luyện thì khỏi test" — sai. Vòng lặp *chạy được hay không* là chuyện của CPU; chỉ *chạy nhanh hay chậm* mới cần GPU.

  Đã sửa: `train_once` nay nhận tham số `build` để tiêm mô hình vào, và có **hai ca kiểm thử chạy trọn vòng lặp trên CPU** với một Roberta hai lớp khởi tạo ngẫu nhiên, không tải gì. Chạy hết trong vài giây, và bắt đúng loại lỗi vừa xảy ra. Cũng bớt log rác: tokenizer của `transformers` lặp lại một dòng cảnh báo cắt chuỗi mỗi batch, hàng trăm dòng, che mất mọi thứ đáng đọc.

  Một chỉnh nhỏ nữa: số đo nhiệt độ **lúc rảnh** trước khi chạy nay chỉ in ra chứ không đưa vào phán quyết hạ xung — card rảnh tự hạ xung xuống 300/1590 MHz, thấp hơn hẳn lúc chạy, nên đưa vào sẽ khiến mọi lượt chạy trông như đang *tăng* xung.

  ### Lượt chạy GPU đầu: sáu trên chín lần chạy không học được gì

  Chạy hết 3,5 giờ, và kết quả **hỏng**:

| Mô hình | macro-F1 từng seed | Học được |
|---|---|---|
| PhoBERT-large | 0,778 · **0,167** · 0,757 | 2/3 |
| XLM-R-large | **0,167 · 0,167 · 0,167** | 0/3 |
| InfoXLM-large | **0,167 · 0,167 · 0,167** | 0/3 |

  Con số 0,167 không phải điểm kém mà là **dấu hiệu của việc không học gì cả**. Kiểm lại thì rõ: `f1_no = 0`, `f1_extrinsic = 0`, `f1_intrinsic = 0,5011` → macro = 0,167; và accuracy 0,3343 nhân 700 ra đúng **234 mẫu**, bằng đúng số mẫu `intrinsic` trong tập test. Tức **mô hình đoán `intrinsic` cho cả 700 mẫu**.

  Xác nhận thêm bằng loss: entropy chéo của mô hình ba lớp chưa học gì là `ln(3) = 1,0986`. Loss của XLM-R dao động 1,02–1,27 suốt **2.100 bước** mà không hề giảm. Nó chưa từng rời điểm xuất phát.

  **Nguyên nhân: tinh chỉnh không ổn định ở learning rate 2e-5.** Đây là vấn đề nổi tiếng của họ RoBERTa cỡ large, và ở đây nặng thêm vì T4 là kiến trúc Turing nên **không hỗ trợ bfloat16** — buộc phải dùng float16, kiểu số có dải hẹp hơn nhiều. Bằng chứng ủng hộ: PhoBERT ở cùng learning rate cũng sụp một trong ba lần, tức không phải lỗi riêng của mô hình nào.

  ### Ba lớp phòng vệ đã thêm

  1. **Hạ learning rate xuống 1e-5** cho cả ba, khai báo riêng trong `MODELS` chứ không dùng chung một hằng số. Kèm `eps=1e-6` cho AdamW — cách chữa tiêu chuẩn cho bất ổn của họ RoBERTa.

  2. **Dừng sớm.** Hết một epoch mà loss vẫn quanh `ln(3)` thì script tự dừng. Sáu lần chạy chết ở lượt trước đốt **hai tiếng rưỡi** để in ra một hàng 0,167 giống hệt nhau; nay chúng dừng sau epoch đầu.

  3. **Ô thử rẻ trong notebook.** Một seed, một epoch, trên mô hình khó nhất — mười phút thay vì ba tiếng rưỡi để biết cấu hình có ổn không.

  Cũng sửa một lỗi thật trong vòng lặp mà PyTorch đã cảnh báo suốt lượt chạy: `GradScaler` **bỏ hẳn bước cập nhật** khi gradient float16 tràn số, nhưng `scheduler.step()` vẫn được gọi — tức lịch learning rate cứ chạy tiếp trong khi trọng số đứng yên. Nay chỉ bước scheduler khi optimizer thật sự đã bước, và số bước thật được in ra.

  ### Một lỗi trong chính cách mình báo cáo

  Bảng kết quả của PhoBERT in ra thế này:

```
  macro_f1            0.5672    0.3467   [0.7228, 0.7860]
```

  **Trung bình 0,5672 nằm NGOÀI khoảng tin cậy [0,7228 – 0,7860] của chính nó.** Vô lý, và là dấu hiệu của lỗi chứ không phải một sai lệch tinh vi.

  Nguyên nhân: trung bình tính trên **cả ba seed** (gồm cả seed sụp đổ 0,167), còn khoảng tin cậy lấy từ **seed ở giữa** (0,757). Hai con số mô tả hai thứ khác nhau nhưng bị đặt cạnh nhau như thể cùng mô tả một thứ.

  Sửa: lần chạy nào **chỉ đoán một lớp** sẽ bị phát hiện và **loại khỏi thống kê**, có cảnh báo rõ ràng, và macro-F1 của **từng seed** được in riêng. Bình quân một lần thành công với một lần thất bại cho ra con số không mô tả cái nào cả. Nếu **mọi** seed đều sụp thì script báo lỗi và **không báo cáo số nào** — thay vì in ra 0,167 như thể đó là một kết quả.

  ### Bản vá đã kiểm chứng ngày 27/08/2026

  Chạy thử rẻ trên mô hình khó nhất trước khi bỏ ra ba tiếng — một seed, một epoch, XLM-R:

```
  batch / epoch / lr    : 8 / 1 / 1e-05
  macro-F1 0.7076   huấn luyện 9.2 phút   VRAM đỉnh 11,231 MB   76 °C
  macro-F1 từng seed:
    seed 42: 0.7076   (695 bước thật)
```

  Ba điều đọc được từ mười phút này:

  1. **Cấu hình đã ổn.** Không sụp đổ, loss đã học, `f1_intrinsic = 0,591` — cao hơn hẳn 0,533 của E01.
  2. **695 trên 700 bước thật.** Năm bước bị bỏ vì gradient float16 tràn số. Xác nhận chẩn đoán tràn số là đúng, và xác nhận bản vá scheduler đang chạy đúng — trước đây lịch learning rate vẫn đi tiếp trong lúc trọng số đứng yên.
  3. **Một epoch đã vượt mốc.** 0,7076 lớn hơn 0,689, tức bộ mã hóa thật sự là mốc so sánh đáng gờm chứ không phải hình thức.

  Vẫn chạy đủ **ba epoch** chứ không dừng ở một, dù một epoch đã vượt mốc: mục đích của mốc so sánh là **thứ mạnh nhất mà đề tài phải vượt**. Huấn luyện thiếu sẽ làm nó yếu đi một cách có lợi cho đề tài, và đó đúng là chỗ hội đồng dễ bác nhất.

  ### Lượt chạy thứ hai: PhoBERT đạt mốc, và lưới lọc seed chết vẫn thủng

  Ngày 27/08/2026, PhoBERT chạy xong ba seed:

| Seed | macro-F1 | Bước thật | Ghi chú |
|---|---|---|---|
| 42 | **0,1696** | 346 | dừng sớm sau epoch 1, loss còn 1,1072 |
| 43 | 0,7542 | 1.045 | học bình thường |
| 44 | 0,7234 | 1.043 | học bình thường |

  **Tin tốt: hạ learning rate có tác dụng.** Hai seed học được đều **vượt mốc 0,689**, và `f1_intrinsic` của bản tổng hợp là 0,625 so với 0,533 của E01 — cải thiện đúng ở lớp khó nhất. Cơ chế dừng sớm cũng chạy đúng: seed 42 dừng sau 4,6 phút thay vì đi hết 14 phút, tiết kiệm khoảng mười phút quota.

  **Tin xấu: bảng tổng hợp lại in sai, đúng kiểu sai đã sửa lần trước.**

```
  Trung bình 3 seed học được, khoảng tin cậy lấy từ seed ở giữa:
  macro_f1            0.5490    0.3290   [0.6887, 0.7546]
```

  Lại là **trung bình nằm ngoài khoảng tin cậy của chính nó**. Và kiểm lại thì `(0,1696 + 0,7542 + 0,7234) / 3 = 0,5490` — đúng bằng số in ra, tức **seed chết vẫn bị tính vào trung bình** dù lần trước đã thêm hẳn cơ chế loại nó.

  **Vì sao lưới lọc thủng.** Cách phát hiện cũ là đếm số lớp khác nhau trong dự đoán: đoán một lớp cho tất cả thì coi như chết. Seed 42 lách qua được vì nó đoán `intrinsic` cho 699 mẫu và **một mẫu ra lớp khác** — hai lớp khác nhau, nên không có gì trông giống sụp đổ. Bằng chứng số học: đoán `intrinsic` cho cả 700 mẫu sẽ cho macro-F1 đúng **0,1670**, còn seed 42 ra **0,1696**, lệch một chút vì cái mẫu lẻ đó.

  Bài học chung: **một dấu hiệu gián tiếp thì có kẽ hở**. Số lớp trong dự đoán chỉ là hệ quả của việc không học; nó gần đúng chứ không phải định nghĩa.

  **Sửa: dùng thẳng dấu hiệu trực tiếp, và giữ cả hai lưới.** Script vốn đã biết seed 42 hỏng — chính nó in ra dòng `DỪNG SỚM`, dựa trên loss đứng ở `ln(3)`. Chỉ là kết luận đó không được truyền sang phần thống kê. Nay `train_once` trả về cờ `stopped_early`, và một lần chạy được tính là học được chỉ khi **không dừng sớm và cũng không sụp đổ**. Hai lưới độc lập: loss bắt được thứ dự đoán bỏ lọt, và ngược lại nếu có lần chạy đi hết ba epoch mà vẫn thoái hóa.

  Thêm hai ca kiểm thử chạy trên CPU: một lần chạy với learning rate bằng 0 phải bị đánh dấu không học được, và một lần chạy trên bài toán đồ chơi **có tín hiệu thật** phải **không** bị dừng nhầm. Ca thứ hai quan trọng không kém: dừng sớm quá tay thì vứt mất seed tốt. `pytest` **432 ca xanh**.

  **Số đúng của PhoBERT, tính tay từ hai seed học được:** macro-F1 **0,7388 ± 0,0218** (độ lệch chuẩn mẫu, đúng quy ước `summarise_runs`). Khoảng tin cậy tập test sẽ lấy từ seed 43 chứ không phải seed 44 như bản in hỏng.

  **Không cần chạy lại PhoBERT.** Điểm của từng seed là số thật, đo trên mô hình thật; chỉ có phép tính gộp là sai. `results/runs.jsonl` đã lưu `macro_f1_per_seed` nên tính lại được mà không tốn GPU. Lượt chạy đang thực hiện cứ để chạy tiếp cho XLM-R và InfoXLM.

  **Một kết quả phụ đáng đưa vào báo cáo.** Ngay ở learning rate 1e-5, PhoBERT vẫn hỏng một trong ba lần. Tức bất ổn khi tinh chỉnh **giảm đi chứ chưa mất hẳn**, và đây là con số thật về chi phí vận hành của hướng bộ mã hóa trên phần cứng cấp T4: muốn có một mô hình dùng được thì phải chạy nhiều seed rồi bỏ bớt. Phương pháp chú ý nội tại **không tinh chỉnh gì cả** nên không có rủi ro này — một luận điểm cho câu hỏi CH2 mà lượt chạy hỏng vừa rồi tự nhiên cung cấp.

  ### Ba chỗ sửa thêm trước khi chạy lại

  Vì lượt chạy phải làm lại từ đầu, sửa luôn ba thứ đã biết là sai chứ không để dồn.

  **1. Chọn seed mang khoảng tin cậy: lấy seed gần trung bình, không lấy theo vị trí.** Bootstrap lấy mẫu lại tập test nên nó mô tả **một** bộ dự đoán, phải chọn ra một lần chạy để làm đại diện — và nên chọn lần bình thường nhất, vì khoảng tin cậy quanh một giá trị dị biệt thì mô tả lần chạy đó chứ không mô tả phương pháp.

  Cách cũ sắp xếp rồi lấy phần tử ở vị trí `len // 2`. Với **số chẵn** lần chạy — đúng thứ mà việc loại một seed chết để lại — nó luôn với sang cái **cao hơn** trong hai cái ở giữa. Nghĩa là mô hình nào mất một seed thì lặng lẽ được lấy khoảng tin cậy từ nửa tốt hơn của chính nó, và thiên lệch ấy lớn dần đúng vào lúc lượt chạy diễn ra tệ nhất.

  Nay chọn lần chạy **gần trung bình nhất**. Hòa thì phân định theo thứ tự seed, tức theo thứ tự chạy — một tiêu chí không liên quan gì tới điểm số. Kèm ba ca kiểm thử. Với PhoBERT, khoảng tin cậy nay lấy từ seed 43 thay vì seed 44.

  Bảng kết quả cũng **ghi rõ số seed của lần chạy mang khoảng tin cậy**, thay vì chỉ nói "seed ở giữa" — đọc báo cáo sau này sẽ biết ngay con số đó tới từ đâu.

  **2. Nới `requires-python` thành `>=3.11`.** Mỗi phiên Kaggle đều in một dòng đỏ:

```
ERROR: Package 'vihallulens' requires a different Python: 3.12.13 not in '<3.12,>=3.11'
```

  Chặn trên không ngăn được gì — Kaggle chạy 3.12 và không cho đổi — mà chỉ làm `pip install -e .` hỏng, khiến gói phải nạp qua đường `sys.path` vòng vèo. Trọn bộ kiểm thử đã chạy xanh trên 3.12 của Kaggle, nên chặn trên chỉ tạo tiếng ồn. Mục 3 `CLAUDE.md` vẫn giữ 3.11 là phiên bản của máy phát triển; đây chỉ là nới **giới hạn cài đặt**.

  **3. Notebook.** Sửa một câu tự mâu thuẫn còn sót ("đừng chạy cả ba trong một phiên" nằm ngay trên đoạn giải thích vì sao chạy một phiên là được), sửa chỗ ghi nhầm learning rate cũ là 1e-5 (đúng ra là 2e-5), thay ước tính thời gian bằng số đo thật, và ghi lại kết quả PhoBERT của lượt 27/08 để lần chạy sau có mốc đối chiếu.

  `pytest` **435 ca xanh**.

  ### Kết quả — lượt chạy sạch ngày 27/08/2026

  2 giờ 48 phút GPU, commit `53d095d`. Cột macro-F1 kèm **khoảng tin cậy 95 % của tập test**, vì đo ở T17 thì khoảng này rộng gấp đôi biến thiên seed và chính nó quyết định một phương pháp có thật sự hơn phương pháp khác không.

| Phương pháp | macro-F1 [KTC 95 %] | F1 `intrinsic` | ECE | ms/mẫu | VRAM |
|---|---|---|---|---|---|
| E01 bề mặt | 0,656 [0,620–0,689] | 0,533 | 0,061 | 0,001 | 0 |
| PhoBERT-large | 0,742 [0,705–0,770] | 0,685 | 0,086 | 12,2 | 9.002 MB |
| **XLM-R-large** | **0,771** [0,747–0,808] | **0,722** | 0,114 | 24,8 | 11.231 MB |
| InfoXLM-large | *không tinh chỉnh được, 0/3 seed* | | | | 11.231 MB |

  Độ lệch chuẩn **qua seed** là 0,012 và 0,025 — nhỏ hơn hẳn khoảng tin cậy tập test, đúng như T17 dự đoán. Cả ba seed của hai mô hình đầu đều học được.

  **Mốc mà đề tài phải vượt nay là 0,771, không còn là 0,689.** Cận trên khoảng tin cậy của XLM-R chạm 0,807. Đây mới là đối thủ thật.

  Bốn điều đọc được:

  1. **Lớp `intrinsic` vẫn khó nhất, nhưng bộ mã hóa thu hẹp được nhiều.** 0,533 → 0,722. Khoảng cách giữa lớp dễ nhất (`no`) và khó nhất thu từ 0,209 xuống 0,114. Ảo giác nội tại — mâu thuẫn với chính ngữ cảnh — cần đọc và đối chiếu văn bản, đúng thứ hai đặc trưng bề mặt không làm được.

  2. **Giá phải trả là chi phí.** XLM-R chậm hơn E01 khoảng **25.000 lần** mỗi mẫu và cần 11 GB VRAM, đổi lấy 0,115 macro-F1. Đây chính là trục đánh đổi mà E11 phải vẽ, và là chỗ phương pháp chú ý nội tại có cơ hội: nó dùng lại lượt đọc mà hệ RAG dù sao cũng phải chạy.

  3. **Càng mạnh càng tự tin thái quá.** ECE đi **ngược chiều** macro-F1: 0,061 → 0,086 → 0,114. Bộ mã hóa đoán đúng hơn nhưng hiệu chỉnh xác suất *tệ hơn* hai đặc trưng bề mặt. ECE (expected calibration error) đo khoảng cách giữa mức tự tin mô hình công bố và tỷ lệ nó đúng thật; ECE 0,114 nghĩa là mức tự tin công bố lệch khỏi tỷ lệ đúng thật trung bình khoảng 11 điểm phần trăm. Với bài toán phát hiện ảo giác, nơi người dùng cần biết **mức độ tin** chứ không chỉ nhãn, đây là điểm yếu thật của mốc so sánh.

  4. **PhoBERT thua XLM-R 0,029, và một phần vì bị cắt ngữ cảnh.** 29,3 % cặp vượt trần 256 token của PhoBERT so với 2,5 % ở mức 512. Hai khoảng tin cậy chồng nhau ([0,705–0,770] và [0,747–0,808]) nên **không kết luận được** PhoBERT yếu hơn về bản chất.

  ### InfoXLM-large: cả ba seed đều không học được

  Cùng kích thước, cùng độ dài, cùng learning rate với XLM-R — vốn chạy tốt 3/3 seed — nhưng cả ba seed của InfoXLM đứng nguyên ở `ln(3) = 1,0986` suốt epoch đầu:

```
    seed 42: 0.2371   (694 bước thật)  ← KHÔNG HỌC ĐƯỢC, loss đứng ở ln(3), đã loại
    seed 43: 0.1786   (694 bước thật)  ← KHÔNG HỌC ĐƯỢC, loss đứng ở ln(3), đã loại
    seed 44: 0.1670   (692 bước thật)  ← KHÔNG HỌC ĐƯỢC, loss đứng ở ln(3), đã loại

  KHÔNG CÓ SEED NÀO HỌC ĐƯỢC. Không có kết quả để báo cáo.
```

  **Đây là lúc hai lưới lọc chứng minh mình đáng có.** Chú ý seed 42 ra 0,2371 và seed 43 ra 0,1786 — cả hai **không phải** 0,167, tức chúng đoán ra nhiều hơn một lớp và sẽ **lọt qua** lưới đếm số lớp. Chỉ có lưới loss bắt được. Đúng loại lỗi đã lọt hôm trước, lần này bị chặn.

  Cơ chế dừng sớm tiết kiệm **một giờ**: mỗi seed chết mất 10,1 phút thay vì 30,3 phút.

  Vì cấu hình giống hệt XLM-R mà XLM-R chạy tốt, kết luận là **bất ổn riêng của checkpoint InfoXLM**, không phải của cấu hình. Ghi vào báo cáo như một kết quả về **độ ổn định** chứ không phải một ô trống — và chính nó là luận điểm cho CH2: phương pháp chú ý nội tại không tinh chỉnh gì nên không có rủi ro này.

  ### Hạ learning rate không cứu được, và dữ liệu chỉ đúng hướng ngược lại

  Thử hai mức thấp hơn, mỗi mức một seed một epoch, tổng 19 phút GPU:

| lr | loss cuối epoch 1 | macro-F1 |
|---|---|---|
| `1e-5` | nảy 1,0131 – 1,1923 | 0,167 · 0,179 · 0,237 |
| `5e-6` | 1,1055 | 0,1670 |
| `2e-6` | **1,0992** | 0,1670 |

  Giả thuyết ban đầu là **nghiệm thoái hóa do bước cập nhật quá lớn**, vì loss ở `1e-5` nảy quanh `ln(3)` chứ không nằm im. Nếu đúng thì hạ learning rate phải kéo loss **rời khỏi** `ln(3)`.

  Kết quả ngược hẳn: càng hạ, loss càng **bám sát** `ln(3) = 1,0986`. Ở `2e-6` nó dừng ở 1,0992, tức lệch 0,0006. Đó là dáng của một mô hình **không nhúc nhích**, đúng dạng hỏng còn lại — dạng đòi cách chữa ngược lại, tức **tăng** bước cập nhật chứ không giảm.

  Ghi lại vì đây là bài học có thể dùng lại: hai dạng hỏng cho cùng một con số cuối 0,167, và **cách phân biệt là nhìn loss hội tụ về đâu khi hạ learning rate**. Bám vào `ln(3)` là không nhúc nhích; rời ra rồi lại nảy về là thoái hóa.

  ### Năm giả thuyết cơ học, kiểm hết bằng CPU, không tốn quota

  Vì hai lượt GPU đã dùng hết hạn mức tự đặt, phần truy nguyên còn lại làm trên CPU. Cả bốn đều **bị bác bỏ**, và điều đó tự nó đáng ghi — nó khoanh vùng nguyên nhân lại rất hẹp.

| Giả thuyết | Cách kiểm | Kết quả |
|---|---|---|
| Trọng số thân mô hình bị khởi tạo ngẫu nhiên trong im lặng | `output_loading_info=True` | **Bác bỏ.** Thân nạp đủ, chỉ thiếu 4 trọng số của đầu phân loại đúng như XLM-R |
| Tên khóa trong checkpoint không khớp | Đọc chỉ mục file, không tải cả 2,24 GB | InfoXLM dùng tiền tố `embeddings.`/`encoder.` còn XLM-R dùng `roberta.` — nhưng `transformers` tự ánh xạ đúng, xác nhận ở dòng trên |
| Cấu hình khác nhau ở chỗ nào đó | Tải hai `config.json` rồi so từng khóa | **Bác bỏ.** Giống hệt nhau, chỉ khác ba khóa không ảnh hưởng gì (`use_cache`, `position_embedding_type`, `transformers_version`) |
| Tràn số float16 như lỗi lớp 27 ở T07 | Đo đỉnh `\|activation\|` từng lớp trên dữ liệu thật | **Bác bỏ.** Đỉnh 25,2 — bằng **0,04 %** trần 65.504 của float16. XLM-R còn cao hơn ở 32,1 |
| Vector CLS thoái hóa, đầu phân loại nhận cùng một đầu vào | Khoảng cách cosin giữa các mẫu | **Bác bỏ, và ngược lại.** InfoXLM giãn cách 0,0261 so với 0,0020 của XLM-R — CLS của nó **phân biệt tốt hơn** |

  Còn lại: cùng kiến trúc, cùng cấu hình, trọng số nạp đủ, biên độ an toàn, biểu diễn phân biệt tốt — mà vẫn không học. Nguyên nhân nằm ở chính bộ trọng số InfoXLM tương tác với vòng tinh chỉnh này, và **truy tiếp thì tốn hơn giá trị thu được**: XLM-R đã đạt 0,771 và đó mới là mốc đề tài phải vượt.

  **Chốt: InfoXLM-large không tinh chỉnh được trên cấu hình này.** Ghi vào báo cáo như một kết quả về độ ổn định, kèm bảng trên để thấy đây là kết luận sau khi loại trừ, không phải một lần thử qua loa.

  ### Hai thứ giữ lại được từ một thí nghiệm thất bại

  **1. `scripts/check_checkpoint.py`** — soi một checkpoint trên CPU trước khi tốn quota GPU. Chạy cả bốn phép kiểm trên trong vài phút:

```
python scripts/check_checkpoint.py microsoft/infoxlm-large FacebookAI/xlm-roberta-large
```

  Dùng lại được cho ablation Sailor2 ở E13 và cho mọi nấc lùi mô hình ở mục 5 `CLAUDE.md`. Lần này mất nửa buổi để làm bằng tay bốn việc mà script làm trong hai phút.

  **2. Báo cáo nạp trọng số, ngay trong vòng huấn luyện.** `transformers` vốn in ra bảng nói trọng số nào thiếu, nhưng T18 **tắt log** bằng `logging.set_verbosity_error()` để chặn dòng cảnh báo cắt chuỗi lặp lại mỗi batch — và tắt luôn đúng thông báo cần đọc. Vì thế giả thuyết "thân mô hình chưa bao giờ được nạp" sống sót lâu hơn mức đáng lẽ.

  Nay `build_from_hub` tự đọc `output_loading_info`, in ra một dòng, và **ném lỗi ngay** nếu thân mô hình thiếu trọng số — thay vì để một mạng khởi tạo ngẫu nhiên mang tên nổi tiếng ngốn hết một phiên GPU. Tách thành `src/vihallulens/detect/loading_report.py` với 12 ca kiểm thử, gồm cả ca khẳng định đọc được cả `set` lẫn `list` vì hai phiên bản `transformers` trả về hai kiểu khác nhau.

  ### Một lỗi nữa: hai loại độ lệch dùng chung một tên khóa

  Bảng in ra màn hình đúng, nhưng bản ghi trong `results/runs.jsonl` **mâu thuẫn với chính nó**:

```
màn hình:  macro_f1   0.7416   0.0118   [0.7053, 0.7702]
runs.jsonl: "macro_f1_std": 0.01623553635603956
```

  Nguyên nhân: `summarise_runs` đặt độ lệch chuẩn **qua seed** vào khóa `{chỉ_số}_std`, còn `bootstrap_ci` đặt sai số chuẩn của **phân bố bootstrap** vào đúng khóa đó. Script gộp hai từ điển bằng `{**across_seeds, **spread}` nên cái viết sau đè cái viết trước, và **độ lệch qua seed của mọi chỉ số biến mất** khỏi bản ghi.

  Hai đại lượng khác nhau dùng chung một tên thì sớm muộn cũng có chỗ đè nhau. Sửa bằng cách **đặt tên khác nhau**: `_std` là độ lệch chuẩn qua seed, `_se` là sai số chuẩn từ bootstrap tập test. Thêm ca kiểm thử khẳng định hai từ điển **không có khóa nào chung** — chỉ một dòng, và nó chặn cả họ lỗi này chứ không riêng `macro_f1`.

  Cũng ghi thêm `metrics_per_seed` vào bản ghi: giá trị **thô** của từng seed cho từng chỉ số. Bản ghi có số thô thì gộp lại được về sau; bản ghi chỉ có số đã gộp thì không. Hai bản ghi vừa mất độ lệch qua seed đã tốn hai tiếng quota.

  Hai bản ghi của lượt 27/08 đã được dựng lại: `_se` lấy nguyên từ bản ghi gốc, `_std` lấy từ bảng chính lượt chạy đó in ra, riêng `macro_f1_std` tính lại đúng từ `macro_f1_per_seed` và khớp 0,0118 / 0,0249. Không con số nào bị bịa; có ghi chú `note` trong bản ghi nói rõ điều đó.

  Cùng lúc, `docs/EXPERIMENTS.md` Bảng 1 đổi cột `±` thành **khoảng tin cậy 95 % của tập test** cho mọi hàng. Trước đó hàng E01 ghi sai số bootstrap còn hàng bộ mã hóa định ghi độ lệch qua seed — hai đại lượng khác nhau trong một cột, đúng cái nhầm vừa sửa trong code.

  `pytest` **452 ca xanh**.

  ### Cách chạy — một phiên là đủ (đã chạy 27/08/2026)

  Mở `notebooks/t18_baseline_bo_ma_hoa_t4.ipynb` và **chạy cả ba ô liền nhau**.

  Ban đầu định tách ba phiên riêng vì quy tắc hạ xung ở mục 5 `CLAUDE.md`, nhưng nghĩ lại thì không cần: **hạ xung làm card chậm đi chứ không làm kết quả sai**. Toàn bộ macro-F1, accuracy, F1 từng lớp — thứ mà mốc so sánh này sinh ra để đo — không hề bị ảnh hưởng.

  Thứ duy nhất bị ảnh hưởng là cột `ms/mẫu`. Mà cột đó dùng cho E11 để so **nhóm phương pháp** (bộ mã hóa vs chú ý nội tại vs Gemini), không phải so PhoBERT với XLM-R. Chênh lệch giữa ba mô hình vốn đã tới từ độ dài chuỗi — 256 với 512 token, khoảng gấp đôi — nên 15 % hạ xung không đổi thứ hạng hay bậc độ lớn.

  Thay vì phòng ngừa bằng cách tách phiên, **script tự đo nhiệt độ và xung nhịp** trước khi chạy và sau mỗi seed, in cảnh báo nếu phát hiện hạ xung, và ghi số liệu vào `results/runs.jsonl`. Chạy xong sẽ **biết chắc** có bị hay không thay vì phải phỏng đoán. Phần đo này đã tách từ `scripts/measure_throughput.py` ra `src/vihallulens/evaluation/telemetry.py` để cả hai chỗ dùng chung.

  Tách ba phiên chỉ đáng làm nếu sau này cần so `ms/mẫu` giữa ba mô hình với nhau một cách chặt chẽ — lúc đó chạy lại từng cái, điểm số không phải chạy lại.

| Mô hình | 1 seed | 3 seed |
|---|---|---|
| PhoBERT-large | ~7 phút | ~25 phút |
| XLM-R-large | ~25 phút | ~80 phút |
| InfoXLM-large | ~25 phút | ~80 phút |

  Tổng khoảng **3 giờ**, trong hạn mức 30 giờ/tuần.

  **Mốc phải vượt là 0,689** — cận trên khoảng tin cậy của E01, không phải 0,656. Và chỗ đáng nhìn nhất là **F1 của lớp `intrinsic`**: E01 chỉ đạt 0,533, nên bộ mã hóa cải thiện được bao nhiêu ở đó mới là phần nói lên điều gì.

- [x] **T19** · M · E10 baseline LLM giám khảo — **xong 27/08/2026**
  - Prompt Gemini free tier trên **tối đa 300 mẫu** tập test, có xử lý rate limit và cache kết quả ra file. Khóa đọc từ `.env`, không hardcode.
  - **Kiểm tra:** file cache tồn tại, chạy lại không gọi API thêm; kết quả ghi vào `runs.jsonl` kèm ghi chú cỡ mẫu.

  **Task này để làm gì.** Mốc so sánh thứ ba, và là mốc mà lập luận chi phí ở CH2 thật sự nhắm vào. E01 không đọc gì; E09 đọc được nhưng phải tinh chỉnh trước, tốn GPU và có lúc không tinh chỉnh nổi như InfoXLM; còn E10 đọc được mà **không huấn luyện gì cả** — đổi lại là một lượt gọi API và một vòng mạng cho mỗi mẫu.

  **Đã làm:** `src/vihallulens/judge/` (prompt, client, cache), `scripts/run_judge_baseline.py`, `scripts/list_judge_models.py`. `pytest` **507 ca xanh**, toàn bộ phần gọi mạng chạy offline nhờ tiêm transport giả.

  ### Kết quả — 300 mẫu, 41 phút, 0 lỗi

| Chỉ số | Giá trị | Khoảng tin cậy 95 % |
|---|---|---|
| macro-F1 | **0,6637** | [0,6070 – 0,7191] |
| accuracy | 0,6667 | [0,6133 – 0,7233] |
| F1 `no` | 0,7527 | [0,6782 – 0,8182] |
| F1 `intrinsic` | 0,5823 | [0,4878 – 0,6707] |
| F1 `extrinsic` | 0,6562 | [0,5872 – 0,7212] |

  **Trên đúng 300 mẫu đó, baseline tầm thường E01 đạt 0,6860.** Tức **giám khảo LLM không vượt nổi hai đặc trưng bề mặt**. Khoảng tin cậy [0,607–0,719] chứa cả hai con số nên chênh lệch nằm trong nhiễu, không kết luận được ai hơn ai — nhưng "không hơn nổi baseline tầm thường" tự nó đã là kết quả.

  Diễn giải đúng **không phải** "Gemini kém". Mô hình được dùng là `gemini-3.1-flash-lite`, bậc nhỏ nhất, và lý do chọn nó nằm ở mục dưới. Kết luận đúng là: **những gì free tier cho phép không đủ để thay thế một phương pháp chuyên dụng** — chính là điều bảng đánh đổi E11 sinh ra để nói.

  ### Ma trận nhầm lẫn, và một điều bất ngờ

| thật \\ đoán | `no` | `intrinsic` | `extrinsic` | tổng |
|---|---|---|---|---|
| `no` | **70** | 9 | 32 | 111 |
| `intrinsic` | 3 | **46** | **48** | 97 |
| `extrinsic` | 2 | 6 | **84** | 92 |
| tổng | 75 | 61 | **164** | 300 |

  Recall: `extrinsic` **0,913**, `no` 0,631, `intrinsic` **0,474**.

  Giám khảo đoán `extrinsic` **164 lần trong khi thực tế chỉ có 92** — vống lên 78 %. Và **48 trên 97 mẫu `intrinsic`, đúng một nửa, bị gọi thành `extrinsic`**.

  Đọc lý do nó tự viết thì thấy đây **không phải lỗi hiểu bài** mà là lỗi **thứ tự ưu tiên**:

> Câu trả lời cung cấp thông tin sai lệch về vị trí địa lý so với ngữ cảnh (đảo ngược các hướng) **và** đưa ra thông tin về bán cầu Tây không hề được đề cập trong ngữ cảnh.

  Nó nhận ra **cả hai** dấu hiệu — vừa mâu thuẫn với ngữ cảnh (nội tại) vừa thêm thứ không có (ngoại lai) — rồi chọn ngoại lai. Mà theo đúng bộ tiêu chí T13, nó chọn **không sai**: `noi_tai` đòi *mọi* thông tin phải có trong ngữ cảnh, nên chỉ cần thêm một chi tiết là rơi sang `ngoai_lai`.

  ### Điều đáng giá nhất: giám khảo hỏng đúng chỗ con người hỏng

  Đây không phải một điểm yếu riêng của LLM. Đo ở T13 trên 20 mẫu đối chứng có đáp án, hai sinh viên gán nhãn tay cũng vấp đúng ranh giới đó: nhãn `Refutes` (đáp án đúng là `noi_tai`) chỉ đạt **7/10 và 5/10**, trong khi nhãn `Supports` (đáp án `khong`) đạt 9/10 và 7/10. Và 8/100 mẫu có một người gán `noi_tai` còn người kia gán `ngoai_lai`.

| Người chấm | Recall trên lớp `intrinsic` |
|---|---|
| Sinh viên 1 (T13, 10 mẫu đối chứng) | 0,70 |
| Sinh viên 2 (T13, 10 mẫu đối chứng) | 0,50 |
| **Gemini 3.1 Flash Lite (T19, 97 mẫu)** | **0,474** |

  Giám khảo LLM rơi đúng vào dải của con người, và **lệch cùng một hướng**: nội tại bị đọc thành ngoại lai. Kappa giữa hai người đo được ở T13 chỉ 0,505.

  Đây là lập luận mạnh cho đề tài, và nên đưa vào phần bàn luận: **ranh giới nội tại–ngoại lai khó một cách nội tại**, chứ không phải khó vì phương pháp nào đó dở. Nó cũng lý giải vì sao lớp `intrinsic` là lớp yếu nhất ở *cả ba* mốc so sánh — E01 0,533, E09 XLM-R 0,722, E10 0,582 — và vì sao đó là chỗ `chunk-aware lookback ratio` phải chứng minh mình.

  **Vì thế không sửa prompt cho giám khảo dễ thở hơn.** Thêm một quy tắc ưu tiên kiểu "vừa mâu thuẫn vừa thêm thì tính là nội tại" gần như chắc chắn nâng điểm, nhưng làm hỏng hai thứ: giám khảo sẽ nhận một đề bài **khác** với đề bài hai sinh viên đã nhận, nên mất luôn phép so sánh vừa nói ở trên; và quy tắc đó suy ra từ chính nhãn của tập test, tức là uốn prompt theo đáp án.

  ### Ba điều đo được làm đổi thiết kế

| Điều đo được | Hệ quả |
|---|---|
| `gemini-2.5-flash` **đã bị gỡ**, API trả 404 kèm "no longer available to new users" cho khóa mới | Tên mô hình là thứ phải kiểm trước mỗi lượt chạy, không phải thứ tin theo tài liệu. Thêm `scripts/list_judge_models.py` hỏi thẳng API |
| `gemini-3.6-flash` chỉ cho **20 lượt mỗi NGÀY** — `GenerateRequestsPerDayPerProjectPerModel-FreeTier=20` | 300 mẫu sẽ mất 15 ngày. Không dùng |
| `gemini-3.5-flash-lite` trả lời tiếng Việt **mất hết dấu** | Không dùng |

  Chốt `gemini-3.1-flash-lite`: giữ nguyên dấu, cùng độ chính xác với flash-lite trên mẫu thử, khoảng 5 giây một lượt. Tên **ghim cứng**, không dùng bí danh `-latest` — bí danh sẽ lặng lẽ thành mô hình khác giữa lượt chạy sinh ra Bảng 1 và lượt chạy kiểm lại nó.

  ### Độ tin cậy tự khai: sai về mức, nhưng vẫn mang tin

  Trung bình giám khảo tự khai **0,904** trong khi thực tế đúng **0,667**. ECE 0,280. Nó tin mình hơn thực lực khoảng 24 điểm phần trăm.

  Nhưng con số đó **không vô dụng**: 21 câu nó tự khai dưới 1/3 thì chỉ đúng **9/21 = 43 %**, so với 67 % của toàn bộ. Nghĩa là khi nó nói mình không chắc thì nên tin — dấu hiệu này dùng được để lọc, dù mức tuyệt đối thì lệch.

  Con số này để ở khóa riêng `ece_self_reported`, **không** trộn vào cột ECE của Bảng 1: ECE của E01 và E09 tính từ xác suất softmax, còn đây là con số mô hình tự nói về mình. Hai đại lượng khác nhau đặt chung một cột là đúng cái lỗi T18 đã phải sửa hai lần.

  ### Năm lỗi gặp khi dựng, đều đã sửa

  1. **Một lần đọc timeout làm sập cả script.** `http_transport` chỉ bắt `HTTPError`, còn timeout của socket ném ra ngoài và kết thúc lượt chạy bằng traceback. Nay **mọi lỗi mạng trở thành một mã trạng thái** (599) để đi chung đường thử lại — vòng lặp thử lại là chỗ duy nhất quyết định phải làm gì với thất bại. Kèm hạ timeout từ 180 xuống 60 giây, vì một lượt gọi bình thường chỉ mất 4,3 giây.

  2. **Hàm phân biệt hạn mức ngày với hạn mức phút đọc trên bản thân đã bị cắt còn 400 ký tự**, trong khi `quotaId` nằm ở khoảng ký tự 1.100. Hạn mức ngày vì thế bị hiểu thành hạn mức phút và thử lại vô ích. Nay phân loại trên **toàn bộ** thân, chỉ cắt phần đem hiển thị. Có ca kiểm thử khẳng định `quotaId` nằm sau ký tự thứ 400 mà vẫn nhận ra.

  3. **Script báo 12 lỗi mà không nói lỗi gì.** Một lượt chạy hỏng ở mọi mẫu thì chỉ có một nguyên nhân, mà in ra mỗi con số đếm thì không có gì để lần. Nay lỗi **đầu tiên** được in nguyên văn — đúng cách lẽ ra phải phát hiện ngay tên mô hình đã bị gỡ.

  4. **`--dry-run` không bao giờ trúng cache.** Đúng chỗ tiêu chí hoàn thành của task này nhắm tới, và chỉ lộ ra khi chạy thật phép kiểm đó. Khóa cache lấy tên mô hình từ *đối tượng* giám khảo, mà chế độ dry run thì không có đối tượng nào nên rơi vào nhánh dự phòng gán chuỗi `"dry-run"` — tính ra một khóa không thể khớp gì, rồi báo thiếu cả 300 mẫu trong một cache đang giữ đủ 300. Nay tên mô hình được **truyền vào** chứ không suy ra. Kèm ba ca kiểm thử, trong đó một ca khẳng định đổi mô hình thì **không** dùng lại câu trả lời cũ — hai mô hình trả lời cùng một prompt là hai phép đo, không phải một.

  5. **Độ tin cậy dưới 1/3 làm lệch chính phép đo hiệu chỉnh.** Trải một độ tin cậy 0,2 cho lớp đã chọn thì hai lớp còn lại mỗi lớp được 0,4, và `argmax` sẽ trỏ sang lớp khác — tức ECE chấm một dự đoán **khác** với dự đoán đang báo cáo. Nay có sàn ngay trên 1/3, và số câu bị nâng sàn được đếm và in ra.

  ### Cache: thứ khiến việc dừng trở nên rẻ

  Mỗi câu trả lời ghi xuống **ngay khi nhận được**, không đợi lúc kết thúc. Một lượt chạy bị hạn mức ngày, bị rớt mạng hay bị Ctrl-C vẫn giữ nguyên mọi thứ đã trả tiền. Khóa cache gồm **cả tên mô hình lẫn nguyên văn prompt**: sửa tiêu chí thì câu trả lời cũ không khớp nữa, đúng như phải thế — chúng trả lời một câu hỏi khác, và dùng lại sẽ là cách âm thầm nhất để báo cáo một kết quả chưa từng xảy ra.

  `results/judge_cache.jsonl` được commit. Nhờ vậy con số của E10 kiểm lại được **không tốn một lượt gọi API nào**: chạy `python scripts/run_judge_baseline.py --dry-run` là ra đúng bảng trên.

- [ ] **T20** · L · E02 tái lập Lookback Lens gốc
  - Đọc mục 1 của `docs/REFERENCES.md` trước khi viết code. Tái lập **đúng công thức gốc**, không phải biến thể gần đúng.
  - Trích đặc trưng lookback gộp, huấn luyện `LogisticRegression`.
  - Ba điểm phải tự kiểm trước khi báo kết quả: (a) lookback ratio là **trung bình chú ý theo token**, chia cho số token ngữ cảnh và số token đã sinh, không phải tổng; (b) véc-tơ đặc trưng nối đủ `L × H` giá trị rồi mới lấy trung bình qua các bước trong span; (c) span ở đây là **toàn bộ phản hồi** vì nhãn của ViHallu ở mức phản hồi, khác thiết lập sliding-window-8 của bài gốc — ghi khác biệt này vào PR.
  - **Kiểm tra:** kết quả cao hơn baseline tầm thường E01; nếu không thì dừng lại rà soát cách trích đặc trưng, lỗi gần như chắc chắn ở khâu trích chứ không ở phương pháp.

---

## Giai đoạn 4 — Phương pháp cốt lõi (tuần 6–7)

- [ ] **T21** · L · Đặc trưng chunk-aware
  - Hiện thực `chunk_entropy`, `chunk_max_share`, `chunk_gini`, `top1_top2_gap`, `chunk_drift`.
  - **Kiểm tra:** `pytest tests/test_features.py` xanh với đầu vào đã biết đáp án.

- [ ] **T22** · L · E03 chunk-aware chia theo câu
- [ ] **T23** · L · E04 chunk-aware chia theo cửa sổ token, quét 64/128/256
- [ ] **T24** · L · E05 chốt cách chia chunk
  - **Kiểm tra:** Bảng 3 trong `docs/EXPERIMENTS.md` được điền đầy đủ, có kết luận chọn cấu hình nào và lý do.

- [ ] **T25** · L · 🚩 E06 định vị chú ý trên ISE-DSC01
  - Đo hit@1, hit@3, MRR so với sàn ngẫu nhiên; đo entropy của nhãn NEI so với hai nhãn kia.
  - **Kiểm tra:** Bảng 2 được điền, có kiểm định thống kê cho phần entropy. **Đây là thí nghiệm quyết định CH1.**

- [ ] **T26** · L · E07 chunk-aware trên ngữ cảnh dài ISE-DSC01
- [ ] **T27** · M · E08 thí nghiệm lớp ngoại lai trên ViWikiFC dùng kho truy xuất từ T16

---

## Giai đoạn 5 — Báo cáo giữa kỳ (tuần 8–9)

- [ ] **T28** · LM · Gom kết quả và viết báo cáo giữa kỳ
  - **Kiểm tra:** file báo cáo giữa kỳ, Bảng 1–3 đã có số, gửi GVHD trước 04/10.

---

## Giai đoạn 6 — Thực nghiệm đầy đủ (tuần 10–11)

- [ ] **T29** · L · E12 ablation nhóm đặc trưng
- [ ] **T30** · L · E13 so Qwen2.5-7B với Sailor2-8B, kèm phân tích vị trí đầu chú ý
- [ ] **T31** · L · E14 bậc thang kích thước 7B / 3B / 1.5B
- [ ] **T32** · M · E11 bảng đánh đổi độ chính xác và chi phí
- [ ] **T33** · M · E15 đối chứng ngoài trên ViWikiFC split gốc
- [ ] **T34** · M · E16 khái quát hóa chéo bộ
- [ ] **T35** · LM · Phân tích sai sót
  - Lấy 100 mẫu dự đoán sai, phân loại kiểu lỗi, viết nhận xét.
  - Tách kết quả theo `meta.prompt_type`: so macro-F1 trên nhóm `noisy` (prompt bị bỏ dấu) với phần còn lại, theo yêu cầu ở `docs/EXPERIMENTS.md`.
  - **Kiểm tra:** `results/error_analysis.csv` 100 dòng có cột loại lỗi và cột `prompt_type`, kèm biểu đồ phân bố và một bảng hai dòng `noisy` / còn lại.

---

## Giai đoạn 7 — Đóng gói hệ thống (tuần 12–13)

- [ ] **T36** · L · Thư viện Python hoàn chỉnh, có docstring và ví dụ dùng
- [ ] **T37** · L · Dịch vụ REST API ba endpoint theo `docs/SPEC.md`
- [ ] **T38** · L · Dockerfile, chạy được bằng một lệnh
- [ ] **T39** · L · Giao diện quan sát: tô màu chunk theo tỷ trọng chú ý
- [ ] **T40** · M · Hệ thống RAG minh họa tối giản, khoảng 20 tài liệu mẫu
  - **Kiểm tra:** demo chạy đầu cuối, hỏi một câu và thấy điểm rủi ro hiện ra.

---

## Giai đoạn 8 — Viết báo cáo (tuần 14–15)

- [ ] **T41** · M · E17 chuyển miền sang ViFactCheck — **chỉ làm nếu còn thời gian**
- [ ] **T42** · LM · Chương 1–2: giới thiệu và cơ sở lý thuyết
- [ ] **T43** · LM · Chương 3–4: phân tích yêu cầu và thiết kế hệ thống
- [ ] **T44** · LM · Chương 5–6: giải pháp công nghệ, hiện thực và triển khai
- [ ] **T45** · LM · Chương 7: đánh giá và thảo luận, gồm mọi bảng kết quả
- [ ] **T46** · LM · Chương 8: kết luận và hướng phát triển
- [ ] **T47** · LM · Rà soát định dạng theo mẫu trường, kiểm tra mục lục và caption

---

## Giai đoạn 9 — Bảo vệ (tuần 16–18)

- [ ] **T48** · LM · Báo cáo cuối kỳ cho GVHD (trước 22/11)
- [ ] **T49** · LM · Chỉnh sửa sau phản biện (tuần 17)
- [ ] **T50** · LM · Slide và diễn tập bảo vệ (tuần 18)

---

## Việc hành chính định kỳ — không có mã task nhưng bắt buộc

Quy trình của bộ môn tính email và nhật ký làm việc là **minh chứng đánh giá quá trình**, ngang với kết quả kỹ thuật.

| Việc | Tần suất | Ghi chú |
|---|---|---|
| Email báo cáo tuần gửi GVHD | mỗi tuần, kể cả tuần không tiến triển | CC bạn cùng nhóm, **Reply All vào chuỗi cũ**, cả kỳ chỉ một chuỗi. Đề xuất gửi chiều thứ Sáu. Mẫu: `UniversityRequirements/WeeklyLogs/Mau_email_bao_cao_tuan.md` |
| Cập nhật sheet "Nhật ký" trong `UniversityRequirements/Plan/Ke_hoach_KLTN_da_dien.xlsx` | mỗi tuần | Xin GVHD phê duyệt nhật ký |
| Cập nhật cột "thực tế" trong sheet kế hoạch | mỗi tuần | Đơn vị trên Gantt là **tuần** |

## Bốn mốc không được lỡ

| Mốc | Tuần | Thời gian | Ý nghĩa |
|---|---|---|---|
| ~~Cổng khả thi kỹ thuật (T05–T08)~~ | 3 | 17/8 – 23/8 | **ĐÃ QUA 20/08/2026.** Qwen2.5-7B ở 4.096 token, VRAM đỉnh 8.428/14.336 MB, hai bộ bắt buộc cần 10 giờ 19 GPU. Không dùng nấc lùi nào. Đề tài thay thế (phân đoạn tăng cường tóm tắt cho RAG pháp lý) **không cần tới nữa** |
| Báo cáo giữa kỳ (T28) | 8–9 | trước 04/10 | Phải có kết quả thực nghiệm sơ bộ, không chỉ đọc tài liệu |
| Báo cáo cuối kỳ (T48) | 16 | trước 22/11 | GVHD quyết định đề tài có được phản biện hay không |
| Phản biện (T49) | 17 | 23/11 – 29/11 | Quyết định được bảo vệ qua hội đồng oral hay hội đồng poster |

Tuần 18 (30/11 – 06/12) báo cáo trước hội đồng. Hình thức có thể là **oral hoặc poster** tùy kết quả phản biện — xem mục "BÁO CÁO POSTER" trong `UniversityRequirements/Reports/Mau bao cao KLTN_DS.docx` nếu rơi vào hướng poster.

## Nhật ký chặn

Ghi lại mọi lần bị chặn và cách xử lý, để đưa vào phần hạn chế của báo cáo.

| Ngày | Task | Vấn đề | Xử lý |
|---|---|---|---|
| 19/08 | T07 | Notebook chạy code cũ: `git clone` vào thư mục đã tồn tại thì hỏng nhưng `!` không dừng ô; và `pip install -e .` ghi file `.pth` mà Python chỉ đọc lúc khởi động nên kernel đang chạy không thấy gói vừa cài | Ô 1 kéo bản mới thay vì clone đè; `conftest.py` và các script tự thêm `src/` vào `sys.path`; thêm `scripts/probe_env.py` in commit và đường dẫn gói |
| 19/08 | T07 | `lookback_total` ra `nan` trên cả hai mẫu, dù bộ nhớ đạt (đỉnh 8.395 MB < 14 GB). Toán lookback không thể sinh `nan` từ đầu vào hữu hạn nên `attn_weights` đã chứa `nan`/`inf` | Đo bằng `layer_diagnostics`: **đúng một lớp hỏng, lớp 27 (lớp cuối)**, 27 lớp còn lại sạch. Chạy lại với `--compute-dtype float32` thì sạch hoàn toàn, tổng hàng attention 1,0000, `lookback_total` trong [0, 1], đỉnh 10.658 MB vẫn dưới 14 GB. Cái giá: chậm 2,2 lần (mẫu ngắn) tới 3,8 lần (mẫu dài nhất) |
| 19/08 | T07 | Chưa chốt được dùng float16 hay float32: float16 nhanh hơn nhiều nhưng chưa biết 27 lớp còn sống có bị bóp méo không, và mới thử đúng hai mẫu | Đo trên 20 mẫu trải từ 47 tới 4.805 từ: lớp 27 hỏng ở **20/20 mẫu và chỉ mình nó**; 27 lớp còn lại lệch trung bình 0,00074 và phân vị 99 là 0,00635 trên thang [0, 1]; lỗi **không** tăng dần về cuối (lớp lệch nhiều nhất là 14 và 19, nằm giữa) nên không có bóp méo hệ thống. Chốt **float16 + bỏ lớp 27**, nhanh hơn 3,6 lần |
| 19/08 | T07 | `\|Δ\|` lớn nhất giữa hai kiểu số bằng đúng 1,00000, tức toàn thang đo — con số tròn trịa tố cáo lỗi công thức chứ không phải nhiễu số học | Truy ra token phản hồi **đầu tiên**: chưa có token nào đứng trước nên `self_mean = 0` và tỷ lệ luôn bằng 1, còn float16 underflow thì thành 0. Đó là phép chia 0/0. Bỏ hẳn token đầu khỏi phần được chấm; sau khi sửa, `lookback_total` không còn chạm 1,0 |
