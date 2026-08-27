# EXPERIMENTS.md — Kế hoạch thực nghiệm

## 1. Ba câu hỏi nghiên cứu

- **CH1** — `chunk-aware lookback ratio` có hơn lookback gộp không, và phân bố chú ý có tập trung đúng vào đoạn chứa bằng chứng không?
- **CH2** — Hướng nội tại đứng ở đâu trên mặt phẳng đánh đổi độ chính xác và chi phí, so với bộ mã hóa và LLM giám khảo?
- **CH3** — Tín hiệu chú ý đóng góp thêm bao nhiêu so với đặc trưng bề mặt, và có khái quát hóa ra ngoài phân phối huấn luyện không?

## 2. Danh sách thí nghiệm

| Mã | Tên | Trả lời | Bộ dữ liệu | Phụ thuộc |
|---|---|---|---|---|
| E01 | Baseline tầm thường (độ dài + trùng lặp từ vựng) | CH3 | ViHallu | — |
| E02 | Tái lập Lookback Lens gốc (lookback gộp) | CH1 | ViHallu | — |
| E03 | Chunk-aware, chia theo câu | CH1 | ViHallu | E02 |
| E04 | Chunk-aware, chia theo cửa sổ token | CH1 | ViHallu | E02 |
| E05 | So sánh hai cách chia chunk, chọn cách tốt hơn | CH1 | ViHallu | E03, E04 |
| E06 | Định vị chú ý so với đoạn bằng chứng vàng | CH1 | ISE-DSC01 | E05 |
| E07 | Chunk-aware trên ngữ cảnh dài | CH1 | ISE-DSC01 | E05 |
| E08 | Thí nghiệm lớp ngoại lai (NEI có bằng chứng) | CH1 | ViWikiFC | E05 |
| E09 | Baseline bộ mã hóa (PhoBERT, XLM-R, InfoXLM) | CH2 | ViHallu | — |
| E10 | Baseline LLM giám khảo (Gemini free, mẫu nhỏ) | CH2 | ViHallu | — |
| E11 | Bảng đánh đổi độ chính xác và chi phí | CH2 | ViHallu | E05, E09, E10 |
| E12 | Ablation: nhóm đặc trưng nào đóng góp | CH3 | ViHallu | E05 |
| E13 | Ablation: mô hình đọc Qwen2.5-7B với Sailor2-8B | CH1, CH3 | ViHallu | E05 |
| E14 | Ablation: bậc thang kích thước 7B / 3B / 1.5B | CH2 | ViHallu | E05 |
| E15 | Đối chứng ngoài trên split gốc | CH2 | ViWikiFC | E05 |
| E16 | Chuyển giao ViHallu sang ISE-DSC01 và ngược lại | CH3 | cả hai | E05, E07 |
| E17 | Chuyển miền sang tin tức (chỉ nếu còn thời gian) | CH3 | ViFactCheck | E15 |

## 3. Chỉ số

**Chính:** macro-F1. **Phụ:** accuracy, F1 từng lớp, ECE (khi có xác suất).

**Vận hành, bắt buộc báo cáo với mọi phương pháp:**
- `ms_per_sample` — thời gian trung bình mỗi mẫu, đo bằng `time.perf_counter`, đã loại thời gian nạp mô hình
- `peak_vram_mb` — `torch.cuda.max_memory_allocated()` chia 1024²
- `n_params_trainable` — số tham số phải huấn luyện

**Quy tắc về độ bất định — sửa ở T17 ngày 27/08/2026.** Yêu cầu cũ là "độ lệch chuẩn qua 5 seed cho phần huấn luyện bộ phân loại". Đo thật thì yêu cầu đó **rỗng với mô hình tất định** và **bỏ sót nguồn biến thiên lớn nhất**:

