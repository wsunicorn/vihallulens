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

**Thêm ở T19 — chỉ số nhị phân, gộp `intrinsic` và `extrinsic` làm một.** Báo cạnh chỉ số ba lớp, không bao giờ thay nó. Lý do là macro-F1 ba lớp đang **trộn hai câu hỏi** vào một con số:

- *Có phát hiện được ảo giác không?* — chấm trên ranh giới mà không ai tranh cãi.
- *Có gọi đúng tên loại ảo giác không?* — chấm trên ranh giới mà **chính con người cũng không thống nhất**: kappa 0,505 giữa hai người gán nhãn ở T13, và 8/100 mẫu một người gán `noi_tai` còn người kia gán `ngoai_lai`.

Một phương pháp mạnh ở câu đầu mà yếu ở câu sau sẽ ra cùng một điểm ba lớp với một phương pháp yếu ở cả hai. Chỉ số nhị phân tách chúng ra.

Đo được ngay ở T19 và nó đổi hẳn cách đọc E10: trên cùng 300 mẫu, Gemini **kém** E01 ở ba lớp (0,664 so với 0,686) nhưng **hơn** ở nhị phân (0,821 so với 0,814), và bắt được **97,4 %** số mẫu có ảo giác so với 88,9 % của E01. Nó là một bộ phát hiện tốt và một bộ phân loại kém, mà con số ba lớp che mất điều đó.

Bốn khóa: `binary_macro_f1`, `binary_accuracy`, `binary_precision`, `binary_recall`. Precision và recall là của lớp `hallucinated`, vì đó là thứ một hệ thống triển khai thật bị chấm: recall nói bắt được bao nhiêu, precision nói bao nhiêu phần báo động là thật.

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

### E10 — Baseline LLM giám khảo

Mốc so sánh thứ ba, và là mốc mà lập luận chi phí ở CH2 thật sự nhắm vào. E01 không đọc gì, E09 đọc được nhưng phải tinh chỉnh trước, còn E10 đọc được mà **không huấn luyện gì cả** — đổi lại là một lượt gọi API và một vòng mạng cho mỗi mẫu.

**Bộ tiêu chí chấm chép nguyên từ `results/nei_mapping_audit_HUONGDAN.md`** — bản hướng dẫn hai sinh viên đã gán nhãn tay ở T13 — chứ không viết lại. Đưa cho giám khảo một định nghĩa ba lớp khác với định nghĩa con người đã dùng thì Bảng 1 thành ra so **đề bài**, và người phản biện có quyền nói vậy.

Hai chỗ cố ý khác bản hướng dẫn, ghi lại vì chúng ảnh hưởng cách đọc điểm:

1. Con người được trả lời `khong_chac`. Giám khảo thì không: một mốc so sánh phải ra nhãn cho mọi mẫu, nếu không macro-F1 của nó tính trên một tập khác với mọi dòng còn lại.
2. Giám khảo phải **nêu lý do trước rồi mới chốt nhãn**. `propertyOrdering` trong schema ép thứ tự đó, nên mô hình lần theo bằng chứng trước khi quyết, thay vì biện minh cho một nhãn đã trót đưa ra.

#### Cỡ mẫu, và vì sao chỉ 300

Mục 2 `CLAUDE.md` chỉ cho dùng free tier ở quy mô rất nhỏ. Tập con **300 trên 700 mẫu test** được chọn **tất định bằng SHA-256** đúng như cách chia tập, để cache không trượt và con số không nhúc nhích giữa hai lần chạy.

Hệ quả phải nói rõ khi đọc Bảng 1: **dòng E10 đo trên tập con, các dòng khác đo trên cả 700 mẫu.** Không so thẳng bằng mắt được. Vì vậy script tính thêm **macro-F1 của E01 trên đúng 300 mẫu đó** làm neo — E01 chỉ là hai đặc trưng và một hồi quy logistic nên tính lại tốn một giây, và nó biến con số của giám khảo thành thứ người đọc đặt được vào đâu đó.

#### Chọn mô hình bằng đo, không bằng danh tiếng

Đo ở T19, và cả ba điều đều làm đổi thiết kế:

| Điều đo được | Hệ quả |
|---|---|
| `gemini-2.5-flash` **đã bị gỡ** — API trả 404 kèm câu "no longer available to new users" | Tên mô hình là thứ phải kiểm trước mỗi lượt chạy. Thêm `scripts/list_judge_models.py` để hỏi thẳng API |
| `gemini-3.6-flash` chỉ cho **20 lượt mỗi ngày** (`GenerateRequestsPerDayPerProjectPerModel-FreeTier=20`) | 300 mẫu sẽ mất 15 ngày. Không dùng |
| `gemini-3.5-flash-lite` trả lời tiếng Việt **mất hết dấu** | Không dùng |

Chốt **`gemini-3.1-flash-lite`**: giữ nguyên dấu, cùng độ chính xác với flash-lite trên mẫu thử, khoảng 5 giây một lượt. Tên được **ghim cứng**, không dùng bí danh `-latest` — bí danh sẽ lặng lẽ thành mô hình khác giữa lượt chạy sinh ra Bảng 1 và lượt chạy kiểm lại nó.

Đây không phải một sự nhân nhượng. Trần thật của free tier chính là thứ bảng đánh đổi ở E11 sinh ra để nói, nên chạy đúng mô hình mà free tier cho phép mới là phép đo trung thực.

#### Hai loại hạn mức, hai cách xử lý ngược nhau

Cùng mang mã 429 nhưng đòi hai phản ứng trái ngược:

- **Hạn mức phút** — chờ rồi gọi lại. Nó tự hết.
- **Hạn mức ngày** — dừng hẳn. Chờ không giúp được gì, và một script cứ thử lại sẽ biến một câu "mai chạy tiếp" gọn gàng thành một tiếng im lặng.

