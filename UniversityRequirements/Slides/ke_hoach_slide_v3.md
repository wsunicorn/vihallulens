# Kế hoạch slide v3 — bản hoàn thiện, dùng từ giờ đến buổi bảo vệ

> Bản thảo luận, 02/10/2026. **Đã chốt** (mục 6): hướng A — học thuật nền sáng; cú Lens chỉ ở
> bìa; số slide được tăng nếu hợp lý. Bước tiếp: dựng slide mẫu để duyệt kiểu sơ đồ, rồi mới làm
> cả bộ.
>
> Mục tiêu do người dùng đặt: một bản dùng được cả lúc gửi thầy góp ý lẫn lúc bảo vệ; số slide
> vừa đúng lượng nội dung, không dồn; chữ cô đọng; người xem lần đầu hiểu được; sửa mọi mặt —
> phong cách, chuyển động, hình ảnh, sơ đồ mô hình và quy trình, câu chữ. Gửi thầy dạng HTML
> tự chứa + PDF.

---

## 1. Chẩn đoán bản v2 hiện tại (36 slide)

| Vấn đề | Biểu hiện cụ thể ở v2 |
|---|---|
| **Mạch kể** | Bảy phần đi theo thứ tự chương của quyển báo cáo (dữ liệu → phương pháp → hệ thống → kết quả), nên người nghe phải đi qua 23 slide mới tới kết quả chính. Phát hiện quan trọng nhất (định vị 87,8 % và "nhìn đúng chỗ nhưng không gọi đúng tên lỗi") nằm ở slide 25–28. Slide lưới 16 thí nghiệm bắt người nghe nhớ mã E01–E16 mà không dùng lại. |
| **Sơ đồ động khó theo** | Nhiều thứ chuyển động cùng lúc: slide 8 vừa bắn tia vừa tô ma trận và lặp vô hạn; slide 17 chạy hai bảng 28 lớp song song; slide 25 nhấp nháy 41 mẫu liên tiếp. Không có nhãn "đang ở bước mấy", nên người xem không biết phải nhìn vào đâu. Tốc độ do máy quyết định, người trình bày không theo kịp lời nói. |
| **Chữ và bố cục** | Khoảng một nửa số slide là 3–6 thẻ chữ, mỗi thẻ một đoạn văn cỡ 20–22 px trên sân khấu 1920 px — tương đương cỡ 10–11 pt khi chiếu, đọc từ cuối phòng không thấy. Nhãn trong sơ đồ 13–16 px còn nhỏ hơn. Dòng nguồn ở chân slide dài cả câu. |
| **Tiêu đề và từ ngữ** | Tiêu đề là chủ đề hoặc câu chơi chữ ("Nói thẳng ①", "Ánh mắt của nó thì không") — người trong nhóm hiểu, người xem lần đầu không. Thuật ngữ (chunk-aware, lookback, hook, ECE, macro-F1, NF4) xuất hiện trước khi được giải thích, hoặc không bao giờ được giải thích trên slide. |
| **Nguồn số liệu** | Chân slide dẫn theo số bảng trong kho mã ("Bảng 1, docs/EXPERIMENTS.md", "Bảng 4c (T35B)"). Thầy và hội đồng cầm quyển báo cáo sẽ không dò được — phải đổi sang số trong quyển (Bảng 6.1, 6.9…). |
| **Lỗi thời** | Slide tiến độ còn ghi 41/52 và bốn câu hỏi cũ; chưa có câu định vị so với 84,80 % của cuộc thi. |
| **Giao diện** | Nền tối với nét lam ngọc mảnh: đẹp trên màn hình nhưng dễ mất chi tiết trên máy chiếu ở phòng sáng, và in PDF tốn mực, khó đọc. |
| **Đóng gói** | `slide_v2.html` cộng thư mục `img/` riêng — gửi mail một file thì mất ảnh. |

---

## 2. Bảy nguyên tắc cho v3

