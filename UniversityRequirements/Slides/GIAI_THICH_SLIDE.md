# Giải thích từng slide và kịch bản thời gian — bộ `slide_hoi_dong_23.html`

Viết ngày 22/10/2026 cho bộ chính 23 slide, thay bản cũ của `slide_v2.html` (bản cũ giữ ở
`GIAI_THICH_SLIDE_v2_cu.md`). File này dành cho hai việc:

1. **Diễn tập.** Phần đầu là kịch bản thời gian có hai phương án, vì GVHD chưa cho biết thời lượng
   trình bày.
2. **Hiểu từng slide đủ sâu để trả lời câu hỏi.** Mỗi slide có bốn phần: *nói gì* (một câu),
   *trên màn hình* (thao tác được với hình), *giải thích* (thuật ngữ và lý do), và *nguồn số liệu*.
   Câu hỏi dễ gặp thì trỏ sang `HOI_DAP_HOI_DONG.md`, ví dụ (→ A1).

Lời nói cho từng slide nằm sẵn trong ghi chú diễn giả (phím `N` khi trình chiếu). File này không
chép lại lời nói đó, chỉ giải thích những gì nằm phía sau.

---

## Kịch bản thời gian

Thời lượng bản đủ tính từ số chữ của ghi chú diễn giả, ở tốc độ khoảng 125 chữ/phút, cộng 10 giây
cho slide có thao tác. Bản 15 phút giữ nguyên thứ tự slide, chỉ rút lời: những slide ghi *lướt* thì
nói một câu rồi chuyển.

| Slide | Nội dung | Bản đủ | Mốc | Bản 15 phút | Mốc | Người nói |
|---|---|---|---|---|---|---|
| 1 | Bìa | 0:50 | 0:50 | 0:30 | 0:30 | |
| 2 | Hai kiểu bịa | 1:00 | 1:50 | 0:45 | 1:15 | |
| 3 | Bài toán | 1:10 | 3:00 | 0:50 | 2:05 | |
| 4 | Động lực: ba cách hiện có đều đắt | 0:55 | 3:55 | 0:40 | 2:45 | |
| 5 | Khoảng trống, ba câu hỏi | 0:50 | 4:45 | 0:40 | 3:25 | |
| 6 | Bản đồ các hướng | 1:05 | 5:50 | 0:20 *lướt* | 3:45 | |
| 7 | Lookback Lens | 0:55 | 6:45 | 0:45 | 4:30 | |
| 8 | Ba bộ dữ liệu, chia theo ngữ cảnh | 1:00 | 7:45 | 0:40 | 5:10 | |
| 9 | Chunk-aware | 0:50 | 8:35 | 0:45 | 5:55 | |
| 10 | Quy trình một lượt đọc | 0:55 | 9:30 | 0:45 | 6:40 | |
| 11 | Bộ nhớ và forward hook | 0:55 | 10:25 | 0:30 | 7:10 | |
| 12 | Hệ thống bốn tầng | 0:50 | 11:15 | 0:25 *lướt* | 7:35 | |
| 13 | Demo Hồ Hoàn Kiếm | 0:55 | 12:10 | 0:40 | 8:15 | |
| 14 | Kết quả chính | 0:50 | 13:00 | 0:50 | 9:05 | |
| 15 | Định vị 87,8 % | 0:45 | 13:45 | 0:45 | 9:50 | |
| 16 | Can thiệp | 0:50 | 14:35 | 0:45 | 10:35 | |
| 17 | Kết quả bất lợi | 1:00 | 15:35 | 0:50 | 11:25 | |
| 18 | Chi phí, bậc thang mô hình | 0:55 | 16:30 | 0:30 | 11:55 | |
| 19 | Chuyển giao chéo bộ | 0:55 | 17:25 | 0:40 | 12:35 | |
| 20 | Năm giả thuyết | 1:10 | 18:35 | 0:50 | 13:25 | |
| 21 | Làm được, chưa làm được | 0:55 | 19:30 | 0:40 | 14:05 | |
| 22 | Tài liệu tham khảo | 0:40 | 20:10 | 0:10 *lướt* | 14:15 | |
| 23 | Cảm ơn | 0:15 | 20:25 | 0:10 | 14:25 | |