| Nguồn biến thiên | Độ lệch chuẩn của macro-F1 |
|---|---|
| Đổi riêng `random_state` của logistic regression | **0,000000** |
| Lấy lại mẫu tập huấn luyện (bootstrap) | ±0,0036 |
| **Lấy lại mẫu tập test (bootstrap)** | **±0,0174** |

Lý do rất đơn giản: logistic regression giải bằng lbfgs trên bài toán lồi là tất định, đổi seed không làm gì cả. Còn tập test ViHallu chỉ có **700 mẫu**, nên bản thân việc mẫu nào rơi vào tập test đã làm macro-F1 xê dịch gấp gần năm lần biến thiên huấn luyện.

Quy tắc mới, áp cho mọi thí nghiệm từ đây:

1. **Con số bất định chính là khoảng tin cậy 95 % lấy từ 2.000 lần lấy lại mẫu tập test.** Đây là con số quyết định một phương pháp có thật sự hơn phương pháp khác hay không.
2. **Vẫn chạy 5 seed với những mô hình có yếu tố ngẫu nhiên** — E09 tinh chỉnh bộ mã hóa (khởi tạo trọng số, dropout, thứ tự dữ liệu), hay LightGBM (lấy mẫu con). Với chúng, biến thiên do seed là thật và phải báo cáo.
3. **Với mô hình tất định thì ghi thẳng là 0**, đừng bịa ra biến thiên. Logistic regression trên cùng một tập huấn luyện luôn cho đúng một kết quả.

Hệ quả thực dụng phải nhớ khi so bảng: **hai phương pháp lệch nhau dưới 0,03 macro-F1 trên tập test 700 mẫu là chưa phân định được**, khoảng tin cậy của chúng chồng lên nhau gần hết.

Phần trích đặc trưng chạy một lần vì tất định.

## 4. Chi tiết vài thí nghiệm quan trọng

### E01 — Baseline tầm thường

Đây là thí nghiệm **bắt buộc chạy sớm nhất**, vì nó định nghĩa sàn thật sự.

Đặc trưng chỉ gồm hai số: số từ của `response`, và tỷ lệ từ trong `response` cũng xuất hiện trong `context`. Bộ phân loại logistic. Trên ViHallu, nhóm đã đo trước hai chỉ số này biến thiên đơn điệu theo nhãn:

| Nhãn | Độ dài phản hồi | Tỷ lệ trùng lặp |
|---|---|---|
| no | 32,9 từ | 0,815 |
| intrinsic | 39,5 từ | 0,650 |
| extrinsic | 45,9 từ | 0,545 |

Nếu baseline này đạt macro-F1 cao, mọi phương pháp phức tạp hơn phải chứng minh vượt nó chứ không phải vượt PhoBERT 32,83%.

**Đã chạy ở T17 ngày 27/08/2026. Sàn cao hơn dự đoán: macro-F1 = 0,670.**

| Chỉ số | Giá trị | ± lệch chuẩn | Khoảng tin cậy 95 % |
|---|---|---|---|
| **macro-F1** | **0,6562** | 0,0177 | **[0,6200 – 0,6891]** |
| Accuracy | 0,6614 | 0,0178 | [0,6257 – 0,6957] |
| F1 `no` | 0,7418 | 0,0226 | [0,6930 – 0,7830] |
| F1 `intrinsic` | **0,5327** | 0,0293 | [0,4736 – 0,5852] |
| F1 `extrinsic` | 0,6942 | 0,0239 | [0,6462 – 0,7394] |
| ECE | 0,0613 | — | — |

Chạy lại ngày 27/08/2026 sau khi T18 sửa cách chia tập cho tái lập được trên mọi máy. Con số cũ trên tập chia trước là 0,6696; lệch 0,013, **nằm gọn trong khoảng nhiễu ±0,018** — đúng minh họa cho quy tắc ở mục 3.

Chín tham số phải huấn luyện, 0,001 ms mỗi mẫu, không cần GPU. Khoảng tin cậy lấy từ 2.000 lần lấy lại mẫu **tập test**, theo quy tắc ở mục 3.