Cache là thứ khiến việc dừng trở nên rẻ: mỗi câu trả lời được ghi xuống **ngay khi nhận được**, nên một lượt chạy bị hạn mức, bị rớt mạng hay bị Ctrl-C vẫn giữ nguyên mọi thứ đã trả tiền. Khóa cache gồm cả tên mô hình lẫn nguyên văn prompt: sửa tiêu chí thì câu trả lời cũ không khớp nữa, đúng như phải thế — chúng trả lời một câu hỏi khác.

#### Độ tin cậy tự khai — để riêng, không trộn vào cột ECE

Giám khảo tự khai một con số tin cậy, và nó được ghi lại. Nhưng nó **không** vào cột ECE của Bảng 1: ECE của E01 và E09 tính từ xác suất softmax, còn đây là con số mô hình tự nói về mình. Hai đại lượng khác nhau đặt chung một cột là đúng cái lỗi T18 đã phải sửa hai lần. Nó nằm ở khóa `ece_self_reported` trong `results/runs.jsonl`.

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

| Phương pháp | macro-F1 [KTC 95 %] | Nhị phân | Bắt được | Báo đúng | F1 no | F1 intr | F1 extr | ECE | ms/mẫu | VRAM MB |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline tầm thường (E01) | **0,656** [0,620–0,689] | 0,802 | 0,854 | 0,870 | 0,742 | 0,533 | 0,694 | 0,061 | 0,001 | 0 |
| PhoBERT tinh chỉnh (E09) | **0,749** [0,714–0,778] | 0,851 | 0,921 | 0,883 | 0,800 | 0,693 | 0,754 | 0,081 | 12,3 | 9.002 |
| XLM-R large tinh chỉnh (E09) § | **0,776** [0,757–0,818] | **0,881** | 0,920 | **0,918** | **0,844** | 0,729 | 0,756 | 0,097 | 25,2 | 11.231 |
| InfoXLM large tinh chỉnh (E09) | *không tinh chỉnh được* | | | | | | | | | 11.231 |
| Gemini free giám khảo (E10) † | **0,664** [0,607–0,719] | 0,821 | **0,974** | 0,818 | 0,753 | 0,582 | 0,656 | — | 8.194 | 0 |
| **Lookback gộp (E02)** ¶ | **0,745** [0,711–0,776] | 0,843 | 0,896 | 0,890 | 0,793 | **0,731** | 0,712 | 0,109 | 464 | 8.428 |
| **Chunk-aware câu (E03)** ¶ | 0,757 [0,724–0,789] | 0,864 | 0,894 | 0,915 | 0,823 | 0,686 | **0,762** | **0,044** | 528 | 8.428 |
| **Chunk-aware (E05)** | | | | | | | | | | |

Đo ngày 28/08/2026 trên T4, 3 seed mỗi mô hình, 3 epoch, learning rate 1e-5. Độ lệch chuẩn qua seed — 0,011 cho PhoBERT và 0,017 cho XLM-R — nằm trong `results/runs.jsonl` dưới khóa `_std`, tách khỏi sai số chuẩn bootstrap ở khóa `_se`. Dòng E10 đo ngày 27/08.

**¶** Cột `ms/mẫu` của E02 là **thời gian chạy mô hình đọc để lấy ma trận chú ý**, không phải thời gian của bộ phân loại — bộ phân loại chỉ có 2.271 tham số và chạy trong micro giây. VRAM lấy từ phép đo T08 trên đúng cấu hình này. Con số 464 ms là chi phí **tuyệt đối**; lập luận của đề tài là chi phí **biên** trong một hệ RAG thật gần bằng 0 vì lượt đọc đó dù sao cũng phải chạy — nhưng thí nghiệm này **không đo** điều đó, nên phải nói rõ khi trình bày.

**§** XLM-R chỉ **2 trên 3 seed học được** ở lượt chạy này; seed 42 đứng ở `ln(3)` và bị loại. Chính seed đó **học được** ở lượt 27/08 với cùng cấu hình — xem phần T18 của `TASKS.md`. Gộp cả hai lượt thì 5 trên 6 lượt seed thành công, trung bình **0,7730 ± 0,0199**, và đó là ước lượng đáng tin hơn bất kỳ lượt đơn lẻ nào. Bảng này dùng lượt 28/08 cho mọi cột vì chỉ lượt đó có dự đoán thô để tính chỉ số nhị phân.

**†** Dòng E10 đo trên **300 trên 700 mẫu test**, các dòng khác đo trên cả 700 — không so thẳng bằng mắt được. Trên đúng 300 mẫu đó, baseline tầm thường E01 đạt **0,686**. Cột ECE để trống vì con số duy nhất có được là độ tin cậy mô hình **tự khai**, không phải xác suất softmax; nó nằm ở khóa `ece_self_reported` trong `results/runs.jsonl` và bằng 0,280. Cột ms/mẫu đã gồm cả thời gian **tự giữ nhịp** để không vượt hạn mức; riêng độ trễ gọi API là khoảng 5.000 ms.

Năm điều bảng này nói:

1. **Giám khảo LLM là bộ phát hiện tốt và bộ phân loại kém, và con số ba lớp che mất điều đó.** Trên cùng 300 mẫu: ba lớp 0,664 so với 0,686 của E01 — thua; nhị phân 0,821 so với 0,814 — hơn; và **bắt được 97,4 % số mẫu có ảo giác so với 88,9 %**. Nghĩa là nó gần như không bỏ sót ảo giác nào, chỉ gọi sai tên loại. Đây là lý do chỉ số nhị phân được thêm vào mục 3: nếu chỉ nhìn con số ba lớp thì kết luận sẽ là "Gemini không hơn hai đặc trưng bề mặt", mà kết luận đó bỏ sót phần quan trọng nhất.

