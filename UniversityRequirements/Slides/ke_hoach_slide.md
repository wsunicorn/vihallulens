# Kế hoạch slide — trình bày đề tài với GVHD, thứ Tư 16/09/2026

> Bản duyệt. Sửa thẳng vào file này (thêm/bớt slide, đổi thứ tự, đổi lời), tôi dựng theo bản
> cuối. Mọi con số dưới đây chép từ `docs/EXPERIMENTS.md` và `results/`, kèm chỉ dẫn nguồn để
> đối chiếu.

## Khung chung

| Mục | Quyết định đề xuất |
|---|---|
| Thời lượng | 20–25 phút trình bày + 10 phút hỏi đáp → **22 slide**, mỗi slide ≈ 1 phút |
| Khổ | 16:9, 1920 × 1080 |
| Chủ đề | **Sáng**: nền kem ấm `#FAF7F1`, chữ than `#1D1A17`, nhấn **cam đất** `#B0561A` (màu "chú ý") và **lam ngọc** `#12B7A7` (màu mắt cú Lens) — cùng bộ màu với trang web để nhận diện thống nhất |
| Chữ | **Be Vietnam Pro** (tiêu đề 700–800, thân 400–500) — font Việt hiện đại, có dấu đẹp; số dùng tabular |
| Hiệu ứng | Mỗi slide một hiệu ứng vào (fade-up), phần tử xuất hiện theo bước khi cần dẫn dắt (bảng, sơ đồ 5 bước, bộ đếm số); không xoay/lật lòe loẹt. Chuyển slide: trượt ngang mượt |
| Mascot | Cú Lens (ảnh giáo sư) xuất hiện ở bìa, slide cơ chế và slide demo; góc trang dùng biểu tượng nhỏ |
| Hình minh họa | Sơ đồ SVG vẽ riêng (cơ chế, chunk-aware, bộ nhớ), ảnh chụp trang web/demo, biểu đồ cột cho các bảng, ảnh cú từ `static/img/` |
| Số liệu | Mỗi slide kết quả có **một con số lớn** làm điểm neo, bảng rút gọn bên dưới, chú thích nguồn (Bảng mấy) |
| Ngôn ngữ | Tiếng Việt; thuật ngữ tiếng Anh giữ nguyên trong ngoặc lần đầu |

Cấu trúc 6 phần: **Mở đầu (1–3) → Bài toán & ý tưởng (4–7) → Dữ liệu & thiết kế (8–9) → Kết quả (10–16) → Hệ thống & demo (17–18) → Tiến độ & xin ý kiến (19–22).**

---

## Phần 1 — Mở đầu

### Slide 1 · Bìa
- Tên đề tài đầy đủ; "Khóa luận tốt nghiệp ngành Khoa học dữ liệu — Trường ĐH Công nghiệp TP.HCM".
- Nguyễn Ngọc Lân 22635801 · Nguyễn Tấn Minh 22643511 · GVHD ThS. Trương Vĩnh Linh · 16/09/2026.
- Hình: cú Lens giáo sư (ảnh `owl-prof.webp`) bên phải, nền kem có quầng lam ngọc nhẹ.
- Hiệu ứng: tên đề tài hiện từng dòng; mắt cú "chớp" một lần (GIF/animation nhẹ nếu công cụ cho phép, không thì tĩnh).

### Slide 2 · Một câu
- Chữ lớn giữa slide: **"Mô hình có thể bịa chữ. Ánh mắt của nó thì không."**
- Dòng dưới: *Khi LLM đọc lại câu trả lời cùng ngữ cảnh, phân bố chú ý của nó lên từng đoạn ngữ cảnh đủ để phân biệt trung thực, ảo giác nội tại, ảo giác ngoại lai — không cần LLM giám khảo.*
- Hiệu ứng: hai câu hiện lần lượt; từ "ánh mắt" đổi sang màu lam ngọc.

