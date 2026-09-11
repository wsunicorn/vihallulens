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

**E14 — ba nấc, ba kiểu hỏng số học khác nhau, và một nấc lệch kiểu số.** Đo ở T31 ngày
09/09/2026 trên 20 mẫu trải từ 47 tới 4.805 từ:

| | Qwen2.5-7B | Qwen2.5-3B | Qwen2.5-1.5B |
|---|---|---|---|
| Số lớp | 28 | 36 | 28 |
| Lớp tràn số ở `float16` | lớp 27 | **không lớp nào** | **cả 28 lớp** |
| Mẫu có ít nhất một lớp nan | 20/20 | 0/20 | 20/20 |
| Kiểu số dùng để trích | `float16` | `float16` | **`bfloat16`** |
| ms/mẫu ở kiểu số ấy (lượt dò) | 528 | 513 | **1.101** |

Ba cỡ của **cùng một họ mô hình** cho ba hình dạng hỏng khác hẳn nhau, nên chuyện tràn số ở
`float16` không suy ra được từ kiến trúc hay từ cỡ — phải đo từng bản một.

Nấc 1.5B phải chạy `bfloat16` vì `float16` không còn lớp nào dùng được. Hai hạn chế phải ghi
kèm bảng kết quả:

1. **So nấc 1.5B với nấc 3B là để hai thứ đổi cùng lúc** — cỡ mô hình và kiểu số. Chỉ đụng
   vào phần so tuyệt đối; phần "chunk-aware có hơn mốc lookback của chính nó không" tính
   trong nội bộ từng cỡ, chung mô hình chung kiểu số chung shard, nên sạch. `bfloat16` lại
   trung thực hơn `float16`, nên nếu 1.5B vẫn kém hơn thì đó là kết luận thận trọng.
2. **Con số chi phí gắn với T4.** Turing không có `bfloat16` gốc nên phải giả lập, chậm 4,1
   lần. Trên Ampere trở lên bf16 nhanh ngang fp16 và cả vấn đề này biến mất. Kết luận "nấc
   lùi 1.5B đắt hơn gấp đôi nấc 3B" phải luôn đi kèm tên phần cứng.

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

**Đo ở T35 (11/09/2026) trên E03, tập test ViHallu**, bằng `scripts/error_analysis.py`:

| Nhóm | n | macro-F1 [KTC 95 %] | Sai | Tỷ lệ sai |
|---|---|---|---|---|
| `noisy` | 23 | 0,7798 [0,5765–0,9151] | 5 | 21,7 % |
| còn lại | 677 | 0,7558 [0,7235–0,7866] | 164 | 24,2 % |

Chênh **+0,0239** nghiêng về phía `noisy`, và khoảng tin cậy của nhóm ấy rộng **0,34** vì chỉ có 23
mẫu. Kết luận đọc được: **không có bằng chứng prompt bị bỏ dấu làm bộ phát hiện kém đi** — nếu
có tác động thì nó nhỏ hơn mức 23 mẫu phân biệt được. Mô hình không "phát hiện prompt nhiễu"
thay vì phát hiện ảo giác. Phần này phải đi kèm khoảng tin cậy khi trình bày, đừng trích riêng
con số điểm.

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

## 5. Bảng kết quả

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
| **Lookback gộp (E02)** ¶ | **0,745** [0,711–0,776] | 0,843 | 0,896 | 0,890 | 0,793 | **0,731** | 0,712 | 0,109 | 438 | 8.328 |
| **Chunk-aware câu (E03)** ¶ | 0,757 [0,724–0,789] | 0,864 | 0,894 | 0,915 | 0,823 | 0,686 | **0,762** | **0,044** | 438 | 8.328 |

Dòng "Chunk-aware (E05)" của bản đặc tả đầu không còn: E05 là bước **chọn** cách chia đoạn
(Bảng 3), và cách được chọn — chia theo câu, `min_words=5` — chính là dòng E03 ở trên.

Đo ngày 28/08/2026 trên T4, 3 seed mỗi mô hình, 3 epoch, learning rate 1e-5. Độ lệch chuẩn qua seed — 0,011 cho PhoBERT và 0,017 cho XLM-R — nằm trong `results/runs.jsonl` dưới khóa `_std`, tách khỏi sai số chuẩn bootstrap ở khóa `_se`. Dòng E10 đo ngày 27/08.

**¶** Cột `ms/mẫu` sửa ngày 10/09/2026. Bản cũ ghi 464 ms cho E02 và 528 ms cho E03 — hai con số cho **cùng một lượt trích**, vì hai dòng dùng chung shard `8c49fc0417f1` và chung `extraction_hash`. Chênh lệch 64 ms là nhiễu giữa hai phép đo, không phải chi phí thật của chunk-aware. Số mới 438 ms lấy từ lượt đo **xen kẽ** của T31, quy về phân bố độ dài của ViHallu, độ trôi giữa hai lượt 2,09 %; VRAM 8.328 MB đo trong cùng lượt ấy. Xem Bảng 8. Cột này là **thời gian chạy mô hình đọc để lấy ma trận chú ý**, không phải thời gian của bộ phân loại — bộ phân loại chỉ có 2.271 tham số và chạy trong micro giây. VRAM lấy từ phép đo T08 trên đúng cấu hình này. Con số 464 ms là chi phí **tuyệt đối**; lập luận của đề tài là chi phí **biên** trong một hệ RAG thật gần bằng 0 vì lượt đọc đó dù sao cũng phải chạy — nhưng thí nghiệm này **không đo** điều đó, nên phải nói rõ khi trình bày.

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

### Bảng 2b — Chunk-aware trên ngữ cảnh dài (E07, ISE-DSC01)

Chạy 31/08–01/09/2026. Trích 10,1 giờ GPU, **0 lỗi trên 32.723 mẫu**, 0 cắt ngữ cảnh, 0 lớp tràn
số. Chấm điểm chạy trên máy cá nhân, cùng máy đã chấm E02 và E03, theo nguyên tắc chốt ở T23.

| Bộ dữ liệu | Đoạn/ngữ cảnh | train | Lookback gộp | Chunk-aware | Chênh |
|---|---|---|---|---|---|
| ViHallu | 5,3 | 5.600 | 0,7451 | 0,7567 | **+0,0116** |
| ISE-DSC01 | 22,6 | 5.600 | 0,7337 | 0,7388 | **+0,0051** |
| ISE-DSC01 | 22,6 | 29.077 | 0,7851 | **0,7919** | **+0,0068** |

Chi tiết lượt đầy đủ trên ISE-DSC01: macro-F1 **0,7919** [0,7791; 0,8054], nhị phân 0,8536,
`no` 0,8111 · `intrinsic` 0,7633 · `extrinsic` 0,8011, ECE 0,0334.

### Chunk-aware chuyển được sang ngữ cảnh dài, nhưng lợi thế KHÔNG lớn lên

Giả thuyết trước khi chạy: ngữ cảnh càng nhiều đoạn thì hình dạng phân bố càng có chỗ để nói lên
điều gì, nên đây phải là chỗ chunk-aware mạnh lên.

**Không đúng.** Lợi thế so với lookback gộp là **+0,0116 trên ViHallu (5,3 đoạn)** nhưng chỉ
**+0,0051 tới +0,0068 trên ISE-DSC01 (22,6 đoạn)**. Gấp bốn số đoạn thì lợi thế **co lại còn
một nửa**.

Cả ba chênh lệch đều nhỏ so với khoảng tin cậy — [0,7791; 0,8054] của chunk-aware chồng gần hết
lên [0,7714; 0,7982] của lookback gộp. Đúng đắn nhất là nói: **chunk-aware nhỉnh hơn lookback gộp
một cách nhất quán về hướng nhưng không có ý nghĩa thống kê, ở cả hai bộ dữ liệu.**

Lý do lợi thế co lại thì đọc được ngay từ bảng: **lookback gộp trên ISE-DSC01 đã rất mạnh sẵn**
(0,7851 so với 0,7451 trên ViHallu). Ngữ cảnh dài không làm chunk-aware yếu đi — nó làm *mốc so*
khỏe lên, và phần dư địa còn lại để cải thiện thì ít đi.

### Khoảng cách giữa "định vị đúng" và "phân loại đúng" mới là phát hiện

E06 cho thấy chú ý rơi đúng đoạn bằng chứng **87,8 %** số lần, gấp 14 lần sàn ngẫu nhiên. E07 cho
thấy biết *chỗ nào* được nhìn chỉ thêm **+0,007** so với biết *bao nhiêu* phần chú ý rơi vào ngữ
cảnh.

Hai kết quả này không mâu thuẫn, và đặt cạnh nhau chúng nói một điều đáng viết: **tín hiệu định
vị có thật và rất mạnh, nhưng bài toán phân loại ba lớp này phần lớn đã được giải bằng đại lượng
gộp.** Định vị đúng không tự động thành phân biệt đúng.

Đây là chỗ hướng phát triển nằm: một bài toán *cần* biết chỗ — chỉ ra câu nào trong ngữ cảnh
chống đỡ hay mâu thuẫn với phản hồi — sẽ khai thác được phần E06 đo, còn nhãn ba lớp thì không.

### Cột phần trăm trọng số dễ đọc sai, phải quy về mỗi cột

Nhìn thô thì đặc trưng chunk chiếm **87 % trọng số ở E03** nhưng chỉ **27 % ở E07** — như thể
chúng mất tác dụng trên ngữ cảnh dài. Đó là hiện vật của cách gộp đầu mà dev chọn, không phải
của dữ liệu.

E03 chọn `topk k=32` nên khối lookback còn 32 cột; E07 chọn `mixed k=32` nên khối lookback giữ
**nguyên 756 cột** còn năm khối chunk mỗi khối 32 cột. Quy về mỗi cột:

| | lookback | chunk-aware | tỷ lệ |
|---|---|---|---|
| E03, ViHallu 5,3 đoạn | 0,4016 %/cột | 0,5447 %/cột | 1,36× |
| E07, ISE-DSC01 22,6 đoạn | 0,0963 %/cột | 0,1700 %/cột | **1,77×** |

**Mỗi cột đặc trưng chunk nặng ký hơn trên ngữ cảnh dài, không nhẹ đi.** Bộ phân loại dựa vào
chúng *nhiều hơn*; chỉ là phần dư địa để cải thiện điểm số thì nhỏ hơn.

### Đường cong học dốc hơn hẳn dự đoán, và dự đoán ấy là của tôi

Trước khi chạy tôi ước lượng từ ViHallu rằng trích đủ 29.077 mẫu thay vì 5.600 sẽ mua khoảng
**+0,015**. Đo thật:

