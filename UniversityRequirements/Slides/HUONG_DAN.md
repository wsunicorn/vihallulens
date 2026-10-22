# Bộ slide — cách dùng

Cập nhật 22/10/2026. Bộ dùng để báo cáo trước Hội đồng là **`slide_hoi_dong_23.html`**.

## File trong thư mục

| File | Là gì |
|---|---|
| **`slide_hoi_dong_23.html`** / `.pdf` | **Bộ chính, 23 slide**, sắp theo bố cục quyển khóa luận như GVHD yêu cầu ngày 05/10: giới thiệu và bài toán → động lực, khoảng trống → cơ sở lý thuyết → dữ liệu → phương pháp đề xuất → hệ thống → thực nghiệm → tự đánh giá → tài liệu tham khảo. Số liệu khớp quyển v4. Bản PDF là trạng thái cuối của từng slide. |
| `slide_rut_gon_19.html` / `.pdf` | Bộ 19 slide Minh dựng ngày 14/10, là nền của bộ chính. Minh giữ script dựng (`build_slide19.py`, trên máy Minh). |
| `nguon_bo_sung_15-10/` | Sơ đồ và script chèn bốn slide còn thiếu so với yêu cầu của thầy (bài toán, các hướng đã có, kiểm định giả thuyết, tài liệu tham khảo) vào bộ 19 slide. Cách chạy ghi ở `GHI_CHU_CHO_MINH.txt`. |
| `slide_v2.html` | **Bộ cũ**, 36 slide theme "Đêm cú", dùng cho buổi báo cáo GVHD ngày 26/09. Không dùng nữa. |
| `GIAI_THICH_SLIDE.md` | **Viết cho bộ cũ `slide_v2.html`**, chưa cập nhật cho bộ chính. |
| `ke_hoach_slide_v2.md`, `ke_hoach_slide_v3.md` | Kế hoạch của hai đợt làm slide trước, giữ để tra lại lý do thiết kế. |
| `BI_KIP_HTML_SLIDE.md` | Bộ skill đã cài và luật dựng slide HTML. |
| `img/` | Logo trường và ảnh dùng trong slide. |

## Trình chiếu

Mở `slide_hoi_dong_23.html` bằng **Edge hoặc Chrome**. File tự chứa (font, thư viện, ảnh, số liệu
đều nhúng sẵn), chạy không cần mạng. Mỗi slide tự chạy hoạt ảnh khi chuyển tới, không phải bấm.

| Phím / thao tác | Việc |
|---|---|
| `→` `Space` `Enter` `PageDown` | slide sau |
| `←` `PageUp` `Backspace` | slide trước |
| `Home` / `End` | slide đầu / cuối |
| `R` | chạy lại hoạt ảnh của slide hiện tại |
| `N` | bật / tắt ghi chú diễn giả |
| `F` | toàn màn hình |
| click phía phải / trái màn hình | slide sau / trước; click **trong sơ đồ** thì không đổi slide (dành cho rê chuột, bấm nút) |

Địa chỉ dạng `slide_hoi_dong_23.html#14` mở thẳng slide 14. Thêm `?all` vào địa chỉ
(`slide_hoi_dong_23.html?all#1`) thì mọi sơ đồ hiện sẵn trạng thái cuối — dùng để chụp hoặc in.

## Ghi chú diễn giả

Mỗi slide có ghi chú khoảng một phút nói (thuộc tính `data-notes`), xưng "nhóm em"; thao tác rê
chuột, bấm nút ghi ở cuối ghi chú của slide đó. Cả bộ khoảng 23–24 phút. Khi chiếu hai màn hình:
mở file hai lần, một cửa sổ trên máy chiếu bấm `F`, cửa sổ trên laptop bấm `N`.

## Sửa bộ chính

Không sửa thẳng `slide_hoi_dong_23.html`. Sửa ở nguồn rồi dựng lại:

1. Slide gốc của Minh: Minh sửa trong `build_slide19.py` và dựng lại `slide_rut_gon_19.html`.
2. Bốn slide bổ sung: sửa `nguon_bo_sung_15-10/figs_minh_bo_sung.js` (sơ đồ) hoặc
   `bo_sung_slide_minh.py` (chữ, ghi chú, chân trang), rồi chạy
   `python nguon_bo_sung_15-10/bo_sung_slide_minh.py slide_rut_gon_19.html nguon_bo_sung_15-10/figs_minh_bo_sung.js slide_hoi_dong_23.html`.
3. Xuất lại PDF: chụp từng slide ở chế độ `?all` rồi ghép, hoặc `Ctrl+P` → Save as PDF, bật
   Background graphics.