Cộng thêm khoảng 1–2 phút chuyển slide và ngắt nghỉ, **bản đủ chừng 22 phút**, bản rút chừng
15–16 phút.

**Chọn người nói.** Nên đổi người ở ranh giới phần, không đổi giữa một phần, để mỗi người nói
liền mạch một đoạn. Hai chỗ cắt tự nhiên: sau slide 8 (hết dữ liệu, sang phương pháp) và sau
slide 13 (hết hệ thống, sang kết quả). Cột *Người nói* để trống cho nhóm tự điền.

**Khi diễn tập**, bấm giờ theo cột *Mốc*. Trễ quá 30 giây ở một mốc thì bản sau rút lời ở các
slide *lướt*, không cắt slide kết quả 14–20.

---

## Phần 1 · Giới thiệu (Chương 1)

### Slide 1 — Bìa

**Nói gì.** Tên đề tài, hai sinh viên, giảng viên hướng dẫn.

**Giải thích.** Tên đề tài tách ra từng cụm:

- *Mô hình ngôn ngữ lớn* (LLM): mô hình học trên rất nhiều văn bản để viết tiếp văn bản. Nó viết
  trôi chảy nhưng không có gì bảo đảm điều nó viết là đúng.
- *Tăng cường truy xuất* (RAG): trước khi LLM trả lời, hệ thống tìm vài đoạn tài liệu liên quan
  (gọi là *ngữ cảnh*) đưa cho nó đọc.
- *Ảo giác*: câu trả lời sai hoặc không có căn cứ trong tài liệu, nhưng giọng văn vẫn tự tin.
- *Tín hiệu chú ý nội tại*: *chú ý* (attention) là cơ chế bên trong LLM quyết định khi xử lý mỗi
  từ thì nhìn vào những từ nào. *Nội tại* nghĩa là tín hiệu này có sẵn trong mô hình, không phải
  hỏi thêm ai.

**Nguồn.** `CLAUDE.md` mục 1.

### Slide 2 — Có hai kiểu bịa

**Nói gì.** Bài toán không dừng ở "đúng hay sai": phải tách được hai kiểu ảo giác.

**Trên màn hình.** Ba câu trả lời mẫu cạnh một đoạn tài liệu. Rê chuột lên phần tô màu thì thấy
chỗ tương ứng trong tài liệu; bấm một thẻ thì đường nối nổi lên.

**Giải thích.**

- *Nội tại* (intrinsic): có đọc tài liệu nhưng nói ngược với nó, ví dụ đổi triều Lý thành triều
  Trần.
- *Ngoại lai* (extrinsic): nói điều tài liệu không hề có.
- Hai kiểu này cần hai cách sửa khác nhau. Nội tại thì sửa cho khớp tài liệu; ngoại lai thì xóa
  hoặc đi tìm thêm tài liệu. Vì vậy biết *kiểu* lỗi có giá trị thực tế.
- Ba điểm rủi ro trên slide (0,001; 0,998; 1,000) là điểm thật do hệ thống chấm.

**Nguồn.** Cách gán nhãn theo ViHallu; phân loại theo Ji và cộng sự (2023), Maynez và cộng sự
(2020). Quyển mục 2.3.

### Slide 3 — Bài toán

**Nói gì.** Đầu vào là ngữ cảnh, câu hỏi và câu trả lời; đầu ra là một trong ba nhãn, kèm điểm
rủi ro.

**Trên màn hình.** Sơ đồ đầu vào → mô hình đọc → bộ phân loại → nhãn. Rê chuột lên khối bộ phát
hiện để xem chú thích.

**Giải thích.**

- Câu trả lời có thể của *bất kỳ* hệ RAG nào. Mô hình đọc chỉ đọc lại, không tự viết.
- *Điểm rủi ro* = 1 − xác suất trung thực.
- Bốn ràng buộc là ràng buộc của đề tài chứ không phải tùy chọn: không gọi giám khảo, không tinh
  chỉnh LLM, vừa một GPU T4 16 GB, tiếng Việt ba lớp.

