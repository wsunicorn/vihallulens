# Câu hỏi hội đồng dễ hỏi — kèm hướng trả lời

Soạn 22/10/2026 cho buổi phản biện (tuần 17) và bảo vệ (tuần 18). Mỗi câu trả lời là **ý chính
để nói trong khoảng 30–60 giây**, không phải văn để đọc thuộc. Số liệu lấy từ quyển v4 và
`docs/EXPERIMENTS.md`; số nào trên slide thì ghi số slide trong ngoặc vuông, ví dụ [14].

Nguyên tắc chung khi trả lời:

- **Nói kết luận trước, số sau.** Ví dụ "ngang, không hơn — vì khoảng tin cậy chồng nhau".
- **Kết quả bất lợi thì nói thẳng**, rồi nói nhóm đã đo gì để biết vì sao. Hội đồng đánh giá
  cao việc tự thấy giới hạn hơn là một con số đẹp.
- Không biết thì nói không biết, và nói sẽ kiểm tra bằng cách nào.

Các câu đánh dấu **⏳** phụ thuộc thí nghiệm đang chờ chạy (E17, E18, E19). Phải cập nhật sau
khi có số.

---

## A. Đóng góp và kết quả

### A1. Giả thuyết chính về chunk-aware không được ủng hộ. Vậy đóng góp của đề tài là gì?

- Nói thẳng: H2 **không được ủng hộ**. Chunk-aware hơn lookback gộp 0,0116 (0,757 so với 0,745),
  nằm trong khoảng tin cậy, và đổi dấu khi đổi mô hình đọc [17, 20].
- Đóng góp nằm ở ba chỗ khác:
  1. **Tái lập Lookback Lens cho tiếng Việt, bài toán ba lớp.** Một bộ phân loại tuyến tính
     2.271 tham số đạt 0,745, ngang PhoBERT tinh chỉnh (0,749) [14].
  2. **Kiểm chứng trực tiếp cơ chế.** Đầu chú ý mạnh nhất nhìn đúng đoạn chứa bằng chứng ở
     87,8 % số mẫu, giữa trung bình 22,6 đoạn [15]. Thí nghiệm can thiệp có hướng ghi trước khi
     chạy [16].
  3. **Một phát hiện có giá trị**: mô hình *nhìn đúng chỗ* nhưng điều đó *không giúp gọi đúng
     loại lỗi*. Nhóm đo được lý do: 99,9 % tín hiệu hình dạng đã có sẵn trong tỷ lệ gộp.
- Một công trình độc lập năm 2025 (Multi-View Attention, arXiv:2504.04335) đi tới cùng kết luận
  bằng con đường khác: Lookback Lens gộp cả phản hồi gần như sập ở mức đoạn.

### A2. Đội đứng đầu cuộc thi ViHallu đạt 84,80 %, nhóm chỉ đạt 0,757?

Hai con số không đặt cạnh nhau được, vì ba lẽ:

1. **Khác tập đánh giá.** Bản công khai chỉ có 7.000 mẫu train có nhãn, nhóm tự chia 80/10/10
   theo ngữ cảnh. Tập kiểm tra riêng của cuộc thi không phát hành nhãn. Ví dụ cho thấy hai thang
   khác nhau: baseline của ban tổ chức là 32,83 %, còn XLM-R trên tập của nhóm đạt 0,776.
2. **Khác chế độ.** Các đội dẫn đầu dùng LLM tinh chỉnh theo chỉ dẫn, prompt có cấu trúc và
   ensemble. Đề tài cố tình không tinh chỉnh: một lượt đọc, 579 tham số.
3. **Khác câu hỏi.** Đề tài không thi đấu trên bảng xếp hạng; nó đo tín hiệu chú ý nội tại mang
   được bao nhiêu thông tin về ảo giác tiếng Việt.

Câu chốt: *"Nói 'thua 9 điểm' là sai, mà nói 'gần ngang top' cũng sai."*