Hai đặc trưng tái lập đúng bảng trên: độ dài trung bình ra **chính xác** 32,9 / 39,5 / 45,9 từ. Tỷ lệ trùng lặp ra 0,827 / 0,671 / 0,574, cao hơn số cũ khoảng 0,02 vì cách đếm ở đây bỏ dấu câu và không phân biệt hoa thường trước khi so; thứ tự và khoảng cách giữa ba nhãn giữ nguyên.

**Ba điều con số này quyết định:**

1. **Ngưỡng thật để vượt là 0,689, không phải 0,328 mà cũng không phải 0,656.** PhoBERT công bố 32,83 %, nhưng hai đặc trưng bề mặt đã đạt gấp đôi con số đó. Và vì khoảng tin cậy của E01 chạm tới **0,689**, một phương pháp muốn nói là hơn hẳn E01 thì phải vượt mốc đó chứ không phải vượt 0,656 — vượt 0,67 chỉ là nằm trong khoảng nhiễu của cùng một kết quả.
2. **`intrinsic` là lớp khó nhất, cách hai lớp kia hơn 0,2 điểm F1.** Điều đó hợp lý: ảo giác nội tại là xáo trộn thông tin đã có trong ngữ cảnh, nên nó *vẫn* trùng lặp từ vựng cao và không lộ ra ở hai đặc trưng bề mặt. Đây chính là chỗ tín hiệu chú ý theo đoạn có cơ hội đóng góp nhiều nhất, và nên là chỗ E05 tập trung chứng minh.
3. **Chi phí gần bằng không** — 9 tham số, 0,001 ms/mẫu, không GPU. Cột chi phí của E11 vì thế có một mốc dưới rất khắc nghiệt.

### E02 — Tái lập Lookback Lens gốc

Đây là mốc so sánh nội bộ quan trọng nhất: nếu chunk-aware không hơn E02 thì đóng góp của đề tài không đứng vững. Vì vậy E02 phải tái lập **đúng** công thức gốc, không phải một biến thể gần đúng.

Công thức nguyên bản, bốn điểm dễ làm sai và khác biệt về bài toán: xem mục 1 của `docs/REFERENCES.md`. Tóm tắt điểm dễ sai nhất — lookback ratio gốc là **trung bình chú ý theo token** (chia cho số token ngữ cảnh và số token đã sinh), không phải tổng khối lượng chú ý.

Chỉ khi E02 vượt được baseline tầm thường E01 mới chạy tiếp E03–E05. Không vượt thì dừng lại rà soát cách trích đặc trưng, vì lỗi gần như chắc chắn nằm ở khâu trích chứ không ở phương pháp.

### E05 — Chọn cách chia chunk

Chạy E03 và E04 với cùng mọi thứ khác. Với `token_window` quét `window_size` thuộc `{64, 128, 256}` và `stride` bằng nửa cửa sổ. Báo cáo bảng đầy đủ, chọn cấu hình tốt nhất trên tập dev, và **giữ nguyên cấu hình đó cho mọi thí nghiệm sau**.

Ghi rõ trong báo cáo rằng nhóm đã thử cả hai họ chiến lược trước khi chốt — đây là một kết quả, không phải bước phụ.

### E06 — Định vị chú ý

Thí nghiệm quan trọng nhất cho CH1. Chỉ chạy trên các mẫu ISE-DSC01 có bằng chứng, tức nhãn SUPPORTED và REFUTED.

Với mỗi mẫu: chia ngữ cảnh thành chunk, xác định chunk chứa bằng chứng vàng, tính phân bố chú ý trên các chunk, rồi đo:

- `hit@1` — chunk được chú ý nhiều nhất có phải chunk bằng chứng không
- `hit@3`
- `MRR` của chunk bằng chứng
- So với sàn ngẫu nhiên `1/n_chunks`