```
  chunk-aware   5.600 → 29.077   0,7388 → 0,7919   +0,0531
  lookback gộp  5.600 → 29.077   0,7337 → 0,7851   +0,0514
```

**+0,053, gấp ba lần rưỡi ước lượng.** Đường cong học của ISE-DSC01 dốc hơn ViHallu nhiều, và
ngoại suy từ bộ này sang bộ kia không đứng được. Quyết định trích đủ hóa ra đúng với biên độ lớn
hơn hẳn lý do đã dùng để biện minh cho nó.

Ghi lại như một hạn chế của phương pháp làm việc: **đường cong học đo trên một bộ không dự báo
được cho bộ khác**, kể cả cùng một mô hình đọc và cùng một bộ đặc trưng.

### Một chỗ ECE đảo chiều so với ViHallu

Trên ViHallu, chunk-aware **giảm** ECE hơn một nửa (0,1090 → 0,0441) và đó là một trong ba điều
E03 làm được. Trên ISE-DSC01 nó **tăng** nhẹ (0,0258 → 0,0334). Lookback gộp ở đây hiệu chỉnh tốt
hơn.

Chưa có cách giải thích chắc chắn, và không nên bịa một cách. Ghi lại như một quan sát cần đối
chiếu ở E12 khi tách riêng đóng góp từng nhóm đặc trưng.

### Bảng 2c — Bỏ bằng chứng đi (E08, ViWikiFC)

Chạy 01/09/2026, 43,1 phút GPU, **0 lỗi trên 3.672 dòng**, 0 cắt ngữ cảnh, 0 lớp tràn số.
1.836 cặp, mỗi cặp là **cùng một claim đọc hai lần** trên hai ngữ cảnh mười câu khác nhau **đúng
một câu ở đúng một vị trí**.

| Đặc trưng | Có vàng | Mất vàng | Đổi | % cặp đúng hướng | Cỡ ảnh hưởng |
|---|---|---|---|---|---|
| `chunk_entropy` ↑ | 0,7966 | 0,8176 | **+0,0156** | **75,4 %** | +0,7156 |
| `chunk_gini` ↓ | 0,5064 | 0,4860 | −0,0158 | 74,5 % | −0,6855 |
| `chunk_max_share` ↓ | 0,3597 | 0,3392 | −0,0139 | 72,4 % | −0,6570 |
| `top1_top2_gap` ↓ | 0,1829 | 0,1611 | −0,0129 | 71,2 % | −0,6237 |
| `chunk_drift` *(không dự đoán)* | 0,2081 | 0,2110 | +0,0024 | 63,3 % | +0,4009 |

**Cả bốn hướng dự đoán đều đúng.** Mũi tên trong cột đầu là hướng đã ghi vào `EXPECTED_DIRECTION`
**trước khi chạy**, có ca kiểm thử khóa lại, nên không có cách nào mô tả lại một kết quả đi ngược
thành xác nhận.

### Vì sao đây là bằng chứng khác loại với mọi bảng còn lại

Bảng 1, 2, 2b và 3 đều **tương quan**: đo một tín hiệu, so với nhãn ai đó gán, báo mức khớp. Khi
hai bên khớp, câu "cơ chế hoạt động" là một **suy luận** — tín hiệu có thể đang bắt bất kỳ thứ gì
đi kèm với nhãn.

Bảng này **can thiệp**. Giữ nguyên phản hồi, giữ nguyên chín câu nhiễu, giữ nguyên độ dài, số
đoạn và thứ tự — chỉ **rút câu bằng chứng ra** và thay bằng câu nhiễu kế tiếp. Rồi đo lại. Ba đến
bốn cặp trên năm chuyển động **đúng hướng cơ chế dự đoán**, với cỡ ảnh hưởng 0,62–0,72, tức mức
**lớn** trên thang rank-biserial.

Nhãn nửa "mất vàng" cũng không do ai gán: rút câu vàng ra thì phản hồi khẳng định điều ngữ cảnh
không chứa, đúng định nghĩa ảo giác ngoại lai. T13 đo được ranh giới nội tại–ngoại lai đánh bại
hai người gán nhãn (kappa 0,70 và 0,50) và cả Gemini (0,474); ở đây ranh giới ấy được **dựng ra**
chứ không được **đoán**, nên lần đầu tiên phần khó nhất của bài toán không phụ thuộc chất lượng
nhãn.

### Độ lớn nhỏ, và phải nói rõ điều đó

Chênh lệch tuyệt đối chỉ **0,013–0,016 trên thang 0–1**. Kiểm định theo cặp đo mức **nhất quán
của hướng**, không đo độ lớn — một dịch chuyển nhỏ tới mức vô nghĩa vẫn cho tỷ lệ cặp đúng hướng
rất cao nếu nó đều. Có một ca kiểm thử dựng đúng cái bẫy ấy để khóa lại.

Cách đọc đúng: **rút bằng chứng ra làm chú ý tản hơn một cách nhỏ nhưng rất nhất quán.** Đó vẫn
là điều đề tài cần — nó chứng minh tín hiệu *phản ứng với sự có mặt của bằng chứng*, chứ không
chứng minh tín hiệu ấy đủ mạnh để một mình phân loại. Hai điều khác nhau, và E03 với E07 đã cho
thấy điều thứ hai không đúng.

### `chunk_drift` phản ứng mà không được dự đoán

63,3 % cặp, cỡ ảnh hưởng +0,4009 — thấp hơn bốn đặc trưng kia nhưng vẫn trên mức ngẫu nhiên rõ
rệt. `EXPECTED_DIRECTION` ghi 0 cho nó vì drift nói về **chuyển động của phân bố qua các token
phản hồi**, không phải hình dạng ở một thời điểm, nên không có lý do tiên nghiệm để nó đổi.

Ghi lại như **quan sát thăm dò**, không phải xác nhận: nó không nằm trong dự đoán, nên dùng nó
làm bằng chứng bây giờ là chọn giả thuyết sau khi thấy dữ liệu. Nếu muốn dùng thì phải kiểm lại
trên bộ khác.

### E08 lặp lại E06 trên bộ dữ liệu thứ hai, và con số gần như trùng

Nửa "có vàng" của mỗi cặp đo được đúng thứ E06 đo, nên E08 là một **phép lặp độc lập**:

| | E06 · ISE-DSC01 | E08 · ViWikiFC |
|---|---|---|
| Cách dựng ngữ cảnh | tài liệu tự nhiên | mười câu BM25 truy xuất, **đã xáo thứ tự** |
| Đoạn mỗi ngữ cảnh | 22,6 | 9,8 |
| Sàn ngẫu nhiên hit@1 | 0,0614 | 0,1027 |
| **hit@1 đầu mạnh nhất** | 0,8779 (lớp 14, đầu 6) | **0,8529** (lớp 19, đầu 20) |
| **hit@1 trung bình 756 đầu** | 0,3320 | **0,3289** |
| hit@3 | 0,9562 | 0,9461 |
| MRR | 0,9200 | 0,9049 |

Hai corpus khác nhau về thể loại, khác cách dựng ngữ cảnh, khác số đoạn gần ba lần, khác sàn ngẫu
nhiên — mà **hit@1 trung bình mọi đầu lệch nhau 0,003**. Con số ấy không dính lựa chọn nào, nên
sự trùng khớp không thể là hiện vật của việc chọn đầu tốt nhất.

**Định vị bằng chứng là thuộc tính của mô hình đọc, không phải của một bộ dữ liệu.** Đây là điều
E06 một mình không nói được.

### Chi phí và tái lập

**705 ms/mẫu**, khớp mô hình tuyến tính theo token của T08 với ngữ cảnh 496 token. Chấm lại trên
máy cá nhân từ shard tải về cho **trùng từng chữ số**, như E06 và khác T23 — vì cả hai đều là số
học thuần, không có bộ tối ưu lặp nào.

Nhưng phần **dựng ngữ cảnh** thì không tái lập được giữa hai máy, và điều đó chỉ lộ ra khi so
file. BM25 xếp hạng bằng `argsort`, vốn không ổn định, nên hai câu cùng điểm ra theo thứ tự tùy
phiên bản numpy — **17 trên 1.836 cặp** (0,9 %) dựng ngữ cảnh khác nhau trên Kaggle và trên máy
cá nhân, một cặp thậm chí khác số đoạn. Đã sửa thành `lexsort` phân định hòa bằng `evidence_id`,
tức bằng nội dung câu, kèm hai ca kiểm thử.

Con số trong bảng **không đổi**: phép ghép cặp chỉ dùng `sample_id` và `pair_id` vốn giống nhau ở
cả hai bản, còn đặc trưng lấy từ shard trích trên Kaggle. Bản parquet giữ lại là bản của Kaggle,
đúng bản đã sinh ra shard. Shard vì thế **có trước bản sửa**, và dựng lại kho bây giờ sẽ ra một
bản thứ ba khác cả hai ở đúng những cặp hòa điểm ấy.

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

### Điều này từng chưa tách được, và đã tách xong ở T24

Đoạn này giữ lại vì lịch sử của nó đáng đọc, chứ không phải vì còn nợ.

Khi T23 chạy xong, "câu thắng" còn hai cách giải thích: **ranh giới ngữ nghĩa**, hoặc đơn giản là
**không chồng lấn** — vì cả ba cỡ cửa sổ đều bước bằng nửa, còn câu thì phủ kín không đè. Lập
luận về số đoạn ở trên nghiêng về cách thứ nhất nhưng không loại trừ cách thứ hai. Phương án ghi
lúc đó là chạy thêm cửa sổ 128 **bước 128**.

**T24 chạy phép đối chứng, và chọn một cấu hình tốt hơn phương án ấy:** cửa sổ 48 **bước 48**, cho
**5,56** đoạn — sát 5,29 của chia theo câu, trong khi 128/128 chỉ cho 2,43 đoạn và như vậy còn lẫn
biến mật độ vào. Kết quả nằm ở mục "Phép đối chứng bác bỏ cách giải thích chồng lấn" phía trên:
**0,7649, thấp hơn cả hai cỡ cửa sổ chồng lấn.** Bỏ chồng lấn đi không giúp được gì, nên chồng lấn
chưa bao giờ là lời giải thích.

Không còn nợ lượt GPU nào ở đây.

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

### Bảng 4 — Ablation nhóm đặc trưng (E12, ViHallu)