### A3. XLM-R vừa chính xác hơn vừa nhanh hơn 17 lần. Hướng của nhóm có ích gì?

- Thừa nhận: XLM-R thắng cả hai trục tuyệt đối, 0,776 ở 25,2 ms so với 0,757 ở 437,6 ms [18].
- Hướng chú ý thắng ở **số tham số phải huấn luyện**: 195 (nấc 3B, 0,7345) so với khoảng 560
  triệu, ít hơn khoảng 2,87 triệu lần. Bộ phân loại huấn luyện trên CPU trong vài giây, không có
  rủi ro không hội tụ. Ở E09, InfoXLM không tinh chỉnh nổi, và XLM-R có 1/3 seed không học.
- **Hiệu chỉnh xác suất tốt hơn**: ECE 0,044 so với 0,097 của XLM-R. Người dùng cần biết *mức độ
  tin* chứ không chỉ nhãn.
- Về chi phí biên trong một hệ RAG thật (lượt đọc dù sao cũng phải chạy), nói rõ đó là **lập
  luận, chưa đo**. Trên T4 thì bộ sinh và bộ đọc là hai mô hình, nên chi phí biên chưa gần 0
  (xem D2).

### A4. ⏳ Trọng số chú ý có phải là lời giải thích không? ContextCite nói là không đáng tin.

- Đề tài **không dùng chú ý làm lời giải thích cho người dùng**. Nó dùng chú ý làm **đặc trưng**
  cho bộ phân loại, và đã kiểm riêng xem đặc trưng đó có trùng vị trí bằng chứng không: 87,8 %
  trên ISE-DSC01, lặp lại trên ViWikiFC [15].
- Phép can thiệp E08 cho thấy quan hệ nhân quả theo hướng ngược lại: rút câu bằng chứng ra thì
  chú ý tản ra, ở 71–75 % số cặp, đúng hướng đã ghi trước [16].
- **Sau E19, thêm số:** trên cùng 300 mẫu, định vị bằng cắt bỏ ngữ cảnh (ARC-JSD, khoảng 10,9 lượt
  đọc mỗi mẫu) đạt hit@1 = __, đầu chú ý tốt nhất đạt 0,850 với một lượt đọc. Câu chốt dạng:
  *"chú ý rẻ hơn khoảng 11 lần và đạt X % hit@1 của phương pháp cắt bỏ"*.

### A5. Con số 87,8 % có phải do chọn đầu tốt nhất trên chính tập báo cáo không?

- Đúng là chọn trên chính tập đó, nên 0,878 là cận trên. Nhưng phần may mắn không đáng kể:
  - Nếu mọi đầu chỉ mạnh ngang trung bình (0,332), max của 756 đầu chỉ kỳ vọng khoảng 0,363.
  - Mười đầu dẫn đầu đều nằm trong khoảng 0,878–0,863, tức không phải một đầu ăn may.
- Con số **không dính lựa chọn nào** là trung bình cả 756 đầu: 0,332, gấp 5,4 lần mức chọn bừa.
  Nếu chỉ được nói một số thì nói số này.
- Đầu (lớp 14, đầu 6) chọn trên ISE-DSC01 vẫn đạt 0,797 trên 300 mẫu ViWikiFC của E19, tức chuyển
  được sang bộ khác.

### A6. Thí nghiệm can thiệp đổi đúng hướng 71–75 %, nhưng mức đổi chỉ 0,013–0,016. Có ý nghĩa gì?

- Kiểm định theo cặp đo **mức nhất quán của hướng**, không đo độ lớn. Hướng ổn định trên 1.836
  cặp và được ghi trong mã trước khi chạy, nên đây là bằng chứng về cơ chế.
- Độ lớn nhỏ, và nhóm nói rõ điều đó [16]. Nó cũng giải thích vì sao đặc trưng hình dạng không
  kéo điểm phân loại lên (A1).