2. **Mốc phải vượt nay là 0,776 chứ không phải 0,689.** Và muốn nói *hơn hẳn* XLM-R thì phải vượt **0,818**, cận trên khoảng tin cậy của nó — cùng nguyên tắc đã dùng để đặt mốc 0,689 cho E01.
3. **Lớp `intrinsic` vẫn khó nhất ở cả bốn phương pháp**, nhưng bộ mã hóa cải thiện được nhiều: 0,533 → 0,729. Khoảng cách giữa lớp dễ nhất và khó nhất thu từ 0,209 xuống 0,115.
4. **Giá phải trả là chi phí suy luận.** XLM-R chậm hơn E01 khoảng **25.000 lần** mỗi mẫu và cần 11 GB VRAM, đổi lấy 0,120 macro-F1. Đây chính là trục đánh đổi mà E11 phải vẽ ra.

5. **Càng mạnh càng tự tin thái quá.** ECE đi ngược chiều macro-F1: 0,061 → 0,081 → 0,097. Bộ mã hóa tinh chỉnh đoán đúng hơn nhưng **hiệu chỉnh xác suất tệ hơn** hai đặc trưng bề mặt. Với bài toán phát hiện ảo giác, nơi người dùng cần biết *mức độ tin* chứ không chỉ nhãn, đây là một điểm yếu thật của mốc so sánh và đáng nêu ở phần bàn luận.

### E02 tái lập được, và nó nói đúng điều đề tài cần nghe

Chạy ngày 28/08/2026: 43,3 phút trích đặc trưng tập train, 5,4 phút tập test, **0 lỗi trên 6.300 mẫu**. Ba phép tự kiểm đều sạch: 100 % giá trị hữu hạn, 100 % nằm trong đoạn `[0, 1]` đúng như định nghĩa đòi hỏi, 0 trên 756 đặc trưng bị hằng số. Không mẫu nào bị cắt ngữ cảnh, không lớp nào tràn số.

| Phương pháp | ba lớp | F1 `intrinsic` | Tham số phải huấn luyện |
|---|---|---|---|
| E01 bề mặt | 0,656 | 0,533 | 9 |
| Gemini free | 0,664 | 0,582 | 0 |
| **E02 Lookback gộp** | **0,746** | **0,731** | **2.271** |
| PhoBERT-large | 0,749 | 0,693 | 369.166.339 |
| XLM-R-large | 0,776 | 0,729 | 559.893.507 |

Ba điều, và điều thứ hai là quan trọng nhất từ đầu đề tài tới giờ:

1. **Một bộ phân loại tuyến tính trên 756 con số chú ý ngang với một bộ mã hóa 369 triệu tham số đã tinh chỉnh.** 0,746 so với 0,749 của PhoBERT — lệch 0,002, nằm sâu trong nhiễu. Đây chính là phát hiện chủ đạo của bài Lookback Lens, **tái lập được trên tiếng Việt**: tín hiệu chú ý mang gần như toàn bộ thông tin mà việc tinh chỉnh cả mô hình moi ra được. Với **162.557 lần ít tham số hơn**.

2. **Trên lớp `intrinsic` — lớp khó nhất — E02 vượt PhoBERT và ngang XLM-R.** 0,731 so với 0,693 và 0,729. Nghĩa là tín hiệu chú ý mạnh **đúng ở chỗ mọi phương pháp dựa trên văn bản đều yếu**. Đây là bằng chứng trực tiếp cho cơ chế mà đề tài dựa vào: ảo giác nội tại là mô hình *có đọc* ngữ cảnh rồi nói sai, còn ngoại lai là *không đọc* mà tự bịa — hai dấu vết chú ý khác nhau, trong khi phần văn bản đọc được thì giống nhau.

   Đáng chú ý hơn: E02 thắng ở `intrinsic` (+0,038 so với PhoBERT) nhưng **thua ở `extrinsic`** (0,714 so với 0,754). Hai hướng bù trừ nhau ra tổng gần bằng. Nếu chỉ nhìn macro-F1 thì kết luận là "ngang nhau"; nhìn từng lớp mới thấy **chúng mạnh yếu ở hai chỗ khác nhau**, và đó là chỗ đề tài đứng.

3. **Tín hiệu dồn vào một số ít đầu, đúng như bài gốc.** Hai đầu dẫn đầu cách hẳn phần còn lại: `l5_h7` trọng số 0,970 và `l17_h4` 0,898, so với 0,54 của đầu thứ mười. Các đầu có ích trải khắp độ sâu — lớp 0, 1, 2, 5, 9, 17, 20, 24 — chứ không dồn về cuối. Đây là số liệu vào thẳng E13, thí nghiệm hỏi liệu các đầu đó có nằm ở cùng vị trí trong một mô hình đọc khác không.

**Điều E02 KHÔNG chứng minh, phải nói rõ.** Nó chưa vượt XLM-R: 0,746 so với 0,776, và hai khoảng tin cậy chồng nhau nhiều ([0,713–0,777] và [0,757–0,818]) nên cũng chưa kết luận được XLM-R hơn hẳn. Và chi phí tuyệt đối cao hơn — 464 ms mỗi mẫu so với 25 ms. Lập luận chi phí của đề tài dựa trên chi phí **biên** trong hệ RAG thật, thứ thí nghiệm này không đo.

**Và đây mới là mốc thật của phần đóng góp.** `chunk-aware` phải vượt **0,746**, không phải vượt 0,656 của E01 — vì nó là cùng một họ phương pháp, chỉ khác cách chia mẫu số. Vượt E01 thì chỉ chứng minh chú ý có ích; vượt E02 mới chứng minh **chia theo đoạn** có ích.

### E03 vượt E02 ở tổng, nhưng câu chuyện nằm ở từng lớp

Chạy ngày 29/08/2026. E02 được chạy lại trên **chính lượt trích của E03** để hai bên khác nhau đúng một biến; nó cho 0,7451 so với 0,7465 của lượt T20, lệch 0,0014 nên hai lượt trích nhất quán.