1. **Tiêu đề là một câu kết luận**, không phải chủ đề (kiểu *assertion–evidence*). Đọc riêng các
   tiêu đề từ slide 1 đến hết phải kể được toàn bộ câu chuyện. Ví dụ: thay "Kết quả chính" bằng
   "Chỉ một bộ phân loại tuyến tính trên chú ý đã ngang PhoBERT tinh chỉnh".
2. **Một slide, một ý, một hình làm bằng chứng.** Không còn slide toàn thẻ chữ, trừ slide kết
   luận. Ngoài phần hình, mỗi slide tối đa khoảng 30 chữ.
3. **Thuật ngữ giải thích ngay lần đầu** bằng một câu đời thường ngay trên slide (một dải nhỏ
   "Thuật ngữ:" dưới tiêu đề). Thuật ngữ nào không cần cho câu chuyện thì bỏ khỏi slide, chỉ để
   trong quyển.
4. **Cỡ chữ đọc được từ cuối phòng:** thân bài ≥ 30 px, nhãn trong hình ≥ 22 px, số liệu chính ≥
   48 px trên sân khấu 1920 × 1080.
5. **Chuyển động phục vụ lời nói:** mỗi sơ đồ chia thành các bước có tên (thanh "Bước 1 · 2 · 3"
   ở góc), mỗi lúc chỉ một thứ chuyển động, mỗi bước dừng đủ lâu để nói một câu. Vào slide là
   tự chạy một lần rồi **dừng ở trạng thái cuối đầy đủ**. Không còn sơ đồ dữ liệu lặp vô hạn —
   lặp chỉ dùng cho nền không khí. Phím `R` chạy lại.
6. **Một ngôn ngữ hình thống nhất** cho mọi sơ đồ: cùng một hình cho "mô hình đọc", "đoạn ngữ
   cảnh", "token phản hồi"; cùng một màu cho cùng một khái niệm trên mọi slide (ngữ cảnh, phản
   hồi, trung thực, nội tại, ngoại lai).
7. **Nguồn ghi theo số trong quyển báo cáo** ("Nguồn: Bảng 6.3"), một dòng ngắn.

---

## 3. Mạch kể và danh sách slide — 24 slide chính + 6 slide dự phòng

Mạch kể đi theo câu chuyện, không theo chương: **vấn đề → ý tưởng → cách làm → bằng chứng →
giới hạn → hệ thống → kết luận**. Ví dụ Hồ Hoàn Kiếm mở đầu ở slide 2 và quay lại ở slide 21 để
khép vòng câu chuyện.