### Slide 3 · Ba loại phản hồi — ví dụ thật
- Ngữ cảnh chung (Hà Nội, 4 câu) ở trên; ba thẻ: **Trung thực / Nội tại / Ngoại lai** với câu trả lời và **điểm thật bộ phát hiện chấm trên T4**: `no` 0,001 · `intrinsic` 0,998 · `extrinsic` 1,000 (nguồn: `results/t40/t36_thu_vien.json`).
- Ghi chú nhỏ: "ba ví dụ không nằm trong dữ liệu huấn luyện".
- Hiệu ứng: ba thẻ lật lần lượt; điểm rủi ro đếm lên.

## Phần 2 — Bài toán và ý tưởng

### Slide 4 · Vì sao cần phát hiện ảo giác trong RAG
- Sơ đồ RAG: truy xuất → sinh → người dùng; chỗ hỏng: câu trả lời trông rất ổn nhưng không bám ngữ cảnh.
- Ba con đường hiện có và giá của chúng (Bảng 8): **LLM giám khảo** 8.194 ms/mẫu, dữ liệu rời máy, phụ thuộc API · **Bộ mã hóa tinh chỉnh** 560 triệu tham số, cần GPU và tinh chỉnh (InfoXLM không hội tụ) · **Đặc trưng bề mặt** rẻ nhưng chỉ 0,656.
- Điểm chốt: cần một tín hiệu **có sẵn trong chính lượt đọc** của mô hình.

### Slide 5 · Lookback Lens và khoảng trống
- Công thức lookback ratio gốc (Chuang và cộng sự, EMNLP 2024): tỷ lệ chú ý vào ngữ cảnh so với phần đã sinh, trung bình theo token.
- Khoảng trống: gộp cả ngữ cảnh thành **một con số** — không biết nhìn **đoạn nào**; bài gốc chỉ nhị phân, tiếng Anh, AUROC.
- Hình: hai thanh cạnh nhau — "một khối" và "theo đoạn" (dùng lại minh họa `chunk-aware.webp`).

### Slide 6 · Đóng góp: chunk-aware lookback ratio
- Tách tỷ lệ theo từng đoạn ngữ cảnh → năm đại lượng hình dạng: entropy, tỷ trọng lớn nhất, Gini, khoảng cách top-1/top-2, độ trôi.
- Ba câu hỏi nghiên cứu: **CH1** tín hiệu có đủ để phân ba lớp trên tiếng Việt? **CH2** chi phí so với các hướng khác? **CH3** chuyển được giữa mô hình / bộ dữ liệu không?
- Hiệu ứng: năm đại lượng hiện dần theo thanh trượt "tản → tập trung" (ảnh động 2 khung hoặc tĩnh).

### Slide 7 · Cơ chế trong 5 bước
- Sơ đồ ngang 5 ô: (1) ghép prompt theo chat template Qwen — chốt một lần, không đổi; (2) một lượt đọc (teacher forcing), NF4 float16, bỏ lớp 27; (3) **hook trong từng lớp**: cộng chú ý của token phản hồi rơi vào từng đoạn rồi xóa ma trận; (4) đặc trưng theo đoạn; (5) hồi quy logistic **579 tham số**.
- Hộp cảnh báo "Rủi ro số một": ma trận chú ý 4.096 token × 28 lớp = **26 GB nếu giữ cả**, hook giữ **0,94 GB** một lớp → vừa 16 GB, đỉnh đo 8.328 MB.
- Hiệu ứng: 5 ô sáng lần lượt; hộp bộ nhớ hiện sau cùng.

## Phần 3 — Dữ liệu và thiết kế thực nghiệm