**Nguồn.** Quyển mục 1.3–1.4, 4.1, 4.7.

### Slide 4 — Động lực

**Nói gì.** Ba cách bắt ảo giác hiện có, cách nào cũng phải trả một cái giá.

**Giải thích.**

- *LLM giám khảo*: hỏi một LLM khác chấm. Gemini bản miễn phí mất khoảng 8,2 giây mỗi câu, đã gồm
  thời gian tự giãn nhịp theo hạn mức; dữ liệu phải gửi ra ngoài.
- *Bộ mã hóa tinh chỉnh*: PhoBERT, XLM-R. Chính xác nhất, nhưng phải huấn luyện hàng trăm triệu
  tham số trên GPU.
- *Đặc trưng bề mặt*: chín tham số, rẻ nhưng thô.
- *macro-F1*: điểm từ 0 đến 1, trung bình F1 của ba lớp; đoán bừa được khoảng 0,33.

**Nguồn.** Quyển Bảng 6.1 và 6.14. Gemini chỉ chấm 300 mẫu (→ C2).

### Slide 5 — Khoảng trống và ba câu hỏi

**Nói gì.** Ba khoảng trống trở thành ba câu hỏi nghiên cứu. Mỗi thẻ câu hỏi ghi slide nào trả
lời nó.

**Giải thích.** Ba câu hỏi được phát biểu lại thành năm giả thuyết ở Bảng 1.1 của quyển, và được
kiểm từng cái ở slide 20. Khi bị hỏi "đề tài trả lời được câu hỏi nào", chỉ vào slide 20.

---

## Phần 2 · Cơ sở lý thuyết (Chương 2)

### Slide 6 — Các hướng phát hiện ảo giác

**Nói gì.** Đặt các hướng đã có lên hai trục: số tham số phải huấn luyện, và chi phí mỗi lần chấm.
Khóa luận nằm ở nhánh trọng số chú ý.

**Trên màn hình.** Rê chuột lên từng ô để xem tín hiệu mà hướng đó dùng và hạn chế của nó.

**Giải thích.**

- *SelfCheckGPT*: kiểm tính nhất quán bằng cách cho mô hình sinh nhiều lần rồi so các bản với
  nhau, nên tốn nhiều lượt sinh.
- *Hướng nội tại*: dùng trạng thái bên trong mô hình, như trọng số chú ý (Lookback Lens, ReDeEP)
  hoặc trạng thái ẩn (Azaria và Mitchell, 2023). Chỉ cần một lượt đọc và một bộ dò nhỏ.

**Nguồn.** Quyển Bảng 2.1. Các công trình 2025–2026 (ContextCite, ARC-JSD, Multi-View Attention,
LUMINA) đang chờ thêm vào mục 2.4 ở T42B (→ A4).

### Slide 7 — Lookback Lens

**Nói gì.** Phương pháp nền: với mỗi token của câu trả lời, đo xem chú ý dành cho tài liệu nhiều
hay dành cho phần câu trả lời đã viết nhiều.

**Giải thích.**

- *Token*: mẩu chữ mà mô hình xử lý, thường là một âm tiết hoặc một phần của từ.
- *Tỷ lệ nhìn lại* = chú ý trung bình trên một token ngữ cảnh, chia cho tổng của nó với chú ý
  trung bình trên một token câu trả lời trước đó. Lấy trung bình theo token chứ không cộng dồn, để
  ngữ cảnh dài không tự nhiên thắng (→ B7).
- *Lớp và đầu chú ý*: Qwen2.5-7B có 28 lớp, mỗi lớp 28 đầu chạy song song. Bỏ lớp 27 vì tràn số
  (→ B2), còn 27 × 28 = 756 con số cho mỗi câu trả lời.

**Nguồn.** Chuang và cộng sự, EMNLP 2024. Công thức gốc ở `docs/REFERENCES.md` mục 1.

---

## Phần 3 · Dữ liệu (Chương 3)

### Slide 8 — Ba bộ dữ liệu, chia theo ngữ cảnh

**Nói gì.** Ba bộ tiếng Việt công khai. Cách chia tập quan trọng không kém cách chọn bộ.