### A7. Vì sao bộ phát hiện ba lớp không chuyển được sang bộ dữ liệu khác?

- Train ViHallu, chấm ISE-DSC01: ba lớp còn 0,358. Trong 1.286 câu ngoại lai chỉ 66 câu đoán
  đúng, 988 câu bị gọi thành nội tại [19].
- Nguyên nhân khả dĩ: **hai bộ định nghĩa "ngoại lai" khác nhau**. Ở ViHallu đó là nội dung GPT-4o
  tự thêm vào; ở ISE-DSC01 đó là phát biểu NEI do người viết. Nhãn nội tại – ngoại lai còn nhiễu
  sẵn: ở ViWikiFC chỉ 67 % nhãn NEI thật sự là ngoại lai, κ 0,505.
- Câu hỏi nhị phân "có ảo giác hay không" thì **vẫn chuyển được**: 0,664 và 0,776.

### A8. ⏳ Hướng tiếp theo cụ thể là gì?

- Chấm theo từng câu hoặc mệnh đề, thay vì lấy trung bình cả phản hồi. Ngành đang đi theo hướng
  này, và Bảng 9 cho thấy ba trong năm hình dạng lỗi là do một mệnh đề bịa bị trung bình hóa mất.
- **Sau E18, thêm số.** Lưu ý 71,6 % phản hồi ViHallu chỉ có một câu, nên trên bộ này hiệu ứng có
  trần.
- Đo chi phí biên trên GPU có bf16 gốc, nơi một mô hình vừa sinh vừa đọc (E20, cần phần cứng
  Ampere).

---

## B. Phương pháp

### B1. Sao chọn Qwen2.5-7B mà không chọn mô hình tiếng Việt?

- Qwen2.5 đọc tiếng Việt tốt, có bản 7B vừa T4 sau lượng tử hóa 4-bit, và có cùng họ 3B và 1.5B
  để làm bậc thang lùi.
- Đã thử **Sailor2-8B**, một mô hình mở rộng từ Qwen2.5 cho Đông Nam Á, gồm cả tiếng Việt (E13).
  Lookback gộp đạt 0,7377, gần bản Qwen (0,7451); chunk-aware giảm xuống 0,7120. Tức tín hiệu
  không phụ thuộc một mô hình cụ thể.

### B2. Vì sao bỏ lớp 27?

- Ở float16, lớp 27 của Qwen2.5-7B tràn số ở 20/20 mẫu đo. 27 lớp còn lại khớp float32 với sai lệch
  trung bình 0,07 % thang đo. Chạy float32 thì sạch nhưng chậm 3,6 lần.
- Tràn số không suy ra được từ cỡ mô hình, phải đo từng bản: bản 3B sạch hoàn toàn, còn bản 1.5B
  tràn cả 28 lớp nên phải chạy bfloat16.

### B3. Lượng tử hóa 4-bit có làm sai lệch tín hiệu chú ý không?

- Mọi lượt trích và mọi thí nghiệm dùng **cùng một** cấu hình NF4. Vì vậy so sánh giữa các phương
  pháp chú ý là công bằng.
- Nhóm chưa đo riêng NF4 so với trọng số đầy đủ, vì bản đầy đủ không vừa 16 GB. Đây là giới hạn
  nên nói ra. Bằng chứng gián tiếp cho thấy tín hiệu vẫn còn: định vị 87,8 % và ngang PhoBERT.

### B4. Vì sao dùng hồi quy logistic mà không dùng mô hình mạnh hơn?

- Đề tài hỏi *tín hiệu chú ý mang bao nhiêu thông tin*. Một bộ đọc tuyến tính trả lời thẳng câu
  đó; mô hình phi tuyến mạnh có thể tự học thêm và che mất câu trả lời.
