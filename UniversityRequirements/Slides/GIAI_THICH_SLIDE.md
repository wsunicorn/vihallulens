# Giải thích từng slide — đọc kèm `slide_v2.html`

> File này dành cho người **chưa từng tiếp xúc** với đề tài, kể cả người ngoài ngành. Mỗi slide có một mục,
> viết theo thứ tự xuất hiện. Thuật ngữ được giải thích ngay trong ngoặc ở lần đầu nó xuất hiện, nên đọc
> từ đầu tới cuối sẽ không gặp từ nào chưa được giải thích. Cuối mỗi mục có dòng **Số liệu lấy từ** để
> ai muốn kiểm chứng biết mở file nào trong kho mã nguồn.
>
> Cách đọc: mở `slide_v2.html`, tới slide nào thì đọc mục đó. Mỗi mục có ba phần nhỏ: *Slide này nói gì*
> (một câu), *Nhìn hình thế nào* (hình chạy ra sao, phần tử nào nghĩa là gì, rê chuột hay bấm được gì),
> và *Giải thích chi tiết*.

---

## Phần 0 · Mở màn

### Slide 1 — Bìa

**Slide này nói gì.** Tên đề tài, hai người làm, người hướng dẫn.

**Nhìn hình thế nào.** Bên phải là cú Lens — linh vật của đề tài, một con cú mặc áo giáo sư, hai mắt màu
lam ngọc. Những hạt sáng nhỏ trôi về phía mắt cú là hình ảnh ẩn dụ cho "sự chú ý dồn về một điểm" — ý
tưởng trung tâm của toàn bộ đề tài. Cú hơi nhấp nhô lên xuống chậm rãi; đó chỉ là hoạt ảnh nền.

**Giải thích chi tiết.** Tên đề tài dài, hãy tách ra từng cụm:

- *Mô hình ngôn ngữ lớn* (LLM — Large Language Model: chương trình máy tính được huấn luyện trên lượng
  văn bản khổng lồ để viết tiếp văn bản một cách tự nhiên; ChatGPT, Gemini là các LLM). LLM viết rất
  trôi chảy nhưng không có cơ chế nào bảo đảm điều nó viết là đúng.
- *Tăng cường truy xuất* (RAG — Retrieval-Augmented Generation: trước khi LLM trả lời, hệ thống đi tìm
  vài đoạn tài liệu liên quan và đưa cho LLM đọc, để câu trả lời bám vào tài liệu thay vì bám vào trí
  nhớ mơ hồ của mô hình). Đây là cách phổ biến nhất để doanh nghiệp dùng LLM với tài liệu nội bộ.
- *Ảo giác* (hallucination: LLM viết ra thông tin sai hoặc không có căn cứ nhưng bằng giọng văn tự
  tin như thật). Ngay cả khi có RAG, LLM vẫn có thể "bịa" — và vì nó bịa trôi chảy nên người đọc khó
  nhận ra.
- *Tín hiệu chú ý nội tại*: "chú ý" (attention) là một cơ chế bên trong LLM, quyết định khi viết mỗi
  từ thì mô hình "nhìn" vào những từ nào trước đó nhiều hay ít. "Nội tại" nghĩa là tín hiệu này có sẵn
  bên trong mô hình, không phải hỏi thêm ai. Đề tài dùng chính tín hiệu này để đoán xem một câu trả lời
  có ảo giác hay không.
- *Tiếng Việt*: mọi thí nghiệm làm trên dữ liệu tiếng Việt, điều chưa ai làm với phương pháp này.

**Số liệu lấy từ.** Không có số liệu; thông tin nhóm ở `CLAUDE.md` mục 1.

### Slide 2 — "Mô hình có thể bịa chữ. Ánh mắt của nó thì không."

**Slide này nói gì.** Toàn bộ đề tài gói trong một câu.

**Nhìn hình thế nào.** Chỉ có chữ, hiện hai nhịp: dòng đầu rồi dòng sau đổi màu lam ngọc.

**Giải thích chi tiết.** "Bịa chữ" là ảo giác. "Ánh mắt" là cơ chế chú ý vừa nói ở slide 1. Ý tưởng:
khi cho LLM **đọc lại** một câu trả lời cùng với tài liệu (ngữ cảnh) đã truy xuất, ta có thể đo xem mô
hình nhìn vào phần nào của tài liệu, nhìn nhiều hay ít. Nếu câu trả lời bám tài liệu thì ánh nhìn dồn
vào đúng chỗ; nếu câu trả lời bịa thì ánh nhìn tản mát vì không có gì để nhìn. Điểm mấu chốt ở cuối
câu: **"không cần LLM giám khảo"** — cách phổ biến hiện nay để bắt ảo giác là thuê một LLM khác (thường
qua dịch vụ trả phí như GPT-4 hay Gemini) đọc và chấm; đề tài không cần bước đó, chỉ dùng thứ có sẵn
trong chính lượt đọc của mô hình.

### Slide 3 — Lộ trình

**Slide này nói gì.** Bộ slide có bảy phần, tương ứng tám chương của quyển báo cáo theo mẫu của Khoa.

**Nhìn hình thế nào.** Dải bảy ô đánh số là bảy phần; ba thẻ bên dưới ghi phần nào ứng với chương nào.
Trong bộ slide, dòng chữ nhỏ màu cam ở góc trên trái mỗi slide (gọi là *eyebrow*) luôn cho biết đang ở
phần nào.

**Giải thích chi tiết.** Chương 1–2 (Giới thiệu, Cơ sở lý thuyết) là phần 1–2 của slide. Chương 3–6 (Phân
tích yêu cầu, Thiết kế, Giải pháp công nghệ, Hiện thực) là phần 3–5. Chương 7–8 (Đánh giá và thảo luận,
Kết luận) là phần 6–7 — phần 6 dài nhất vì đó là nơi trình bày kết quả. Phần 8 cuối cùng là xin ý kiến
và cảm ơn, không ứng với chương nào.

---

## Phần 1 · Bài toán (Chương 1)

### Slide 4 — Hệ RAG làm gì, và ảo giác chui vào ở đâu

**Slide này nói gì.** Mô phỏng một lượt hỏi–đáp thật của hệ RAG, cho thấy ảo giác xuất hiện ở bước LLM
viết câu trả lời — và nó trông hoàn toàn bình thường.

**Nhìn hình thế nào.** Hình tự chạy khoảng 12 giây theo đúng thứ tự một hệ RAG hoạt động:

1. Ô **Câu hỏi** bên trái gõ ra từng chữ: *"Hồ Hoàn Kiếm gắn với truyền thuyết nào?"* — đây là một câu
   hỏi thật đã chạy trên máy Kaggle ngày 11/09/2026.
2. Một chấm cam (tượng trưng cho dữ liệu đang chảy) chạy sang **Kho 21 tài liệu**. Từng ô tài liệu sáng
   lên lần lượt: hệ thống đang quét kho bằng BM25 (một thuật toán tìm kiếm cổ điển, chấm điểm mỗi tài
   liệu theo số từ trùng với câu hỏi; không dùng trí tuệ nhân tạo). Ba ô sáng hẳn màu lam ngọc là ba tài
   liệu được chọn: Hà Nội, Tết Nguyên Đán, Tết Trung Thu. Rê chuột lên ô sẽ hiện tên đầy đủ.
3. Khung **Ngữ cảnh ghép từ 3 tài liệu** mọc ra, liệt kê ba tài liệu kèm điểm BM25 (11,79 · 5,41 · 2,95).
   "Ngữ cảnh" (context) là từ chuyên ngành chỉ toàn bộ đoạn tài liệu được đưa cho LLM đọc.