Chạy 02/09/2026 trên máy cá nhân, **0 giây GPU** — mọi mức đọc lại shard `8c49fc0417f1` mà E02 và
E03 đã dùng, chỉ khớp lại bộ phân loại trên các tập con cột. Bốn mức **cộng dồn**, nên cột chênh
đọc là "nhóm này cộng thêm bao nhiêu vào mọi nhóm phía trên".

Hai đặc trưng bề mặt của E01 có mặt ở **mọi** mức, kể cả mức 1. Câu hỏi được đặt là chú ý cộng
thêm bao nhiêu vào *thứ lấy được miễn phí*, chứ không phải chú ý một mình đạt bao nhiêu.

Bảng chạy hai lần với hai cách xử lý gộp đầu, vì cách thứ nhất trộn hai thứ vào một cột chênh:

| Nhóm đặc trưng | Dev chọn riêng từng mức | Chênh | Gộp chung `topk k=32` | Chênh |
|---|---|---|---|---|
| Chỉ bề mặt | 0,6562 | — | 0,6562 | — |
| + lookback gộp | 0,7653 | **+0,1091** | 0,7759 | **+0,1197** |
| + chunk-aware | 0,7388 | **−0,0266** | 0,7688 | **−0,0071** |
| + ổn định | 0,7746 | +0,0358 | 0,7746 | +0,0057 |

Khoảng tin cậy 95 % của dòng cuối là [0,7431; 0,8060], rộng **0,063**.

### Nhóm chunk-aware cộng thêm một số âm, và phải nói thẳng

Đây là kết quả bất lợi cho đóng góp cốt lõi của đề tài, ghi lại nguyên trạng.

Cột chênh của cách đo thứ nhất không đọc thẳng được: dev chọn `k=64` cho mức 2, `k=16` cho mức 3
rồi `k=32` cho mức 4, nên **−0,0266** trộn "thêm bốn đại lượng hình dạng" với "số cột tụt từ 64
đầu xuống 16 đầu". Cách đo thứ hai khóa cách gộp lại ở `topk k=32` cho cả bảng, và phần lớn con
số âm biến mất: còn **−0,0071**.

Nhưng **dấu thì không đổi**. Ở cả hai cách đo, thêm nhóm chunk-aware vào tỷ lệ gộp cộng với đặc
trưng bề mặt làm điểm **giảm nhẹ** chứ không tăng.

### Vì sao điều này không mâu thuẫn với E03, và nó thật sự nói gì

E03 đo được chunk-aware **hơn** lookback gộp +0,0116. E12 đo được nó **kém** 0,0071. Khác nhau ở
đúng một điều: **E03 không có hai đặc trưng bề mặt trong véc-tơ, E12 thì có ở mọi mức.**

Đặt cạnh nhau thì ba con số +0,0116, −0,0071 và −0,0266 đều nằm sâu trong khoảng tin cậy rộng
0,063 của một tập test 700 mẫu. Kết luận đúng đắn nhất:

> **Đóng góp riêng của nhóm chunk-aware trên ViHallu không phân biệt được với 0.** Dấu của nó
> đổi tùy theo có mặt đặc trưng bề mặt hay không, và mọi độ lớn đo được đều nhỏ hơn nhiễu của
> tập test.

Cách giải thích khả dĩ nhất, và cần kiểm thêm trước khi khẳng định: **phần tín hiệu mà hình dạng
phân bố mang có chồng lấn với phần mà độ dài phản hồi và độ trùng lặp từ vựng đã mang.** Cả hai
đều bắt được cùng một hiện tượng — phản hồi không bám vào ngữ cảnh — chỉ bằng hai đường khác
nhau. Khi tỷ lệ gộp và hai đặc trưng bề mặt đã có mặt, phần dư địa còn lại cho hình dạng thì ít.

### Điều bảng này KHÔNG bác bỏ

Nó nói về **giá trị cộng thêm cho bài toán phân loại**, không nói về cơ chế. Bốn kết quả sau
không bị đụng tới:

- Định vị đúng đoạn bằng chứng 87,8 % giữa 22,6 đoạn (E06), lặp lại trên bộ thứ hai (E08).
- Phép kiểm can thiệp đúng cả bốn hướng dự đoán (E08).
- Sai số hiệu chỉnh xác suất giảm hơn một nửa, 0,109 → 0,044 (E03).
- Đầu ra chỉ được đoạn nào — thứ tỷ lệ gộp không cho được, bất kể điểm số.

Nói cách khác, E12 củng cố đúng cái kết luận mục 5.7 của báo cáo giữa kỳ đã nêu: **định vị đúng
và phân loại đúng là hai việc khác nhau.** Bây giờ có thêm một phép đo trực tiếp cho vế thứ hai.

### Hai việc để lại — làm xong ở T35B, 11/09/2026

Cả hai chạy trên máy cá nhân, **0 giây GPU**, đọc lại shard E07 (`15ef31521fd6`). Khung bốn mức giữ
nguyên; mức phụ ghi vào `extra["extra_levels"]` qua cờ `--extra-level`, không chèn vào bảng.

#### Bảng 4b — E12 trên ISE-DSC01, đặt cạnh ViHallu

| Bộ | Cách gộp đầu | Chỉ bề mặt | + lookback gộp | + chunk-aware | **chênh** | + ổn định |
|---|---|---|---|---|---|---|
| ViHallu | dev chọn riêng | 0,6562 | 0,7653 | 0,7388 | **−0,0266** | 0,7746 |
| ViHallu | gộp chung k=32 | 0,6562 | 0,7759 | 0,7688 | **−0,0071** | 0,7746 |
| ISE-DSC01 | dev chọn riêng | 0,4767 | 0,7837 | 0,7839 | **+0,0002** | 0,7918 |
| ISE-DSC01 | gộp chung k=32 | 0,4767 | 0,6554 | 0,6950 | **+0,0396** | 0,7024 |

Test ISE-DSC01 có 3.646 mẫu nên khoảng tin cậy hẹp, khoảng ±0,014.

**Việc 1 trả lời: ở 22,6 đoạn, chênh là +0,0002.** Không âm như ViHallu, cũng không dương — bằng
không, với sai số nhỏ hơn cả ViHallu. Kết luận "đóng góp riêng không phân biệt được với 0"
**vững, và không phụ thuộc số đoạn**.

Dòng gộp chung của ISE-DSC01 cho +0,0396 và cần đọc kỹ, vì nó là một hiện tượng khác. Khóa cách
gộp ở 32 đầu làm lookback gộp **mất 0,128** trên bộ này (0,6554 so với 0,7837 khi dùng đủ 758
cột) — ngữ cảnh 22,6 đoạn cần nhiều đầu hơn ngữ cảnh 5,3 đoạn. Bốn khối chunk-aware ở k=32 thêm
128 cột **từ chính 32 đầu ấy**, và một phần thông tin bị cắt đi quay lại theo đường đó. Đây là
"thêm cột từ cùng những đầu", không phải "thêm thông tin": khi lookback được dùng đủ bề rộng thì
phần cộng thêm biến mất. Chế độ gộp chung — vốn được thêm ở T29 để cột chênh sạch trên ViHallu —
tạo ra một hiện tượng giả trên bộ nhiều đoạn. **Chế độ dev chọn riêng là chế độ đọc đúng cho
ISE-DSC01.**

Hai điều phụ đọc được từ bảng:

- **Đặc trưng bề mặt yếu hơn hẳn trên ISE-DSC01**: 0,4767 so với 0,6562. Câu khẳng định do người
  viết không mang dấu vết độ dài và trùng lặp như phản hồi GPT-4o. Chú ý vì thế cộng thêm **+0,31**
  ở đây so với +0,11 trên ViHallu — tín hiệu chú ý quan trọng hơn đúng ở chỗ bề mặt bất lực.
- **Nhóm ổn định là nhóm duy nhất cộng thêm dương ở cả bốn dòng** (+0,0057 tới +0,0358).

#### Bảng 4c — Mức phụ: chồng lấn giữa chunk-aware và lookback gộp

Mức phụ chấm **bề mặt + chunk-aware, bỏ lookback gộp**. Từ ba mức có chung gốc bề mặt tính được:

    chồng lấn = gain(lookback một mình) + gain(chunk-aware một mình) − gain(cả hai)

Bằng 0 là hai nhóm cộng được vào nhau; dương là mang cùng một thông tin; bằng đúng gain của
chunk-aware là **mọi thứ chunk-aware mang, lookback đã mang rồi**.

| Bộ | Cách gộp | lookback một mình | chunk-aware một mình | cả hai | **chồng lấn** | chồng lấn / chunk riêng |
|---|---|---|---|---|---|---|
| ViHallu | dev | +0,1091 | +0,0232 | +0,0825 | +0,0497 | 214 % |
| ViHallu | gộp chung | +0,1197 | +0,0237 | +0,1126 | +0,0308 | 130 % |
| ISE-DSC01 | dev | +0,3070 | +0,2268 | +0,3072 | **+0,2266** | **99,9 %** |
| ISE-DSC01 | gộp chung | +0,1787 | +0,1438 | +0,2183 | +0,1042 | 72 % |

**Việc 2 trả lời, và nó sửa lại giả thuyết cũ.** Mục trên đoán chunk-aware chồng lấn với **đặc
trưng bề mặt**. Số đo nói khác: chunk-aware một mình cộng thêm +0,0232 trên ViHallu và **+0,2268**
trên ISE-DSC01 so với bề mặt — tức nó *có* mang tín hiệu mà bề mặt không có, và mang khá nhiều
khi ngữ cảnh dài. Thứ nó chồng lấn là **lookback gộp**: trên ISE-DSC01 ở chế độ dev, 99,9 % phần
chunk-aware cộng thêm nằm sẵn trong lookback. Trên ViHallu tỷ lệ vượt 100 %, nghĩa là đặt
chunk-aware lên trên lookback còn kéo điểm xuống — đúng cột chênh âm của Bảng 4.

Kết luận gộp cả T29 và T35B, viết cho chương 7:

> Năm đại lượng hình dạng phân bố chú ý **có** mang tín hiệu phát hiện ảo giác — càng nhiều đoạn
> càng mang nhiều — nhưng đó là **cùng một tín hiệu** mà tỷ lệ lookback gộp đã mang, đo được ở
> mức 99,9 % trên ngữ cảnh 22,6 đoạn. Chúng không cộng thêm gì vào bộ phát hiện, và điều này
> không phụ thuộc số đoạn.

Cái chúng có mà lookback không có là **đầu ra chỉ được đoạn nào** — Bảng 2, 2b, 2c — và đó vẫn là
đóng góp thật, chỉ không phải đóng góp về điểm phân loại.

