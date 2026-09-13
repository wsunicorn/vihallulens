# Bộ slide trình bày với GVHD — cách dùng

Mọi thứ nằm trong thư mục này: `slide.html` (bộ slide, một file), `img/` (ảnh), `ke_hoach_slide.md`
(kế hoạch đã duyệt). Không cần cài gì, không cần mạng — font Google chỉ là thêm, không có thì
dùng font hệ thống.

## Trình chiếu

1. Mở `slide.html` bằng **Edge hoặc Chrome** (kéo thả vào trình duyệt là được).
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
| click phải màn hình / cuộn chuột / vuốt | cũng đi tới, đi lui |

Địa chỉ có dạng `slide.html#13` — mở thẳng slide 13 khi cần.

## Ghi chú diễn giả

Mỗi slide có sẵn 2–4 câu ghi chú (thuộc tính `data-notes` trong file). Cách dùng hai màn hình:
mở `slide.html` hai lần, một cửa sổ kéo sang máy chiếu bấm `F`, cửa sổ kia trên laptop bấm `N`;
hai cửa sổ không đồng bộ nên bấm tiến ở cả hai — hoặc đơn giản in ghi chú ra giấy.

## Bản dự phòng PDF (đề phòng máy phòng thầy không mở được HTML)

1. Mở `slide.html?all#1` (tham số `?all` hiện sẵn mọi phần tử).
2. `Ctrl+P` → máy in "Save as PDF" → bật **Background graphics** → khổ giấy mặc định (đã khai
   1920 × 1080) → Save. Ra 22 trang, mỗi trang một slide.

Muốn PowerPoint thật: mở PDF ấy trong PowerPoint (Insert → Pictures từng trang) hoặc đưa PDF
cho tôi để tôi dựng `.pptx` — nhưng khi đó mất animation.

## Sửa nội dung

`slide.html` là văn bản thuần. Mỗi slide là một khối `<section class="slide">`. Phần tử có
`class="f"` là phần tử hiện theo bước; số có `data-count` sẽ đếm lên. Sửa chữ xong lưu, F5.
Muốn thêm slide thì chép một khối `<section>` và dán vào chỗ mong muốn — số trang tự cập nhật.

## Demo trực tiếp (tùy chọn, cần laptop có mạng hoặc server chạy sẵn)

Trước buổi: trong thư mục repo chạy `python scripts/serve.py`-không-mô-hình theo cách ở dưới,
rồi ở slide 17 nhấn `Alt+Tab` sang tab trình duyệt mở `http://127.0.0.1:8000/` — trang chạy
chế độ phát lại, đủ để cú Lens cử động và bấm năm câu hỏi.

```
uv run python -c "import sys; sys.path.insert(0,'src'); import uvicorn; from vihallulens.serve.app import create_app; uvicorn.run(create_app(detector=None, load_on_startup=False), port=8000)"
```
