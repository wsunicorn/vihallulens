# Kế hoạch slide v2 — dựng lại từ đầu theo bộ skill, bám 8 chương mẫu báo cáo Khoa

> Đã duyệt; theme chốt E "Đêm cú" (18/09/2026). Bản dựng: `slide_v2.html`. Mọi số liệu chép từ
> `docs/EXPERIMENTS.md` và `results/`; nguồn ghi ở chân từng slide.

## Nguyên tắc dựng (từ BI_KIP_HTML_SLIDE.md)

- **Speaker-led, một ý một slide**: chữ ≤ 3 dòng ngắn, phần còn lại là hình. Nhiều slide ngắn hơn là ít slide dày.
- Mỗi slide ghi rõ **thiết bị thị giác** và **kiểu chuyển động**: `lặp` (vô hạn, nền/ẩn dụ) · `một-lần` (dựng xong dừng) · `bước` (hiện theo phím).
- Mỗi slide một **hành động nhận thức** của khán giả (theo visual-cognition-slides): *thấy* · *so* · *theo dõi* · *nhớ số* · *đồng ý*.
- Sân khấu 1920 × 1080 cố định, phím ←/→, `N` ghi chú, `?all` để in PDF.

## Cấu trúc: 8 chương của mẫu báo cáo → 9 phần, 36 slide (~25–28 phút)

| Chương mẫu báo cáo | Phần slide | Slide |
|---|---|---|
| Mở đầu | 0 · Mở màn | 1–3 |
| 1. Giới thiệu | 1 · Bài toán | 4–7 |
| 2. Cơ sở lý thuyết | 2 · Nền tảng | 8–10 |
| 3. Phân tích yêu cầu | 3 · Yêu cầu và dữ liệu | 11–13 |
| 4. Thiết kế hệ thống · 5. Giải pháp công nghệ | 4 · Phương pháp và thiết kế | 14–19 |
| 6. Hiện thực và triển khai | 5 · Hiện thực | 20–23 |
| 7. Đánh giá và thảo luận | 6 · Kết quả | 24–31 |
| 8. Kết luận | 7 · Kết luận | 32–34 |
| — | 8 · Xin ý kiến, cảm ơn | 35–36 |

---

## Phần 0 · Mở màn

| # | Slide | Thiết bị thị giác | Chuyển động | Khán giả |
|---|---|---|---|---|
| 1 | **Bìa** — tên đề tài, nhóm, GVHD | Cú Lens toàn thân; hai mắt lam ngọc sáng dần từ tối | mắt chớp `lặp` chậm; tên đề tài `một-lần` từng dòng | thấy |
| 2 | **Một câu** — "Mô hình có thể bịa chữ. Ánh mắt của nó thì không." | Chữ lớn, không gì khác | hai vế hiện `bước` | nhớ |
| 3 | **Lộ trình** — 9 phần, mỗi phần một biểu tượng | Dải tiến trình ngang, phần hiện tại sáng | dải chạy `một-lần` | theo dõi |

## Phần 1 · Bài toán (Chương 1)

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 4 | **RAG làm gì** — hỏi → truy xuất → LLM → trả lời | Sơ đồ SVG 4 khối | khối hiện nối tiếp `một-lần`, dữ liệu chảy `lặp` | theo dõi |
| 5 | **Ảo giác chui vào ở đâu** — cùng sơ đồ, điểm đỏ ở "LLM sinh"; câu trả lời trôi chảy nhưng sai | Sơ đồ 4 khối, điểm đỏ nhấp | nhấp `lặp` | thấy |
| 6 | **Ba loại phản hồi** — trung thực / nội tại / ngoại lai với ví dụ Hà Nội thật (0,001 · 0,998 · 1,000) | Ba thẻ + bộ đếm | thẻ lật `bước`, số đếm `một-lần` | so |
| 7 | **Ba con đường hiện có và giá** — giám khảo 8.194 ms, bộ mã hóa 560 M tham số, bề mặt 0,656 → cần tín hiệu *có sẵn trong lượt đọc* | Ba cột chi phí | cột mọc `một-lần`, kết luận `bước` | đồng ý |

## Phần 2 · Nền tảng (Chương 2)

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 8 | **Chú ý là gì, nhìn thấy được** — một token trả lời "nhìn" về các token ngữ cảnh | SVG chuỗi token, tia chú ý | tia chảy `lặp` | thấy |
| 9 | **Lookback Lens (EMNLP 2024)** — tỷ lệ chú ý vào ngữ cảnh ÷ (ngữ cảnh + đã sinh) | Cùng SVG, thanh gộp "một tỷ lệ" | gộp lại `một-lần` | theo dõi |
| 10 | **Khoảng trống** — một con số không nói *đoạn nào*; chỉ nhị phân, tiếng Anh | Thanh gộp mờ đi, dấu hỏi trên từng đoạn | `bước` | đồng ý |

## Phần 3 · Yêu cầu và dữ liệu (Chương 3)

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 11 | **Ba câu hỏi nghiên cứu** CH1 tín hiệu & cơ chế · CH2 chi phí · CH3 chuyển giao | Ba thẻ màu (cam / lam / tím) — màu này dùng lại ở lưới thí nghiệm và kết quả | `bước` | nhớ |
| 12 | **Ràng buộc** — T4 16 GB, 30 giờ/tuần, không API, tái lập seed 42 | Bốn biểu tượng | `một-lần` | thấy |
| 13 | **Bốn bộ dữ liệu, chia theo ngữ cảnh** — 7.000 · 36 k · 20.919; hai bẫy đã đo (rò rỉ 100 %, NEI 67 %) | Thẻ số + sơ đồ khối chia tập | số đếm `một-lần`, khối chia `bước` | so |

