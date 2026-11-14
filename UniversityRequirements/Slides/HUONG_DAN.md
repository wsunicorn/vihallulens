# Bộ slide — cách dùng

Cập nhật 14/11/2026. Bộ dùng để báo cáo trước Hội đồng là **`slide_hoi_dong_31.html`**.

## File trong thư mục

| File | Là gì |
|---|---|
| **`slide_hoi_dong_31.html`** / `.pdf` | **Bộ chính, 31 slide**, dựng từ bộ 23 slide bằng `nguon_hoan_thien/hoan_thien_slide.py` (14/11): thêm slide *Nội dung trình bày* và bảy slide chuyển phần; tiêu đề nêu tên nội dung, kết luận chuyển thành dòng tóm tắt dưới tiêu đề; từ ngữ trên slide, nhãn hình và ghi chú diễn giả theo cách diễn đạt học thuật của quyển; kết quả E19 thành bước 5 của slide 22. Bản PDF là trạng thái cuối của từng slide. |
| `slide_hoi_dong_31.pptx` | **Bản PowerPoint** cho máy chỉ có PowerPoint (không commit, nặng 13,4 MB; dựng lại bằng lệnh ở mục *Bản PowerPoint*). Mỗi slide là một video quay lại đúng hoạt ảnh của bản HTML, tự chạy khi vào slide và dừng ở trạng thái cuối; chuyển slide mờ dần như bản HTML; ghi chú diễn giả nằm ở phần Notes. Không mang theo được: ô gợi ý khi rê chuột và các nút đổi góc nhìn trong hình (nút vẫn hiện nhưng không bấm được). |
| `slide_hoi_dong_23.html` / `.pdf` | Bộ 23 slide, đầu vào của bước hoàn thiện; sắp theo bố cục quyển khóa luận như GVHD yêu cầu ngày 05/10: giới thiệu và bài toán → động lực, khoảng trống → cơ sở lý thuyết → dữ liệu → phương pháp đề xuất → hệ thống → thực nghiệm → tự đánh giá → tài liệu tham khảo. Số liệu khớp quyển v5 (số mục, số bảng giữ như v4 nên chân slide vẫn đúng); bốn slide cập nhật theo lượt chạy 23/10: slide 12 (825 ca kiểm thử), 14 (câu về 84,80 %), 21 (kết quả E17, E18), 22 (danh mục 36 tài liệu). Bản PDF là trạng thái cuối của từng slide. |
| `slide_rut_gon_19.html` / `.pdf` | Bộ 19 slide Minh dựng ngày 14/10, là nền của bộ chính. Dựng bằng script trong `nguon_19_slide/`. |
| `nguon_19_slide/` | Script `build_slide19.py` dựng bộ 19 slide từ bộ 32 slide ngày 02/10 (`slide_goc_32.html`, không sửa file này). Mỗi chỗ sửa là một phép thay chuỗi có kiểm số lần khớp, nguồn gốc không khớp thì script dừng. |
| `nguon_hoan_thien/` | Script `hoan_thien_slide.py` dựng bộ 31 slide từ bộ 23 slide. Mỗi phép thay chữ ghi số lần phải khớp; script cũng chặn các từ ngữ đời thường đã loại (ví dụ "bịa", "đoán bừa") nếu còn sót. |
| `nguon_bo_sung_15-10/` | Sơ đồ và script chèn bốn slide còn thiếu so với yêu cầu của thầy (bài toán, các hướng đã có, kiểm định giả thuyết, tài liệu tham khảo) vào bộ 19 slide. Cách chạy ghi ở `GHI_CHU_CHO_MINH.txt`. |
| `slide_v2.html` | **Bộ cũ**, 36 slide theme "Đêm cú", dùng cho buổi báo cáo GVHD ngày 26/09. Không dùng nữa. |
| `GIAI_THICH_SLIDE.md` | Giải thích từng slide của bộ chính và **kịch bản thời gian** hai phương án (đủ khoảng 26–27 phút, rút khoảng 15 phút). Bản cho bộ cũ giữ ở `GIAI_THICH_SLIDE_v2_cu.md`. |
| `HOI_DAP_HOI_DONG.md` | Câu hỏi hội đồng dễ hỏi kèm hướng trả lời, có số liệu và trỏ về slide. |
| `ke_hoach_slide_v2.md`, `ke_hoach_slide_v3.md` | Kế hoạch của hai đợt làm slide trước, giữ để tra lại lý do thiết kế. |
| `BI_KIP_HTML_SLIDE.md` | Bộ skill đã cài và luật dựng slide HTML. |
| `img/` | Logo trường và ảnh dùng trong slide. |

