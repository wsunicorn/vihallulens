# Bộ slide trình bày với GVHD — cách dùng

Mọi thứ nằm trong thư mục này. Có **hai bộ**, dùng bộ nào cũng được, phím bấm giống nhau:

| File | Là gì |
|---|---|
| **`slide_v2.html`** | **Bộ chính (18/09/2026)** — 36 slide theme "Đêm cú" (nền tối, lam ngọc + hổ phách), bám 8 chương mẫu báo cáo Khoa, sân khấu 1920 × 1080 cố định nên không bao giờ tràn chữ theo màn hình. Kế hoạch: `ke_hoach_slide_v2.md`; luật dựng: `BI_KIP_HTML_SLIDE.md`; năm mẫu theme đã so: `mau/`. |
| `slide.html` | Bộ v1 (13/09) — 22 slide nền sáng, giữ để đối chiếu. |

Cả hai là một file HTML tự chứa, `img/` là ảnh dùng chung. Không cần cài gì, không cần mạng —
font Google chỉ là thêm, không có thì dùng font hệ thống.

Ba kiểu hoạt ảnh trong `slide_v2.html`, cố ý dùng đúng chỗ: **lặp** (tia chú ý chảy, hạt trôi về
mắt cú, điểm đỏ nhấp — không khí và ẩn dụ), **một lần rồi dừng** (sơ đồ dựng lên, cột mọc, số đếm
— để khán giả còn đọc trạng thái cuối), **theo bước** (phím `→` cho lập luận nhiều nhịp).

## Trình chiếu

1. Mở `slide_v2.html` (hoặc `slide.html`) bằng **Edge hoặc Chrome** (kéo thả vào trình duyệt là được).
2. Bấm **F** (hoặc F11) để toàn màn hình.
3. Điều khiển:

| Phím | Việc |
|---|---|
| `→` `Space` `Enter` `PageDown` | bước tiếp: hiện phần tử kế, hết phần tử thì sang slide sau |
| `←` `PageUp` `Backspace` | về slide trước |
| `A` | hiện **tất cả** phần tử của slide hiện tại (khi cần nhảy nhanh) |
| `N` | bật/tắt **ghi chú diễn giả** ở cạnh phải (chỉ bạn thấy nếu chiếu bằng "mở rộng màn hình") |
| `1`–`9`, `0` | nhảy tới slide 1–10; `Home`/`End` slide đầu/cuối |
| `?` | hiện/ẩn thanh trợ giúp |
| click phải màn hình / cuộn chuột / vuốt | cũng đi tới, đi lui (v2: click phải 80 % màn hình đi tới, 20 % bên trái đi lui) |

Địa chỉ có dạng `slide.html#13` — mở thẳng slide 13 khi cần.

## Ghi chú diễn giả

Mỗi slide có sẵn 2–4 câu ghi chú (thuộc tính `data-notes` trong file). Cách dùng hai màn hình:
mở `slide.html` hai lần, một cửa sổ kéo sang máy chiếu bấm `F`, cửa sổ kia trên laptop bấm `N`;
hai cửa sổ không đồng bộ nên bấm tiến ở cả hai — hoặc đơn giản in ghi chú ra giấy.

## Bản dự phòng PDF (đề phòng máy phòng thầy không mở được HTML)

1. Mở `slide_v2.html?all#1` (tham số `?all` hiện sẵn mọi phần tử, tắt mọi hoạt ảnh vào).
2. `Ctrl+P` → máy in "Save as PDF" → bật **Background graphics** → khổ giấy mặc định (đã khai
   1920 × 1080) → Save. Ra 36 trang (v1: 22), mỗi trang một slide.

Muốn PowerPoint thật: mở PDF ấy trong PowerPoint (Insert → Pictures từng trang) hoặc đưa PDF
cho tôi để tôi dựng `.pptx` — nhưng khi đó mất animation.

## Sửa nội dung

`slide.html` là văn bản thuần. Mỗi slide là một khối `<section class="slide">`. Phần tử có
`class="f"` là phần tử hiện theo bước; số có `data-count` sẽ đếm lên. Sửa chữ xong lưu, F5.
Muốn thêm slide thì chép một khối `<section>` và dán vào chỗ mong muốn — số trang tự cập nhật.

## Demo trực tiếp (tùy chọn, cần laptop có mạng hoặc server chạy sẵn)

Trước buổi: trong thư mục repo chạy `python scripts/serve.py`-không-mô-hình theo cách ở dưới,
rồi ở slide 23 (v1: slide 17) nhấn `Alt+Tab` sang tab trình duyệt mở `http://127.0.0.1:8000/` — trang chạy
chế độ phát lại, đủ để cú Lens cử động và bấm năm câu hỏi.

```
uv run python -c "import sys; sys.path.insert(0,'src'); import uvicorn; from vihallulens.serve.app import create_app; uvicorn.run(create_app(detector=None, load_on_startup=False), port=8000)"
```