**Trên màn hình.** Bấm hai nút ở góc phải để so chia ngẫu nhiên với chia theo ngữ cảnh.

**Giải thích.**

| Bộ | Vai trò | Điều đặc biệt |
|---|---|---|
| ViHallu | bộ chính, 7.000 mẫu | duy nhất có câu trả lời do LLM thật sự sinh (GPT-4o) |
| ISE-DSC01 | ngữ cảnh dài, trung vị 19 câu | đánh dấu sẵn câu bằng chứng, nên dùng để kiểm định vị |
| ViWikiFC | đối chứng | có bằng chứng cho cả nhãn NEI |

- *Chia theo ngữ cảnh*: mọi câu trả lời trên cùng một tài liệu nằm chung một tập; tỷ lệ 80/10/10,
  seed 42, rò rỉ bằng 0.
- Tập test gốc của ViWikiFC dùng lại 100 % ngữ cảnh của train, nhóm đo được và ghi chú cạnh mọi số
  trên bộ đó (→ C1).

**Nguồn.** Quyển Bảng 3.1, 3.2, 3.4, 3.5; `docs/DATA.md`.

---

## Phần 4 · Phương pháp đề xuất (Chương 4)

### Slide 9 — Chunk-aware

**Nói gì.** Hai câu trả lời cùng dành 62 % chú ý cho ngữ cảnh: một câu dồn vào đúng câu chứa
thông tin, câu kia rải đều. Con số gộp không phân biệt được, còn hình dạng phân bố thì có.

**Giải thích.**

- *Đoạn* (chunk): ở đây là một câu của ngữ cảnh. Câu dưới 5 chữ được gộp vào câu trước (→ B5).
- Năm đặc trưng hình dạng:
  - *entropy*: chú ý dàn trải tới đâu, chuẩn hóa về [0, 1] để không phụ thuộc số đoạn;
  - *tỷ trọng lớn nhất*: phần chú ý của đoạn được nhìn nhiều nhất;
  - *Gini*: chú ý chia đều hay lệch về vài đoạn;
  - *khoảng cách hạng 1–2*: đoạn dẫn đầu bỏ xa đoạn thứ hai bao nhiêu;
  - *độ trôi*: chú ý chuyển đoạn bao nhiêu giữa hai token liền nhau.
- Số trên hình là minh họa nguyên lý, không phải số đo.

**Nguồn.** Quyển mục 4.4–4.5; `src/vihallulens/features/chunk_aware.py`.

### Slide 10 — Một lượt đọc

**Nói gì.** Cả quy trình chỉ cần mô hình đọc một lượt, không sinh thêm chữ nào.

**Giải thích.**

- *Teacher forcing*: đưa sẵn câu trả lời cho mô hình đọc thay vì để nó tự viết, nhờ vậy chấm được
  câu trả lời của bất kỳ ai.
- Mẫu prompt chốt ngày 19/08 và không đổi nữa, vì nó quyết định vị trí mọi token.
- *Giữ 32 đầu*: chọn trên tập dev trong số các cách gộp đầu chú ý. 32 đầu × 6 con số = 192 cột.
  Hồi quy logistic trên 192 cột có 579 tham số.

**Nguồn.** Quyển mục 4.1, 4.2, 4.7; `src/vihallulens/extract/prompt.py`.

### Slide 11 — Bộ nhớ và forward hook

**Nói gì.** Giữ ma trận chú ý của cả 28 lớp thì tràn T4; tính xong lớp nào xóa lớp đó thì vừa.

**Trên màn hình.** Rê chuột lên từng lớp để xem bộ nhớ ở lớp đó.

**Giải thích.**

- Muốn đọc trọng số chú ý thì phải tắt FlashAttention, một cách tính attention nhanh nhưng không
  trả ra ma trận.
- Một lớp ở 4.096 token cần khoảng 0,94 GB; 28 lớp cần khoảng 26 GB.
- *Forward hook*: hàm nhỏ tự chạy ngay khi một lớp tính xong. Hook cộng chú ý theo đoạn rồi trả
  `None` thay cho ma trận, nên không lớp nào phải giữ lại.