| | ba lớp | nhị phân | `no` | `intrinsic` | `extrinsic` | ECE |
|---|---|---|---|---|---|---|
| E02 lượng | 0,7451 | 0,8426 | 0,7925 | **0,7308** | 0,7121 | 0,1090 |
| E03 lượng + hình dạng | **0,7567** | **0,8636** | **0,8228** | 0,6858 | **0,7615** | **0,0441** |
| chênh | **+0,0116** | +0,0210 | +0,0303 | **−0,0450** | **+0,0494** | −0,0649 |

**Chunk-aware thắng ở `extrinsic` đúng chừng nào thì thua ở `intrinsic` chừng ấy.** Hai chiều gần như triệt tiêu, còn lại +0,012 ở tổng — mà khoảng tin cậy [0,724–0,789] chồng gần hết lên [0,711–0,776] của E02. **Vượt điểm, chưa hơn hẳn.**

Đây là **một nửa giả thuyết được xác nhận, một nửa bị bác**. Giả thuyết nói phân bố chú ý tách được hai loại: nội tại thì nhọn vì mô hình *có đọc*, ngoại lai thì tản vì *không đọc*. Nửa "ngoại lai thì tản" đúng rõ ràng. Nửa "nội tại thì nhọn" thì không thêm được gì — vì tỷ lệ gộp **đã** nắm phần đó rồi: 0,7308 của E02 là con số cao nhất cả bảng trên lớp này.

### Hai phép đối chứng, cả hai đều bác giả thuyết của chính tôi

**Hình dạng một mình chỉ đạt 0,6054** — thua cả 0,6562 của hai đặc trưng bề mặt E01. Năm đặc trưng chunk **không phải bộ phát hiện độc lập**; chúng là tín hiệu bổ sung, chỉ có giá trị khi đứng cạnh tỷ lệ gộp. Trên lớp `intrinsic` chúng đạt 0,5055, gần sàn.

**Cách chọn đầu chú ý không phải thủ phạm.** Nghi ngờ đầu tiên là `topk_heads k=32` chỉ giữ 32 trong 756 cột lookback, nên phần tụt ở `intrinsic` có thể do mất cột chứ không do đặc trưng chunk. Đã kiểm hai cách:

- Chạy E02 qua **cùng quy trình chọn**: dev chọn `all` với đủ 756 cột. Nghĩa là 32 đầu không phải handicap áp đặt, mà là thứ dev chọn cho riêng bộ đặc trưng rộng.
- Thêm hẳn một ứng viên `mixed_all_basic_topk_rest` — giữ **nguyên vẹn** khối lookback, chỉ tỉa các khối rộng — rồi chấm lại trên dev. Bốn biến thể của nó đều **thua**: tốt nhất 0,7645 so với 0,7768 của `topk k=32`.

Không gian tìm kiếm vì thế đã chứa E02 như một trường hợp riêng, và dev vẫn không chọn nó. **Chênh lệch từng lớp là thật.**

### Ba điều E03 làm được, ghi rõ để khỏi bị con số tổng che

1. **Hiệu chỉnh xác suất tốt nhất cả bảng.** ECE 0,044 so với 0,109 của E02 và 0,097 của XLM-R — giảm hơn một nửa. Với bài toán mà người dùng cần biết *mức độ tin* chứ không chỉ nhãn, đây là kết quả đứng riêng được, và nó đi ngược xu hướng "càng mạnh càng tự tin thái quá" của ba mốc kia.
2. **Chỉ số nhị phân 0,8636**, cao thứ hai cả bảng sau XLM-R, với `báo đúng` 0,915 — cao nhất.
3. **Năm đặc trưng mới chiếm 87 % trọng số** (`chunk_entropy` 26,8 %, `chunk_max_share` 22,6 %, `top1_top2_gap` 15,5 %, `chunk_gini` 15,0 %, `chunk_drift` 7,2 %) so với 12,9 % của `lookback_total`. Bộ phân loại không dùng lại E02 rồi ăn may — nó thật sự dựa vào hình dạng.

### Còn phải làm gì trước khi kết luận về đóng góp

E03 mới là **một** cách chia đoạn. T23 quét cách chia theo cửa sổ token 64/128/256, T24 chốt. Chia theo câu cho trung bình 5,3 đoạn mỗi ngữ cảnh, có thể là quá thô để hình dạng phân bố nói lên điều gì trên lớp `intrinsic`.

Và E06 — định vị chú ý so với đoạn bằng chứng vàng trên ISE-DSC01 — mới là phép kiểm **trực tiếp** của cơ chế, thay vì suy ra từ điểm phân loại.

### Cột nhị phân nói gì

Cả bốn phương pháp đều **được thêm 0,10 tới 0,16 điểm** khi bỏ đòi hỏi gọi đúng tên loại ảo giác. Đó là bằng chứng số học cho điều mục 3 nêu: phần khó nằm ở **ranh giới nội tại–ngoại lai**, không nằm ở việc phát hiện.

| Phương pháp | ba lớp | nhị phân | chênh | bắt được | báo đúng |
|---|---|---|---|---|---|
| E01 bề mặt | 0,656 | 0,802 | **+0,146** | 0,854 | 0,870 |
| Gemini free | 0,664 | 0,821 | **+0,157** | **0,974** | 0,818 |
| PhoBERT | 0,749 | 0,851 | +0,102 | 0,921 | 0,883 |
| XLM-R | 0,776 | **0,881** | +0,105 | 0,920 | **0,918** |

Ba điều đọc thêm được:

1. **Chênh lệch LỚN HƠN ở hai phương pháp yếu** (+0,146 và +0,157) so với hai bộ mã hóa (+0,102 và +0,105). Nghĩa là bộ mã hóa không chỉ tốt hơn nói chung, mà tốt hơn **đúng ở phần khó** — chúng thu hẹp được ranh giới chứ không chỉ đẩy điểm chung lên.

2. **Gemini bắt được nhiều nhất nhưng báo động sai nhiều nhất.** Recall 0,974 là cao nhất bảng, precision 0,818 là thấp nhất trong ba phương pháp mạnh. Nó gần như không bỏ sót ảo giác nào, đổi lại gọi nhầm 18 % câu trả lời trung thực thành có ảo giác — khớp với ma trận nhầm lẫn, nơi 32 trên 111 mẫu `no` bị gán thành `extrinsic`.

3. **XLM-R cân bằng nhất:** recall 0,920 và precision 0,918 gần bằng nhau. Với một hệ thống triển khai thật, đây là hồ sơ dễ đặt ngưỡng nhất — nhưng nó đòi GPU và tinh chỉnh không ổn định, còn Gemini thì đòi hạn mức API.

**InfoXLM-large không tinh chỉnh được** trên cấu hình này. Cả ba seed đứng ở `ln(3) = 1,0986` hết epoch đầu, và hai mức learning rate thấp hơn (`5e-6`, `2e-6`) cũng vậy — loss thậm chí **bám sát `ln(3)` hơn** khi hạ learning rate, tức mô hình không nhúc nhích chứ không phải bị đẩy quá đà.

Đã loại trừ bốn nguyên nhân cơ học bằng CPU, không tốn quota GPU: trọng số thân nạp đủ; cấu hình giống hệt XLM-R; đỉnh activation chỉ bằng 0,04 % trần float16; vector CLS phân biệt các mẫu **tốt hơn** XLM-R. Công cụ kiểm nằm ở `scripts/check_checkpoint.py`, dùng lại được cho E13 và cho các nấc lùi mô hình.

Ghi lại như một kết quả về **độ ổn định**, không phải một ô trống. Chính nó là luận điểm cho CH2: hướng bộ mã hóa đòi dò tham số riêng cho từng checkpoint, còn phương pháp chú ý nội tại không tinh chỉnh gì nên không có rủi ro này.

### Bảng 2 — Định vị chú ý trên ISE-DSC01 (E06)

Chạy 31/08/2026 trên toàn bộ tập dev, 3.646 mẫu, 65,1 phút GPU, **0 lỗi**. Chia theo câu, cấu
hình chốt ở T24. 2.376 mẫu có bằng chứng định vị được, trung bình **22,6 đoạn** mỗi ngữ cảnh.

| Chỉ số | Đầu mạnh nhất | Trung bình 756 đầu | Sàn ngẫu nhiên | Gấp sàn (đầu / trung bình) |
|---|---|---|---|---|
| **hit@1** | **0,8779** (lớp 14, đầu 6) | 0,3320 | 0,0614 | **14,29×** / 5,40× |
| hit@3 | 0,9562 (lớp 16, đầu 7) | 0,5177 | 0,1843 | 5,19× / 2,81× |
| MRR | 0,9200 (lớp 16, đầu 7) | 0,4709 | 0,1987 | 4,63× / 2,37× |

**Đầu mạnh nhất chỉ đúng đoạn chứa bằng chứng trong 87,8 % số mẫu, chọn giữa trung bình 22,6
đoạn.** Đây là phép kiểm trực tiếp của cơ chế, không suy ra từ điểm phân loại nào.

### Đầu mạnh nhất chọn trên chính dữ liệu báo cáo — và điều đó không giải thích được kết quả

Con số 0,8779 là cận trên: nó là max trên 756 ô, chọn trên đúng tập được báo cáo. Câu hỏi đúng
là phần nào của nó do may mắn khi chọn.

Không phần nào đáng kể. Nếu **mọi** đầu đều mạnh ngang mức trung bình 0,3320, sai số chuẩn trên
2.376 mẫu là 0,0097, nên max trên 756 lần rút chỉ kỳ vọng khoảng **0,363**. Quan sát được
**0,878**.

Và nó không phải một đầu ăn may:

```
  đầu tốt nhất        0,878          10 đầu đầu bảng   0,878 … 0,863
  trung vị 756 đầu    0,178 (2,9x)   192/756 đầu vượt 10x sàn
  trung bình          0,332 (5,4x)   453/756 đầu vượt  2x sàn
  đầu kém nhất        0,048          5 lớp mạnh nhất: 14, 16, 15, 19, 8
```

**Trung bình mọi đầu đã là 5,40× sàn**, và con số ấy **không dính lựa chọn nào**. Nếu chỉ được
báo cáo một số thì nên là số này.

Khác Lookback Lens ở một điểm đáng nói: bài gốc thấy tín hiệu tập trung ở vài đầu. Ở đây **một
phần tư số đầu vượt 10 lần sàn**, và các lớp mạnh nhất quây quanh giữa mạng (14, 15, 16, 19).
Định vị bằng chứng là thuộc tính rộng của Qwen2.5-7B chứ không phải một mạch chuyên biệt.

### Nhãn không có bằng chứng thì chú ý tản hơn

| | Trung vị entropy | Số mẫu |
|---|---|---|
| Không bằng chứng (NEI) | 0,7975 | 1.269 |
| Có bằng chứng (SUPPORTED + REFUTED) | 0,7676 | 2.376 |

P(mẫu NEI tản hơn mẫu có bằng chứng) = **0,7213**, cỡ ảnh hưởng rank-biserial **+0,4426** — mức
**lớn**. Mann-Whitney U cho z = 22,05, p = 1,04 × 10⁻¹⁰⁷.

**Đọc p ở đây gần như vô nghĩa** và bảng ghi nó chỉ cho đủ. Với 1.269 và 2.376 mẫu, một khác biệt
nhỏ tới mức không đáng kể vẫn ra p dưới 0,001. Con số phải đọc là cỡ ảnh hưởng.