## Trình chiếu

Mở `slide_hoi_dong_31.html` bằng **Edge hoặc Chrome**. File tự chứa (font, thư viện, ảnh, số liệu
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

Địa chỉ dạng `slide_hoi_dong_31.html#21` mở thẳng slide 21. Thêm `?all` vào địa chỉ
(`slide_hoi_dong_31.html?all#1`) thì mọi sơ đồ hiện sẵn trạng thái cuối — dùng để chụp hoặc in.

## Ghi chú diễn giả

Mỗi slide có ghi chú khoảng một phút nói (thuộc tính `data-notes`), xưng "nhóm em"; thao tác rê
chuột, bấm nút ghi ở cuối ghi chú của slide đó. Cả bộ khoảng 25 phút nói, chưa tính chuyển slide. Khi chiếu hai màn hình:
mở file hai lần, một cửa sổ trên máy chiếu bấm `F`, cửa sổ trên laptop bấm `N`.

## Sửa bộ chính

Không sửa trực tiếp `slide_hoi_dong_31.html`. Sửa ở nguồn rồi dựng lại; các lệnh chạy trong thư mục này:

1. Mười chín slide gốc: sửa `nguon_19_slide/build_slide19.py`, chạy
   `python nguon_19_slide/build_slide19.py nguon_19_slide/slide_goc_32.html slide_rut_gon_19.html`,
   rồi chạy lệnh ở bước 2 và 3.
2. Bốn slide bổ sung: sửa `nguon_bo_sung_15-10/figs_minh_bo_sung.js` (sơ đồ) hoặc
   `bo_sung_slide_minh.py` (chữ, ghi chú, chân trang), rồi chạy
   `python nguon_bo_sung_15-10/bo_sung_slide_minh.py slide_rut_gon_19.html nguon_bo_sung_15-10/figs_minh_bo_sung.js slide_hoi_dong_23.html`,
   rồi chạy lệnh ở bước 3.
3. Tiêu đề, dòng tóm tắt, từ ngữ, ghi chú, mục lục, slide chuyển phần, bước E19: sửa
   `nguon_hoan_thien/hoan_thien_slide.py`, chạy
   `python nguon_hoan_thien/hoan_thien_slide.py slide_hoi_dong_23.html slide_hoi_dong_31.html`.
   Mở `slide_hoi_dong_31.html?qa` để kiểm: góc dưới trang phải hiện `QA-OK`.
4. Xuất lại PDF: chụp từng slide ở chế độ `?all` rồi ghép, hoặc `Ctrl+P` → Save as PDF, bật
   Background graphics.

## Bản PowerPoint

Dựng lại sau mỗi lần sửa bộ chính (khoảng 7 phút, cần Google Chrome):

```
uv run --no-project --with playwright==1.48.0 --with python-pptx==1.0.2 --with imageio-ffmpeg==0.5.1 --with pillow python nguon_hoan_thien/xuat_pptx.py slide_hoi_dong_31.html slide_hoi_dong_31.pptx
```

Khi trình chiếu bằng PowerPoint: mỗi slide tự chạy hoạt ảnh, bấm sang slide sau như bình thường.
Nếu cần dừng ở một bước để giải thích thì dùng bản HTML, vì video không dừng theo bước. Hãy mở
thử trên đúng máy của phòng bảo vệ trước buổi bảo vệ: PowerPoint 2013 trở lên phát được video
H.264 nhúng sẵn.