### Bảng 5 — Mô hình đọc (E13, ViHallu)

Chạy 09/09/2026. Trích Sailor2 mất 66 phút GPU cho 7.000 mẫu, **0 lỗi**, 0 cắt ngữ cảnh. Chấm
trên máy cá nhân, cùng máy đã chấm E02 và E03.

| Mô hình đọc | Lưới | Nhóm đặc trưng | macro-F1 | Nhị phân | `no` | `intr` | `extr` | ECE |
|---|---|---|---|---|---|---|---|---|
| Qwen2.5-7B | 27 × 28 | lookback gộp | 0,7451 | 0,8426 | 0,7925 | **0,7308** | 0,7121 | 0,1090 |
| Qwen2.5-7B | 27 × 28 | chunk-aware | **0,7567** | **0,8636** | **0,8228** | 0,6858 | **0,7615** | **0,0441** |
| Sailor2-8B | 30 × 28 | lookback gộp | 0,7377 | 0,8406 | 0,7880 | 0,6971 | 0,7281 | 0,0484 |
| Sailor2-8B | 30 × 28 | chunk-aware | 0,7120 | 0,8245 | 0,7666 | 0,6653 | 0,7040 | 0,0715 |

Hai dòng Sailor2 chấm trên **697** mẫu test thay vì 700 — ba mẫu bị loại vì đặc trưng không hữu
hạn, xem mục "0,7 % mẫu hỏng" bên dưới.

### Kết quả chính: một họ đặc trưng chuyển được, họ kia thì không

Đọc bảng theo **cột chênh** chứ không theo dòng nào cao nhất:

| | Qwen2.5-7B | Sailor2-8B | chênh giữa hai mô hình |
|---|---|---|---|
| lookback gộp | 0,7451 | 0,7377 | **−0,0074** |
| chunk-aware | 0,7567 | 0,7120 | **−0,0447** |
| chunk-aware − lookback | **+0,0116** | **−0,0257** | |

Hai điều, và điều thứ hai là kết quả thật của E13:

1. **Tỷ lệ lookback gộp chuyển gần như hoàn hảo giữa hai mô hình đọc.** 0,7451 so với 0,7377,
   lệch 0,0074 — nhỏ hơn cả biên độ trôi 0,0075 giữa hai môi trường máy tính đo ở T23. Đổi hẳn
   mô hình đọc mà điểm gần như không nhúc nhích.

2. **Nhóm chunk-aware thì không chuyển.** Trên Qwen nó cộng +0,0116; trên Sailor2 nó **trừ
   0,0257**. Đổi dấu, và độ lớn gấp đôi. Toàn bộ khoảng cách 0,0447 giữa hai mô hình nằm ở đúng
   nhóm đặc trưng này.

Nói gọn: **thứ đo "mô hình có bám vào ngữ cảnh không" là thuộc tính bền của kiến trúc; thứ đo
"hình dạng phân bố trên các đoạn" thì gắn với từng mô hình cụ thể.**

Đây là kết quả bất lợi cho đóng góp của đề tài và nó **độc lập** với E12: E12 hỏi nhóm chunk-aware
cộng thêm bao nhiêu khi đứng cạnh đặc trưng bề mặt (trả lời: không phân biệt được với 0); E13 hỏi
nó có chuyển sang mô hình đọc khác không (trả lời: không). Hai phép đo khác nhau, cùng một hướng.

### Vị trí đầu chú ý — hai lưới khác nhau nên chỉ so được độ sâu

Sailor2 có 32 lớp, bỏ hai lớp cuối còn **30**; Qwen có 28, bỏ lớp 27 còn **27**. Lớp 5 của mô
hình 28 lớp và lớp 5 của mô hình 32 lớp nằm ở hai độ sâu khác nhau, nên phép trùng chỉ số và
Spearman đều vô nghĩa ở đây. `scripts/compare_heads.py` **từ chối** in chúng và chỉ báo phân bố
theo độ sâu tương đối, vốn định nghĩa được cho cả hai.

| k | Bên | TB độ sâu | 1/3 đầu | 1/3 giữa | 1/3 cuối |
|---|---|---|---|---|---|
| 10 | Qwen | 0,638 | 20,0 % | 30,0 % | 50,0 % |
| 10 | Sailor2 | 0,479 | 30,0 % | 40,0 % | 30,0 % |
| 32 | Qwen | 0,590 | 28,1 % | 31,2 % | 40,6 % |
| 32 | Sailor2 | 0,547 | 25,0 % | 37,5 % | 37,5 % |
| 64 | Qwen | 0,572 | 23,4 % | 37,5 % | 39,1 % |
| 64 | Sailor2 | 0,517 | 29,7 % | 35,9 % | 34,4 % |

Ba điều đọc được:

1. **Cả hai mô hình đều rải đầu có ích khắp độ sâu**, không mô hình nào dồn về một vùng. Ở k=64,
   cả hai đều có 23–30 % ở một phần ba đầu và 34–39 % ở một phần ba cuối. Đây là phép lặp của
   quan sát đã ghi ở E02 — các đầu có ích trải khắp, không dồn về cuối.

2. **Khoảng cách thu hẹp khi k lớn dần:** 0,159 ở k=10, còn 0,043 ở k=32 và 0,055 ở k=64. Nghĩa
   là khác biệt nằm ở *vài đầu dẫn đầu* chứ không ở cả quần thể. Con số k=10 là con số nhiễu
   nhất, đừng dẫn nó.

3. **Sailor2 nghiêng nông hơn một chút** — 0,517 so với 0,572 ở k=64, tức khoảng 5,5 % độ sâu
   mạng. Nhỏ, cùng chiều ở cả ba mức k, nhưng chưa có phép kiểm nào nói nó vượt mức ngẫu nhiên.

Phát biểu đúng đắn nhất: **phân bố độ sâu của các đầu có ích gần giống nhau ở hai mô hình, không
trùng khít.** Nó không đủ mạnh để nói vị trí đầu sao chép là thuộc tính thuần của kiến trúc, mà
cũng không cho thấy huấn luyện tiếng Việt dịch chuyển chúng đi đâu rõ rệt.

### 0,7 % mẫu hỏng, và vì sao không bỏ thêm lớp được

49 trên 7.000 mẫu (0,70 %) có đặc trưng không hữu hạn: train 38 (0,68 %), dev 8 (1,14 %), test
3 (0,43 %). Bảng theo lớp cho thấy **cùng một tập mẫu ấy hỏng ở mọi lớp từ 1 trở đi** — không
phải lớp nào yếu, mà vài mẫu làm activation tràn `float16` ngay từ lớp đầu rồi `nan` lan khắp
mạng.

Khác hẳn Qwen, nơi đúng lớp 27 hỏng trên *mọi* mẫu nên bỏ một lớp là xong cho tất cả. Với Sailor2
không có tập lớp nào bỏ được ngoài việc bỏ cả 30. Nên các mẫu ấy bị **loại lúc chấm và tỷ lệ được
báo cáo**, đúng cách đang làm với tỷ lệ cắt ngữ cảnh.

### Ba hạn chế phải nói rõ

1. **Chưa kiểm được các lớp còn sống của Sailor2 có bị bóp méo không.** Lượt mốc `bfloat16` hết
   bộ nhớ hai lần, kể cả sau khi sửa phần giải phóng mô hình. Với Qwen, T07 kiểm được 27 lớp còn
   lại khớp `float32` tới 0,07 % thang đo; với Sailor2 không có con số tương đương. Hai bên vì
   thế đứng trên hai mức kiểm chứng khác nhau.
2. **Cột chi phí không so được giữa hai mô hình.** Sailor2 đo 566–572 ms/mẫu, Qwen đo 528, nhưng
   hai lượt chạy ở hai phiên GPU khác nhau. Mục 5 của `CLAUDE.md` ghi rõ T4 bị hạ xung 10–15 %
   sau vài phút chạy liên tục, nên chênh lệch 8 % này nằm gọn trong phần nhiễu đó. Muốn so chi
   phí thật thì phải đo xen kẽ trong cùng một phiên.
3. **Mới đo trên một bộ dữ liệu.** Kết luận "chunk-aware không chuyển giữa hai mô hình" hiện chỉ
   đứng trên ViHallu. E16 khái quát hóa chéo bộ sẽ nói thêm.

### Bảng 5b — Bậc thang kích thước mô hình đọc (E14, ViHallu)

Chạy 10/09/2026. Trích trên Kaggle: Qwen2.5-3B mất 28 phút, Qwen2.5-1.5B mất 71 phút, **0 lỗi
trên 7.000 mẫu mỗi cỡ**, 0 mẫu bị cắt ngữ cảnh, 0 mẫu có lớp tràn số. Chấm trên máy cá nhân,
cùng máy đã chấm E02, E03 và E13.

| Mô hình đọc | Tham số | Lưới | lookback gộp | chunk-aware | chênh |
|---|---|---|---|---|---|
| Qwen2.5-7B | 7,6 B | 27 × 28 | 0,7451 | **0,7567** | **+0,0116** |
| Qwen2.5-3B | 3,1 B | 36 × 16 | **0,7345** | 0,7217 | **−0,0128** |
| Qwen2.5-1.5B | 1,5 B | 28 × 12 | 0,7232 | **0,7345** | **+0,0114** |
| *Sailor2-8B (E13)* | *8,0 B* | *30 × 28* | *0,7377* | *0,7120* | *−0,0257* |

Khoảng tin cậy 95 % của mọi dòng rộng khoảng **0,065**, ví dụ 3B chunk-aware là [0,6877; 0,7544].

### Dấu đảo hai lần trong cùng một họ mô hình — đây là kết quả của E14

Đọc cột cuối theo thứ tự cỡ giảm dần: **+0,0116 → −0,0128 → +0,0114**.

Không đơn điệu, không nhất quán, và trung bình ba cỡ là **+0,0034** — nhỏ hơn hai mươi lần độ
rộng khoảng tin cậy. Ba cỡ này khác nhau **đúng một biến**: số tham số. Cùng họ, cùng dữ liệu
huấn luyện, cùng kiến trúc, cùng bộ dữ liệu chấm, cùng cách chia đoạn, cùng nhóm đặc trưng.

Nếu nhóm chunk-aware mang một đóng góp thật thì dấu của nó **không thể đảo hai lần** qua ba cỡ
của cùng một họ. Đây là bằng chứng mạnh nhất từ trước tới nay cho kết luận đã nêu ở Bảng 4:

> Đóng góp riêng của nhóm chunk-aware trên ViHallu **không phân biệt được với 0**.

