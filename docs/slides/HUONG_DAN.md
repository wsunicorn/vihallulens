# Bộ slide — cách dùng

Cập nhật 28/11/2026. Bộ báo cáo trước Hội đồng là `slide_hoi_dong.pptx` (và bản `.pdf`), 19 trang.

## Yêu cầu của GVHD

- Cấu trúc slide theo cấu trúc quyển khóa luận (thư ngày 05/10 và 28/11/2026).
- Tổng thời gian tối đa 20 phút gồm cả hỏi đáp; phần trình bày khoảng **10 phút**, còn lại dành cho câu hỏi.
- Từ 10 đến 20 slide; mẫu tùy chọn.

## Bố cục

Thanh đầu trang có tám mục theo tám chương của quyển, chương đang trình bày in đậm; số lớn bên trái tiêu đề là
số chương. Dưới tiêu đề là một câu kết luận; chân trang ghi công trình được dùng và bảng, hình, mục tương ứng
trong quyển.

| Trang | Chương | Nội dung |
|---|---|---|
| 1 | — | Bìa |
| 2–4 | 1 Giới thiệu | Ba loại câu trả lời; phát biểu bài toán và động lực; khoảng trống, câu hỏi, giả thuyết |
| 5–6 | 2 Cơ sở lý thuyết | Các hướng phát hiện ảo giác đã có; phương pháp nền Lookback Lens |
| 7 | 3 Dữ liệu | Bốn bộ dữ liệu, chia tập theo ngữ cảnh, kiểm chứng nhãn |
| 8–9 | 4 Phương pháp | Chunk-aware lookback ratio; quy trình một lượt đọc và forward hook |
| 10 | 5 Hệ thống | Bốn tầng, cách dùng, minh họa RAG |
| 11–14 | 6 Thực nghiệm | Kết quả phân loại; định vị bằng chứng; thí nghiệm can thiệp; chi phí và chuyển giao |
| 15 | 7 Thảo luận | Định vị đúng nhưng không phân loại tốt hơn |
| 16–18 | 8 Kết luận | Năm giả thuyết; kết quả, hạn chế, hướng phát triển; tài liệu tham khảo |
| 19 | — | Cảm ơn |

## Trình chiếu

Mở bằng PowerPoint, trình chiếu như bình thường. Mỗi lần bấm hiện thêm một nhóm nội dung; hết nhóm thì bấm
sang trang sau. Ghi chú người nói nằm trong phần Notes của từng trang, tổng khoảng 1.060 chữ (8–9 phút đọc).
Bản `.pdf` hiện đủ nội dung mọi trang, dùng để gửi đọc trước.

## Dựng lại

Mọi chữ, bảng, biểu đồ là đối tượng PowerPoint nên sửa thẳng được, nhưng lần dựng lại sau sẽ ghi đè. Sửa lâu
dài thì sửa `nguon/dung_slide.py` rồi chạy ở thư mục gốc của repo:

```
uv run --no-project --with python-pptx==1.0.2 --with cairosvg==2.7.1 --with pillow --with pywin32==308 \
    python docs/slides/nguon/dung_slide.py --pdf
```

`--pdf` xuất PDF bằng PowerPoint (cần Windows có Office). Bản cuối được chép sang
`UniversityRequirements/Reports/Slide_KLTN_22635801_22643511_PhatHienAoGiac.pptx` / `.pdf`.

Bộ slide giữ riêng như quyển: git chỉ có nguồn dựng (`nguon/dung_slide.py`, ảnh trong `nguon/img/`, biểu tượng
Lucide giấy phép ISC trong `nguon/icons/`); `.pptx`, `.pdf` nằm trong `.gitignore`. Tài liệu chuẩn bị bảo vệ
(hướng dẫn đọc slide, hỏi đáp, sổ tay) ở `UniversityRequirements/MyNotes/`.