Nhưng cũng phải nói cho cân: **chênh lệch tuyệt đối chỉ 0,03 trên thang 0–1**. Hiệu ứng lớn nằm ở
**tính nhất quán của thứ tự** — bốc một mẫu mỗi bên thì bảy trên mười lần NEI tản hơn — chứ không
ở độ lớn. Entropy vì thế là tín hiệu thật nhưng yếu khi dùng một mình, đúng như E03 đã cho thấy
khi đặc trưng hình dạng đứng riêng chỉ đạt 0,6054.

### Ba điều phụ, ghi vì chúng sửa lại hiểu biết trước đó

**Nhánh cắt ngắn cuối cùng cũng chạy: 6/3.646 mẫu.** Sau bảy lượt trích trước đó không mẫu nào
chạm trần 4.096 token. Và nó làm đúng việc: 1 mẫu mất đoạn bằng chứng vì đoạn ấy bị cắt, được
loại khỏi phần định vị thay vì âm thầm chấm nhầm đoạn khác. Đây là lần đầu cơ chế bảo vệ ấy được
thử trên dữ liệu thật.

**Kết quả tái lập chính xác giữa hai môi trường.** Chấm lại trên máy cá nhân từ shard tải về cho
**trùng từng chữ số** — khác hẳn độ trôi tới 0,0075 đo ở T23. Lý do là E06 chỉ có số học thuần
(xếp hạng, đếm, trung bình), không có bộ tối ưu lặp nào như `LogisticRegression` để hội tụ khác
nhau theo phiên bản BLAS.

**Chi phí 1.071 ms/mẫu**, gấp đôi ViHallu (528 ms) đúng theo tỷ lệ độ dài ngữ cảnh 794 so với
243 token — khớp mô hình chi phí tuyến tính theo token đo ở T08.

### Vì sao Bảng 2 chỉ có một cách chia

Kế hoạch ban đầu có thêm dòng "cửa sổ 128 token", viết **trước** khi T24 chốt cách chia. Chia
theo câu nay là cấu hình chốt cho mọi thí nghiệm còn lại, nên 70 phút GPU cho một cách chia đã bị
loại là tiêu hạn mức để điền một ô không ai dùng. Câu hỏi so sánh cách chia đã được Bảng 3 trả
lời, trên bộ dữ liệu và bằng phép đối chứng thiết kế riêng cho nó.

### Bảng 3 — Chọn cách chia chunk (E05)

**Kết luận: chọn chia theo câu, `min_words=5`.** Giữ nguyên cấu hình này cho mọi thí nghiệm
còn lại. Lý do ở ngay dưới bảng.

Cả năm dòng chấm **trên cùng một máy**, từ chính các shard mà GPU sinh ra. Lý do bắt buộc phải
làm vậy nằm ở mục "Số dev không tái lập giữa hai môi trường".

| Chiến lược | Tham số | Chồng lấn | TB đoạn | Cách gộp dev chọn | macro-F1 dev | Nhị phân | `no` | `intrinsic` | `extrinsic` |
|---|---|---|---|---|---|---|---|---|---|
| **Câu** ← chọn | min_words=5 | không | 5,29 | `topk k=32`, 192 | **0,7768** | **0,8943** | **0,8596** | 0,7202 | **0,7505** |
| Cửa sổ | 128 / stride 64 | có | 3,29 | `topk k=32`, 192 | 0,7683 | 0,8864 | 0,8493 | **0,7325** | 0,7230 |
| Cửa sổ | 64 / stride 32 | có | 7,08 | `topk k=16`, 96 | 0,7662 | 0,8902 | 0,8528 | 0,7158 | 0,7300 |
| **Cửa sổ đối chứng** | 48 / stride 48 | **không** | **5,56** | `topk k=32`, 192 | 0,7649 | 0,8930 | 0,8584 | 0,7111 | 0,7254 |
| Cửa sổ | 256 / stride 128 | có | 1,43 | `mixed k=32`, 916 | 0,7589 | 0,8670 | 0,8210 | 0,7149 | 0,7407 |

Bảy lượt trích trên Kaggle, **0 lỗi trên 25.200 mẫu**, 0 cắt ngữ cảnh, 0 lớp tràn số.

### Phép đối chứng bác bỏ cách giải thích "chồng lấn"

T23 để lại một câu hỏi: chia theo câu thắng vì **ranh giới ngữ nghĩa**, hay chỉ vì nó **không
chồng lấn** trong khi ba cỡ cửa sổ đều chồng lấn nửa cửa sổ? Hai kết luận rất khác nhau — vế sau
thu đóng góp của đề tài xuống thành "đừng chia chồng lấn".

Dòng đối chứng khóa cả hai biến lại: cửa sổ 48 bước 48 **phủ kín không đè**, và cho **5,56** đoạn
so với 5,29 của chia theo câu. Khác chia theo câu đúng một thứ là ranh giới có theo câu hay không.

**Kết quả: 0,7649 — thấp hơn cả hai cỡ cửa sổ chồng lấn** (0,7683 và 0,7662), chứ không cao hơn.
Bỏ chồng lấn đi **không giúp được gì**.

Vậy chồng lấn chưa bao giờ là lời giải thích. Bốn cấu hình cửa sổ nằm gọn trong dải
**0,7589–0,7683** bất kể chồng lấn hay phủ kín, bất kể 1,4 hay 7,1 đoạn mỗi ngữ cảnh. Chia theo
câu đứng trên **cả bốn**. Cách giải thích còn lại là **ranh giới ngữ nghĩa**.

### Độ lớn: nhỏ, nhưng hướng thì nhất quán 8 trên 8