### Slide 8 · Bốn bộ dữ liệu, ba vai trò
- Bảng: **ViHallu** (bộ chính, 7.000 mẫu, phản hồi GPT-4o thật, 3 nhãn) · **ISE-DSC01** (ngữ cảnh dài 21–73 câu, kiểm chứng chunk-aware) · **ViWikiFC** (đối chứng ngoài, 20.919 mẫu, NEI có bằng chứng) · **ViFactCheck** (dự phòng, chưa dùng).
- Chia tập **theo ngữ cảnh** 80/10/10, seed 42 — rò rỉ 0 %. Cảnh báo đã đo: test gốc ViWikiFC rò rỉ 100 % ngữ cảnh với train; chỉ 67 % nhãn NEI thật sự là ngoại lai (κ 0,505).
- Hình: bốn thẻ có biểu tượng, thanh số mẫu.

### Slide 9 · Thiết kế thực nghiệm
- **16 thí nghiệm** trên T4 16 GB Kaggle, 30 giờ/tuần; ~**120.000 lượt đọc** đã trích, 4 mô hình đọc (Qwen2.5-7B/3B/1.5B, Sailor2-8B).
- Chỉ số: macro-F1 ba lớp kèm **khoảng tin cậy 95 % bootstrap**, F1 nhị phân, ECE; chi phí: ms/mẫu **đo xen kẽ** để tránh T4 hạ xung, VRAM đỉnh, số tham số.
- Nguyên tắc: chọn cách gộp đầu trên dev, test chấm **một lần**; mọi số ghi `results/runs.jsonl`, bảng sinh bằng script.
- Hình: lưới 16 ô thí nghiệm tô theo CH1/CH2/CH3.

## Phần 4 — Kết quả

### Slide 10 · Kết quả chính trên ViHallu (Bảng 1)
- Con số neo: **0,757** macro-F1 chunk-aware [0,724–0,789].
- Biểu đồ cột ngang: bề mặt 0,656 · Gemini 0,664 · PhoBERT 0,749 · **XLM-R 0,776** · lookback gộp 0,745 · **chunk-aware 0,757**. Ghi rõ khoảng tin cậy chồng nhau giữa XLM-R và chunk-aware.
- Dòng phụ: ECE **0,044** — hiệu chỉnh tốt nhất bảng (XLM-R 0,097); nhị phân 0,864.
- Hiệu ứng: cột mọc lần lượt, cột của nhóm tô cam.

### Slide 11 · Cơ chế được xác nhận trực tiếp (Bảng 2, 2c)
- Con số neo: **87,8 %** — đầu chú ý mạnh nhất chỉ đúng đoạn bằng chứng, giữa trung bình 22,6 đoạn, gấp **14,29×** chọn hú họa (E06, ISE-DSC01).
- Lặp lại trên bộ thứ hai với sai lệch **0,003** (E08). Phép kiểm can thiệp: bỏ câu bằng chứng → phân bố đổi đúng hướng dự đoán ở **4/4** đại lượng, 71–75 % số cặp.
- Hình: ngữ cảnh mẫu tô màu theo chú ý, đoạn bằng chứng viền lam ngọc.

### Slide 12 · Chia đoạn theo câu thắng (Bảng 3)
- Bảng 5 dòng: câu 0,7768 · cửa sổ 128 0,7683 · 64 0,7662 · đối chứng 48/48 không chồng lấn 0,7649 · 256 0,7589.
- Kết luận: chồng lấn không phải lý do; **ranh giới ngữ nghĩa** mới là thứ quan trọng. Biên độ nhỏ (0,0085) nhưng hướng nhất quán.

### Slide 13 · Nói thẳng: chunk-aware không cộng thêm điểm phân loại (Bảng 4, 4b, 4c)
- Năm phép đo độc lập, cùng một câu trả lời: E03 +0,012 · E12 (thêm bề mặt) −0,007 · E13 (Sailor2) −0,026 · E14 (3B/1.5B) −0,013/+0,011 · E15 (ViWikiFC) −0,001 — tất cả trong khoảng tin cậy rộng 0,065.
- Lý do đo được: năm đại lượng **có** mang tín hiệu (+0,227 trên ISE-DSC01 so với bề mặt) nhưng **chồng lấn 99,9 %** với tỷ lệ gộp.
- Cái nó có mà tỷ lệ gộp không có: **chỉ được đoạn nào** (slide 11) và hiệu chỉnh xác suất tốt hơn.
- Thiết kế: slide nền hơi đậm hơn, tiêu đề "Điều chúng tôi đo được — và điều chúng tôi không". Đây là slide hội đồng sẽ hỏi; nói trước.