Ba phép đo độc lập, ba câu hỏi khác nhau, cùng một hướng:

| Thí nghiệm | Hỏi gì | Trả lời |
|---|---|---|
| E12 (Bảng 4) | cộng thêm bao nhiêu khi đứng cạnh đặc trưng bề mặt | không phân biệt được với 0 |
| E13 (Bảng 5) | có chuyển sang họ mô hình khác không | không, đổi dấu |
| **E14 (bảng này)** | **có ổn định qua các cỡ cùng một họ không** | **không, đổi dấu hai lần** |

### Nhưng cột mốc lookback lại là tin tốt, và nó trả lời CH2

Bỏ cột chunk-aware đi, nhìn riêng cột lookback gộp:

| Mô hình đọc | Tham số | macro-F1 | Mất so với 7B | VRAM đỉnh |
|---|---|---|---|---|
| Qwen2.5-7B | 7,6 B | 0,7451 | — | 8.328 MB |
| Qwen2.5-3B | 3,1 B | 0,7345 | **−0,0106** | 3.710 MB |
| Qwen2.5-1.5B | 1,5 B | 0,7232 | **−0,0219** | 2.718 MB |

**Thu mô hình đọc 4,7 lần chỉ mất 0,022 macro-F1, và tiết kiệm 67 % VRAM.** Cả ba khoảng tin cậy
chồng lên nhau gần hết, nên nói cho chặt thì ba cỡ **không phân biệt được với nhau**.

Đây là câu trả lời trực tiếp và có lợi cho CH2. Hướng chú ý nội tại chịu được việc thu nhỏ mô
hình rất tốt: 1.5B ở 0,7232 vẫn **trên** baseline bề mặt 0,6562 và **ngang** PhoBERT-large 0,749
đã tinh chỉnh, trong khi mô hình đọc chỉ bằng 1/5 và bộ phân loại chỉ có vài nghìn tham số.

Và nó giảm **đều**: 0,7451 → 0,7345 → 0,7232, mỗi nấc mất khoảng 0,011. Cột này đơn điệu còn cột
chunk-aware thì không — chính sự tương phản đó là lập luận, chứ không phải riêng con số nào.

### Chi phí: nấc lùi mua được bộ nhớ, không mua được thời gian

Đo xen kẽ theo thứ tự 7B → 3B → 1.5B → 7B → 3B → 1.5B, **mỗi lượt một tiến trình riêng**, nạp lại
mô hình từ đầu. Cột `ms/mẫu` dưới đây là con số **có trọng số theo phân bố độ dài thật** của hai
bộ dữ liệu chính, không phải trung bình cộng các mức.

| Nấc | Kiểu số | Lượt 1 | Lượt 2 | Trôi | VRAM đỉnh | Giờ GPU cho ViHallu + ISE-DSC01 |
|---|---|---|---|---|---|---|
| Qwen2.5-7B | `float16` | 726,6 ms | 741,7 ms | **2,09 %** | 8.328 MB | 10,1 giờ |
| Qwen2.5-3B | `float16` | **369,7 ms** | **370,2 ms** | **0,13 %** | **3.710 MB** | **5,1 giờ** |
| Qwen2.5-1.5B | `bfloat16` | 1.029,3 ms | 1.029,8 ms | **0,04 %** | 2.718 MB | 14,2 giờ |

Trung vị theo từng mức độ dài, để đối chiếu:

| Nấc | 0–512 | 513–1024 | 1025–2048 | 2049–4096 |
|---|---|---|---|---|
| 7B `float16` | 404 / 416 | 741 / 756 | 1.350 / 1.375 | 2.609 / 2.585 |
| 3B `float16` | 211 / 209 | 366 / 368 | 688 / 692 | 1.402 / 1.404 |
| 1.5B `bfloat16` | 569 / 571 | 1.042 / 1.040 | 1.945 / 1.946 | 3.423 / 3.419 |

**Đo xen kẽ có tác dụng, và lần này đo được chính nó.** Hai lượt của cùng một mô hình lệch nhau
**0,04 % tới 2,09 %**, so với **10–15 %** mà T08 đo được khi chạy nối nhau trong một phiên. Cột
`ms/mẫu` của E14 vì thế so được, khác cột của E13 vốn phải mang hạn chế này.

**Con số đáng chú ý nhất của cả bảng:** Qwen2.5-1.5B ở `bfloat16` tốn **1.029 ms/mẫu**, còn
Qwen2.5-7B ở `float16` tốn **734 ms** — nấc lùi nhỏ nhất **chậm hơn 1,4 lần** mô hình lớn gấp
năm lần nó. Trong khi VRAM thì ngược hẳn: 2.718 so với 8.328 MB, tức **giảm 67 %**.

Quy ra giờ GPU cho hai bộ dữ liệu chính: 7B mất 10,1 giờ, 3B mất **5,1 giờ**, còn 1.5B mất
**14,2 giờ** — vượt cả 7B, và gần chạm nửa hạn mức 30 giờ mỗi tuần.

Nguyên nhân là T4 thuộc kiến trúc Turing, không có `bfloat16` gốc nên phải giả lập. Mà 1.5B thì
**bắt buộc** dùng `bfloat16`: ở `float16` nó tràn số trên cả 28 lớp, 20/20 mẫu.

Nên nấc lùi cuối của mục 5 `CLAUDE.md` có hình dạng như sau, và phải nói đúng như vậy khi trình
bày: **nó mua được bộ nhớ, không mua được thời gian.** Đúng hình dạng bài học đã ghi ở nấc 1 của
cùng mục ấy, nơi hạ `max_context_tokens` giảm 25 % VRAM mà lại *tăng* giờ GPU.

**Nấc đáng dùng là 3B, không phải 1.5B.** Nó nhanh gấp đôi 7B, nhẹ hơn 56 % bộ nhớ, và chỉ mất
0,0106 macro-F1. Bậc thang lùi của mục 5 `CLAUDE.md` trên phần cứng này thực chất chỉ có **một
nấc dùng được**.

### Hạ xung có xảy ra, nhưng không giải thích được thời gian

`measure_throughput.py` đọc telemetry GPU mỗi mức. Số liệu cho thấy card **có** hạ xung: tỷ lệ
xung SM tụt xuống tới **0,33** mức tối đa và nhiệt độ chạm **84 °C**, và 5 trên 6 lượt bị đánh dấu
`gpu_throttled: true`.

Nhưng hai lượt của cùng một mô hình vẫn lệch nhau **0,13 %** ở 3B — trong khi tỷ lệ xung đọc được
ở lượt 1 là 0,858 còn lượt 2 là 0,330 tại cùng mức độ dài. Chênh lệch xung **2,6 lần** cho ra
chênh lệch thời gian **0,13 %**.

Hai cách đọc, và chưa tách được:

1. Telemetry là ảnh chụp một thời điểm mỗi mức, không đại diện cho cả quãng đo.
2. Xung SM **không phải** ràng buộc quyết định với suy luận NF4 — việc giải nén trọng số 4 bit và
   băng thông bộ nhớ mới là, và cả hai không đọc được từ `sm_clock_mhz`.

Cách thứ hai khớp với `forward_share`: phần thời gian nằm trong forward là 0,92 với 7B, 0,95 với
3B, nhưng chỉ **0,86** với 1.5B ở `bfloat16` — mô hình càng nhỏ thì phần chi phí ngoài phép nhân
ma trận càng chiếm tỷ trọng lớn.

Điều dùng được ngay, bất kể cách đọc nào đúng: **hai lượt xen kẽ cho số trùng nhau trong 2 %**,
nên cột chi phí tái lập được trong phiên. Ghi cả quan sát này vào phần bàn luận thay vì lặng lẽ
báo con số trung bình.

Con số này gắn với **T4**. Trên Ampere trở lên `bfloat16` nhanh ngang `float16` và cả nghịch lý
biến mất.

### Vị trí đầu chú ý đổi cả khi chỉ đổi cỡ

`compare_heads.py` từ chối so theo chỉ số vì hai lưới khác nhau — 7B còn 27 lớp sau khi bỏ lớp
27, 3B có 36 lớp — nên chỉ báo phân bố theo độ sâu tương đối.

| k | Bên | TB độ sâu | 1/3 đầu | 1/3 giữa | 1/3 cuối |
|---|---|---|---|---|---|
| 32 | Qwen2.5-7B | 0,590 | 28,1 % | 31,2 % | 40,6 % |
| 32 | Qwen2.5-3B | 0,479 | 43,8 % | 12,5 % | 43,8 % |
| 64 | Qwen2.5-7B | 0,572 | 23,4 % | 37,5 % | 39,1 % |
| 64 | Qwen2.5-3B | **0,458** | **42,2 %** | 28,1 % | 29,7 % |

Ở k = 64, 7B dồn về nửa sau (độ sâu trung bình 0,572) còn 3B dồn về nửa trước (0,458). Khoảng
cách **0,114** này **lớn hơn** khoảng cách giữa Qwen2.5-7B và Sailor2-8B ở E13 (0,572 so với
0,517, tức 0,055) — dù Sailor2 là mô hình **khác họ huấn luyện** còn 3B thì cùng họ.

Nghĩa là **vị trí các đầu mang tín hiệu không phải thuộc tính bền của kiến trúc**. Nó đổi khi
đổi cỡ, và đổi nhiều hơn cả khi đổi dữ liệu huấn luyện.

Và đây chính là **lời giải thích cơ chế** cho cột chênh đảo dấu ở trên. Năm đại lượng hình dạng
đọc phân bố chú ý *từ các đầu cụ thể*. Nếu các đầu ấy nằm ở độ sâu khác nhau tùy cỡ mô hình, thì
hình dạng phân bố mà chúng cho ra không có lý do gì để cư xử giống nhau giữa các cỡ. Tỷ lệ gộp
thì trái lại — nó cộng dồn toàn bộ ngữ cảnh nên không phụ thuộc đầu nào nằm ở đâu, và đó là lý do
cột mốc giảm đều trong khi cột chunk-aware nhảy lung tung.

### Bảng 6 — Đối chứng ngoài trên ViWikiFC (E15)

Chạy 10/09/2026. Trích 20.919 mẫu trên Kaggle trong 138 phút, **0 lỗi, 0 tràn số**, 395 ms/mẫu.
Chấm trên máy cá nhân, tập test **gốc** 2.091 mẫu.

