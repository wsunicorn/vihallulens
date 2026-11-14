# Bộ slide — cách dùng

Cập nhật 14/11/2026. Bộ dùng để báo cáo trước Hội đồng là **`slide_hoi_dong.html`** (31 slide).

## File trong thư mục

| File | Là gì |
|---|---|
| **`slide_hoi_dong.html`** | **Bộ chính, 31 slide**, sắp theo bố cục tám chương của quyển: bìa, nội dung trình bày, rồi bảy phần (giới thiệu, cơ sở lý thuyết, dữ liệu, phương pháp đề xuất, hệ thống, thực nghiệm và kết quả, kết luận), mỗi phần mở đầu bằng một slide chuyển phần; cuối là tài liệu tham khảo và cảm ơn. Tiêu đề nêu tên nội dung, dòng ngay dưới tiêu đề tóm tắt kết luận của slide. Số liệu khớp quyển v5, kể cả ba thí nghiệm E17, E18, E19. |
| `slide_hoi_dong.pdf` | Trạng thái cuối của từng slide, một slide một trang. Dùng để in hoặc gửi kèm. |
| `GIAI_THICH_SLIDE.md` | Giải thích từng slide và **kịch bản thời gian** hai phương án (đủ khoảng 26–27 phút, rút khoảng 15 phút). |
| `HOI_DAP_HOI_DONG.md` | Câu hỏi hội đồng dễ hỏi kèm hướng trả lời, có số liệu và trỏ về số slide. |
| `nguon/` | Nguồn dựng bộ slide, xem mục *Dựng lại*. |
| `_build/` | Hai bộ trung gian (19 và 23 slide) do `dung_lai.py` sinh ra; không commit. |

## Trình chiếu

Mở `slide_hoi_dong.html` bằng **Edge hoặc Chrome**. File tự chứa (font, thư viện, ảnh, số liệu
đều nhúng sẵn), chạy không cần mạng.

**Người nói điều khiển từng bước.** Mỗi sơ đồ có 4–5 bước (các chấm số dưới hình). Khi chuyển tới
một slide, bước 1 tự chạy rồi **dừng**; mỗi lần bấm tới thì chạy thêm một bước, xong bước cuối thì
bấm tới sẽ sang slide sau. Nhờ vậy hình không chạy trước lời nói. Slide không có sơ đồ (bìa, mục
lục, chuyển phần, khoảng trống nghiên cứu, kết quả – hạn chế, tài liệu tham khảo) hiện ngay.

| Phím / thao tác | Việc |
|---|---|
| `→` `↓` `Space` `Enter` `PageDown` | bước kế; đang chạy dở thì cho chạy xong; hết bước thì sang slide sau |
| `←` `↑` `PageUp` `Backspace` | lùi một bước; đang ở bước 1 thì về slide trước, hiện sẵn trạng thái cuối |
| `Shift+→` / `Shift+←` | bỏ qua các bước, sang slide sau / về slide trước |
| gõ số rồi `Enter` (ví dụ `2` `2` `Enter`) | nhảy tới slide đó — tiện khi hội đồng hỏi lại một slide |
| bấm vào một chấm số dưới hình | nhảy tới bước đó |
| `B` hoặc `.` | bật / tắt màn hình đen (bấm chuột cũng tắt) |
| `R` | chạy lại bước hiện tại |
| `Home` / `End` | slide đầu / cuối |
| `N` | bật / tắt ghi chú diễn giả |
| `F` | toàn màn hình |
| click phía phải / trái màn hình | tới / lùi như phím; click **trong sơ đồ** thì không đổi bước (dành cho rê chuột, bấm nút) |

Bút trình chiếu (clicker) gửi `PageDown` / `PageUp`, nên dùng được ngay. Slide 22: bước 2 chỉ chạy
một mẫu; muốn xem thêm thì bấm nút "Mẫu khác" ở góc phải (dùng ở bước 2–4).

Địa chỉ dạng `slide_hoi_dong.html#21` mở thẳng slide 21. Thêm `?all` vào địa chỉ
(`slide_hoi_dong.html?all#1`) thì mọi sơ đồ hiện sẵn trạng thái cuối, dùng để chụp hoặc in.
Thêm `?qa` thì bộ slide tự dựng mọi sơ đồ, tua qua mọi bước và in `QA-OK` ở cuối trang nếu không
có lỗi. Thêm `?auto` thì sơ đồ tự chạy hết các bước như bản cũ (dùng khi quay màn hình).

## Ghi chú diễn giả

Mỗi slide có ghi chú (thuộc tính `data-notes`), xưng "nhóm em"; thao tác rê chuột, bấm nút ghi ở
cuối ghi chú của slide đó. Cả bộ khoảng 25 phút nói, chưa tính chuyển slide. Khi chiếu hai màn
hình: mở file hai lần, một cửa sổ trên máy chiếu bấm `F`, cửa sổ trên laptop bấm `N`.

## Dựng lại

Không sửa trực tiếp `slide_hoi_dong.html`. Sửa ở `nguon/` rồi dựng lại bằng một lệnh, chạy ở thư
mục gốc của repo:

```
python docs/slides/nguon/dung_lai.py
```

Thêm `--pdf` để xuất lại PDF; tùy chọn này cần Google Chrome và vài gói, chạy qua `uv`:

```
uv run --no-project --with playwright==1.48.0 --with pymupdf==1.25.5 --with pillow python docs/slides/nguon/dung_lai.py --pdf
```

Bộ slide dựng qua ba bước. Mỗi chỗ sửa là một phép thay chuỗi có kiểm số lần khớp, nguồn không
khớp thì script dừng thay vì bỏ qua:

| Bước | File trong `nguon/` | Làm gì | Sửa ở đây khi muốn đổi |
|---|---|---|---|
| — | `slide_goc_32.html` | Bộ 32 slide ngày 02/10, đầu vào gốc, không sửa file này | — |
| 1 | `b1_rut_gon_19.py` | Rút còn 19 slide (Minh dựng ngày 14/10) | nội dung 19 slide gốc, số liệu trong hình |
| 2 | `b2_bo_sung.py`, `figs_bo_sung.js` | Chèn bốn slide theo yêu cầu của GVHD ngày 05/10: bài toán, các hướng đã có, kiểm định giả thuyết, tài liệu tham khảo | bốn slide này; danh mục tài liệu (`REFS`) |
| 3 | `b3_hoan_thien.py` | Tiêu đề, dòng tóm tắt, từ ngữ học thuật, ghi chú diễn giả, mục lục, slide chuyển phần, bước E19, điều khiển từng bước và phím tắt | tiêu đề, ghi chú, cách dùng từ, cách điều khiển |
| xuất | `xuat_pdf.py` | PDF | — |

`b3_hoan_thien.py` còn chặn các từ ngữ đời thường đã loại (ví dụ "bịa", "đoán bừa"): nếu một bước
trước đưa lại từ đó lên slide thì script dừng và chỉ ra chỗ. `nguon/img/` giữ ảnh gốc (logo
trường, hình minh họa); trong HTML các ảnh này đã nhúng sẵn.