### Slide 14 · Bậc thang mô hình đọc (Bảng 5b, 8)
- Con số neo: thu mô hình **4,7×** chỉ mất **0,022** macro-F1, tiết kiệm **67 %** VRAM.
- Bảng: 7B 0,745 · 437,6 ms · 8.328 MB — **3B 0,735 · 222,7 ms · 3.710 MB · 195 tham số** — 1.5B 0,723 · 608 ms · 2.718 MB.
- Nghịch lý đo được: 1.5B **chậm hơn 7B** vì phải chạy bfloat16 mà T4 không có bf16 gốc → nấc đáng dùng là 3B. Đo xen kẽ hai lượt lệch 0,04–2,09 %.
- Hình: biểu đồ tán xạ macro-F1 × ms/mẫu, kích thước điểm = tham số.

### Slide 15 · Ra ngoài phân phối: E15 và E16 (Bảng 6, 7)
- **E15** trên split gốc ViWikiFC: nhóm 70,7 so với SemViQA 83,9 — thua **13 điểm**, và ba lý do đo được: test dùng lại 100 % ngữ cảnh train (bộ mã hóa 560 triệu tham số nhớ được); 67 % NEI thật ngoại lai; không tinh chỉnh, 2.271 tham số. Cùng một đầu chú ý `l17_h4` dẫn đầu trên cả ba bộ.
- **E16** chéo bộ: ba lớp sụt về 0,36–0,55 vì hai bộ định nghĩa "ngoại lai" khác nhau; **nhị phân chuyển được** 0,63–0,78. Trả lời CH3: "trung thực hay không" là thuộc tính của mô hình đọc; "sai kiểu nào" gắn với từng bộ.
- Hình: hai ma trận nhầm lẫn rút gọn.

### Slide 16 · Phân tích sai sót (Bảng 9)
- 169/700 sai; **48,5 %** là nhầm giữa hai loại ảo giác, chỉ 16 % bỏ sót.
- Năm hình dạng lỗi: một mệnh đề bịa giữa phần chép lại bị trung bình hóa mất; trộn hai loại ảo giác dưới một nhãn; phủ định lật ngược bằng chính từ ngữ ngữ cảnh; câu hỏi tiền đề sai ("Adversarial Question:" lọt vào 13 câu); nhãn tranh cãi.
- Kết luận: ba trong năm là giới hạn của việc chấm **cả phản hồi bằng một véc-tơ trung bình** → hướng phát triển: chấm theo đoạn phản hồi. Hình: `results/error_analysis.png`.

## Phần 5 — Hệ thống và demo

### Slide 17 · Hệ thống hoàn chỉnh
- Bốn khối: **Thư viện** (`HallucinationDetector.from_pretrained` → `score`; bundle 11,5 KB mang cả công thức dựng cột, chấm lại 700/700 trùng) · **REST** (`/score`, `/score/batch`, `/health`, `/demo/ask`; nạp trong luồng nền) · **Docker** (một lệnh, ảnh 10,5 GB, trọng số ngoài ảnh) · **Trang chủ** (landing + công cụ + cú Lens, chế độ phát lại khi không có GPU).
- **781 → 783** ca kiểm thử tự động, không cần GPU. Hình: ảnh chụp trang chủ (hero mắt cú) và trang công cụ.