Với nhãn NEI (không có bằng chứng), đo entropy phân bố và kiểm định giả thuyết entropy cao hơn đáng kể so với hai nhãn kia.

### Phân tích theo loại prompt — áp dụng cho mọi thí nghiệm trên ViHallu

Ngoài số tổng, mọi thí nghiệm chạy trên ViHallu phải báo thêm macro-F1 **tách theo `meta.prompt_type`**, tối thiểu là hai nhóm `noisy` và phần còn lại.

Lý do: prompt `noisy` bị bỏ dấu tiếng Việt nên tokenize ra chuỗi token khác hẳn, làm thay đổi số token của câu hỏi và do đó thay đổi mẫu số của lookback ratio. Nếu không tách, không phân biệt được "mô hình phát hiện ảo giác" với "mô hình phát hiện prompt bị nhiễu". Đây cũng là một kết quả phụ có giá trị công bố: tín hiệu chú ý bền tới đâu khi đầu vào bị bỏ dấu — một dạng nhiễu rất đặc thù tiếng Việt.

### E11 — Bảng đánh đổi

Bảng trung tâm của chương 7. Mỗi dòng một phương pháp, cột gồm macro-F1, ms/mẫu, VRAM đỉnh, số tham số huấn luyện, và có cần API ngoài không.

**Chi phí của hướng nội tại đã đo xong ở T08**, dùng làm cột chi phí cho mọi dòng lookback và chunk-aware: trên Tesla T4 với Qwen2.5-7B-Instruct lượng tử hóa NF4, một mẫu tốn **khoảng 1,05 ms mỗi token prompt**, gần như tuyến tính từ 371 tới 2.492 token. Quy ra từng bộ: **420 ms/mẫu trên ViHallu**, 941 ms/mẫu trên ISE-DSC01, 404 ms/mẫu trên ViWikiFC. VRAM đỉnh 8.428 MB. Số tham số phải huấn luyện chỉ là của bộ phân loại tuyến tính đặt trên đặc trưng, mô hình đọc không được huấn luyện gì. Chi tiết và bảng theo mức độ dài nằm ở phần T08 của `TASKS.md`; bản ghi máy đọc được ở `results/feasibility.jsonl`.

Khi so với E10 (Gemini giám khảo) nhớ rằng hai cột chi phí không cùng đơn vị: hướng nội tại tốn GPU cục bộ, LLM giám khảo tốn lượt gọi API và độ trễ mạng. Bảng phải ghi rõ cả hai chứ không qua một con số ms/mẫu duy nhất.

### E13 — Qwen2.5 với Sailor2

Cùng code, chỉ đổi `model_name`. Ngoài so sánh macro-F1, đo thêm **vị trí các đầu chú ý có ích nhất** (theo trọng số của bộ phân loại tuyến tính) và kiểm tra chúng có nằm ở cùng lớp/đầu giữa hai mô hình không. Đây là câu hỏi khoa học mới: huấn luyện chuyên sâu tiếng Việt có dịch chuyển vị trí các đầu sao chép không.

## 5. Bảng kết quả cần điền

Điền vào đây khi có số. Ô trống nghĩa là chưa chạy.

### Bảng 1 — Kết quả chính trên ViHallu (tập test tự chia theo ngữ cảnh)

Cột macro-F1 ghi kèm **khoảng tin cậy 95 % của tập test**, không phải độ lệch chuẩn qua seed. Đo ở T17: với 700 mẫu test, khoảng này rộng gấp đôi biến thiên seed và **nó mới là thứ quyết định** một phương pháp có thật sự hơn phương pháp khác hay không. Trộn hai loại độ lệch vào một cột là cách chắc chắn nhất để đọc nhầm bảng.

