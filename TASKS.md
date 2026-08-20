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

  2. **Hệ quả trực tiếp: nấc lùi 1 là đòn bẩy cho bộ nhớ, gần như vô dụng với thời gian.** Hạ `max_context_tokens` từ 4.096 xuống 2.048 chỉ ảnh hưởng 483 mẫu của hai bộ bắt buộc (3 của ViHallu, 480 của ISE-DSC01), tiết kiệm đúng **10 phút** trên tổng 10 giờ 19. Nếu sau này thiếu giờ GPU thì **đòn bẩy thật là lấy mẫu con ISE-DSC01**, không phải cắt ngữ cảnh. Ghi lại đây để sau này khỏi lùi nhầm nấc.

  3. **ISE-DSC01 nuốt 92 % chi phí của hai bộ bắt buộc** trong khi chỉ chiếm 84 % số mẫu — vì mẫu của nó dài hơn gấp đôi (941 ms/mẫu so với 420 ms/mẫu của ViHallu). Nó cũng là bộ duy nhất có nhiều mẫu ở mức đắt nhất (480 mẫu).

  4. **Phần ngoài GPU chỉ chiếm 9 %.** Lời gọi mô hình chiếm 90–92 % thời gian ở cả bốn mức; render prompt, cắt theo ngân sách và chuyển đặc trưng về CPU gộp lại chưa tới một phần mười. Tối ưu phía CPU không đáng công.

  **Ghi chú chuyển cho giai đoạn trích đặc trưng (T21 trở đi), chưa làm bây giờ:** một lượt ISE-DSC01 mất 9 giờ 30 liên tục, sát giới hạn thời gian một phiên Kaggle. Script trích đặc trưng thật phải **chạy được theo lô và nối lại được** — ghi ra từng phần rồi bỏ qua phần đã có khi chạy lại — chứ không thể là một vòng lặp duy nhất mất chín tiếng rồi mất sạch nếu phiên đứt. Ngoài ra một số thí nghiệm cần **trích lại toàn bộ** chứ không dùng lại được: E04 quét ba cỡ cửa sổ token (ranh giới chunk đổi), E13 đổi mô hình đọc sang Sailor2-8B, E14 lùi 3B và 1.5B. Ước tổng cộng khoảng 19 giờ GPU trải từ tuần 6 tới tuần 11, tức 2–4 giờ mỗi tuần — vẫn thoải mái trong quota, nhưng phải xếp lịch chứ không dồn.

---

## Giai đoạn 2 — Chuẩn hóa dữ liệu (tuần 3–4)

- [x] **T08B** · M · Khảo sát thư mục dữ liệu — hoàn thành 19/08/2026
  - Đã quét `data/raw/`, liệt kê mọi file `.csv`, `.json`, `.parquet` kèm kích thước, số dòng và tên cột.
  - Nhận diện bốn bộ **theo nội dung cột, không dựa vào tên file**: có `prompt` và `response` là ViHallu; có `verdict` và `domain` là ISE-DSC01; có `pairID` và `gold_label` là ViWikiFC; có `Statement` và `Topic` là ViFactCheck.
  - Đã đổi tên về quy ước `{dataset}_{split}.{ext}`, dời hết lên `data/raw/` (bỏ bốn thư mục con), bảng ánh xạ ghi ở `data/raw/MANIFEST.md`. Danh sách đường dẫn chốt nằm ở mục 2 của `docs/DATA.md`.
  - **Kết quả kiểm tra:** `data/raw/MANIFEST.md` liệt kê đủ bốn bộ với tên file trước và sau khi đổi; số dòng và phân bố nhãn khớp 100 % bảng mục 4 của `docs/DATA.md` (7.000 / 36.369 / 16.738+2.090+2.091 / 5.062+723+1.447). Không có file lạ, không thiếu bộ nào.

- [ ] **T09** · M · Chuẩn hóa ViHallu
  - Viết `src/vihallulens/data/vihallu.py` theo `docs/DATA.md`. Nguồn: `data/raw/vihallu_train.csv`. Bỏ qua `data/raw/vihallu_test_public.csv` vì không có nhãn.
  - Suy ra `meta.prompt_type` theo luật ở mục 7 của `docs/DATA.md`: prompt không có ký tự có dấu tiếng Việt thì gán `noisy`, còn lại gán `unknown`. Ghi kèm `meta.prompt_has_diacritics`.
  - **Kiểm tra:** `python scripts/normalize_data.py --dataset vihallu` sinh Parquet 7.000 dòng, phân bố nhãn khớp 2.245 / 2.448 / 2.307.