### Slide 18 · Demo thật trên T4 — bộ phát hiện tự bắt được một ảo giác không ai dàn dựng
- Hệ RAG 21 tài liệu: BM25 → Qwen2.5-3B sinh → chấm. Bảng 5 câu: Fansipan `no` 0,008 · Võ Nguyên Giáp `no` 0,135 · Phở `extrinsic` 0,883 (tranh cãi) · **Hồ Hoàn Kiếm `extrinsic` 0,997** — mô hình bịa "sau khi đánh đuổi giặc Minh… trở về dinh thự" không có trong ngữ cảnh · Hạ Long `no` 0,018.
- Phát hiện kèm: mô hình đọc float16 **không sinh được** (lớp 27 tràn số → logit NaN → toàn `!`) → điều khoản phần cứng cho lập luận chi phí biên.
- Nếu có mạng và máy: mở trang thật; không thì ảnh chụp + video ngắn 20 s.

## Phần 6 — Tiến độ và xin ý kiến

### Slide 19 · Tiến độ
- Thanh tiến độ: **41/52** task, giai đoạn 1–7 xong (11/09), sớm hơn kế hoạch ~7 tuần. Còn: T41 E17 (tùy chọn), T42–T47 viết báo cáo, T48–T50 bảo vệ.
- Mốc: báo cáo cuối kỳ trước 22/11 · phản biện 23–29/11 · bảo vệ 30/11–06/12.
- Hình: Gantt rút gọn 9 giai đoạn, kế hoạch vs thực tế.

### Slide 20 · Hạn chế và hướng phát triển
- Hạn chế: chunk-aware không thêm điểm phân loại (nói rõ ở slide 13); ba lớp không chuyển chéo bộ; Docker chưa kiểm trên máy GPU; ms/mẫu gắn với T4; lượt đọc tay 100 mẫu chưa xong.
- Hướng phát triển: chấm theo đoạn phản hồi; huấn luyện gộp nhiều bộ hoặc chấp nhận nhị phân; đo chi phí biên trên hệ RAG thật với phần cứng bf16 gốc; E17 ViFactCheck.

### Slide 21 · Xin ý kiến thầy
1. Cách định vị đóng góp trong quyển báo cáo: đóng góp là bằng chứng cơ chế + chỉ được đoạn nào, còn điểm phân loại báo cáo trung thực là không phân biệt được với 0?
2. Bố cục chương đánh giá theo ba câu hỏi nghiên cứu thay vì theo thứ tự thí nghiệm?
3. Có làm E17 không, hay dồn sức viết?
4. Bộ phát hiện mặc định giữ 7B (nhất quán bảng) hay đổi 3B (điểm cân bằng)?

### Slide 22 · Cảm ơn
- "Mắt không nói dối." · link repo `github.com/wsunicorn/vihallulens` · QR tới trang chủ (nếu có địa chỉ công khai) · cú Lens vẫy cánh.

---

## Việc cần bạn chốt

1. **Ngày**: tôi hiểu "thứ Tư tuần sau" là **16/09**. Đúng không?
2. **Thời lượng** thầy cho bao nhiêu phút? 22 slide hợp 20–25 phút; nếu chỉ 10–15 phút tôi gộp còn ~14 (bỏ 5, 12, 16, gộp 14–15).
3. **Slide 13 "Nói thẳng"** giữ hay giảm nhẹ? Tôi khuyên giữ nguyên — thầy đã đọc các báo cáo tuần nên biết rồi, và trình bày trước còn hơn bị hỏi.
4. **Công cụ dựng**: tôi sẽ dùng **Claude Design** (skill `design`): mỗi slide là một artboard 1920 × 1080 trên một canvas, bạn mở trong trình duyệt, chỉnh từng chữ/ảnh bằng tay, rồi **xuất PNG/PDF**. Lưu ý thật: nó xuất PDF/PNG, **không xuất PPTX** và hiệu ứng chuyển slide chỉ có khi trình chiếu PDF/ảnh qua PowerPoint hoặc Keynote. Nếu bạn cần file `.pptx` có animation thật, phương án B là tôi dựng bằng `python-pptx` (được hiệu ứng vào/ra cơ bản, kém đẹp hơn về bố cục). Chọn A (Claude Design, đẹp, sửa tay) hay B (PPTX, animation)?