| # | Tiêu đề dự kiến (câu kết luận) | Hình làm bằng chứng | Chương |
|---|---|---|---|
| **A. Vấn đề** ||||
| 1 | Bìa — tên đề tài, nhóm, GVHD | Cú Lens (nếu giữ) | — |
| 2 | Hệ RAG trả lời trôi chảy — kể cả khi nó bịa | Câu trả lời Hồ Hoàn Kiếm thật, phần bịa hiện dần màu đỏ | 1 |
| 3 | Có hai kiểu bịa: đọc rồi nói sai, và không đọc mà tự thêm | Một ngữ cảnh, ba câu trả lời đặt cạnh nhau | 1, 2 |
| 4 | Các cách bắt ảo giác hiện nay đều phải trả một cái giá lớn | Ba cột giá: giám khảo LLM, bộ mã hóa tinh chỉnh, đặc trưng bề mặt | 1, 2 |
| **B. Ý tưởng** ||||
| 5 | Khi đọc, mô hình để lộ nó đang nhìn vào đâu | Token trả lời → tia chú ý về ngữ cảnh (định nghĩa "chú ý") | 2 |
| 6 | Lookback Lens: đo xem mô hình nhìn ngữ cảnh nhiều hay ít | Mọi tia gom thành một thanh tỷ lệ | 2 |
| 7 | Ý tưởng của đề tài: không chỉ nhìn bao nhiêu, mà nhìn vào đoạn nào | Thanh tỷ lệ tách thành các cột theo câu; nhọn ↔ tản | 4 |
| 8 | Ba câu hỏi nghiên cứu | Ba thẻ, mỗi thẻ một màu dùng lại ở phần kết quả | 1 |
| 9 | Ba bộ dữ liệu tiếng Việt, chia theo ngữ cảnh để không tự chấm bài mình | Ba khối dữ liệu + sơ đồ chia tập đúng/sai | 3 |
| **C. Cách làm** ||||
| 10 | Chỉ một lượt đọc, không sinh thêm chữ nào | Đường ống 5 bước, từng bước sáng lên | 4 |
| 11 | Giữ cả 28 lớp thì tràn 26 GB; tính xong lớp nào xóa lớp đó thì vừa 8,3 GB | Hai cột bộ nhớ dâng lên, một cột tràn | 4 |
| 12 | Chia ngữ cảnh theo câu tốt hơn chia theo cửa sổ token | Cùng một ngữ cảnh, hai cách cắt; điểm số năm cấu hình | 4, 6 |
| **D. Bằng chứng** ||||
| 13 | Chỉ một bộ phân loại tuyến tính trên chú ý đã ngang PhoBERT tinh chỉnh | Thanh macro-F1 sáu phương pháp + khoảng tin cậy | 6 |
| 14 | Mô hình nhìn đúng đoạn chứa bằng chứng ở 87,8 % số mẫu | 22 đoạn, kim chỉ dừng đúng đoạn bằng chứng; gấp 14 lần đoán bừa | 6 |
| 15 | Rút câu bằng chứng ra thì chú ý tản ra — đúng như dự đoán trước | Cùng phát biểu, hai ngữ cảnh; bốn mũi tên đổi đúng hướng | 6 |
| 16 | Nhưng biết nhìn vào đâu không giúp gọi đúng tên lỗi | Hai vòng tròn trùng 99,9 %; năm phép đo đều nằm trong nhiễu | 6, 7 |
| 17 | Mô hình nhỏ hơn 2,3 lần chỉ mất 0,01 điểm và nhanh gấp đôi | Bậc thang 7B → 3B → 1.5B trên mặt phẳng chính xác – thời gian | 6 |
| 18 | Phân biệt "đúng hay sai" chuyển được sang bộ dữ liệu khác, phân biệt "sai kiểu nào" thì không | Dòng chảy nhãn giữa hai bộ dữ liệu | 6 |
| 19 | Gần một nửa số lỗi là nhầm giữa hai kiểu ảo giác | Ma trận nhầm lẫn, ô nội tại ↔ ngoại lai nổi lên | 6 |
| **E. Hệ thống** ||||
| 20 | Đóng gói thành một hệ thống dùng được: thư viện, dịch vụ, giao diện | Sơ đồ bốn tầng + ảnh giao diện | 5 |
| 21 | Chạy thật: hệ thống tự bắt được câu bịa về Hồ Hoàn Kiếm | Quay lại ví dụ slide 2: điểm rủi ro 0,997, đoạn ngữ cảnh tô màu | 5 |
| **F. Kết luận** ||||
| 22 | Đã làm được gì, và chưa làm được gì | Hai cột | 8 |
| 23 | Bước tiếp theo: chấm theo từng câu của câu trả lời | Ba hướng phát triển | 8 |
| 24 | Cảm ơn | — | — |
| **Dự phòng — chỉ mở khi hội đồng hỏi** ||||
| D1 | Vì sao không đặt 0,757 cạnh 84,80 % của cuộc thi ViHallu | Hai cột: khác tập đánh giá, khác chế độ (đội đứng đầu tinh chỉnh LoRA) | 2, 7 |
| D2 | Chunk-aware hiệu chỉnh xác suất tốt hơn ở ViHallu nhưng không ở sáu cấu hình khác | Bảng 7.2 thành biểu đồ | 7 |
| D3 | Vì sao thua SemViQA 13 điểm trên ViWikiFC | Ba lý do đã đo | 6 |
| D4 | float16 làm lớp 27 tràn số — và hệ quả cho chi phí | Lưới lớp, ô tràn tô đỏ | 4 |
| D5 | Bảng đánh đổi đầy đủ độ chính xác – thời gian – bộ nhớ – tham số | Bảng 6.14 | 6 |
| D6 | Mười sáu thí nghiệm và câu hỏi mỗi thí nghiệm trả lời | Bảng 3.6 | 3 |

