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

- [ ] **T02** · L · Cấu hình lint và test
  - Thêm cấu hình `ruff` vào `pyproject.toml`, dòng tối đa 100 ký tự.
  - Tạo `tests/test_smoke.py` với một test tầm thường.
  - **Kiểm tra:** `ruff check .` và `pytest` đều xanh.

- [ ] **T03** · M · Module cấu hình
  - Viết `src/vihallulens/config.py` định nghĩa các pydantic model theo mục 3 của `docs/SPEC.md`.
  - Hàm `load_config(path) -> ExperimentConfig` và `config_hash(cfg) -> str`.
  - Tạo `configs/example.yaml`.
  - **Kiểm tra:** `pytest tests/test_config.py` xanh, gồm ca hợp lệ và ca thiếu trường bắt buộc phải raise.

- [ ] **T04** · M · Module ghi kết quả
  - Viết `src/vihallulens/evaluation/logging.py` với `log_result` và `export_table` theo `docs/SPEC.md`.
  - **Kiểm tra:** gọi `log_result` hai lần rồi `export_table` trả về DataFrame 2 dòng.

---

## Giai đoạn 1 — 🚩 Cổng khả thi kỹ thuật (tuần 3, ưu tiên cao nhất)

> Nếu giai đoạn này thất bại, **dừng toàn bộ** và báo người dùng. Không tự đổi hướng đề tài.

- [ ] **T05** · L · Đo ngân sách bộ nhớ trên giấy
  - Viết `scripts/probe_vram.py --model ... --seq-len ...` in ra: số lớp, số đầu chú ý, dung lượng trọng số sau lượng tử hóa 4-bit, và ước tính dung lượng ma trận chú ý **một lớp** theo công thức `n_heads × seq_len² × 2 byte`.
  - Chạy với `seq_len` thuộc `{1024, 2048, 4096, 8192}`. Đối chiếu với bảng ngân sách ở mục 5 của `CLAUDE.md`.
  - **Đo tỷ lệ token trên từ của tokenizer Qwen2.5 với tiếng Việt.** Mọi số liệu trong `docs/DATA.md` tính bằng **từ**, còn ngân sách bộ nhớ tính bằng **token** — không có tỷ lệ thật thì không biết `max_context_tokens = 4096` cắt mất bao nhiêu phần trăm mẫu. Tokenize toàn bộ ngữ cảnh của bốn bộ, in ra phân vị 50/90/99 và tỷ lệ mẫu vượt 2.048 và 4.096 token.
  - **Kiểm tra:** in ra bảng ước tính bộ nhớ và bảng phân bố độ dài token, không cần GPU. Ghi tỷ lệ mẫu bị cắt vào PR.

- [ ] **T06** · L · Nạp mô hình 4-bit trên T4
  - Nạp `Qwen/Qwen2.5-7B-Instruct` với NF4, `attn_implementation="eager"`, `torch_dtype=float16`.
  - In VRAM sau khi nạp.
  - **Kiểm tra:** nạp thành công trên Kaggle T4, VRAM sau nạp dưới 7 GB. Dán log vào PR.

- [ ] **T07** · L · 🚩 Trích attention bằng hook, không tràn bộ nhớ
  - Đăng ký forward hook trên từng `self_attn`, tính tổng theo chunk ngay trong hook, `del` tensor trước khi ra khỏi hook. Chặn `all_self_attns` tích lũy bằng cách cho hook trả về `(attn_output, None)`.
  - **Việc đầu tiên phải làm:** kiểm tra `output` của hook có thật sự chứa `attn_weights` không — điều này phụ thuộc phiên bản `transformers` (xem mục 5 của `CLAUDE.md`). Xong thì ghim đúng phiên bản đó vào `pyproject.toml` và viết một test khẳng định `attn_weights is not None`. Không ghim thì một lần `uv pip install` sau này có thể làm hỏng toàn bộ pipeline mà không báo lỗi.
  - Chạy thử với một mẫu ViHallu (~200 từ) và một mẫu ISE-DSC01 dài nhất (~4.805 từ).
  - Chốt **mẫu prompt duy nhất** ghép ngữ cảnh, câu hỏi và phản hồi. Ghi nguyên văn vào mục 8 của `CLAUDE.md`. Sau task này không được đổi.
  - **Kiểm tra:** cả hai chạy xong, `torch.cuda.max_memory_allocated()` dưới 14 GB, in ra shape của `lookback_per_chunk`, và mục 8 của `CLAUDE.md` đã có mẫu prompt. **Đây là cổng chặn — không qua thì dừng.**

- [ ] **T08** · L · Đo thông lượng và quyết định bậc thang
  - Đo ms/mẫu với 20 mẫu ở mỗi mức độ dài. Nếu 7B không qua T07, thử lại với 3B rồi 1.5B.
  - Ghi kết quả vào `results/feasibility.jsonl`.
  - **Kiểm tra:** file kết quả tồn tại, có kết luận rõ mô hình nào dùng được với ngữ cảnh tối đa bao nhiêu token.

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
| Email báo cáo tuần gửi GVHD | mỗi tuần, kể cả tuần không tiến triển | CC bạn cùng nhóm, **Reply All vào chuỗi cũ**, cả kỳ chỉ một chuỗi. Đề xuất gửi chiều thứ Sáu. Mẫu: `UniversityRequirements/Mau_email_bao_cao_tuan.md` |
| Cập nhật sheet "Nhật ký" trong `Ke_hoach_KLTN_da_dien.xlsx` | mỗi tuần | Xin GVHD phê duyệt nhật ký |
| Cập nhật cột "thực tế" trong sheet kế hoạch | mỗi tuần | Đơn vị trên Gantt là **tuần** |

## Bốn mốc không được lỡ

| Mốc | Tuần | Thời gian | Ý nghĩa |
|---|---|---|---|
| Cổng khả thi kỹ thuật (T05–T08) | 3 | 17/8 – 23/8 | Không qua thì chuyển sang đề tài thay thế (phân đoạn tăng cường tóm tắt cho RAG pháp lý). Biết càng sớm càng đỡ mất thời gian |
| Báo cáo giữa kỳ (T28) | 8–9 | trước 04/10 | Phải có kết quả thực nghiệm sơ bộ, không chỉ đọc tài liệu |
| Báo cáo cuối kỳ (T48) | 16 | trước 22/11 | GVHD quyết định đề tài có được phản biện hay không |
| Phản biện (T49) | 17 | 23/11 – 29/11 | Quyết định được bảo vệ qua hội đồng oral hay hội đồng poster |

Tuần 18 (30/11 – 06/12) báo cáo trước hội đồng. Hình thức có thể là **oral hoặc poster** tùy kết quả phản biện — xem mục "BÁO CÁO POSTER" trong `UniversityRequirements/Mau bao cao KLTN_DS.docx` nếu rơi vào hướng poster.

## Nhật ký chặn

Ghi lại mọi lần bị chặn và cách xử lý, để đưa vào phần hạn chế của báo cáo.

| Ngày | Task | Vấn đề | Xử lý |
|---|---|---|---|
| | | | |