| Phương pháp | macro-F1 [KTC 95 %] | Acc | F1 no | F1 intr | F1 extr | ECE | ms/mẫu | VRAM MB |
|---|---|---|---|---|---|---|---|---|
| Baseline tầm thường (E01) | **0,656** [0,620–0,689] | 0,661 | 0,742 | 0,533 | 0,694 | 0,061 | 0,001 | 0 |
| PhoBERT tinh chỉnh (E09) | **0,742** [0,705–0,770] | 0,740 | 0,790 | 0,685 | 0,750 | 0,086 | 12,2 | 9.002 |
| XLM-R large tinh chỉnh (E09) | **0,771** [0,747–0,808] | 0,770 | 0,836 | 0,722 | 0,754 | 0,114 | 24,8 | 11.231 |
| InfoXLM large tinh chỉnh (E09) | *không tinh chỉnh được* | | | | | | | 11.231 |
| Gemini free giám khảo (E10) | | | | | | | | |
| Lookback gộp (E02) | | | | | | | | |
| **Chunk-aware (E05)** | | | | | | | | |

Đo ngày 27/08/2026 trên T4, 3 seed mỗi mô hình, 3 epoch, learning rate 1e-5. Độ lệch chuẩn qua seed — 0,012 cho PhoBERT và 0,025 cho XLM-R — nằm trong `results/runs.jsonl` dưới khóa `_std`, tách khỏi sai số chuẩn bootstrap ở khóa `_se`.

Bốn điều bảng này nói:

1. **Mốc phải vượt nay là 0,771 chứ không phải 0,689.** Khoảng tin cậy tập test của XLM-R chạm tới 0,807. Đây là đối thủ thật sự của phương pháp chú ý nội tại.
2. **Lớp `intrinsic` vẫn khó nhất ở cả ba phương pháp**, nhưng bộ mã hóa cải thiện được nhiều: 0,533 → 0,722. Khoảng cách giữa lớp dễ nhất và khó nhất thu từ 0,209 xuống 0,114.
3. **Giá phải trả là chi phí suy luận.** XLM-R chậm hơn E01 khoảng **25.000 lần** mỗi mẫu và cần 11 GB VRAM, đổi lấy 0,115 macro-F1. Đây chính là trục đánh đổi mà E11 phải vẽ ra.

4. **Càng mạnh càng tự tin thái quá.** ECE đi ngược chiều macro-F1: 0,061 → 0,086 → 0,114. Bộ mã hóa tinh chỉnh đoán đúng hơn nhưng **hiệu chỉnh xác suất tệ hơn** hai đặc trưng bề mặt. Với bài toán phát hiện ảo giác, nơi người dùng cần biết *mức độ tin* chứ không chỉ nhãn, đây là một điểm yếu thật của mốc so sánh và đáng nêu ở phần bàn luận.

**InfoXLM-large không tinh chỉnh được** trên cấu hình này: cả ba seed đều đứng ở `ln(3) = 1,0986` hết epoch đầu và bị cơ chế dừng sớm loại. Cùng kích thước và cùng learning rate với XLM-R, vốn chạy tốt 3/3 seed — nên đây là bất ổn riêng của checkpoint đó, không phải của cấu hình. Ghi lại như một kết quả về **độ ổn định**, và chính nó là luận điểm cho CH2: phương pháp chú ý nội tại không tinh chỉnh gì nên không có rủi ro này.

### Bảng 2 — Định vị chú ý trên ISE-DSC01 (E06)

| Cấu hình | hit@1 | hit@3 | MRR | Sàn ngẫu nhiên |
|---|---|---|---|---|
| Chia theo câu | | | | |
| Cửa sổ 128 token | | | | |

### Bảng 3 — Chọn cách chia chunk (E05)

| Chiến lược | Tham số | macro-F1 dev |
|---|---|---|
| Câu | min_words=5 | |
| Cửa sổ | 64 / stride 32 | |
| Cửa sổ | 128 / stride 64 | |
| Cửa sổ | 256 / stride 128 | |