- [ ] **T10** · M · Chuẩn hóa ISE-DSC01
  - Nguồn: `data/raw/isedsc01_train.json`. Bỏ qua hai file `isedsc01_test_public.json` và `isedsc01_test_private.json` vì thiếu `verdict`.
  - **Kiểm tra:** 36.369 dòng, phân bố 12.786 / 11.000 / 12.583, số mẫu tìm được `evidence_start` là 23.785.

- [ ] **T11** · M · Chuẩn hóa ViWikiFC
  - Nguồn: `data/raw/viwikifc_{train,dev,test}.csv`, giữ nguyên split gốc.
  - **Kiểm tra:** 16.738 / 2.090 / 2.091 dòng, `evidence_start` tìm được 100 % ở cả ba nhãn. Nếu không đủ 100 % thì có lỗi encoding, dừng lại.

- [ ] **T12** · M · Chuẩn hóa ViFactCheck
  - Nguồn: `data/raw/vifactcheck_{train,dev,test}.parquet`, giữ nguyên split gốc. Bỏ cột `Unnamed: 0`.
  - **Kiểm tra:** 5.062 / 723 / 1.447 dòng, tỷ lệ `evidence_start` tìm được xấp xỉ 59 %.

- [ ] **T13** · LM · Kiểm tra thủ công ánh xạ NEI sang ngoại lai
  - Lấy ngẫu nhiên 100 mẫu nhãn NEI từ ViWikiFC, hai người gán độc lập xem có đúng là "chứa thông tin ngoài ngữ cảnh" không.
  - **Kiểm tra:** file `results/nei_mapping_audit.csv` có 100 dòng, báo cáo tỷ lệ khớp và hệ số đồng thuận.

- [ ] **T14** · M · Chia tập và báo cáo rò rỉ
  - Hiện thực `group_split`. Chia ViHallu và ISE-DSC01 80/10/10 seed 42. ViWikiFC và ViFactCheck giữ split gốc.
  - Sinh `results/leakage_report.md` với số liệu rò rỉ của cả bốn bộ.
  - **Kiểm tra:** báo cáo khớp bảng mục 6 của `docs/DATA.md`; `group_split` raise khi cố tình truyền dữ liệu rò rỉ.

- [ ] **T15** · M · Chia chunk
  - Hiện thực `chunk_context` cả hai chiến lược và `locate_evidence_chunk`.
  - **Kiểm tra:** `pytest tests/test_chunking.py` xanh, gồm ca câu tiếng Việt có số thập phân, ca bằng chứng vắt qua ranh giới chunk.

- [ ] **T16** · M · Kho truy xuất ViWikiFC
  - Trích 3.814 câu bằng chứng duy nhất, dựng chỉ mục BM25.
  - **Kiểm tra:** file `data/interim/viwikifc_evidence_corpus.parquet` có 3.814 dòng; truy vấn thử một claim trả về top-5 hợp lý.

---

## Giai đoạn 3 — Các baseline (tuần 4–5)

- [ ] **T17** · M · E01 baseline tầm thường
  - Hai đặc trưng: độ dài phản hồi và tỷ lệ trùng lặp từ vựng. Logistic regression, 5 seed.
  - **Kiểm tra:** kết quả ghi vào `results/runs.jsonl`, điền Bảng 1 dòng đầu trong `docs/EXPERIMENTS.md`.

- [ ] **T18** · M · E09 baseline bộ mã hóa
  - Tinh chỉnh PhoBERT-large, XLM-R-large, InfoXLM-large ba lớp trên ViHallu.
  - **Kiểm tra:** ba dòng kết quả, kèm ms/mẫu và VRAM đỉnh.

- [ ] **T19** · M · E10 baseline LLM giám khảo
  - Prompt Gemini free tier trên **tối đa 300 mẫu** tập test, có xử lý rate limit và cache kết quả ra file. Khóa đọc từ `.env`, không hardcode.
  - **Kiểm tra:** file cache tồn tại, chạy lại không gọi API thêm; kết quả ghi vào `runs.jsonl` kèm ghi chú cỡ mẫu.

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