- Đỉnh đo thực tế 8.428 MB ở 4.096 token. Con số 8.328 MB ở Bảng 8 là đỉnh trên phân bố độ dài thật
  của ViHallu, ngắn hơn; hai số không mâu thuẫn (→ D1).

**Nguồn.** Quyển mục 4.8, Bảng 2.2; `CLAUDE.md` mục 5.

---

## Phần 5 · Hệ thống (Chương 5)

### Slide 12 — Bốn tầng

**Nói gì.** Thư viện, dịch vụ REST, Docker và giao diện web. Tầng trên chỉ gọi tầng ngay dưới.

**Trên màn hình.** Rê chuột lên từng tầng để xem mô-đun tương ứng.

**Giải thích.**

- Bộ phát hiện đã khớp là một tệp 11,5 KB. Tệp này kèm luôn công thức dựng cột, nên nạp lại chấm
  ra kết quả trùng 700/700 với lúc thí nghiệm.
- **Số ca kiểm thử trên slide (688) đã cũ.** Hiện có 825 ca; phải cập nhật slide và quyển theo
  con số lúc chốt bản cuối.
- Docker chưa build thử trên máy có GPU; chỉ nói "có Dockerfile", không nói "đã chạy Docker".

**Nguồn.** Quyển chương 5.

### Slide 13 — Demo Hồ Hoàn Kiếm

**Nói gì.** Một lượt chạy thật: hệ thống tìm tài liệu, mô hình 3B tự sinh câu trả lời có cụm bịa,
và bộ phát hiện tự chấm ngoại lai với rủi ro 0,997.

**Trên màn hình.** Bấm tên câu hỏi ở góc phải để xem ba ví dụ còn lại.

**Giải thích.**

- Hai mô hình: 3B sinh, 7B đọc. Lý do: ở float16, 7B không sinh được chữ vì lớp 27 tràn số, và T4
  không đủ chỗ cho một bản 7B bfloat16 thứ hai (→ D2).
- *BM25*: cách tìm tài liệu cổ điển theo từ khóa, không cần mô hình.

**Nguồn.** Kaggle T4, 11/09/2026, `notebooks/t40_demo_t4.ipynb`; quyển mục 5.6.

---

## Phần 6 · Thực nghiệm (Chương 6)

### Slide 14 — Kết quả chính

**Nói gì.** Một bộ phân loại tuyến tính trên chú ý đã ngang PhoBERT tinh chỉnh toàn bộ.

**Trên màn hình.** Rê chuột lên từng dòng để xem khoảng tin cậy và số tham số.

**Giải thích.**

- *Khoảng tin cậy 95 %*: vùng điểm có thể dao động nếu đổi tập kiểm tra, tính bằng bootstrap trên
  700 mẫu test. Hai khoảng chồng nhau thì nói "ngang", không nói "hơn" (→ C4).
- Số cần nhớ:

| Phương pháp | macro-F1 | Tham số huấn luyện |
|---|---|---|
| Đặc trưng bề mặt | 0,656 | 9 |
| Gemini (300 mẫu) | 0,664 | 0 |
| Lookback gộp | 0,745 | 2.271 |
| PhoBERT tinh chỉnh | 0,749 | 369 triệu |
| Chunk-aware | 0,757 | 579 |
| XLM-R tinh chỉnh | 0,776 | 560 triệu |

- Hội đồng có thể hỏi về con số 84,80 % của cuộc thi (→ A2).

**Nguồn.** Quyển Bảng 6.1; `docs/EXPERIMENTS.md` Bảng 1.

### Slide 15 — Định vị 87,8 %

**Nói gì.** Kiểm cơ chế trực tiếp: đầu chú ý mạnh nhất nhìn đúng đoạn chứa bằng chứng ở 87,8 % số
mẫu.

**Trên màn hình.** Bấm "Mẫu khác" để xem thêm ví dụ.

**Giải thích.**

- *hit@1*: tỷ lệ mẫu mà đoạn được nhìn nhiều nhất chính là đoạn chứa bằng chứng. Hòa điểm tính là
  trượt.