- Bài Lookback Lens gốc cũng dùng hồi quy logistic, nên giữ nguyên để tái lập đúng.
- Số tham số rất nhỏ (195–2.271), huấn luyện trên CPU, và cho xác suất hiệu chỉnh tốt.

### B5. Vì sao chia ngữ cảnh theo câu, với `min_words=5`?

- Nhóm đã chạy cả hai cách, theo câu và theo cửa sổ token 64/128/256, rồi chọn trên **tập dev**
  (E05). Kèm một phép đối chứng cửa sổ không chồng lấn để loại cách giải thích "chồng lấn".
- Theo câu thắng vì nó bám **ranh giới ngữ nghĩa**, không phải vì độ phân giải.
- `min_words=5`: câu ngắn hơn ngưỡng này được gộp vào câu trước, chốt ở T15.

### B6. Vì sao bỏ token đầu tiên của câu trả lời?

- Token đầu chưa có token nào của câu trả lời đứng trước để so, nên tỷ lệ của nó luôn bằng 1, bất
  kể mô hình làm gì. Ở float16 nó có khi thành 0 do underflow. Cả hai giá trị đều vô nghĩa.

### B7. Mẫu số của tỷ lệ lookback tính thế nào?

- Lưu song song hai cách:
  - `lookback_total`: mẫu số gồm toàn bộ prompt, đúng như bài gốc. E02 dùng cách này để gọi là
    tái lập.
  - `lookback_context`: chỉ tính ngữ cảnh truy xuất, dễ diễn giải hơn, và là nền của phần
    chunk-aware.
- Chú ý được **lấy trung bình theo từng token nguồn**, không cộng dồn. Cộng dồn thì tỷ lệ sẽ phản
  ánh độ dài ngữ cảnh chứ không phản ánh hành vi của mô hình.

---

## C. Dữ liệu và đánh giá

### C1. Vì sao chia tập theo ngữ cảnh?

- ViHallu có nhiều câu trả lời trên cùng một tài liệu. Chia ngẫu nhiên theo dòng thì cùng tài liệu
  rơi vào cả tập train lẫn test, và mô hình "học thuộc đề" [8].
- Chia theo ngữ cảnh, 80/10/10, seed 42, rò rỉ bằng 0.
- Nhóm cũng đo được tập test gốc của ViWikiFC dùng lại 100 % ngữ cảnh của train, nên nhóm ghi chú
  điều này cạnh mọi con số trên bộ đó.

### C2. Gemini chỉ chấm 300 mẫu, so có công bằng không?

- Không so thẳng được, và bảng ghi rõ điều đó. Lý do là hạn mức của bản miễn phí, vì đề tài không
  có ngân sách API.
- So **trên đúng 300 mẫu đó**: ba lớp Gemini 0,664 so với 0,686 của baseline bề mặt; nhưng
  Gemini bắt được 97,4 % số ảo giác. Tức Gemini là bộ phát hiện tốt nhưng phân loại kém.

### C3. Nhãn của ISE-DSC01 và ViWikiFC là nhãn kiểm chứng thông tin, không phải ảo giác LLM thật?

- Đúng. Chỉ ViHallu có câu trả lời do LLM sinh thật (GPT-4o), nên ViHallu là bộ chính.
- Hai bộ kia được dùng cho việc chúng làm được mà ViHallu không làm được: **có bằng chứng đánh dấu
  sẵn** để kiểm định vị (E06, E08), và ngữ cảnh dài (ISE-DSC01).

### C4. Khoảng tin cậy tính thế nào, vì sao nói "ngang" mà không nói "hơn"?

- Bootstrap trên tập test 700 mẫu. Đo ở T17: khoảng này rộng gấp đôi biến thiên theo seed, nên nó
  mới là thứ quyết định.
- Hai khoảng chồng nhau thì không kết luận hơn. Muốn nói *hơn hẳn* XLM-R thì phải vượt 0,818, tức
  cận trên khoảng tin cậy của XLM-R.

---

## D. Hệ thống