| Phương pháp | Nguồn | Đầu vào | Strict Acc | VC Acc | ER Acc | macro-F1 |
|---|---|---|---|---|---|---|
| InfoXLM large | Bài gốc ViWikiFC | **bằng chứng vàng** | — | — | — | 86,51 |
| BM25 + InfoXLM large | Bài gốc ViWikiFC | câu BM25 xếp hạng 1 | 67,00 | — | — | — |
| SemViQA | Bài SemViQA | câu do hệ tự truy xuất | 80,82 | 83,88 | 95,31 | — |
| **Lookback gộp, Qwen2.5-7B** | nhóm | **toàn bộ `context`** | — | 70,73 | — | **70,66** [68,72–72,55] |
| **Chunk-aware, Qwen2.5-7B** | nhóm | **toàn bộ `context`** | — | 70,59 | — | **70,54** [68,57–72,48] |

Cột "VC Acc" của hai dòng nhóm là accuracy phân loại nhãn — thứ gần nhất với cách SemViQA định
nghĩa VC Acc. Hai dòng nhóm không có Strict Acc và ER Acc vì phương pháp **không truy xuất
bằng chứng**: mô hình đọc cả ngữ cảnh rồi phân loại, không chỉ ra câu nào.

### Cột "đầu vào" mới là cột quyết định cách đọc bảng này

Bốn dòng trên nhận **bốn thứ khác nhau**, và đó là lý do không đặt con số nào cạnh con số nào
mà không nói rõ.

InfoXLM ở dòng đầu được đưa **đúng câu bằng chứng vàng** rồi mới phân loại. Đó là bài toán dễ
hơn hẳn bài toán mà hai dòng nhóm giải — đọc cả ngữ cảnh ba tới năm câu, tự tìm chỗ cần nhìn, rồi
phân loại — nên 86,51 **không phải mốc để vượt**, nó là trần của một bài toán khác.

Mốc so được nhất là **SemViQA VC Acc 83,88**: verdict accuracy của một hệ đầu cuối tự truy xuất
rồi phân loại. Hai dòng nhóm đạt **70,73** và **70,59**. Khoảng cách **13 điểm**, và phải viết
đúng như vậy.

### Ba điều bảng này nói, kể cả phần bất lợi

**1. Trên benchmark đã công bố, hướng nội tại thua bộ mã hóa tinh chỉnh 13 điểm.** Không có cách
đọc nào làm khoảng cách đó biến mất. Nhưng có ba thứ làm nó **nhỏ hơn con số trần trụi**, và cả
ba đều đo được chứ không phải chống chế:

- **Tập test dùng lại 100 % ngữ cảnh của train**, đo ở T14. Một bộ mã hóa 560 triệu tham số tinh
  chỉnh trọn vẹn **nhớ được** 1.481 ngữ cảnh; một hồi quy logistic 2.271 tham số trên đặc trưng
  chú ý thì không. Rò rỉ vì thế nâng số của bên kia lên nhiều hơn nâng số của nhóm. Đây là lập
  luận về **hướng** của sai lệch, không đo được độ lớn.
- **Chỉ 67 % nhãn NEI thật sự là ngoại lai**, kappa 0,505, đo ở T13. Lớp `extrinsic` của nhóm
  đạt 0,6962 dù một phần ba nhãn của nó lẫn sang loại khác.
- **2.271 tham số so với 560 triệu**, không tinh chỉnh gì, chạy trên CPU. Đúng trục mà Bảng 8 đã
  chỉ ra là trục duy nhất hướng nội tại thắng.

**2. Chunk-aware bằng lookback gộp, lần thứ tư, và lần này đo chặt nhất.** Chênh **−0,0012** trên
**2.091** mẫu test — gấp ba lần cỡ test của ViHallu — nên khoảng tin cậy hẹp lại còn 0,038 và hai
khoảng chồng gần khít. Bộ này còn thiên vị chunk-aware nhẹ vì chỉ 5,9 % mẫu có một đoạn. Bốn phép
đo độc lập, bốn bộ hoặc mô hình khác nhau, cùng một câu trả lời:

| Phép đo | Khác biệt so với E03 | Chunk-aware − lookback |
|---|---|---|
| E03, ViHallu, 7B | — | +0,0116 |
| E12, ViHallu, có bề mặt | thêm đặc trưng bề mặt | −0,0071 |
| E13, ViHallu, Sailor2 | đổi họ mô hình | −0,0257 |
| E14, ViHallu, 3B / 1.5B | đổi cỡ | −0,0128 / +0,0114 |
| **E15, ViWikiFC, 7B** | **đổi bộ dữ liệu, split gốc** | **−0,0012** |

**3. Hiệu chỉnh xác suất vẫn tốt ở bộ mới.** ECE 0,0503 và 0,0617 — cùng cỡ với 0,044 của E03
và tốt hơn hẳn 0,097 của XLM-R ở Bảng 1. Đây là tính chất đi theo phương pháp qua các bộ, không
phải may ở một bộ.

### Cùng một đầu chú ý dẫn đầu trên cả ba bộ dữ liệu

Với **cùng** mô hình Qwen2.5-7B, đầu mạnh nhất theo trọng số của bộ phân loại lookback:

| Bộ dữ liệu | #1 | #2 | #3 |
|---|---|---|---|
| ViHallu (E02) | `l5_h7` | **`l17_h4`** | `l24_h3` |
| ISE-DSC01 (E07) | **`l17_h4`** | `l18_h0` | `l5_h7` |
| ViWikiFC (E15) | **`l17_h4`** | `l15_h5` | `l16_h2` |

`l17_h4` nằm trong top-2 ở **cả ba** bộ; `l5_h7` ở top-3 của hai bộ. Ba bộ này khác nhau về
miền, độ dài, cách gán nhãn và cả bài toán gốc — vậy mà cùng những đầu ấy mang tín hiệu.

Ghép với E13 và E14, nơi **đổi mô hình** thì đầu dời chỗ hẳn (độ sâu trung bình 0,572 → 0,517 →
0,458), mệnh đề trở nên sạch:

> **Vị trí các đầu mang tín hiệu lookback là thuộc tính của mô hình đọc, không phải của bộ dữ
> liệu.** Đổi bộ thì chúng đứng yên; đổi mô hình thì chúng dời chỗ.

Đây là kết quả dùng được ngay cho T34 / E16: nếu đầu không đổi giữa các bộ thì bộ phân loại huấn
luyện trên bộ này có cơ sở để chuyển sang bộ kia — và E16 đo chính điều đó.


### Bảng 7 — Khái quát hóa chéo bộ (E16)

Chạy 11/09/2026 trên máy cá nhân, **0 giây GPU** — đọc lại shard `8c49fc0417f1` (ViHallu) và
`15ef31521fd6` (ISE-DSC01), cùng Qwen2.5-7B, cùng lưới 27 × 28. Cách gộp đầu chọn trên **dev của
bộ nguồn**; bộ đích chỉ được đụng tới một lần, để chấm. Cùng một mô hình đã khớp chấm trên cả hai
tập test, nên điểm trên test nguồn là phép kiểm tái lập tích hợp: **cả bốn lượt trùng E02, E03,
E07 từng chữ số.**

| Huấn luyện trên | Đánh giá trên | Nhóm | macro-F1 chéo bộ [KTC 95 %] | Đích tự chấm | Sụt | Nhị phân chéo | ECE |
|---|---|---|---|---|---|---|---|
| ViHallu | ISE-DSC01 | lookback gộp | **0,4301** [0,4146–0,4456] | 0,7851 | **−0,3550** | 0,6309 | 0,372 |
| ViHallu | ISE-DSC01 | chunk-aware | **0,3584** [0,3450–0,3719] | 0,7919 | **−0,4334** | 0,6640 | 0,354 |
| ISE-DSC01 | ViHallu | lookback gộp | **0,5540** [0,5179–0,5913] | 0,7451 | **−0,1911** | 0,7838 | 0,291 |
| ISE-DSC01 | ViHallu | chunk-aware | **0,5521** [0,5160–0,5897] | 0,7567 | **−0,2047** | 0,7756 | 0,297 |

Cột "Đích tự chấm" là điểm khi huấn luyện *và* chấm trên chính bộ đích (E02/E03 cho ViHallu,
E07 cho ISE-DSC01). Cột "Sụt" so với cột đó — đó mới là giá của việc đổi phân phối. Mức ngẫu
nhiên của macro-F1 ba lớp là khoảng 0,33.

### Tín hiệu không khái quát hóa được thành bộ phát hiện ba lớp — câu trả lời cho nửa sau CH3

Hai chiều đều sụt nặng, và sụt **bất đối xứng**. Huấn luyện trên ViHallu rồi chấm ISE-DSC01 rơi
về **gần mức ngẫu nhiên** (0,36–0,43). Chiều ngược lại giữ được 0,55 — tốt hơn, nhưng vẫn **dưới
cả baseline bề mặt E01** của ViHallu (0,6562). Bộ lớn hơn, ngữ cảnh dài hơn, đa dạng hơn thì
chuyển đi tốt hơn; nhưng không chiều nào chuyển được tới mức dùng.

Hiệu chỉnh xác suất **sụp hoàn toàn**: ECE 0,29–0,37 khi chéo bộ, so với 0,03–0,11 khi cùng bộ.
Mô hình chéo bộ không chỉ đoán sai mà **tự tin khi đoán sai** — với bài toán mà người dùng cần
biết mức tin cậy, đó là kiểu hỏng tệ nhất.

### Mỗi chiều mất đúng một lớp, và đó là lớp hai bộ định nghĩa khác nhau

Ma trận nhầm lẫn giải thích được toàn bộ con số, và cách giải thích này quan trọng hơn con số.

| Chiều | Lớp gần như biến mất | Mô hình đoán lớp đó | Thật sự có | Dồn đi đâu |
|---|---|---|---|---|
| ViHallu → ISE-DSC01, chunk-aware | **`extrinsic`** | 82 / 3.646 | 1.286 | 988 vào `intrinsic` |
| ISE-DSC01 → ViHallu, chunk-aware | **`intrinsic`** | 72 / 700 | 234 | 136 vào `extrinsic` |

Lớp `no` chuyển được ở cả hai chiều: 62 % và 82 % đúng. Hai lớp ảo giác thì mỗi chiều mất một.

Lý do nằm ở **định nghĩa nhãn**, không nằm ở đặc trưng. `extrinsic` của ViHallu là phản hồi do
GPT-4o **bịa** thêm nội dung ngữ cảnh không có; `extrinsic` của ISE-DSC01 là nhãn NEI — một câu
khẳng định **do người viết** mà ngữ cảnh không xác nhận cũng không bác bỏ. Hai thứ ấy để lại hai
dấu vết chú ý khác nhau: mô hình "bịa" thì không nhìn vào ngữ cảnh, còn một câu NEI của người thì
mô hình vẫn nhìn, chỉ không tìm thấy. T13 đã đo được chuyện này từ phía nhãn — chỉ 67 % NEI của
ViWikiFC thật sự là ngoại lai — và E16 đo được nó từ phía đặc trưng.