4. Chấm cam chảy vào ô **LLM sinh** (Qwen2.5-3B — một LLM mã nguồn mở của Alibaba, cỡ 3 tỷ tham số; "tham
   số" là các con số bên trong mô hình, càng nhiều thì mô hình càng mạnh và càng nặng). Vòng tròn nhỏ ở
   góc ô nhấp nháy nghĩa là mô hình đang "suy nghĩ".
5. Khung **Câu trả lời** gõ ra từng chữ. Ba mệnh đề đầu đúng với tài liệu. Đến cụm cuối *"sau đó anh ta
   đã trở về dinh thự"* chữ chuyển đỏ và có gạch chân, một chấm đỏ nhấp nháy với nhãn **"không có trong
   ngữ cảnh"**.

**Giải thích chi tiết.** Đây là toàn bộ bài toán trong một hình. Tài liệu chỉ nói *"Hồ Hoàn Kiếm nằm ở
trung tâm khu phố cổ và gắn với truyền thuyết vua Lê Lợi trả gươm"*. Mô hình viết thêm *"sau khi đánh
đuổi giặc Minh"* (đúng ngoài đời nhưng tài liệu không nói) và *"trở về dinh thự"* (bịa hẳn). Người đọc
bình thường không thể phân biệt câu nào lấy từ tài liệu, câu nào mô hình tự thêm — tất cả cùng một giọng
văn. Con số **0,997** ở nhãn là "điểm rủi ro" mà hệ thống của đề tài chấm cho câu trả lời này (thang 0
tới 1, càng gần 1 càng chắc là ảo giác) — sẽ giải thích ở slide 6 và 31.

**Số liệu lấy từ.** `results/t40/t40_rag.json`, mẫu thứ tư.

### Slide 5 — Hai loại ảo giác

**Slide này nói gì.** Ảo giác có hai loại, phân biệt bằng câu hỏi "mô hình có đọc tài liệu không".

**Nhìn hình thế nào.** Hai thẻ. Thẻ vàng **Nội tại** có một thanh ngang với một khúc sáng ở giữa: ánh
nhìn dồn đúng một chỗ. Thẻ đỏ **Ngoại lai** có thanh tô đỏ nhạt đều: ánh nhìn tản khắp nơi.

**Giải thích chi tiết.**

- *Ảo giác nội tại* (intrinsic): mô hình **có đọc** tài liệu nhưng **nói lệch** đi. Ví dụ tài liệu ghi
  "Thăng Long dưới triều Lý", mô hình trả lời "dưới triều Trần". Nó nhìn đúng câu, nhưng đổi chi tiết.
- *Ảo giác ngoại lai* (extrinsic): mô hình **không dựa vào** tài liệu mà **tự bịa** thứ tài liệu không hề
  có. Ví dụ tài liệu không nói gì về công trình, mô hình trả lời "tháp Eiffel thu nhỏ, tàu điện ngầm dài
  nhất Đông Nam Á".

Tại sao phải tách hai loại? Vì cách chữa khác nhau: nội tại là lỗi *đọc sai*, ngoại lai là lỗi *không
đọc*. Và vì hai loại này để lại **dấu vết chú ý khác nhau** — nội tại thì ánh nhìn nhọn (dồn vào một câu),
ngoại lai thì ánh nhìn tản — đó chính là thứ đề tài muốn đo. Ba nhãn của bài toán vì thế là: *trung
thực* (no), *nội tại* (intrinsic), *ngoại lai* (extrinsic). Định nghĩa này lấy theo bộ dữ liệu ViHallu,
sẽ giới thiệu ở slide 13.

**Số liệu lấy từ.** Hai ví dụ là hai câu trả lời thật trong `results/t40/t36_thu_vien.json`.

### Slide 6 — Ba loại phản hồi, mô hình đọc nhìn đi đâu

**Slide này nói gì.** Lấy cùng một tài liệu, cho ba câu trả lời (một trung thực, một nội tại, một
ngoại lai) và xem hệ thống chấm thật ra sao.

**Nhìn hình thế nào.** Bên trái là **ngữ cảnh** gồm bốn câu về Hà Nội, mỗi câu một ô. Bên phải là ba
thẻ: Trung thực (xanh lá), Nội tại (vàng), Ngoại lai (đỏ). Hình tự chạy lần lượt ba thẻ, mỗi lượt:

1. Chữ trong thẻ **sáng dần từng từ** — đó là mô hình đọc câu trả lời (cách gọi chuyên ngành: mô hình
   "đọc lại" câu trả lời, không tự viết).
2. Từ đáy thẻ **bắn ra bốn tia** về bốn câu của ngữ cảnh. Tia càng dày thì mô hình càng nhìn nhiều vào
   câu đó. Con số phần trăm hiện ở góc phải mỗi câu là *tỷ trọng chú ý* (phần ánh nhìn rơi vào câu đó,
   bốn câu cộng lại là 100 %). Ô câu cũng tô đậm hơn nếu tỷ trọng cao.
3. **Đồng hồ** phía dưới quay tới *điểm rủi ro*: 0,001 cho câu trung thực, 0,998 cho nội tại, 1,000 cho
   ngoại lai. Dưới đồng hồ hiện nhãn hệ thống kết luận.

Bấm vào một thẻ để chạy lại riêng thẻ đó.

**Giải thích chi tiết.** *Điểm rủi ro* = 1 − P(trung thực), trong đó P(trung thực) là xác suất hệ thống
tin rằng câu trả lời trung thực. Điểm càng gần 1 thì càng đáng ngờ. Ba con số 0,001 / 0,998 / 1,000 là
số thật, đo trên card đồ họa Tesla T4 (một loại GPU — bộ xử lý đồ họa, thứ dùng để chạy LLM — thuộc loại
rẻ, được Kaggle cấp miễn phí; sẽ nói ở slide 12). Ba câu này **không nằm trong dữ liệu huấn luyện**,
tức hệ thống chưa từng thấy chúng — điểm cao thấp là nó tự suy ra.

Một điều cần trung thực: ở ví dụ nhỏ này, các tỷ trọng của ba câu trả lời không khác nhau quá rõ (câu
trung thực 23,9 / 35,3 / 15,6 / 25,3 %; câu ngoại lai 31,6 / 21,1 / 19,4 / 27,9 %). Hệ thống phân biệt
được ba trường hợp là nhờ tổng hợp tín hiệu từ **hàng trăm "đầu chú ý"** (giải thích ở slide 8) chứ
không chỉ bốn con số hiện trên hình. Hình chỉ vẽ một lát cắt để dễ nhìn.

**Số liệu lấy từ.** `results/t40/t36_thu_vien.json` — mục `chunk_attention` (tỷ trọng từng câu) và
`risk_score`.

### Slide 7 — Ba con đường hiện có và giá của chúng

**Slide này nói gì.** Ba cách người ta đang dùng để bắt ảo giác, mỗi cách trả một cái giá; từ đó suy ra
đề tài cần gì.

**Nhìn hình thế nào.** Ba thẻ với ba con số lớn đếm lên: **8.194 ms**, **560 triệu**, **0,656**. Dòng kết
luận màu trắng hiện sau cùng.

**Giải thích chi tiết.**

- *LLM giám khảo* (LLM-as-judge): thuê một LLM khác đọc câu trả lời và phán. Đề tài đã thử với Gemini
  bản miễn phí: mất **8.194 mili-giây** (hơn 8 giây) mỗi mẫu, phải gửi dữ liệu ra máy chủ bên ngoài (với
  tài liệu nội bộ đây là vấn đề bảo mật), và độ chính xác chỉ đạt macro-F1 0,664.
  *macro-F1* là thước đo độ chính xác cho bài toán phân loại nhiều lớp, thang 0 tới 1; nó tính riêng
  cho từng lớp rồi lấy trung bình, nên lớp ít mẫu cũng được coi trọng ngang lớp nhiều mẫu. Đoán bừa
  giữa ba lớp cho khoảng 0,33.
- *Bộ mã hóa tinh chỉnh* (fine-tuned encoder): lấy một mô hình ngôn ngữ cỡ vừa như XLM-R hay PhoBERT
  rồi huấn luyện lại toàn bộ trên dữ liệu có nhãn. Phải cập nhật **560 triệu tham số**, cần GPU để huấn
  luyện, và có mô hình (InfoXLM) huấn luyện mãi không hội tụ. Bù lại XLM-R đạt 0,776 — cao nhất bảng.
- *Đặc trưng bề mặt*: chỉ nhìn những thứ bề ngoài như độ dài câu trả lời, số từ trùng với tài liệu.
  Rẻ (9 tham số) nhưng yếu, 0,656.

→ Đề tài cần một tín hiệu **có sẵn trong chính lượt đọc** của mô hình: không phải thuê giám khảo, không
phải huấn luyện lại mô hình lớn, không phải gửi dữ liệu đi đâu.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 1 (E01, E09, E10) và Bảng 8.

---

## Phần 2 · Nền tảng (Chương 2)

### Slide 8 — Chú ý là thứ nhìn thấy được

**Slide này nói gì.** Giải thích cơ chế "chú ý" bằng hình: mỗi từ của câu trả lời phân bổ ánh nhìn lên
các từ của tài liệu, và toàn bộ phân bổ này ghi được thành một bảng số.

**Nhìn hình thế nào.** Hàng trên là các *token* của ngữ cảnh (token: đơn vị nhỏ nhất mà LLM xử lý, gần
như là một từ hoặc một mảnh từ; ở đây mỗi ô là một từ cho dễ đọc). Hàng dưới là các token của câu trả
lời. Hình lặp vô hạn: từng token trả lời sáng lên, từ nó **bắn các tia** lên hàng trên — tia dày là nhìn
nhiều, tia mảnh là nhìn ít. Cùng lúc, **ma trận** bên phải tô thêm một hàng: mỗi ô là một cặp (token trả
lời, token ngữ cảnh), ô càng sáng thì chú ý càng lớn; ký hiệu Σ = 1 ở cuối hàng nhắc rằng mỗi hàng cộng
lại đúng bằng 1 (100 % ánh nhìn của token đó). Rê chuột lên một token trả lời để dừng hình và xem riêng
tia của token đó; rê lên một ô ma trận để xem con số.

**Giải thích chi tiết.** *Chú ý* (attention) là phép tính nằm trong mọi LLM hiện đại: khi xử lý một
token, mô hình tính cho mỗi token đứng trước một trọng số từ 0 tới 1, tổng bằng 1, cho biết token đó
được "nhìn" nhiều hay ít. Trọng số này **có thể đọc ra** khi chạy mô hình — nó không phải hộp đen.

Một LLM không chỉ có một phép chú ý mà có rất nhiều: mô hình Qwen2.5-7B mà đề tài dùng có **28 lớp**
(layer — các tầng xử lý xếp chồng, tín hiệu đi qua lần lượt) và mỗi lớp có **28 đầu chú ý** (head — mỗi
đầu là một phép chú ý độc lập, học một kiểu "nhìn" riêng), tức 28 × 28 = 784 ma trận như trong hình cho
mỗi lượt đọc. Đề tài bỏ lớp cuối (lớp 27) vì lý do kỹ thuật (slide 16), còn 27 × 28 = 756 đầu.

Lưu ý: trọng số trong hình này là **mô phỏng** để minh họa cơ chế (chân slide ghi rõ); mọi con số ở các
slide kết quả là số đo thật.

**Số liệu lấy từ.** Minh họa; cấu trúc mô hình theo `CLAUDE.md` mục 5.

### Slide 9 — Lookback Lens gộp thành một tỷ lệ, chunk-aware tách theo từng câu

**Slide này nói gì.** Đây là slide quan trọng nhất về phương pháp: trình bày công trình nền (Lookback
Lens) và đóng góp của đề tài (chunk-aware) trên cùng một hình.

**Nhìn hình thế nào.** Hình chạy ba nhịp:

1. Hàng token ngữ cảnh ở trên sáng lên theo mức chú ý — token nào được nhìn nhiều thì sáng hơn.
2. Tất cả token **gom lại thành một thanh** ghi *LR = 62 %*; phần xám bên phải ghi *đã sinh 38 %*. Đây là
   cách của Lookback Lens: cộng toàn bộ chú ý rơi vào ngữ cảnh thành **một con số**.
3. Token trở về chỗ cũ rồi **tách thành năm cột**, mỗi cột là một câu của ngữ cảnh (câu 1 tới câu 5) với
   phần trăm riêng. Đây là cách của đề tài. Bên phải, bốn thanh *entropy, tỷ trọng lớn nhất, Gini,
   khoảng cách top-1/top-2* mọc ra với con số — bốn đại lượng đo "hình dạng" của năm cột này.

**Kéo thanh trượt "số đoạn"** ở góc trên phải (1 tới 8) để chia ngữ cảnh thành ít hay nhiều đoạn hơn; các
cột và bốn đại lượng tính lại tức thì. Kéo về 1 sẽ thấy: chỉ còn một cột, bốn đại lượng mất nghĩa — đó
chính là tình trạng của Lookback Lens.

**Giải thích chi tiết.** *Lookback Lens* là bài báo ở hội nghị EMNLP 2024 (một trong những hội nghị hàng
đầu về xử lý ngôn ngữ tự nhiên) của Chuang và cộng sự. Họ phát hiện: chỉ cần tính **tỷ lệ chú ý rơi vào
ngữ cảnh** so với chú ý rơi vào phần câu trả lời đã viết trước đó — gọi là *lookback ratio*, "tỷ lệ nhìn
lại" — cho từng đầu chú ý, rồi đưa các tỷ lệ ấy vào một bộ phân loại đơn giản, là đủ để bắt ảo giác
ngang với những cách phức tạp hơn nhiều. Đề tài tái lập đúng công thức này trên tiếng Việt (thí nghiệm
E02, kết quả ở slide 24).

*Chunk-aware* (nhận biết đoạn; "chunk" là đoạn — ở đây là mỗi câu của ngữ cảnh) là đóng góp của đề tài:
thay vì gộp cả ngữ cảnh thành một khối, **tách theo từng đoạn** rồi hỏi thêm: ánh nhìn có **hình dạng** gì?
Nhọn vào một đoạn hay tản đều? Cùng một con số 62 % có thể là "62 % dồn cả vào câu 3" hoặc "62 % rải đều
năm câu" — Lookback Lens không phân biệt được, chunk-aware thì có. Slide 5 đã nói vì sao điều này quan
trọng: nội tại thì nhọn, ngoại lai thì tản.

**Số liệu lấy từ.** Minh họa (trọng số mô phỏng); công thức gốc ở `docs/REFERENCES.md`.

### Slide 10 — Khoảng trống bài gốc để lại

**Slide này nói gì.** Ba điều Lookback Lens chưa làm, cũng là ba lý do đề tài tồn tại.

**Nhìn hình thế nào.** Ba thẻ đánh số hiện lần lượt.

**Giải thích chi tiết.** (1) Một con số không nói *đoạn nào* — như vừa giải thích ở slide 9. (2) Bài gốc
chỉ trả lời "có ảo giác hay không" (hai lớp, gọi là *nhị phân*) và đo bằng AUROC (một thước đo cho bài
toán hai lớp); đề tài cần ba lớp và dùng macro-F1 để so được với các công bố trên bộ ViHallu. (3) Bài
gốc làm trên tiếng Anh với mô hình LLaMA-2; chưa có kết quả nào cho tiếng Việt hay họ mô hình Qwen, và
chưa ai **kiểm tra trực tiếp** rằng cơ chế thật sự hoạt động — tức chứng minh mô hình nhìn đúng vào câu
chứa bằng chứng (slide 25 sẽ làm việc này).

**Số liệu lấy từ.** `docs/REFERENCES.md`.

---

## Phần 3 · Yêu cầu và dữ liệu (Chương 3)

### Slide 11 — Ba câu hỏi nghiên cứu

**Slide này nói gì.** Toàn bộ thí nghiệm của đề tài trả lời đúng ba câu hỏi, mỗi câu một màu.

**Nhìn hình thế nào.** Ba thẻ viền màu: cam (CH1), lam ngọc (CH2), tím (CH3). Ba màu này dùng lại ở lưới
thí nghiệm (slide 20) và ở dòng eyebrow của các slide kết quả.

**Giải thích chi tiết.** CH1 — *tín hiệu và cơ chế*: chú ý theo đoạn có đủ để phân ba lớp trên tiếng Việt
không, và có cách nào kiểm tra trực tiếp rằng mô hình thật sự nhìn vào câu bằng chứng không? CH2 — *chi
phí*: so với LLM giám khảo và bộ mã hóa tinh chỉnh, cách này đổi được gì về độ chính xác, thời gian, bộ
nhớ và số tham số phải huấn luyện? CH3 — *chuyển giao*: bộ phát hiện huấn luyện với một mô hình đọc hoặc
một bộ dữ liệu có dùng được cho mô hình khác, bộ dữ liệu khác không?

### Slide 12 — Ràng buộc cứng

**Slide này nói gì.** Bốn giới hạn về tài nguyên; chúng quyết định phương pháp chứ không phải ngược lại.

**Nhìn hình thế nào.** Bốn thẻ với số đếm lên: 16 GB, 30 h, 0 ₫, 42.

**Giải thích chi tiết.** Đề tài chạy trên **một card Tesla T4** có 16 GB bộ nhớ (VRAM — bộ nhớ riêng
của GPU; mô hình và mọi phép tính phải nằm vừa trong đó), được Kaggle (nền tảng thi đấu dữ liệu của
Google) cấp miễn phí **30 giờ mỗi tuần**. Không có ngân sách API (không trả tiền cho dịch vụ LLM bên
ngoài; Gemini bản miễn phí chỉ dùng để dựng một mốc so sánh nhỏ). Và mọi thứ phải **tái lập được**: seed
cố định là 42 (*seed* — số khởi tạo cho mọi phép ngẫu nhiên; cùng seed thì chạy lại ra cùng kết quả),
cấu hình ghi ra file, không có con số giấu trong mã.

Hệ quả trực tiếp: phương pháp chỉ có thể là **một lượt đọc** (không sinh chữ mới, không lặp), **hook trong
lớp** (slide 17) để không tràn 16 GB, và **bộ phân loại tuyến tính** (slide 16) để huấn luyện xong trong
vài giây trên CPU.

**Số liệu lấy từ.** `CLAUDE.md` mục 2–3.

### Slide 13 — Ba bộ dữ liệu, chia theo ngữ cảnh

**Slide này nói gì.** Ba bộ dữ liệu tiếng Việt công khai được dùng, và cách chia tập sao cho điểm số
không bị "ảo".

**Nhìn hình thế nào.** Ba thẻ trên cùng là ba bộ với số mẫu đếm lên. Hình động bên dưới: 30 nhóm chấm,
mỗi nhóm một màu, mỗi chấm là một phản hồi; **cùng màu = cùng ngữ cảnh** (cùng một tài liệu nhưng nhiều
câu trả lời khác nhau). Các nhóm xáo trộn rồi rơi vào ba rổ *train 80 %*, *dev 10 %*, *test 10 %*; chấm
cùng màu luôn rơi cùng rổ. Bấm nút **"Chia ngẫu nhiên từng mẫu"** để xem cách làm sai: chấm cùng màu bị
tách sang các rổ khác, những **đường đỏ** nối chúng lại là chỗ rò rỉ.

**Giải thích chi tiết.** Ba bộ:

- **ViHallu** (7.000 mẫu) — bộ chính, từ cuộc thi DSC 2025. Điểm quý: câu trả lời là do GPT-4o (một LLM
  của OpenAI) **sinh thật**, không phải người viết giả, và có đủ ba nhãn trung thực / nội tại / ngoại lai.
- **ISE-DSC01** (khoảng 36 nghìn mẫu) — bộ kiểm chứng thông tin; ngữ cảnh rất dài, 21–73 câu mỗi mẫu, và
  có đánh dấu **câu bằng chứng** (câu nào trong tài liệu chứa thông tin để phán). Dùng để kiểm chứng
  chunk-aware vì ngữ cảnh dài mới có nhiều đoạn để phân biệt.
- **ViWikiFC** (20.919 mẫu) — bộ kiểm chứng thông tin trên Wikipedia tiếng Việt, dùng làm đối chứng
  ngoài.

Về chia tập: máy học cần ba tập — *train* (để học), *dev* (để chọn cấu hình), *test* (để chấm điểm cuối
cùng, chỉ chấm một lần). Nếu chia ngẫu nhiên từng mẫu, hai câu trả lời của cùng một tài liệu có thể một
cái nằm train, một cái nằm test; bộ phân loại "học thuộc" tài liệu ấy rồi chấm lại chính nó → điểm cao
giả tạo, gọi là **rò rỉ dữ liệu**. Đề tài chia **theo ngữ cảnh** (group split): mỗi tài liệu chỉ ở đúng
một tập, rò rỉ bằng 0.

Chân slide ghi hai cái bẫy đã đo trước khi dùng: tập test gốc của ViWikiFC dùng lại **100 %** ngữ cảnh
của tập train (nên điểm công bố trên bộ này có phần ảo — xem slide 30); và chỉ **67 %** mẫu nhãn NEI
(Not Enough Information — "không đủ thông tin") của ViWikiFC thật sự tương đương ảo giác ngoại lai, đo
bằng hai người gán lại độc lập.

**Số liệu lấy từ.** `docs/DATA.md`; các đầu việc T10–T15 trong `TASKS.md`.

---

## Phần 4 · Phương pháp và thiết kế (Chương 4–5)

### Slide 14 — Giả thuyết: nội tại nhọn, ngoại lai tản — và phép đo can thiệp

**Slide này nói gì.** Đặt giả thuyết về hình dạng chú ý, rồi cho xem hai bằng chứng: ba ví dụ thật và
một phép đo trên gần hai nghìn cặp.

**Nhìn hình thế nào.** Ba bảng cột bên trái ứng với ba câu trả lời của slide 6 (xanh lá trung thực, vàng
nội tại, đỏ ngoại lai); cột mọc lên theo tỷ trọng thật của bốn câu ngữ cảnh, phần trăm ghi trên đầu cột.
Dưới mỗi bảng, bốn con số *entropy, tỷ trọng lớn nhất, Gini, top-1 − top-2* đếm lên — chúng được tính
từ chính bốn cột đó. Rê chuột lên cột để xem số. Khung phải **"Cả tập · E08, 1.836 cặp"** hiện bốn cặp
thanh xanh/đỏ.

**Giải thích chi tiết.** Bốn đại lượng hình dạng (giải thích đầy đủ ở slide 15): *entropy* đo độ tản
(0 = dồn hết vào một đoạn, 1 = rải đều); *tỷ trọng lớn nhất* là phần trăm của đoạn được nhìn nhiều nhất;
*Gini* đo độ bất bình đẳng giữa các đoạn (như chỉ số Gini về thu nhập); *top-1 − top-2* là khoảng cách
giữa đoạn nhìn nhiều nhất và đoạn nhì. Giả thuyết: nội tại thì entropy thấp, tỷ trọng lớn nhất cao;
ngoại lai thì ngược lại.

Khung bên phải là bằng chứng mạnh hơn hẳn ba ví dụ, vì nó là **phép đo can thiệp** (thí nghiệm E08): lấy
1.836 câu khẳng định trong ViWikiFC, mỗi câu đọc **hai lần** trên hai ngữ cảnh gần giống hệt nhau — chỉ
khác đúng một câu: ngữ cảnh thứ nhất có câu bằng chứng, ngữ cảnh thứ hai câu đó bị **rút ra** và thay
bằng một câu nhiễu. Rồi đo lại bốn đại lượng. Kết quả: khi mất bằng chứng, entropy tăng (0,7966 →
0,8176), Gini giảm, tỷ trọng lớn nhất giảm, top-1 − top-2 giảm — **cả bốn đúng hướng đã dự đoán**, và
dự đoán được ghi vào mã **trước khi chạy**, có ca kiểm thử khóa lại để không thể sửa sau khi thấy kết
quả. Từ 71 % tới 75 % số cặp chuyển đúng hướng. Khác với các bảng điểm thông thường (chỉ cho biết tín
hiệu *tương quan* với nhãn), phép can thiệp cho biết tín hiệu *phản ứng đúng* khi ta thay đổi nguyên
nhân.

**Số liệu lấy từ.** Trái: `results/t40/t36_thu_vien.json`. Phải: `docs/EXPERIMENTS.md` Bảng 2c.

### Slide 15 — Năm đại lượng hình dạng, cộng với tỷ lệ gộp

**Slide này nói gì.** Liệt kê đủ sáu loại đặc trưng đưa vào bộ phân loại, kèm trọng số mỗi loại chiếm.

**Nhìn hình thế nào.** Sáu thẻ; thẻ cuối viền cam là tỷ lệ gộp của bài gốc.

**Giải thích chi tiết.** *Đặc trưng* (feature) là các con số tóm tắt một mẫu để đưa vào máy học. Năm đại
lượng hình dạng: entropy (26,8 % trọng số), tỷ trọng lớn nhất (22,6 %), khoảng cách top-1/top-2 (15,5 %),
Gini (15,0 %), và *độ trôi* (7,2 % — đo phân bố chú ý thay đổi bao nhiêu từ từ đầu tới từ cuối của câu
trả lời; câu trả lời bám tài liệu thường nhìn ổn định vào một chỗ). Cộng với *tỷ lệ gộp* của Lookback
Lens (12,9 %) — giữ lại để so sánh công bằng với bài gốc.

Phần trăm là **trọng số** bộ phân loại gán cho mỗi nhóm sau khi huấn luyện; năm đại lượng mới chiếm
87 %, nghĩa là bộ phân loại thật sự dựa vào hình dạng chứ không chỉ dùng lại tỷ lệ gộp.

Mỗi đại lượng tính riêng cho từng cặp (lớp, đầu) trong 756 đầu chú ý — quá nhiều cột. Đề tài chọn **32
đầu tốt nhất trên tập dev** (số 32 cũng chọn trên dev, không đụng test), 32 × 6 = **192 cột** cho mỗi mẫu.

**Số liệu lấy từ.** `docs/SPEC.md` mục 2.3; trọng số theo nhóm ở `docs/EXPERIMENTS.md` mục 3.

### Slide 16 — Cơ chế 5 bước

**Slide này nói gì.** Toàn bộ đường đi của một mẫu, từ văn bản tới nhãn, trong một lượt đọc.

**Nhìn hình thế nào.** Năm ô nối tiếp; một chấm cam chạy lặp qua năm ô, ô nào chấm tới thì sáng viền.
Ở ô 4, các cột nhỏ mọc lên tượng trưng cho 192 đặc trưng; ở ô 5, ba thanh *no / intrinsic / extrinsic*
mọc theo xác suất của một mẫu thật (0,003 / 0,010 / 0,987). Rê chuột lên ô để đọc mô tả.

**Giải thích chi tiết.**

1. **Ghép prompt** — *prompt* là văn bản đưa vào LLM. Ngữ cảnh và câu hỏi được đặt ở lượt "người dùng",
   câu trả lời cần chấm đặt ở lượt "trợ lý", theo đúng khuôn mẫu hội thoại (chat template) của Qwen. Mẫu
   này được chốt một lần và **không bao giờ đổi**, vì đổi sẽ dịch chuyển vị trí mọi token và làm hỏng
   toàn bộ đặc trưng đã trích.
2. **Đọc lại** — mô hình đọc Qwen2.5-7B-Instruct (7 tỷ tham số) được nén 4-bit NF4 (*lượng tử hóa* —
   lưu mỗi tham số bằng 4 bit thay vì 16 để mô hình 7 tỷ tham số vừa 16 GB), tính bằng số float16 (số
   thực 16 bit, nhanh trên T4), bỏ lớp 27 vì lớp đó tràn số ở float16 (đo được ở 20/20 mẫu thử). Tốn
   437 ms mỗi mẫu.
3. **Hook trong lớp** — giải thích ở slide 17.
4. **Đặc trưng** — 192 cột như slide 15.
5. **Hồi quy logistic** — bộ phân loại tuyến tính đơn giản nhất trong máy học: nhân mỗi cột với một
   trọng số, cộng lại, chuyển thành xác suất ba lớp. Chỉ **579 tham số**, huấn luyện xong trong vài giây
   trên CPU. Đầu ra là nhãn và điểm rủi ro.

Dòng dưới nói về *teacher forcing*: câu trả lời được **đọc**, không được mô hình **tự viết**. Nhờ vậy hệ
thống chấm được bất kỳ câu trả lời nào — kể cả do GPT-4o, Gemini hay người viết — không cần mô hình sinh
ra nó.

**Số liệu lấy từ.** `CLAUDE.md` mục 3 và 8; mã ở `src/vihallulens/extract/`.

### Slide 17 — Rủi ro số một: bộ nhớ

**Slide này nói gì.** Vì sao cách làm ngây thơ sẽ tràn 16 GB, và "hook trong lớp" giải quyết thế nào.

**Nhìn hình thế nào.** Hai nửa chạy song song qua 28 lớp. Nửa trái **cách ngây thơ**: mỗi lớp thêm một
thanh đỏ, đồng hồ VRAM dâng thêm 0,94 GB mỗi lớp, đến lớp 12 thì vượt vạch 16 GB → chữ **TRÀN BỘ NHỚ**,
các thanh xám đi. Nửa phải **hook trong lớp**: mỗi lớp thanh sáng lên rồi **mờ ngay** (đã xóa), năm cột
xanh nhỏ ở dưới (bộ cộng dồn theo đoạn) cao dần, đồng hồ VRAM chỉ nhích lên một chút rồi về, cuối cùng
đứng ở **8,3 GB**.

**Giải thích chi tiết.** Ma trận chú ý của một lớp có kích thước (số đầu) × (độ dài chuỗi)². Với 28 đầu và
chuỗi 4.096 token, mỗi ô 2 byte: 28 × 4.096² × 2 = **0,94 GB cho một lớp**. Cách ngây thơ mà thư viện
cung cấp sẵn (`output_attentions=True`) giữ ma trận của **cả 28 lớp** tới cuối để trả về một lượt: 26 GB,
cộng thêm 5,6 GB trọng số mô hình — tràn T4 gần hai lần.

*Hook* là một hàm nhỏ được "móc" vào từng lớp của mô hình, chạy ngay khi lớp đó tính xong. Hook của đề
tài đọc ma trận, **cộng chú ý của các token trả lời theo từng đoạn ngữ cảnh** (chỉ giữ vài chục con số),
rồi trả ma trận cho hệ thống xóa **trước khi** sang lớp kế. Nhờ vậy lúc nào cũng chỉ có một lớp trong bộ
nhớ: 0,94 + 5,6 + phần phụ ≈ 8,3 GB đo được (chính xác 8.328 MB).

Chú thích chân slide nhắc ba điều dễ hiểu sai, đã ghi trong tài liệu: hook không giảm được đỉnh bộ nhớ
của *chính lớp đó* (ma trận vẫn phải tạo ra); hook có thể thay đổi đầu ra của lớp để chặn tích lũy; và
hành vi này phụ thuộc phiên bản thư viện `transformers`, nên phiên bản được ghim và có ca kiểm thử
khẳng định.

**Số liệu lấy từ.** `CLAUDE.md` mục 5 (phép tính); đỉnh VRAM đo ở T08.

### Slide 18 — Chia đoạn theo câu hay theo cửa sổ token?

**Slide này nói gì.** "Đoạn" nên là gì? Đề tài làm cả hai cách rồi đo; theo câu thắng.

**Nhìn hình thế nào.** Trên cùng là ngữ cảnh 10 câu (lấy từ demo thật), mỗi ô một từ; các từ của câu
bằng chứng viền cam. Một **đường dao** quét từ trái sang phải: hàng **Theo câu** (lam ngọc) mọc theo,
mỗi khối là một câu, khối cam là câu bằng chứng — nguyên vẹn. Hàng **Cửa sổ** (vàng) hiện sau: các khối
xếp so le vì chồng lấn nhau; khối nào **cắt ngang** câu bằng chứng thì tô **đỏ**. Kéo thanh trượt để đổi
cỡ cửa sổ 8 / 16 / 24 / 32 từ; dòng dưới đếm số cửa sổ cắt ngang.

**Giải thích chi tiết.** Hai cách chia: *theo câu* dùng dấu chấm làm ranh giới (đoạn ngắn hơn 5 từ ghép
vào đoạn kế); *cửa sổ token* cắt cứng mỗi N token, bước nhảy N/2 nên hai cửa sổ liền nhau chồng lên nhau
một nửa. Thí nghiệm E04–E05 chạy 7 lượt trích trên 25.200 mẫu: theo câu đạt macro-F1 0,7768 trên tập
dev, cao hơn cả bốn cấu hình cửa sổ (0,7589–0,7683). Để loại giả thuyết "thắng vì cửa sổ chồng lấn làm
loãng", có thêm một **đối chứng** cửa sổ 48/48 không chồng lấn: 0,7649 — vẫn thua. Lý do còn lại: câu là
**ranh giới ngữ nghĩa** — bằng chứng nằm trọn trong một câu, cắt ngang nó là chia bằng chứng cho hai đoạn,
tỷ trọng của đoạn nào cũng loãng đi. Biên độ nhỏ (0,0085) nhưng hướng nhất quán 8/8 lượt so.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 3; ngữ cảnh minh họa từ `results/t40/t40_rag.json`.

### Slide 19 — Kiến trúc bốn tầng

**Slide này nói gì.** Mã nguồn được tổ chức thành bốn tầng xếp chồng; tầng trên chỉ gọi tầng dưới.

**Nhìn hình thế nào.** Bốn khối dựng từ dưới lên: `extract/` → `features/` → `detect/` → `serve/`. Ba thẻ
bên phải là ba nguyên tắc kỹ thuật.

**Giải thích chi tiết.** `extract/` chạy mô hình đọc với hook (slide 16–17). `features/` tính sáu loại đặc
trưng (slide 15). `detect/` là hồi quy logistic và **bundle** — gói lưu bộ phân loại cùng "công thức
dựng cột" (chọn đầu nào, đại lượng nào, thứ tự ra sao); bundle từ chối chấm dữ liệu trích trên mô hình
đọc khác, vì cùng một chỉ số cột ở hai mô hình mang nghĩa khác nhau. `serve/` là dịch vụ web, trang chủ,
hệ RAG minh họa và Docker (slide 22–23).

Ba nguyên tắc: cấu hình mỗi thí nghiệm là một file YAML (định dạng văn bản có cấu trúc, dễ đọc) được
kiểm tra bằng pydantic (thư viện xác nhận dữ liệu đúng kiểu) — 21 file, mọi thứ ảnh hưởng kết quả đều
nằm trong file và có mã băm; kết quả là file `results/runs.jsonl` — 35 dòng, mỗi dòng ghi kèm mã commit
(phiên bản mã nguồn) và mã băm cấu hình, mọi bảng trong báo cáo sinh bằng script từ file này chứ không
gõ tay.

**Số liệu lấy từ.** `docs/SPEC.md` mục 1–2.

---

## Phần 5 · Hiện thực (Chương 6)

### Slide 20 — 16 thí nghiệm, một card T4

**Slide này nói gì.** Toàn cảnh khối lượng thực nghiệm.

**Nhìn hình thế nào.** Lưới 16 ô E01–E16, tô theo ba màu của ba câu hỏi nghiên cứu; bốn thẻ số ở dưới.

**Giải thích chi tiết.** Mỗi ô là một *thí nghiệm* (experiment, viết tắt E). CH1 (cam) gồm E01–E08:
baseline bề mặt, tái lập Lookback Lens, chunk-aware, hai cách chia đoạn, định vị chú ý, ngữ cảnh dài, bỏ
bằng chứng. CH2 (lam ngọc) gồm E09–E11 và E14: bộ mã hóa tinh chỉnh, LLM giám khảo, bảng đánh đổi, bậc
thang 7B/3B/1.5B. CH3 (tím) gồm E12, E13, E15, E16: ablation (bỏ từng nhóm đặc trưng xem mất gì), đổi họ
mô hình đọc sang Sailor2, đối chứng ViWikiFC, chéo bộ. Tổng cộng khoảng 120 nghìn lượt đọc trên Kaggle,
4 mô hình đọc, 3 bộ dữ liệu, và **783 ca kiểm thử tự động** (unit test — các đoạn mã tự kiểm tra rằng mã
chính chạy đúng; chạy được trên máy thường, không cần GPU).

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` mục 2.

### Slide 21 — Kỷ luật đo

**Slide này nói gì.** Ba nguyên tắc để con số trong báo cáo tin được — và một lần đề tài tự bắt lỗi mình.

**Nhìn hình thế nào.** Ba thẻ, một đoạn văn.

**Giải thích chi tiết.** (1) *Chọn trên dev, chấm test một lần*: mọi lựa chọn (gộp đầu ra sao, lấy bao
nhiêu đầu) quyết định trên tập dev; tập test chỉ chấm sau khi đã khóa — nếu chọn trên test thì điểm test
không còn khách quan. (2) *Khoảng tin cậy 95 % bootstrap*: với 700 mẫu test, lấy mẫu lại ngẫu nhiên nhiều
lần để ước lượng điểm có thể dao động bao nhiêu; khoảng này rộng khoảng 0,065 — nghĩa là hai phương pháp
chênh nhau dưới mức đó thì **không thể kết luận** ai hơn. Khoảng này rộng gấp đôi biến thiên do đổi seed,
nên nó mới là thứ quyết định. (3) *Đo chi phí xen kẽ*: card T4 tự hạ xung 10–15 % khi chạy liên tục
nhiều phút (tản nhiệt thụ động), nên so tốc độ hai mô hình mà chạy nối nhau trong cùng phiên sẽ thiên
vị mô hình chạy trước; đề tài đo 7B → 3B → 1.5B rồi lặp lại, mỗi lượt một tiến trình riêng, hai lượt
lệch nhau chỉ 0,04–2,09 %.

Đoạn cuối kể một lần tự sửa: Bảng 1 từng ghi hai giá thời gian khác nhau (464 và 528 ms) cho hai dòng
dùng **cùng một lượt trích** — chênh 64 ms chỉ là nhiễu đo. Giờ bảng đánh đổi sinh bằng script lấy chi
phí từ mô hình đọc, có ca kiểm thử khóa để lỗi này không lặp lại.

**Số liệu lấy từ.** `CLAUDE.md` mục 5; `docs/EXPERIMENTS.md` mục 3 và Bảng 8.

### Slide 22 — Ba cách dùng

**Slide này nói gì.** Sản phẩm dùng được theo ba cách: thư viện Python, dịch vụ REST, Docker.

**Nhìn hình thế nào.** Ba thẻ, mỗi thẻ vài dòng mã.

**Giải thích chi tiết.** *Thư viện*: ba dòng Python — nạp bộ phát hiện từ file (`from_pretrained`),
gọi `score(context, question, response)`, nhận nhãn, điểm rủi ro và tỷ trọng chú ý từng đoạn. Bộ phát
hiện chỉ nặng 11,5 KB (mô hình đọc Qwen 15 GB tải riêng). Kiểm tra: bundle chấm lại 700 mẫu test cho kết
quả trùng **700/700** với lúc thí nghiệm. *REST* (giao diện web để chương trình khác gọi qua mạng): các
địa chỉ `POST /score` (chấm một mẫu), `/score/batch` (tối đa 64 mẫu), `/demo/ask` (hỏi hệ RAG minh họa),
`GET /health` (trạng thái: đang nạp / sẵn sàng / lỗi); mô hình nạp trong luồng nền để dịch vụ trả lời
ngay từ giây đầu. *Docker* (đóng gói toàn bộ môi trường vào một "ảnh" chạy giống nhau trên mọi máy):
`docker compose up --build`; máy không có GPU thì báo lỗi rõ sau 6 giây thay vì tải 15 GB rồi mới hỏng.

**Số liệu lấy từ.** Các đầu việc T36–T38 trong `TASKS.md`; `README.md`.

### Slide 23 — Trang chủ

**Slide này nói gì.** Trang web giới thiệu kiêm công cụ chấm, có cú Lens.

**Nhìn hình thế nào.** Ảnh chụp trang chủ và ba thẻ.

**Giải thích chi tiết.** Mắt cú dõi theo con trỏ và đổi màu theo phán quyết (xanh lá trung thực, vàng
nội tại, đỏ ngoại lai) — ẩn dụ của đề tài hiện ra trước khi khách đọc chữ nào. *Chế độ phát lại*: khi mở
trang trên máy không có GPU, trang tự chuyển sang hiển thị kết quả đã chạy sẵn trên Kaggle (file
`replay.json`), nên chép lên GitHub Pages là chạy được. Ngữ cảnh được tô màu theo tỷ trọng chú ý, cắt
đúng theo vị trí ký tự nên không lệch chữ.

**Số liệu lấy từ.** T39, T39B; mã ở `src/vihallulens/serve/static/index.html`.

---

## Phần 6 · Kết quả (Chương 7)

### Slide 24 — Trên ViHallu: 0,757

**Slide này nói gì.** Kết quả chính cho CH1: phương pháp đạt ngang bộ mã hóa tinh chỉnh; và tín hiệu dồn
vào vài đầu chú ý.

**Nhìn hình thế nào.** Trái: sáu thanh ngang mọc lên với con số macro-F1 — bốn thanh xám là các phương
pháp so sánh, thanh cam là Lookback Lens tái lập (0,745), thanh lam ngọc là chunk-aware (0,757). Sau đó
mỗi thanh có thêm **vạch ngang trắng có hai đầu**: đó là khoảng tin cậy 95 %. Rê chuột lên thanh để xem
khoảng. Phải: lưới 27 hàng (lớp) × 28 cột (đầu); các ô cam hiện dần là 20 đầu có trọng số lớn nhất trong
bộ phân loại Lookback Lens; hai ô chuyển lam ngọc và nhấp nháy là `l5_h7` (lớp 5, đầu 7) và `l17_h4`. Rê
chuột lên ô để xem lớp, đầu, trọng số.

**Giải thích chi tiết.** Thứ tự: bề mặt 0,656 · Gemini giám khảo 0,664 · PhoBERT 0,749 · XLM-R 0,776 ·
Lookback gộp 0,745 · **chunk-aware 0,757** (khoảng tin cậy 0,724–0,789). XLM-R cao hơn 0,019 nhưng hai
khoảng tin cậy **chồng nhau**, nên đúng cách nói là "ngang", không phải "thua". Cùng lúc chunk-aware có
**ECE 0,044 tốt nhất bảng** (*ECE* — Expected Calibration Error: khi hệ thống nói "tôi tin 90 %" thì có
đúng 90 % lần không; càng nhỏ càng đáng tin; XLM-R 0,097) và nhị phân (chỉ hỏi có ảo giác hay không)
0,864. Tất cả với 579 tham số chạy trên CPU, so với 560 triệu của XLM-R.

Lưới bên phải trả lời "mô hình nhìn bằng đầu nào": tín hiệu **dồn vào một số ít đầu**, đúng như bài gốc
nhận xét. Hai đầu dẫn đầu (|w| 0,965 và 0,901) cách hẳn phần còn lại (đầu thứ mười chỉ 0,54); các đầu có
ích rải khắp độ sâu (lớp 0, 1, 2, 5, 9, 17, 20, 24) chứ không dồn về cuối. Riêng `l17_h4` **dẫn đầu trên
cả ba bộ dữ liệu** — dấu hiệu nó là thuộc tính của mô hình đọc, không phải của một bộ dữ liệu.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 1; lưới từ `results/runs.jsonl` (dòng E02, khóa
`top_features`).

### Slide 25 — Mô hình thật sự nhìn vào đoạn bằng chứng: 87,8 %

**Slide này nói gì.** Bằng chứng trực tiếp rằng cơ chế hoạt động — không suy ra từ điểm phân loại.

**Nhìn hình thế nào.** 22 ô là 22 đoạn của một ngữ cảnh ISE-DSC01; ô viền cam là đoạn chứa bằng chứng.
Với mỗi mẫu, cột chú ý mọc trong 22 ô, một **mũi tên** hạ xuống đoạn được nhìn nhiều nhất: trùng ô cam
→ "trúng", không trùng → cột đỏ, "trượt". Hình quét 41 mẫu, chậm ở vài mẫu đầu rồi nhanh dần; bộ đếm
bên phải chạy tới **36 / 41 = 87,8 %**; dãy chấm ghi từng mẫu xanh/đỏ.

**Giải thích chi tiết.** Đây là thí nghiệm E06. Bộ ISE-DSC01 có đánh dấu câu bằng chứng, nên với mỗi
mẫu ta biết mô hình **nên** nhìn vào đoạn nào. Chỉ số *hit@1*: đoạn được đầu chú ý nhìn nhiều nhất có
phải đoạn bằng chứng không. Trên 2.376 mẫu có bằng chứng định vị được, trung bình 22,6 đoạn mỗi ngữ
cảnh, đầu chú ý tốt nhất (lớp 14, đầu 6) đạt **hit@1 = 0,8779**. Chọn hú họa giữa 22,6 đoạn cho 0,0614
(không phải 1/22,6 vì các đoạn dài ngắn không đều) — tức gấp **14,29 lần** sàn ngẫu nhiên. Trung bình
của cả 756 đầu là 0,332, vẫn gấp 5,4 lần sàn.

Hình trên slide **tái hiện tỷ lệ** bằng 41 mẫu mô phỏng (36 trúng) để nhìn được quá trình; con số thật
đo trên 2.376 mẫu. Kết quả này được **lặp lại độc lập** trên bộ thứ hai (ViWikiFC, thí nghiệm E08) với
sai lệch chỉ 0,003 — cùng đầu, cùng tỷ lệ, khác bộ dữ liệu, tức đây là tính chất của mô hình đọc.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 2 và Bảng 2c.

### Slide 26 — Chia đoạn theo câu thắng cả bốn cấu hình cửa sổ

**Slide này nói gì.** Bảng số của thí nghiệm đã minh họa ở slide 18.

**Nhìn hình thế nào.** Bảng 5 dòng và 5 thanh; dòng đầu tô sáng là cấu hình được chọn.

**Giải thích chi tiết.** Theo câu (trung bình 5,29 đoạn mỗi mẫu) 0,7768; cửa sổ 128 token bước 64: 0,7683;
cửa sổ 64/32: 0,7662; đối chứng 48/48 không chồng lấn: 0,7649; cửa sổ 256/128 (chỉ 1,43 đoạn — gần như
không chia): 0,7589. Thanh vẽ từ mốc 0,70 để nhìn rõ chênh lệch. Đây là điểm trên tập dev vì đây là bước
**chọn** cấu hình; cấu hình thắng (theo câu, min_words = 5) chính là dòng "chunk-aware" ở slide 24.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 3.

### Slide 27 — Nói thẳng ①: chunk-aware không cộng thêm điểm phân loại

**Slide này nói gì.** Kết quả bất lợi, nói trước khi hội đồng hỏi: năm đại lượng hình dạng **không** làm
điểm phân loại cao hơn tỷ lệ gộp một cách có ý nghĩa.

**Nhìn hình thế nào.** Bảng năm dòng ghi hiệu (chunk-aware − lookback gộp) trong năm phép đo; thẻ cam
bên phải hướng dẫn cách đọc.

**Giải thích chi tiết.** E03 trên ViHallu: +0,012. E12 (thêm đặc trưng bề mặt): −0,007. E13 (đổi họ mô hình
đọc sang Sailor2): −0,026. E14 (đổi cỡ mô hình 3B / 1.5B): −0,013 / +0,011. E15 (bộ ViWikiFC, split gốc,
2.091 mẫu test): −0,001. Tất cả nằm gọn trong khoảng tin cậy rộng 0,065. Quan trọng hơn con số là **dáng
điệu**: đổi họ mô hình thì đổi dấu; qua ba cỡ cùng họ thì đảo dấu hai lần. Một đóng góp thật phải cho
hiệu cùng dấu ở mọi phép đo; ở đây không. Nhóm ghi nguyên trạng, không chọn lại cấu hình để "cứu" con số.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 4, 4b, 5, 5b, 6.

### Slide 28 — Nói thẳng ②: vì sao — chồng lấn 99,9 %

**Slide này nói gì.** Giải thích kết quả ở slide 27, rồi định vị lại đóng góp cho đúng.

**Nhìn hình thế nào.** Hai vòng tròn gần trùng nhau: vòng viền cam là tỷ lệ gộp, vòng lam ngọc là
chunk-aware; con số 99,9 % chỉ phần chunk-aware cộng thêm đã nằm sẵn trong tỷ lệ gộp. Ba thẻ bên phải là
ba thứ chunk-aware cho mà tỷ lệ gộp không cho.

**Giải thích chi tiết.** Thí nghiệm phụ trên ISE-DSC01 (22,6 đoạn): so với baseline bề mặt, chunk-aware
một mình cải thiện +0,227; lookback gộp một mình +0,307; **cả hai cộng lại vẫn +0,307**. Nghĩa là mọi thứ
chunk-aware biết về "trung thực hay không", tỷ lệ gộp đã biết — hai tín hiệu **chồng lấn 99,9 %** về mặt
phân loại. Đây là lý do slide 27 không thấy điểm tăng.

Nhưng chunk-aware cho ba thứ tỷ lệ gộp không cho được: (1) **chỉ được đoạn nào** — 87,8 % trùng đoạn bằng
chứng (slide 25), trong khi tỷ lệ gộp chỉ trả một con số; (2) **hiệu chỉnh xác suất tốt hơn** — ECE giảm
từ 0,109 xuống 0,044 và giữ được trên bộ mới (0,050); (3) **bằng chứng cơ chế** — lặp lại trên bộ thứ hai
và phản ứng đúng 4/4 trong phép can thiệp (slide 14). Kết luận về định vị: *định vị đúng* và *phân loại
đúng* là hai việc khác nhau; đề tài đo được cả hai và nói rõ chunk-aware đóng góp ở việc thứ nhất.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 4c.

### Slide 29 — Chi phí: thu mô hình đọc 4,7 lần chỉ mất 0,022

**Slide này nói gì.** Trả lời CH2 bằng bảng đánh đổi và bậc thang ba cỡ mô hình đọc.

**Nhìn hình thế nào.** Trái là biểu đồ tán xạ: trục ngang là thời gian mỗi mẫu (ms, thang log — mỗi vạch
gấp 100 lần vạch trước), trục dọc là macro-F1, cỡ điểm tỷ lệ với số tham số phải huấn luyện. Bốn điểm xám
hiện trước (bề mặt, PhoBERT, XLM-R, Gemini), rồi điểm lam ngọc (7B chunk-aware), rồi ba điểm cam nối nhau
bằng đường gạch: bậc thang 7B → 3B → 1.5B. Phải: ba cặp thanh VRAM và ms/mẫu mọc theo. Rê chuột lên điểm
để xem đủ bốn số.

**Giải thích chi tiết.** Mô hình đọc 7B: macro-F1 0,745 (lookback gộp), 437,6 ms/mẫu, 8.328 MB VRAM,
2.271 tham số. **3B: 0,735, 222,7 ms, 3.710 MB, chỉ 195 tham số** — mất 0,010 điểm để nhanh gấp đôi và
tiết kiệm 56 % bộ nhớ; đây là điểm cân bằng. 1.5B: 0,723, 2.718 MB, nhưng **608,1 ms — chậm hơn cả 7B**.
Nghịch lý này đo được và có lý do: ở float16 mô hình 1.5B tràn số ở **cả 28 lớp** nên buộc phải chạy
bfloat16 (một định dạng số 16 bit khác), mà T4 không hỗ trợ bfloat16 ở phần cứng nên phải giả lập, chậm
4 lần. Bài học ghi ở chân: nấc lùi nhỏ nhất mua được bộ nhớ, không mua được thời gian.

So với XLM-R (0,776; 25,2 ms; 11.231 MB; 560 triệu tham số): XLM-R thắng hai trục tuyệt đối (chính xác
và tốc độ suy luận), hướng nội tại thắng ở tham số phải huấn luyện (195 so với 560 triệu) và ở chỗ không
cần bước huấn luyện GPU. Tiêu đề "thu 4,7 lần" là tỷ lệ 7 tỷ / 1,5 tỷ tham số; "mất 0,022" là 0,745 −
0,723.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 5b (E14) và Bảng 8 (E11).

### Slide 30 — "Trung thực hay không" chuyển được; "sai kiểu nào" thì không

**Slide này nói gì.** Trả lời CH3: bộ phát hiện huấn luyện trên bộ này đem chấm bộ kia thì mất gì.

**Nhìn hình thế nào.** Hai ô *huấn luyện* và *chấm một lần*, một chấm tím bay từ ô trái sang ô phải. Bên
dưới là **dòng chảy** (sankey): khối màu bên trái là lớp bị mất của bộ đích với số mẫu thật; ba dải chảy
sang phải cho biết mô hình đoán chúng thành gì. Hai con số lớn bên phải: macro-F1 ba lớp (đỏ) và nhị
phân (xanh). Hình chạy chiều ViHallu → ISE-DSC01 rồi tự chuyển sang chiều ngược; hai nút trên cùng để
chọn chiều.

**Giải thích chi tiết.** Chiều ViHallu → ISE-DSC01: ba lớp chỉ còn 0,358 (ngẫu nhiên ≈ 0,33) — gãy; nhị phân
0,664 — qua. Lớp mất là **extrinsic**: 1.286 mẫu thật, mô hình chỉ đoán đúng 82 (6,4 %), 988 bị dồn sang
intrinsic. Chiều ISE-DSC01 → ViHallu: ba lớp 0,552, nhị phân 0,776; lớp mất là **intrinsic**: 234 mẫu thật,
đoán đúng 72 (30,8 %), 136 dồn sang extrinsic. Lớp *no* chuyển được ở cả hai chiều (62 % và 82 % đúng).

Lý do không nằm ở đặc trưng mà ở **định nghĩa nhãn**: "extrinsic" của ViHallu là câu GPT-4o bịa thêm;
"extrinsic" của ISE-DSC01 là nhãn NEI do người gán — cùng tên, khác nghĩa. Tín hiệu "có bám ngữ cảnh
không" là của mô hình đọc nên chuyển được; "sai kiểu nào" là của từng bộ nhãn nên không. Chân slide nhắc
thêm E15: trên split gốc của ViWikiFC đề tài đạt 70,7 so với công bố SemViQA 83,9 — thua 13 điểm, vì
tập test ấy dùng lại 100 % ngữ cảnh train (slide 13), và bộ mã hóa 560 triệu tham số "nhớ" được ngữ
cảnh, còn hồi quy 2.271 tham số thì không.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 7 (E16) và Bảng 6 (E15).

### Slide 31 — Demo thật: bộ phát hiện tự bắt được một ảo giác không ai dàn dựng

**Slide này nói gì.** Chạy cả hệ thống đầu-cuối trên Kaggle; mô hình sinh tự bịa, bộ phát hiện tự bắt.

**Nhìn hình thế nào.** Bốn nút trên cùng là bốn câu hỏi thật. Trái là ngữ cảnh ba tài liệu; phải là khung
câu trả lời **gõ ra từng chữ**, cụm bịa chuyển đỏ. Sau đó từng câu của ngữ cảnh **tô màu** theo tỷ trọng
chú ý (rê chuột để xem phần trăm), thanh rủi ro chạy, nhãn hiện. Cú Lens ở góc phải: **mắt đổi màu** theo
phán quyết và **nhìn theo con trỏ** khi bạn rê chuột trong hình. Hình tự chạy câu Fansipan (trung thực,
0,008) rồi câu Hồ Hoàn Kiếm (ngoại lai, 0,997); bấm nút để xem hai câu còn lại.

**Giải thích chi tiết.** Hệ RAG minh họa: 21 tài liệu, BM25 chọn 3, Qwen2.5-3B (bfloat16) viết câu trả
lời, Qwen2.5-7B đọc lại và chấm. Không ai viết sẵn câu trả lời — mô hình sinh tự viết và tự bịa cụm "trở
về dinh thự"; bộ phát hiện chấm 0,997 và gọi đúng "ngoại lai". Câu "Phở xuất hiện ở đâu" (0,883, ngoại
lai) là trường hợp tranh cãi vì mô hình vừa nói theo tài liệu vừa thêm suy đoán.

*Phát hiện kèm* ở chân slide: mô hình đọc 7B chạy float16 (định dạng để chấm nhanh trên T4) **không sinh
chữ được** — lớp 27 tràn số làm mọi xác suất thành NaN (không phải số), đầu ra toàn dấu "!". Vì thế mô
hình sinh phải là một mô hình thứ hai chạy bfloat16. Hệ quả cho lập luận của đề tài: câu "chi phí biên
gần bằng 0 vì lượt đọc dù sao cũng phải chạy" chỉ đúng trên phần cứng có bfloat16 gốc, chưa đo được trên
T4 — được ghi thành hạn chế ở slide 33.

**Số liệu lấy từ.** `results/t40/t40_rag.json`, `results/t40/kaggle_log_2026-09-11_lan3.txt`.

---

## Phần 7 · Kết luận (Chương 8)

### Slide 32 — Sai sót: bộ phát hiện thấy ảo giác tốt hơn hẳn gọi tên nó

**Slide này nói gì.** Phân tích 169 mẫu chấm sai để biết hệ thống hỏng ở đâu.

**Nhìn hình thế nào.** Số 48,5 % đếm lên; sáu thanh là sáu cặp nhầm với số mẫu; năm thẻ bên phải là
năm "hình dạng lỗi" tìm thấy khi đọc tay.

**Giải thích chi tiết.** Trên 700 mẫu test, sai 169 (24,1 %). Cặp nhầm nhiều nhất: intrinsic → extrinsic
(46) và extrinsic → intrinsic (36) — cộng lại 82/169 = **48,5 %** là nhầm **giữa hai loại ảo giác với
nhau**, tức hệ thống biết đó là ảo giác nhưng gọi sai tên. 49 mẫu (29 %) là bỏ sót ảo giác thành trung thực (33 + 16), 38 mẫu (22 %) là báo nhầm câu trung thực
thành ảo giác (27 + 11). Đây là cùng một ranh giới mà cột nhị phân ở slide 24 (0,864) và slide 30 chỉ ra: **thấy** tốt hơn
**gọi tên**.

Năm hình dạng lỗi khi đọc tay 100 mẫu: (1) một mệnh đề bịa nằm giữa ba câu chép đúng — vì cả câu trả lời
được tóm thành **một** véc-tơ trung bình nên mệnh đề bịa bị nhòa; (2) một câu trả lời trộn cả hai loại ảo
giác nhưng chỉ có một nhãn; (3) phủ định lật ngược bằng chính từ ngữ của tài liệu ("không phải triều Lý")
— chú ý biết mô hình *nhìn đâu* nhưng không biết nó *nói gì* về chỗ đó; (4) câu hỏi có tiền đề sai (13
câu trong dữ liệu lọt cả nhãn "Adversarial Question:" — câu hỏi đối kháng); (5) nhãn gốc tranh cãi. Ba
hình dạng đầu cùng chỉ về một giới hạn: chấm cả phản hồi bằng một véc-tơ.

**Số liệu lấy từ.** `docs/EXPERIMENTS.md` Bảng 9; `results/error_analysis.csv`.

### Slide 33 — Đã làm được, và chưa

**Slide này nói gì.** Tổng kết hai cột, nói rõ cả phần chưa.

**Giải thích chi tiết.** Đã: hệ phát hiện ba lớp cho tiếng Việt từ tín hiệu chú ý, 0,757, ngang bộ mã hóa
tinh chỉnh, hiệu chỉnh xác suất tốt nhất; cơ chế được xác nhận trực tiếp (87,8 %, lặp lại trên bộ thứ hai,
can thiệp 4/4); bậc thang chi phí đo đúng cách, 3B là điểm cân bằng; hệ thống hoàn chỉnh với demo thật
bắt được ảo giác. Chưa: năm đại lượng hình dạng không cộng điểm phân loại (slide 27); ba lớp không chuyển
chéo bộ (slide 30); mệnh đề bịa bị nhòa vì một véc-tơ (slide 32); chi phí gắn với T4, Docker chưa kiểm trên
máy có GPU, lượt đọc tay 100 mẫu chưa xong.

### Slide 34 — Hướng phát triển

**Giải thích chi tiết.** (1) **Chấm theo đoạn phản hồi** thay vì cả phản hồi — tách "nhìn vào đâu" khỏi
"nói gì về chỗ đó"; trả lời trực tiếp ba hình dạng lỗi hàng đầu. (2) **Gộp bộ dữ liệu với nhãn cùng
nghĩa**, hoặc chấp nhận bộ phát hiện nhị phân khi dùng chéo bộ. (3) **Đo chi phí biên trên hệ RAG thật**
với phần cứng có bfloat16 gốc: một bản 7B vừa đọc vừa viết — khi đó lập luận "chi phí gần 0" mới kiểm
được. Tùy chọn: thí nghiệm E17 chuyển miền sang bộ ViFactCheck nếu còn thời gian sau khi viết báo cáo.

---

## Phần 8 · Kết

### Slide 35 — Tiến độ và bốn câu xin ý kiến

**Giải thích chi tiết.** Thanh tiến độ 41/52 đầu việc (theo `TASKS.md`); các mốc còn lại: nộp báo cáo
trước 22/11, phản biện 23–29/11, bảo vệ 30/11–06/12/2026. Bốn câu hỏi dành cho thầy: (1) định vị đóng
góp — đóng góp chính là bằng chứng cơ chế và khả năng chỉ đoạn, còn điểm phân loại báo cáo trung thực là
không hơn; cách định vị này có hợp một khóa luận không? (2) chương đánh giá viết theo ba câu hỏi nghiên
cứu thay vì theo thứ tự 16 thí nghiệm? (3) có làm E17 không? (4) bộ phát hiện mặc định giữ 7B (nhất
quán mọi bảng) hay đổi 3B (điểm cân bằng chi phí)?

### Slide 36 — Cảm ơn

Câu kết lặp lại ý slide 2 — "Mắt không nói dối" — và địa chỉ kho mã nguồn `github.com/wsunicorn/vihallulens`,
nơi có toàn bộ mã, cấu hình, kết quả và tài liệu mà file này dẫn tới.