### D1. Bộ nhớ: tại sao không bật `output_attentions` cho đơn giản?

- Ở 4.096 token, ma trận chú ý của một lớp đã chiếm khoảng 0,94 GB; giữ cả 28 lớp cần khoảng
  26 GB, tràn T4 16 GB [11].
- Forward hook: lớp nào tính xong thì cộng chú ý theo đoạn ngay rồi bỏ ma trận. Đỉnh đo thực tế ở
  4.096 token là 8.428 MB.
- Hook không hạ được đỉnh của chính một lớp. Muốn hạ nữa thì phải thay hàm tính attention.

### D2. Dùng thật được không? Độ trễ bao nhiêu? Vì sao demo cần hai mô hình?

- Khoảng 437,6 ms mỗi mẫu với Qwen2.5-7B trên T4, và 222,7 ms với 3B. Hệ thống có thư viện, REST,
  Docker và giao diện web. Bộ phát hiện chỉ là một tệp 11,5 KB, nạp lại chấm trùng 700/700 [12].
- Demo [13] dùng hai mô hình: 3B bfloat16 sinh, 7B float16 đọc. Lý do là ở float16 lớp 27 tràn số
  đi vào tầng dự đoán token nên mô hình 7B không sinh được chữ, mà T4 không đủ bộ nhớ cho một bản 7B
  bfloat16 thứ hai. Trên GPU có bf16 gốc (Ampere trở lên), một bản 7B vừa sinh vừa đọc được.

### D3. FlashAttention thì sao?

- Lấy được trọng số chú ý thì phải chạy attention dạng eager, tức tắt FlashAttention. Một hệ RAG
  đang dùng FlashAttention sẽ phải trả thêm phần này. Đây là chi phí biên thật và chưa được đo
  (giới hạn đã ghi ở mục 7 của quyển).

---

## E. Quy trình, tái lập, phân công

### E1. Kết quả có tái lập được không?

- Mọi thí nghiệm khai báo bằng YAML và được validate bằng pydantic. Seed cố định 42.
- Phiên bản mô hình được ghim bằng revision Hugging Face, thư viện ghim theo `uv.lock`, dữ liệu
  gốc có mã băm SHA-256.
- Kết quả ghi vào `results/runs.jsonl` kèm commit và hash cấu hình. Mọi bảng trong quyển lấy từ đó,
  không gõ tay.
- Có bộ kiểm thử tự động (hiện 825 ca), chạy được không cần GPU.

### E2. Phân công giữa hai thành viên?

- **Nhóm tự trả lời**, theo cột người làm của từng task trong `TASKS.md`: L là Lân, M là Minh, LM
  là cả hai.
- Hai người thống nhất trước một câu ngắn, và mỗi người nói được phần của người kia ở mức đại cương.

### E3. Nhóm có dùng công cụ AI không?

- Trả lời trung thực, đúng như phụ lục về sử dụng AI trong quyển. Công cụ AI được dùng ở mức
  **hỗ trợ kỹ thuật**: gợi ý và rà lỗi mã, tra cứu thư viện.
- Mọi quyết định do nhóm giữ: chọn đề tài và phương pháp, thiết kế thí nghiệm, ghi dự đoán trước
  khi chạy, đọc và diễn giải kết quả, kết luận.
- Bằng chứng nhóm kiểm soát được kết quả: mọi con số truy được về `results/runs.jsonl`, và các
  kết quả bất lợi được báo cáo thẳng.

### E4. Có gì nhóm sẽ làm khác nếu làm lại?

- Đo sớm tỷ lệ phản hồi chỉ có một câu và tính trần hiệu ứng trước khi thiết kế đặc trưng hình
  dạng ở mức toàn phản hồi.
- Đặt câu hỏi chuyển giao (E16) sớm hơn, vì nó cho thấy nhãn nội tại – ngoại lai khác nghĩa giữa
  các bộ.