So với v2: 36 → 24 slide chính. Bỏ hẳn các slide chỉ có chữ (lộ trình, ràng buộc, năm đại lượng
dạng thẻ, kỷ luật đo, ba cách dùng); nội dung của chúng chuyển vào lời nói, vào hình của slide
khác, hoặc xuống slide dự phòng.

---

## 4. Hướng thị giác — chọn một trong ba (sẽ dựng mẫu 3 slide mỗi hướng để so)

| | Hướng | Mô tả | Hợp với |
|---|---|---|---|
| **A** | **Học thuật sáng** | Nền trắng ngà, chữ xanh đen, một màu nhấn. Sơ đồ nét rõ, kiểu hình minh họa của bài báo khoa học hiện đại. | Máy chiếu phòng sáng, in PDF, hội đồng. **Đề xuất.** |
| **B** | **Tối tinh chỉnh** | Giữ tinh thần "Đêm cú" của v2, nhưng tăng tương phản, chữ to hơn, nét dày hơn. | Màn hình lớn, phòng tối. |
| **C** | **Lai** | Slide nội dung nền sáng, slide mở đầu mỗi phần nền tối có cú Lens. | Muốn giữ dấu ấn cú mà vẫn dễ đọc. |

Bảng màu ngữ nghĩa dùng chung cho cả ba hướng: ngữ cảnh = lam ngọc, phản hồi = hổ phách, trung
thực = xanh lá, nội tại = vàng, ngoại lai = đỏ.

---

## 5. Kỹ thuật

- Giữ sân khấu 1920 × 1080 cố định, GSAP + D3 nhúng sẵn, số liệu đọc từ `results/` như v2.
- **Một file HTML tự chứa:** ảnh nhúng thẳng vào file, không cần thư mục `img/`, mở được không
  cần mạng.
- **PDF xuất tự động** từ trạng thái cuối của mọi slide, 1 slide = 1 trang.
- Ghi chú diễn giả (phím `N`) viết lại theo mạch kể mới; `GIAI_THICH_SLIDE.md` cập nhật theo
  danh sách slide mới.
- Kiểm bằng ảnh chụp từng slide trước khi giao, như v2.

---

## 6. Đã chốt — 02/10/2026

1. **Hướng thị giác A — học thuật nền sáng.**
2. **Cú Lens chỉ xuất hiện ở bìa.** Bỏ khỏi slide kết và mọi slide nội dung.
3. **Số slide được tăng nếu hợp lý** — danh sách ở mục 3 là khung, không phải trần.
4. **Quy tắc sơ đồ (người dùng nhấn mạnh):** slide nào cần trực quan thì phải có sơ đồ minh họa
   **nguyên lý, mô hình, quá trình học thuật** — ví dụ cơ chế chú ý giữa token, ma trận chú ý của
   một đầu, đường đi của dữ liệu qua các lớp, phân bố chú ý theo đoạn, phép can thiệp rút câu bằng
   chứng. **Không** dùng "sơ đồ" là các hộp chữ nối mũi tên để trình bày nội dung văn bản. Sơ đồ
   phải sinh động (chuyển động theo bước như mục 2.5) và tự nó giải thích được nội dung.
5. Gửi thầy: một file HTML tự chứa + PDF.
