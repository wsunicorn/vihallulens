# Bộ slide — cách dùng

Cập nhật 15/11/2026. Bộ dùng để báo cáo trước Hội đồng là `slide_hoi_dong.html` (31 slide).

## Giữ riêng tư như quyển báo cáo

Giống quyển (trên git chỉ có bản thảo `.md`, không có `.docx`, `.pdf`), trên git **chỉ có nguồn
dựng** bộ slide. Các file sau nằm trong `.gitignore`, chỉ có trên máy của nhóm:

| File | Là gì |
|---|---|
| `slide_hoi_dong.html` | **Bộ chính, 31 slide**, sắp theo bố cục tám chương của quyển. Mở bằng Edge hoặc Chrome, chạy không cần mạng. |
| `slide_hoi_dong.pdf` | Trạng thái cuối của từng slide, một slide một trang. |
| `nguon/slide_goc_32.html` | Bộ 32 slide ngày 02/10, đầu vào bước 1. Cần giữ để dựng lại; sao lưu cùng các tài liệu riêng. |
| `_build/` | Hai bộ trung gian 19 và 23 slide. |

Mỗi lần dựng, bản cuối được chép sang `UniversityRequirements/Reports/` với tên
`Slide_KLTN_22635801_22643511_PhatHienAoGiac.html` / `.pdf`, cạnh bản Word và PDF của quyển. Tài
liệu chuẩn bị bảo vệ (giải thích từng slide, câu hỏi hội đồng, sổ tay học) nằm ở
`UniversityRequirements/MyNotes/`.

## Trình chiếu

**Chỉ bấm khi bước sau thay đổi bước trước.** Bốn sơ đồ có bước sau thay nội dung của bước trước:
slide 12 (chia ngẫu nhiên → chia theo ngữ cảnh), 16 (cách thông thường → forward hook), 22 (mẫu
minh họa đổi, bước 5 thay bằng E19) và 26 (đổi chiều chuyển giao). Ở bốn slide này, bước 1 tự chạy
rồi dừng, mỗi lần bấm chạy thêm một bước, hết bước thì bấm sang slide sau. Mười bốn sơ đồ còn lại
chỉ thêm nội dung nên tự chạy hết một lượt khi vào slide, dưới hình là một câu tóm tắt.

| Phím / thao tác | Việc |
|---|---|
| `→` `↓` `Space` `Enter` `PageDown` | slide sau; ở bốn slide chia bước: bước kế, đang chạy dở thì cho xong |
| `←` `↑` `PageUp` `Backspace` | slide trước (hiện sẵn trạng thái cuối); ở bốn slide chia bước: lùi một bước |
| `Shift+→` / `Shift+←` | bỏ qua các bước, sang slide sau / về slide trước |
| gõ số rồi `Enter` (ví dụ `2` `2` `Enter`) | nhảy tới slide đó — tiện khi hội đồng hỏi lại |
| bấm vào một chấm số dưới hình | nhảy tới bước đó (bốn slide chia bước) |
| `B` hoặc `.` | bật / tắt màn hình đen |
| `R` | chạy lại hoạt ảnh (hoặc bước hiện tại) |
| `Home` / `End`, `N`, `F` | slide đầu / cuối, ghi chú diễn giả, toàn màn hình |
| click phía phải / trái màn hình | như phím tới / lùi; click **trong sơ đồ** dành cho rê chuột, bấm nút |

Bút trình chiếu gửi `PageDown` / `PageUp`, dùng được ngay. Slide 22: bước 2 chỉ chạy một mẫu, muốn
xem thêm thì bấm "Mẫu khác".

Địa chỉ `slide_hoi_dong.html#21` mở thẳng slide 21; `?all` hiện sẵn trạng thái cuối (để chụp, in);
`?qa` tự dựng mọi sơ đồ, tua mọi bước và in `QA-OK` nếu không lỗi; `?auto` cho mọi sơ đồ tự chạy hết
các bước kèm chú thích từng bước (dùng khi quay màn hình).

## Dựng lại

Không sửa trực tiếp `slide_hoi_dong.html`. Sửa ở `nguon/` rồi chạy ở thư mục gốc của repo:

```
python docs/slides/nguon/dung_lai.py
```

Thêm `--pdf` để xuất lại PDF (cần Google Chrome):

```
uv run --no-project --with playwright==1.48.0 --with pymupdf==1.25.5 --with pillow python docs/slides/nguon/dung_lai.py --pdf
```

| Bước | File trong `nguon/` | Làm gì | Sửa ở đây khi muốn đổi |
|---|---|---|---|
| — | `slide_goc_32.html` (chỉ trên máy) | Bộ 32 slide ngày 02/10, đầu vào gốc | — |
| 1 | `b1_rut_gon_19.py` | Rút còn 19 slide (Minh dựng ngày 14/10) | nội dung 19 slide gốc, số liệu trong hình |
| 2 | `b2_bo_sung.py`, `figs_bo_sung.js` | Chèn bốn slide theo yêu cầu của GVHD ngày 05/10 | bốn slide này |
| 3 | `b3_hoan_thien.py` | Tiêu đề, dòng tóm tắt, từ ngữ, ghi chú, mục lục, slide chuyển phần, E19, biểu tượng, slide khoảng trống và kết quả, tài liệu tham khảo rút gọn, cách điều khiển | mọi chữ trên slide, cách điều khiển |
| xuất | `xuat_pdf.py` | PDF | — |

Mỗi chỗ sửa là một phép thay chuỗi có kiểm số lần khớp; nguồn không khớp thì script dừng.
`b3_hoan_thien.py` còn chặn các từ ngữ đời thường đã loại (ví dụ "bịa", "đoán bừa"). Biểu tượng là
một bộ SVG nét mảnh vẽ trong `b3_hoan_thien.py` (`ICONS`), không dùng thư viện ngoài. `nguon/img/`
giữ ảnh gốc (logo trường, hình minh họa); trong HTML các ảnh này đã nhúng sẵn.