- Ngữ cảnh trung bình 22,6 đoạn, nên chọn bừa chỉ trúng 6,1 %. 87,8 % gấp 14,3 lần mức đó.
- Chọn đầu trên chính tập báo cáo, nên 0,878 là cận trên. Con số không dính lựa chọn là trung
  bình 756 đầu: 0,332, gấp 5,4 lần chọn bừa (→ A5).
- Lặp lại trên ViWikiFC: trung bình mọi đầu 32,9 % so với 33,2 %.
- Nếu bị hỏi "chú ý có đáng tin bằng cắt bỏ ngữ cảnh không" (E19, không có trên slide): trên 300
  mẫu ViWikiFC, đầu chú ý tốt nhất đạt 0,850, cắt bỏ đạt 0,733 dù tốn 10,9 lượt đọc mỗi mẫu
  (→ A4).

**Nguồn.** Quyển Bảng 6.3, 6.7; `docs/EXPERIMENTS.md` Bảng 2.

### Slide 16 — Can thiệp

**Nói gì.** Rút đúng câu bằng chứng ra khỏi ngữ cảnh thì chú ý tản ra, đúng hướng đã ghi trước
khi chạy.

**Trên màn hình.** Ba nút ở góc phải bật ngữ cảnh A, ngữ cảnh B, hoặc cả hai.

**Giải thích.**

- *Thí nghiệm can thiệp*: giữ nguyên mọi thứ, chỉ thay đúng một yếu tố. Ở đây hai ngữ cảnh mười
  câu chỉ khác nhau đúng câu bằng chứng.
- *Ghi dự đoán trước*: hướng thay đổi mong đợi của từng đặc trưng được ghi trong mã trước khi chạy,
  nên không thể giải thích sau khi đã thấy số.
- 1.836 cặp, bốn đặc trưng hình dạng đổi đúng hướng ở 71–75 % số cặp. Mức thay đổi trung vị nhỏ,
  0,013–0,016 (→ A6).

**Nguồn.** Quyển Bảng 6.6; `scripts/run_extrinsic.py` (`EXPECTED_DIRECTION`).

### Slide 17 — Kết quả bất lợi

**Nói gì.** Thêm đặc trưng hình dạng không làm điểm phân loại tăng; nhóm báo cáo thẳng.

**Trên màn hình.** Rê chuột lên từng điểm.

**Giải thích.**

- *Vùng nhiễu*: chênh nhỏ hơn mức dao động tự nhiên của điểm thì không kết luận được.
- Chunk-aware hơn lookback gộp 0,0116, trong khi điểm tự dao động khoảng ±0,03.
- Năm phép đo thêm (thêm bề mặt, Sailor2, 3B, 1.5B, ViWikiFC) đều nằm trong vùng nhiễu, và dấu còn
  đổi chiều.
- Lý do đo được: trên ISE-DSC01, 99,9 % phần đóng góp của nhóm hình dạng đã có sẵn trong tỷ lệ gộp.
- Đây không phải thất bại của đề tài mà là một phát hiện (→ A1).
- Hai kết quả mới (23/10) cùng chiều, không có trên slide: chấm theo từng câu (E18) không hơn,
  0,734 so với 0,757 (→ A8); trên ViFactCheck (E17), so cùng số đầu thì hình dạng chỉ thêm +0,009,
  lần thứ tư nằm trong vùng nhiễu (→ A9).

**Nguồn.** Quyển Bảng 6.2, 6.8, 6.9, 6.10, 6.12; `docs/EXPERIMENTS.md` Bảng 4, 4c.

### Slide 18 — Chi phí và bậc thang mô hình

**Nói gì.** XLM-R thắng cả độ chính xác lẫn tốc độ tuyệt đối. Hướng chú ý thắng ở số tham số phải
huấn luyện. Nấc 3B là điểm cân bằng.

**Trên màn hình.** Rê chuột lên từng chấm để xem đủ số.

**Giải thích.**

- Số cần nhớ: XLM-R 25,2 ms mỗi mẫu; mô hình đọc 7B 437,6 ms; 3B 222,7 ms với bộ nhớ 3.710 MB, mất
  khoảng 0,01 điểm, và chỉ 195 tham số.