## Phần 4 · Phương pháp và thiết kế (Chương 4–5)

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 14 | **Chunk-aware: hỏi "nhìn đoạn nào"** — đóng góp cốt lõi | SVG: gộp (1 thanh) → theo đoạn (5 thanh) | biến hình `một-lần` | thấy |
| 15 | **Hai hình dạng** — nội tại nhọn, ngoại lai tản | Hai biểu đồ cột mini + thanh trượt minh họa | cột đổi `lặp` chậm | so |
| 16 | **Năm đại lượng hình dạng** — entropy, max, Gini, top-1/2, độ trôi | Mỗi đại lượng một biểu tượng nhỏ | `bước` | nhớ |
| 17 | **Cơ chế 5 bước** — prompt → đọc lại → hook → đặc trưng → hồi quy 579 tham số | Dải 5 ô | ô sáng nối tiếp `một-lần` | theo dõi |
| 18 | **Rủi ro số một: bộ nhớ** — 28 lớp = 26 GB tràn vs hook 1 lớp = 8,3 GB | Hai dãy thanh | dãy đỏ dâng rồi "tràn", dãy xanh một thanh sáng `một-lần` | thấy |
| 19 | **Kiến trúc bốn tầng** — extract → features → detect → serve; data/evaluation ngang | Sơ đồ tầng | tầng dựng từ dưới lên `một-lần` | theo dõi |

## Phần 5 · Hiện thực (Chương 6)

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 20 | **16 thí nghiệm, một card T4** — lưới E01–E16 tô theo CH; ≈120 k lượt đọc; 783 test | Lưới 4 × 4 | ô hiện theo CH `bước` | thấy |
| 21 | **Kỷ luật đo** — dev chọn, test chấm một lần; KTC bootstrap; đo chi phí xen kẽ | Ba biểu tượng | `một-lần` | đồng ý |
| 22 | **Thư viện · REST · Docker** — 3 dòng code; bundle 11,5 KB, 700/700 | Ba khối + đoạn mã | `bước` | thấy |
| 23 | **Trang chủ + cú Lens** — ảnh chụp hero; chế độ phát lại khi không GPU | Ảnh chụp web + chú thích | ảnh trượt vào `một-lần` | thấy |

## Phần 6 · Kết quả (Chương 7) — chỗ nhấn mạnh

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 24 | **Số neo CH1: 0,757** — ngang XLM-R 0,776, ECE 0,044 tốt nhất bảng | Con số lớn + hàng cột ngang 6 phương pháp | số đếm, cột mọc `một-lần` | nhớ số |
| 25 | **Cơ chế được xác nhận: 87,8 %** hit@1 giữa 22,6 đoạn, 14,29× hú họa; lặp lại 0,003; can thiệp 4/4 | Ngữ cảnh tô màu + đoạn bằng chứng viền | tô màu chảy `một-lần` | thấy |
| 26 | **Chia theo câu thắng cả bốn cửa sổ** | Bảng 5 dòng + hình ba cách chia | `bước` | so |
| 27 | **Nói thẳng ①: chunk-aware không cộng thêm điểm** — 5 phép đo | Bảng 5 dòng chênh, nền tối | dòng hiện `bước` | đồng ý |
| 28 | **Nói thẳng ②: vì sao — chồng lấn 99,9 %** với tỷ lệ gộp; nhưng chỉ được đoạn nào | Biểu đồ Venn hai vòng gần trùng | vòng trượt vào `một-lần` | thấy |
| 29 | **CH2: thu 4,7 lần mất 0,022** — 3B là điểm cân bằng; 1.5B chậm hơn 7B (bf16) | Tán xạ F1 × ms | điểm rơi vào `một-lần` | so |
| 30 | **CH3: nhị phân chuyển được, ba lớp không** — E15 70,7 vs 83,9 + 3 lý do; E16 mũi tên | Mũi tên chuyển giao + hai ma trận nhỏ | `bước` | theo dõi |
| 31 | **Demo thật: Hồ Hoàn Kiếm 0,997** — mô hình tự bịa, bộ phát hiện tự bắt; phát hiện kèm float16 không sinh được | Trích ngữ cảnh vs trả lời, phần bịa tô đỏ | tô đỏ `một-lần`, cú shock | thấy |

## Phần 7 · Kết luận (Chương 8)

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 32 | **Sai sót: thấy tốt hơn gọi tên** — 48,5 % nhầm giữa hai loại; 5 hình dạng lỗi | Biểu đồ lỗi + 5 nhãn | `bước` | so |
| 33 | **Đã làm được / chưa** — hai cột | Hai cột đối xứng | `bước` | đồng ý |
| 34 | **Hướng phát triển** — chấm theo đoạn phản hồi; gộp bộ hoặc nhị phân; bf16 gốc | Ba mũi tên tiến | `một-lần` | nhớ |

## Phần 8 · Kết

| # | Slide | Thiết bị | Chuyển động | Khán giả |
|---|---|---|---|---|
| 35 | **Tiến độ 41/52 + bốn câu xin ý kiến** | Thanh tiến độ + 4 thẻ | `bước` | đồng ý |
| 36 | **Cảm ơn** — "Mắt không nói dối." + repo | Cú vẫy cánh | vẫy `lặp` 3 nhịp rồi dừng | — |

---

## Đã chốt

1. Theme E "Đêm cú" (18/09/2026).
2. Giữ 36 slide.
3. Poster A0: chưa quyết.