`intrinsic` cũng vậy theo chiều ngược: REFUTED của ISE-DSC01 là câu bị bằng chứng bác thẳng, còn
`intrinsic` của ViHallu là LLM đọc ngữ cảnh rồi nói lệch. Cùng tên lớp, khác cơ chế.

### Cái chuyển được là "trung thực hay không", cái không chuyển được là "ảo giác kiểu nào"

Cột nhị phân nói rõ điều này. Gộp hai lớp ảo giác làm một thì điểm chéo bộ lên **0,78** ở chiều
ISE-DSC01 → ViHallu và **0,63–0,66** ở chiều ngược — cao hơn hẳn ba lớp và **trên** mức ngẫu
nhiên nhị phân 0,50 ở cả bốn dòng.

Đây là cùng một phát hiện với Bảng 1, nơi mọi phương pháp đều được thêm 0,10–0,16 khi bỏ đòi
hỏi gọi đúng tên loại: **phần khó — và phần không chuyển được — nằm ở ranh giới nội tại–ngoại
lai.** Tín hiệu "mô hình có bám vào ngữ cảnh không" là thuộc tính của mô hình đọc và chuyển
được giữa các bộ; tín hiệu "nó bám sai kiểu nào" thì gắn với cách từng bộ định nghĩa "sai".

### Chunk-aware chuyển kém hơn lookback gộp, lần thứ năm

| Chiều | lookback gộp | chunk-aware | chênh |
|---|---|---|---|
| ViHallu → ISE-DSC01 | 0,4301 | 0,3584 | **−0,0717** |
| ISE-DSC01 → ViHallu | 0,5540 | 0,5521 | −0,0019 |

Ở chiều khó, năm đại lượng hình dạng **kéo điểm xuống 0,07** — chúng học hình dạng phân bố trên
5,3 đoạn rồi gặp 24,5 đoạn. Ở chiều dễ thì ngang nhau. Đây là phép đo thứ năm về đóng góp của
chunk-aware, độc lập với bốn phép trước, và là phép duy nhất cho **dấu âm rõ ràng ngoài nhiễu**:
0,0717 lớn hơn hai lần độ rộng khoảng tin cậy 0,031 của dòng đó.

Ghép với E13 (chunk-aware không chuyển giữa hai họ mô hình) và E14 (đảo dấu qua ba cỡ): hình
dạng phân bố chú ý **gắn với cả mô hình lẫn bộ dữ liệu**, còn tỷ lệ gộp thì bền hơn với cả hai.

### Điều bảng này KHÔNG nói

Nó không nói tín hiệu chú ý vô dụng ngoài phân phối huấn luyện — cột nhị phân bác điều đó. Nó nói
**bộ phân loại ba lớp huấn luyện trên một bộ không dùng được trên bộ khác**, vì ba lớp ấy không
cùng nghĩa giữa hai bộ. Muốn một bộ phát hiện dùng chung thì hoặc huấn luyện gộp trên nhiều bộ,
hoặc chấp nhận bài toán nhị phân. Cả hai đều là hướng phát triển cho chương 8, không phải việc
của đề tài này.


### Bảng 8 — Đánh đổi độ chính xác và chi phí (E11, ViHallu)

Dựng ngày 10/09/2026 bằng `scripts/build_tradeoff.py`, đọc `results/runs.jsonl` cho độ chính xác
và `results/feasibility.jsonl` cho chi phí lượt đọc. Bản máy đọc được ở `results/tradeoff.csv`.

| Phương pháp | macro-F1 [KTC 95 %] | ms/mẫu | VRAM đỉnh | Tham số huấn luyện | Loại chi phí |
|---|---|---|---|---|---|
| Baseline bề mặt (E01) | 0,6562 [0,6200–0,6891] | **0,001** | — | **9** | chỉ CPU |
| Gemini giám khảo (E10) | 0,6637 [0,6070–0,7191] | 8.194,0 | — | 0 | API ngoài |
| PhoBERT-large tinh chỉnh (E09) | 0,7487 [0,7137–0,7776] | 12,3 | 9.002 MB | 369.166.339 | GPU, bộ mã hóa |
| XLM-R-large tinh chỉnh (E09) | **0,7762** [0,7570–0,8184] | 25,2 | 11.231 MB | 559.893.507 | GPU, bộ mã hóa |
| Lookback gộp, Qwen2.5-7B (E02) | 0,7451 [0,7111–0,7762] | 437,6 | 8.328 MB | 2.271 | GPU, lượt đọc |
| Chunk-aware, Qwen2.5-7B (E03) | 0,7567 [0,7242–0,7885] | 437,6 | 8.328 MB | 579 | GPU, lượt đọc |
| **Lookback gộp, Qwen2.5-3B (E14)** | 0,7345 [0,6994–0,7671] | **222,7** | **3.710 MB** | **195** | GPU, lượt đọc |
| Chunk-aware, Qwen2.5-3B (E14) | 0,7217 [0,6877–0,7544] | 222,7 | 3.710 MB | 1.851 | GPU, lượt đọc |
| Lookback gộp, Qwen2.5-1.5B (E14) | 0,7232 [0,6895–0,7558] | 608,1 | 2.718 MB | 1.011 | GPU, lượt đọc |
| Chunk-aware, Qwen2.5-1.5B (E14) | 0,7345 [0,6999–0,7661] | 608,1 | 2.718 MB | 1.131 | GPU, lượt đọc |
| Lookback gộp, Sailor2-8B (E13) | 0,7377 [0,7051–0,7695] | *chưa đo* | *chưa đo* | 195 | GPU, lượt đọc |
| Chunk-aware, Sailor2-8B (E13) | 0,7120 [0,6780–0,7452] | *chưa đo* | *chưa đo* | 1.155 | GPU, lượt đọc |

Cột `ms/mẫu` của các dòng lượt đọc quy về **phân bố độ dài thật của ViHallu**, không phải trung
bình mọi bộ — ViHallu ngắn, 6.461 trên 7.000 mẫu nằm ở mức dưới 512 token, nên con số gộp mọi bộ
sẽ thổi bảng này lên khoảng 70 %.

### Ba loại chi phí, và bảng không được cộng chúng lại

Một con số `ms/mẫu` duy nhất che mất điều mà người triển khai cần biết nhất: **thứ gì chặn họ**.

| Loại | Chặn ở đâu | Dòng nào |
|---|---|---|
| chỉ CPU | không chặn gì | E01 |
| GPU, bộ mã hóa | phải có GPU **và** phải tinh chỉnh được — E09 cho thấy InfoXLM không tinh chỉnh nổi | PhoBERT, XLM-R |
| GPU, lượt đọc | phải có GPU, nhưng **không tinh chỉnh gì** | mọi dòng attention |
| API ngoài | phải có khóa, có hạn mức, có mạng, và dữ liệu rời khỏi máy | E10 |

Cột cuối là loại chi phí **khác hẳn về bản chất**: 8.194 ms của Gemini gần như toàn bộ là độ trễ
mạng, và nó đi kèm một ràng buộc mà không dòng nào khác có — dữ liệu người dùng phải gửi ra ngoài.

### Điều bảng này nói thẳng, kể cả phần bất lợi

**XLM-R thắng cả hai trục tuyệt đối.** 0,7762 ở 25,2 ms, so với 0,7567 ở 437,6 ms của dòng
chunk-aware tốt nhất. Cao hơn **0,0195** điểm và nhanh hơn **17 lần**. Nói cho chặt thì hai khoảng
tin cậy chồng nhau nên chưa kết luận được XLM-R *hơn hẳn*, nhưng không có cách đọc nào biến bảng
này thành "hướng nội tại rẻ hơn về thời gian tuyệt đối". Phải viết đúng như vậy.

**Chỗ hướng nội tại thắng là số tham số phải huấn luyện, và biên độ thì rất lớn.** Dòng
`Lookback gộp, Qwen2.5-3B` đạt **0,7345 với 195 tham số** — so với **559.893.507** của XLM-R. Ít
hơn **2,87 triệu lần**, mất 0,0417 điểm. Và 195 tham số thì huấn luyện trên CPU trong vài giây,
không có rủi ro không hội tụ như InfoXLM ở E09.

**Nấc 3B là điểm cân bằng của cả bảng.** Nhanh gấp đôi 7B, nhẹ hơn 56 % bộ nhớ, chỉ mất 0,0106
điểm, và cần đúng 195 tham số. Mọi dòng khác đều thua nó ở ít nhất một trục quan trọng.

**Nấc 1.5B không có lý do tồn tại trên T4.** Chậm hơn 7B (608 so với 438 ms) trong khi kém chính
xác hơn, chỉ được mỗi VRAM. Lý do ở mục Bảng 5b: nó buộc phải chạy `bfloat16`, mà T4 không có
bf16 gốc.

### Cột chi phí biên là lập luận, không phải phép đo

Lập luận trung tâm của đề tài về chi phí là: trong một hệ RAG thật, lượt đọc **dù sao cũng phải
chạy** để sinh câu trả lời, nên chi phí **biên** của việc thêm phát hiện ảo giác chỉ là phần cộng
dồn trong hook và một hồi quy logistic.

| Phương pháp | tuyệt đối | biên |
|---|---|---|
| Lookback gộp, Qwen2.5-7B | 437,6 ms | **0,010 ms** |
| Chunk-aware, Qwen2.5-7B | 437,6 ms | **0,003 ms** |
| Lookback gộp, Qwen2.5-3B | 222,7 ms | **0,002 ms** |
| Chunk-aware, Qwen2.5-3B | 222,7 ms | **0,008 ms** |

Nếu cột biên là cột đúng để đọc thì hướng nội tại rẻ hơn XLM-R khoảng **hai nghìn lần**, và toàn
bộ kết luận ở trên đảo chiều.

**Nhưng không thí nghiệm nào trong đề tài đo được cột đó.** Nó đòi một hệ RAG đầu cuối chạy thật,
và T40 mới dựng cái đó. Cột biên vì thế là **giả thiết đã lượng hóa**, không phải kết quả đo, và
phải trình bày đúng như vậy — hai cột riêng, có nhãn, không gộp.

Ba điều khiến cột biên đáng tin ở mức giả thiết, ghi để người đọc tự cân:

1. Bộ phân loại thật sự chỉ có 195–2.271 tham số, đo được, chạy trên CPU.
2. Hook cộng dồn ngay trong lớp và giải phóng tensor, nên không thêm lượt forward nào.
3. `forward_share` đo ở T31 cho thấy **86–95 %** thời gian một mẫu nằm trong forward của mô hình
   đọc — phần còn lại mới là chi phí của phương pháp.

Điều nó **chưa** tính: bật `output_attentions` vô hiệu hóa FlashAttention, nên một hệ RAG dùng
FlashAttention sẽ phải trả thêm để lấy được ma trận chú ý. Đó là chi phí biên thật và chưa ai đo.

**Và một điều khoản phần cứng, đo được ở T40 (11/09/2026).** Lập luận "lượt đọc dù sao cũng
trả" giả định hệ RAG sinh câu trả lời **bằng chính mô hình đọc**. Trên T4 ở `float16` — cấu hình
đã chốt cho bộ phát hiện — mô hình ấy **không sinh được**: lớp 27 tràn số (T07), bộ phát hiện né
bằng cách không đọc lớp đó, nhưng dòng dư vẫn đi qua lớp 27 vào LM head, logit thành NaN và
`argmax` trả về token 0 = `!`. Cả bốn câu trả lời của demo ra `![](…!-!-`. Sinh được thì phải
`bfloat16`, tức **một mô hình thứ hai**: nạp thêm bản 7B `bfloat16` thì hết bộ nhớ ngay lúc nạp
(bộ đọc giữ 5,5 GB, nạp 7B cần đỉnh tạm 8–9 GB, tổng 14,3/14,56 GiB), nên demo dùng Qwen2.5-3B
`bfloat16` — cỡ lớn nhất còn vừa. Chi phí biên "gần 0" vì thế chỉ đúng trên phần cứng có
`bfloat16` gốc và đủ bộ nhớ (Ampere trở lên), nơi một bản 7B duy nhất vừa đọc vừa viết. Trên T4
thì bộ sinh và bộ đọc là hai mô hình, và lượt đọc của bộ phát hiện là chi phí thêm thật. Phải
viết kèm khi trình bày Bảng 8.

### Hai ô của Bảng 1 sai, và bảng này chứng minh điều đó

Bảng 1 ghi E02 tốn **464 ms** và E03 tốn **528 ms**. Hai con số ấy không thể cùng đúng: E02 và E03
đọc **chung một shard** `8c49fc0417f1`, cùng một `extraction_hash`, tức **cùng một lượt chạy mô
hình đọc**. Một lượt trích không thể có hai giá đồng thời.

Chênh lệch 64 ms là nhiễu giữa hai phép đo ở hai thời điểm, bị đọc nhầm thành "chunk-aware đắt hơn
lookback". Lượt đo xen kẽ của T31 cho **437,6 ms** cho cả hai, với độ trôi giữa hai lượt là
**2,09 %**. Đã sửa hai ô đó ở Bảng 1.

Bài học chung: **hai dòng dùng chung một `extraction_hash` phải dùng chung một ô chi phí.** Đây là
lý do bảng này sinh bằng script — `scripts/build_tradeoff.py` lấy chi phí từ mô hình đọc chứ không
từ dòng kết quả, nên không viết lại được kiểu sai ấy. `tests/test_tradeoff.py` khóa hành vi đó lại
bằng một ca kiểm riêng.

### Bảng 9 — Phân tích sai sót (T35, E03 trên ViHallu)

Khớp lại đúng mô hình E03 (`topk_heads k=32`, 192 chiều) và đối chiếu với `y_pred` đã lưu ở
T22: **700/700 trùng**. Tập test 700 mẫu, sai **169** (24,1 %). Lấy 100 mẫu sai theo tỷ lệ cặp
nhầm, seed 42, ghi `results/error_analysis.csv` kèm cột `ghi_chu_tay` cho lượt đọc tay. Biểu đồ
`results/error_analysis.png`.

#### Cặp nhầm — toàn bộ 169 mẫu sai

| Cặp (thật → đoán) | Số mẫu | % số mẫu của lớp thật |
|---|---|---|
| `intrinsic` → `extrinsic` | **46** | 19,7 % |
| `extrinsic` → `intrinsic` | **36** | 15,9 % |
| `intrinsic` → `no` | 33 | 14,1 % |
| `no` → `intrinsic` | 27 | 11,2 % |
| `extrinsic` → `no` | 16 | 7,1 % |
| `no` → `extrinsic` | 11 | 4,6 % |

**82 trên 169 lỗi (48,5 %) là nhầm giữa hai loại ảo giác với nhau.** Chỉ 27 lỗi (16 %) là bỏ sót
ảo giác thành `no`. Đây là cùng một ranh giới mà Bảng 1 (cột nhị phân), Bảng 4 và Bảng 7 đều chỉ
vào: bộ phát hiện *thấy* ảo giác tốt hơn hẳn *gọi tên* nó.

#### Nhãn cấu trúc — tự động, mỗi mẫu có thể mang nhiều nhãn

| Nhãn | Có mặt / 169 | Nghĩa |
|---|---|---|
| `tu_tin_sai` | 55 | sai mà xác suất lớp đoán ≥ 0,70 |
| `phan_van` | 34 | hai lớp cao nhất cách nhau < 0,10 |
| `chep_lai_ma_sai` | **23** | phản hồi chép ≥ 80 % từ vựng ngữ cảnh mà vẫn bị gán ảo giác |
| `prompt_noisy` | 5 | prompt bị bỏ dấu |
| `mot_doan` | 0 | ngữ cảnh một đoạn — không xảy ra ở ViHallu |
| `dien_dat_lai` | 0 | trung thực mà diễn đạt khác hẳn — không xảy ra |
| `phan_hoi_ngan` | 0 | phản hồi dưới 8 từ — không xảy ra |
| `khac` | 69 | không rơi vào mẫu nào |

Hai nhãn bằng 0 tự chúng là kết quả: phản hồi GPT-4o trong ViHallu **luôn dài và luôn chép nhiều
từ ngữ cảnh**, kể cả khi trung thực. Nên "diễn đạt lại" không phải nguồn lỗi, và 41 % lỗi (`khac`)
không có lý do cấu trúc nào — mô hình sai ở vùng xác suất giữa, với đầu vào trông bình thường.

#### Đọc tay 8 mẫu — năm hình dạng lỗi

Tám mẫu đọc trong lượt này là **đọc thăm dò để đặt tên hình dạng**, không phải lượt gán nhãn
100 mẫu; lượt ấy là việc hai tác giả làm bằng cột `ghi_chu_tay`. Các mẫu nêu dưới đây tra được
theo `sample_id` trong CSV.

**1. Ảo giác một mệnh đề trong phản hồi chép lại** — nhóm `chep_lai_ma_sai`, 23 mẫu, mô hình
tự tin 0,90–0,97 rằng đó là `no`. Phản hồi chép gần nguyên văn ngữ cảnh rồi **thêm đúng một mệnh
đề**: "…nhưng không đóng vai trò là trung tâm hành chính của Constantinople" — ngữ cảnh không nói
thế. Đặc trưng của đề tài lấy trung bình trên toàn bộ token phản hồi, nên một mệnh đề bịa nằm
giữa ba câu chép lại bị **trung bình hóa mất**. Đây là hạn chế cấu trúc của cách tính, không phải
của bộ phân loại, và nó chỉ thẳng vào hướng phát triển: chấm theo **đoạn của phản hồi** thay vì
theo cả phản hồi.

**2. Phản hồi trộn hai loại ảo giác dưới một nhãn** — phần lớn 82 lỗi `intrinsic` ↔ `extrinsic`.
Mẫu The Immortal World Tour: "khoảng 1 triệu đô mỗi buổi" bóp méo con số 57 triệu của ngữ cảnh
(nội tại) **và** "nhận nhiều lời khen từ giới phê bình" là bịa hoàn toàn (ngoại lai). Nhãn chỉ
cho một loại; mô hình chọn loại kia với 0,84. Sơ đồ ba lớp **ép một nhãn lên một phản hồi có
hai lỗi**, và phần "nhầm" ở đây một phần là của sơ đồ nhãn.

**3. Phủ định lật ngược bằng chính từ ngữ của ngữ cảnh** — mẫu Đế quốc La Mã Thần thánh: ngữ cảnh
"không phải là một quốc gia liên bang", phản hồi "thực chất là một quốc gia liên bang". Trùng lặp
từ vựng 0,50, mô hình đọc đúng đoạn — nhưng phân bố chú ý *giống nhau* dù khẳng định hay phủ định.
Chú ý cho biết mô hình **nhìn vào đâu**, không cho biết nó **nói gì về chỗ đó**. Đây là giới hạn
bản chất của tín hiệu, không sửa được bằng đặc trưng hình dạng.

**4. Câu hỏi có tiền đề sai** — 13 trên 700 câu hỏi test mang nguyên tiền tố **"Adversarial
Question:"** — prompt sinh dữ liệu lọt vào câu hỏi. Tỷ lệ sai của nhóm này **38,5 %** so với
23,9 %, nhưng n = 13 nên chỉ là quan sát. Mẫu "kim tự tháp trên sao Hỏa": câu hỏi giả định điều
sai, phản hồi chấp nhận tiền đề rồi bịa tiếp (cung điện, khu vườn). Nhãn `intrinsic`, mô hình
`extrinsic` — và cách gọi của mô hình **bảo vệ được**. Ghi lại như một điểm chất lượng dữ liệu:
`meta.prompt_type` không bắt được loại này.

**5. Nhãn có thể tranh cãi** — mẫu tinh tinh: phản hồi "5 triệu năm", ngữ cảnh "6,5 triệu năm",
nhãn `no`. Mô hình đoán `intrinsic` với biên 0,08. Trong 8 mẫu đọc có 2–3 mẫu thuộc dạng này;
**không suy ra tỷ lệ** từ 8, nhưng đủ để lượt đọc 100 mẫu phải có một cột riêng cho "nhãn đúng
hay mô hình đúng".

#### Điều rút ra cho chương 7

Ba trong năm hình dạng — trộn hai loại, phủ định lật ngược, một mệnh đề bịa giữa phần chép — đều
là **giới hạn của việc chấm cả phản hồi bằng một véc-tơ chú ý trung bình**, không phải lỗi huấn
luyện. Chúng chỉ cùng một hướng: chấm theo đoạn phản hồi, và tách "nhìn vào đâu" khỏi "nói gì".
Hai hình dạng còn lại là chất lượng nhãn và chất lượng câu hỏi của bộ dữ liệu.

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