- Bản 1.5B chậm hơn cả 7B vì phải chạy bfloat16, mà T4 không hỗ trợ sẵn kiểu số này.
- Chi phí biên trong một hệ RAG thật là lập luận, chưa đo (→ A3, D2).

**Nguồn.** Quyển Bảng 6.10, 6.14; `docs/EXPERIMENTS.md` Bảng 8.

### Slide 19 — Chuyển giao chéo bộ

**Nói gì.** Câu hỏi "có ảo giác hay không" chuyển được sang bộ khác; câu hỏi "ảo giác kiểu nào"
thì không.

**Trên màn hình.** Bấm hai nút ở góc phải để đổi chiều chuyển giao.

**Giải thích.**

- ViHallu → ISE-DSC01: ba lớp còn 0,358; trong 1.286 câu ngoại lai chỉ 66 câu đoán đúng, 988 câu
  bị gọi thành nội tại. Nhị phân vẫn đạt 0,664 và 0,776.
- Nguyên nhân khả dĩ là hai bộ định nghĩa "ngoại lai" khác nhau (→ A7).
- *SUPPORTED / REFUTED / NEI*: nhãn kiểm chứng thông tin theo FEVER, ánh xạ sang trung thực / nội
  tại / ngoại lai.

**Nguồn.** Quyển Bảng 6.13; `docs/EXPERIMENTS.md` Bảng 7.

---

## Phần 7 · Tự đánh giá (Chương 7–8)

### Slide 20 — Năm giả thuyết

**Nói gì.** Ba trên năm giả thuyết được ủng hộ; giả thuyết chính về chunk-aware thì không.

**Trên màn hình.** Rê chuột để xem thí nghiệm ứng với từng giả thuyết.

**Giải thích.**

| Giả thuyết | Kết quả | Bằng chứng |
|---|---|---|
| H1 tỷ lệ gộp có tín hiệu | ủng hộ | 0,745, vượt bề mặt, ngang PhoBERT |
| H2 chunk-aware hơn tỷ lệ gộp | **không ủng hộ** | +0,012 trong khoảng tin cậy, đổi dấu theo mô hình đọc |
| H3 nhìn đúng đoạn bằng chứng | ủng hộ | 87,8 % |
| H4 rút bằng chứng thì chú ý tản ra | ủng hộ | 71–75 % số cặp đúng hướng |
| H5 chuyển được chéo bộ | bác bỏ ở ba lớp | nhị phân vẫn chuyển được |

**Nguồn.** Quyển Bảng 1.1 và 7.1.

### Slide 21 — Làm được, chưa làm được

**Nói gì.** Tóm tắt kết quả, nói rõ giới hạn và hướng tiếp theo.

**Giải thích.**

- **Slide đang lỗi thời ở hai dòng, phải sửa trong HTML:**
  - "Chưa chạy chuyển miền với ViFactCheck": E17 đã chạy ngày 23/10. Thay bằng ý "trên ViFactCheck
    (tin tức), tín hiệu chuyển được, hình dạng vẫn trong vùng nhiễu" (→ A9).
  - Hướng phát triển "chấm theo từng mệnh đề": E18 đã thử ở mức câu và không giúp. Sửa thành "chấm
    theo đoạn có nhãn mức đoạn; chấm theo câu với nhãn mức phản hồi đã thử, không giúp" (→ A8).
- Dòng "Docker chưa kiểm trên máy có GPU" vẫn đúng.
- Có thể thêm vào phần đã làm được: "so với cắt bỏ ngữ cảnh, đầu chú ý định vị đúng hơn và rẻ hơn
  11 lần" (E19, → A4).

### Slide 22 — Tài liệu tham khảo

**Nói gì.** Các công trình chính, đánh số theo danh mục của quyển.

**Giải thích.** Số trong ngoặc vuông phải khớp danh mục của quyển. Khi T42B thêm bốn tài liệu mới
và đánh lại số, phải sửa cả slide này.

### Slide 23 — Cảm ơn

Mời hội đồng đặt câu hỏi. Mở sẵn `HOI_DAP_HOI_DONG.md` trên máy để tra nhanh.