Phải nói thẳng về biên độ. Chia theo câu hơn cửa sổ tốt nhất **0,0085**, hơn đối chứng **0,0119**
— trên 700 mẫu dev, với biên độ trôi giữa hai môi trường đo được tới 0,0075. **Không đủ để gọi là
có ý nghĩa thống kê.**

Thứ nâng nó lên khỏi mức ngẫu nhiên là tính nhất quán. Bốn cấu hình cửa sổ × hai môi trường là
**tám phép so, cả tám đều cho chia theo câu đứng trên**:

```
                      máy cá nhân   Kaggle
  Câu                    0,7768     0,7768
  Cửa sổ 128 chồng lấn   0,7683     0,7655
  Cửa sổ 64 chồng lấn    0,7662     0,7624
  Cửa sổ 48 phủ kín      0,7649     0,7604
  Cửa sổ 256 chồng lấn   0,7589     0,7574
```

Và quan trọng hơn cả: **phép đối chứng được dựng riêng để kiểm cách giải thích cạnh tranh, rồi
cho kết quả chống lại chính cách giải thích ấy.** Đó là bằng chứng mạnh hơn một khoảng cách lớn
mà chưa ai thử bác.

### Cách gộp đầu lại đảo chỗ giữa hai môi trường

Đối chứng chọn `mixed k=8` trên Kaggle (0,7604) và `topk k=32` trên máy cá nhân (0,7649). Bảng
chọn của nó rất phẳng ở đỉnh — ba ứng viên đầu cách nhau 0,002 — nên đây là biểu hiện của độ trôi
đã ghi ở T23, lần thứ ba liên tiếp. Củng cố kết luận: **con số `k` phải để dev chọn từng lần, chỉ
họ `topk_heads` là chốt được.**

**Cửa sổ 128 thắng `intrinsic`.** 0,7325 so với 0,7202 của chia theo câu — chính lớp mà T22 cho
thấy chunk-aware bị thua so với lookback gộp. Chia theo câu bù lại ở `no` và `extrinsic` nên
thắng ở tổng, nhưng chi tiết này đáng giữ: nó nói rằng ranh giới đoạn thô hơn có ích riêng cho
lớp khó nhất. Chênh lệch 0,012 trên 700 mẫu dev thì nhỏ, chưa đủ để đảo kết luận, nhưng đủ để
không bị bỏ quên khi bàn hướng phát triển.

### Số dev không tái lập giữa hai môi trường — phát hiện ngoài dự kiến của T23

Chấm lại trên máy cá nhân từ chính sáu shard của Kaggle, dùng cùng code và cùng seed 42, cho
**số khác**:

| | Kaggle | máy cá nhân | chênh |
|---|---|---|---|
| Cửa sổ 64, `topk k=16` | 0,7587 | 0,7662 | **+0,0075** |
| Cửa sổ 64, `all` | 0,7030 | 0,6961 | −0,0069 |
| Cửa sổ 128, `topk k=32` | 0,7655 | 0,7683 | +0,0028 |
| Câu (E03), `mean_over_heads` | 0,7153 | 0,7138 | −0,0015 |
| Câu (E03), `topk k=32` | 0,7768 | 0,7768 | 0 |

Chạy hai lần **trên cùng một máy** thì trùng từng chữ số, nên đây không phải ngẫu nhiên giữa các
lượt mà là khác biệt **giữa hai môi trường**: Kaggle chạy Python 3.12, máy cá nhân 3.11, và
`LogisticRegression` với lbfgs hội tụ tới điểm hơi khác nhau tùy phiên bản thư viện số và BLAS.
Dữ liệu vào giống hệt — chính là file shard tải về.

Hệ quả phải nhớ khi đọc mọi bảng dev về sau:

1. **Biên độ trôi lên tới 0,0075**, và ở cửa sổ 64 nó đủ để **đổi cấu hình mà dev chọn** từ
   `topk k=32` sang `topk k=16`. Lựa chọn thắng sát nhau thì không bền theo môi trường.
2. **Chỉ so các cấu hình được chấm trên cùng một máy.** Bảng trên vì thế chấm lại cả bốn dòng
   tại chỗ, thay vì ghép số Kaggle của E04 với số cũ của E03.
3. **Thứ tự thì bền.** Cả hai môi trường đều cho `câu > cửa sổ 128 > cửa sổ 64 > cửa sổ 256`.
   Kết luận của T23 dựa vào thứ tự này chứ không vào giá trị tuyệt đối.

Đây là họ hàng của phát hiện ở T18, nơi seed cố định không làm cho việc tinh chỉnh trên GPU tái
lập được. Lần này nhẹ hơn nhiều — một hồi quy logistic chứ không phải mạng nơ-ron — nhưng cùng
một bài học: **"đã cố định seed" không đồng nghĩa với "tái lập được".**

**Chia theo câu thắng cả ba cỡ cửa sổ**, ở cả hai môi trường. Và kết quả **không đơn điệu theo
số đoạn** — đó mới là phần đáng nói.

Nói ngay về độ lớn: khoảng cách tới cửa sổ 128 là **0,0085** trên 700 mẫu dev, so với biên độ
trôi giữa hai môi trường đo được tới **0,0075**. Nghĩa là đây là **một thứ tự nhất quán chứ chưa
phải một chiến thắng có ý nghĩa thống kê**. Điều làm nó đáng tin không phải độ lớn mà là hình
dạng: thứ tự giống nhau ở hai môi trường, và tính không đơn điệu dưới đây không thể sinh ra từ
nhiễu theo cách nào tự nhiên.

### Không phải độ phân giải, mà là ranh giới ngữ nghĩa

Trước khi chạy, Bảng 3 được dựng để phân biệt hai giả thuyết: nếu điểm đi theo **số đoạn** thì
thứ quyết định là độ phân giải; nếu chia theo câu thắng ở mật độ đoạn tương đương thì là **ranh
giới ngữ nghĩa**. Số liệu trả lời dứt khoát.