### Bảng 4 — Ablation nhóm đặc trưng (E12)

| Nhóm đặc trưng | macro-F1 | Chênh lệch |
|---|---|---|
| Chỉ bề mặt | | — |
| + lookback gộp | | |
| + chunk-aware | | |
| + ổn định | | |

### Bảng 5 — Mô hình đọc (E13, E14)

| Mô hình đọc | macro-F1 | ms/mẫu | VRAM MB |
|---|---|---|---|
| Qwen2.5-7B-Instruct | | | |
| Qwen2.5-3B-Instruct | | | |
| Qwen2.5-1.5B-Instruct | | | |
| Sailor2-8B-SFT | | | |

### Bảng 6 — Đối chứng ngoài trên ViWikiFC (E15)

| Phương pháp | Nguồn | Strict Acc | VC Acc | ER Acc | macro-F1 |
|---|---|---|---|---|---|
| InfoXLM large | Bài gốc ViWikiFC | — | — | — | 86,51 |
| BM25 + InfoXLM large | Bài gốc ViWikiFC | 67,00 | — | — | — |
| SemViQA | Bài SemViQA | 80,82 | 83,88 | 95,31 | — |
| **Phương pháp của nhóm** | | | | | |

### Bảng 7 — Khái quát hóa chéo bộ (E16)

| Huấn luyện trên | Đánh giá trên | macro-F1 | Sụt so với cùng bộ |
|---|---|---|---|
| ViHallu | ViHallu | | — |
| ViHallu | ISE-DSC01 | | |
| ISE-DSC01 | ISE-DSC01 | | — |
| ISE-DSC01 | ViHallu | | |

## 6. Các mốc so sánh đã công bố

Ghi lại để không phải tra lại:

- **ViHallu private test:** hệ thống tốt nhất 84,80 % macro-F1; baseline PhoBERT 32,83 %. Lưu ý nhóm không chấm được trên tập này vì không có nhãn — chỉ dùng để định vị, không đặt cạnh số của nhóm trong cùng một cột.
- **ViWikiFC test:** InfoXLM large 86,51 % macro-F1 (verdict prediction); pipeline BM25 + InfoXLM large 67,00 % strict accuracy; SemViQA 80,82 % strict accuracy và 95,31 % evidence retrieval accuracy; BM25 truy xuất top-1 đạt 88,30 % SUPPORTS / 86,93 % REFUTES / 56,67 % NEI.
- **ISE-DSC01 private test:** SemViQA 78,97 % strict accuracy, 82,54 % VC accuracy, 80,91 % ER accuracy. Lưu ý tập train nhóm dùng có 36.369 mẫu còn bài SemViQA ghi 37.967 — xem cảnh báo ở mục 4 của `docs/DATA.md`, **không so trực tiếp nếu không kèm ghi chú**.
- **SemViQA là công trình của chính Trường ĐH Công nghiệp TP.HCM.** Mã nguồn, thư viện PyPI và checkpoint đều công khai, nên nếu cần làm rõ cách tính strict accuracy hay cách chia tập thì hỏi được trực tiếp qua GVHD thay vì suy đoán từ bài báo. Đây là cơ sở so sánh gần nhất về mặt tổ chức mà nhóm có.
- **ViFactCheck test:** Gemma 89,90 % macro-F1 với gold evidence, 85,94 % với full context; XLM-R large 88,02 % / 75,42 %; con người 84,93 %.

## 7. Nguyên tắc báo cáo

- Không so số của nhóm với con số leaderboard của bộ mà nhóm tự chia tập. Đặt ở hai bảng khác nhau, giải thích rõ.
- Mọi bảng phải ghi rõ tập nào, chia thế nào, seed bao nhiêu.
- Kết quả âm tính vẫn báo cáo. Nếu chunk-aware không hơn lookback gộp, đó là một kết quả có giá trị và phải phân tích tại sao.