Cửa sổ 64 cho **7,1** đoạn, cửa sổ 128 cho **3,3** — chênh **2,15 lần** — mà điểm chỉ lệch
**0,0021**. Trong khi đó chia theo câu nằm **giữa** hai cỡ ấy ở 5,3 đoạn và hơn cả hai
**0,0085–0,0106**. Sắp theo số đoạn thì thứ tự điểm là 7,1 → 5,3 → 3,3 → 1,4 ứng với
0,7662 → **0,7768** → 0,7683 → 0,7589: đỉnh rơi vào chia theo câu chứ không vào một đầu nào của
thang phân giải. Hình dạng này giống hệt ở lượt chấm trên Kaggle.

Nếu độ phân giải quyết định, câu ở 5,3 đoạn phải nằm **giữa** cửa sổ 64 và 128 về điểm số. Nó
không. Kết luận: **ranh giới câu mang thông tin mà cửa sổ token tùy tiện không có** — chunk-aware
không chỉ là "chia nhỏ ngữ cảnh ra" mà là "chia theo đơn vị nghĩa".

### Một điều chưa tách được, phải nói rõ

Cửa sổ **chồng lấn** (bước bằng nửa), câu thì **phủ kín và không đè lên nhau**. Nên "câu thắng"
vẫn còn hai cách giải thích: ranh giới ngữ nghĩa, hoặc đơn giản là không chồng lấn. Lập luận về
số đoạn ở trên nghiêng về cách thứ nhất nhưng **không loại trừ** cách thứ hai.

Tách dứt điểm cần thêm một cấu hình cửa sổ 128 **bước 128** (không chồng), khoảng 57 phút GPU.
Ghi vào đây như một việc còn nợ chứ không lờ đi.

### Cửa sổ 256 rơi đúng chỗ đã dự báo — đó là phép kiểm đường ống

**Cột "chỉ 1 đoạn" là phần dữ liệu mà năm đặc trưng hình dạng trở thành hằng số** `(0, 1, 0, 1, 0)`:
với một đoạn thì entropy bằng 0, tỷ trọng lớn nhất bằng 1 và độ dịch chuyển bằng 0, bất kể mô
hình đọc làm gì. Ở đó chunk-aware thoái hóa đúng về lookback gộp.

Dự báo trước khi chạy là cửa sổ 256 sẽ rơi về gần E02. E02 chấm qua **cùng quy trình chọn** cho
dev **0,7607**; cửa sổ 256 cho **0,7589** — lệch 0,0018. Dự báo đúng, và vì nó đúng nên đường
ống được xác nhận chứ không phải một ô trống trong bảng.

### Cửa sổ 256 tự khai ra sự thoái hóa qua cách gộp đầu nó chọn

Chia theo câu và cửa sổ 128 đều chọn `topk_heads k=32`, cửa sổ 64 chọn `topk_heads k=16` — cùng
một họ, chỉ khác bề rộng. **Họ `topk_heads` ổn định qua mọi cách chia đoạn không thoái hóa**, nên
chốt được như một quyết định; còn con số k cụ thể thì nhạy và phải để dev chọn từng lần.

Cửa sổ 256 là ngoại lệ **duy nhất và bền qua cả hai môi trường**: nó chọn họ
`mixed_all_basic_topk_rest` — Kaggle chọn k=16, máy cá nhân chọn k=32, nhưng luôn là họ ấy chứ
không phải `topk_heads`. Đây chính là ứng viên được thêm ở T22 để **giữ nguyên vẹn khối
lookback** và chỉ tỉa các khối rộng; nó đã **thua** ở E03, và giờ **thắng** đúng chỗ lý thuyết
nói nó phải thắng: khi đặc trưng hình dạng là hằng số trên 66,5 % mẫu, bộ chọn tự quay về dựa
vào tỷ lệ lookback đầy đủ. **Cách gộp đầu được chọn tự nó chẩn đoán ra sự thoái hóa**, không cần
ai nói trước.

Cửa sổ 64 thì đổi giữa `topk k=32` và `topk k=16` tùy môi trường — hai ứng viên chỉ cách nhau
0,002 nên việc chúng đảo chỗ là biểu hiện của độ trôi ở trên, không phải của cấu trúc nào.

### Chi phí không phụ thuộc cách chia đoạn — số cho E11

Bốn cách chia, đo trên cùng T4: câu **528** ms/mẫu, cửa sổ 64 **538**, cửa sổ 128 **541**, cửa
sổ 256 **540**. Số đoạn chênh nhau 5 lần mà chi phí chênh 2,5 %. Toàn bộ giá nằm ở forward pass
của mô hình đọc; phần quy kết chú ý theo đoạn gần như miễn phí.

Hệ quả cho E11: **chunk-aware không đắt hơn Lookback Lens gộp một cách có ý nghĩa**, nên nếu nó
chính xác hơn thì không phải trả giá gì để lấy phần chính xác đó.

### Một chỗ phải cẩn thận khi đọc entropy của cửa sổ chồng lấn

Bước bằng nửa cửa sổ nên các đoạn chồng lấn: một token trong vùng chồng được đếm cho cả hai
đoạn, và token ở hai đầu ngữ cảnh chỉ được phủ một lần trong khi token ở giữa được phủ hai lần.
Véc-tơ theo đoạn vì vậy không còn là một phân bố theo nghĩa chặt.

Entropy và Gini vẫn tính được sau khi chuẩn hóa, nhưng phải diễn giải là *"chú ý tản trên các
cửa sổ"* chứ không phải *"tản trên các phần rời nhau của ngữ cảnh"*. Chia theo câu không vướng
điều này vì các câu phủ kín và không đè lên nhau. Nếu cửa sổ thua câu thì đây là một trong hai
cách giải thích, và cách kia là số đoạn — nên phải đọc Bảng 3 theo cả hai cột.

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
