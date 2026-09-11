# Ảnh cho trang chủ — sinh bằng GPT image, thả vào đây, chạy một lệnh hiệu chuẩn

Trang `index.html` chạy được khi **chưa có ảnh nào**: cú vẽ bằng SVG thay chỗ — chỉ là chỗ
giữ, trông "giả" là đúng. Cái nhìn thật đến từ ảnh GPT image sinh theo **ảnh cú đại bàng tham
chiếu** (`img/original.jpg`: cú xám lông vằn trắng-xám, mặt đối xứng, **mắt lam ngọc** rực, nền đen) — kèm ảnh đó vào phiên chat rồi dùng prompt
dưới. Cách ghép ảnh tĩnh với hoạt ảnh: trang **vẽ đè cả mống mắt lẫn đồng tử** lên vùng mắt của
ảnh, nên mắt trong ảnh tốt nhất là **đĩa màu trơn** (lam ngọc theo ảnh gốc; cam cũng nhận với `--eye amber`); có điểm sáng nhỏ hay đồng tử vẫn được
(script đo theo khung bao). `scripts/calibrate_owl.py` tìm hai đĩa màu, ghi tọa độ vào
`static/owl.json`, nén PNG sang WebP.

Giữ **cùng một nhân vật** qua các ảnh: sinh trong cùng phiên chat, tham chiếu ảnh trước.
Nền **trong suốt** (PNG). Sau khi có ảnh:

```
python scripts/calibrate_owl.py face owl-face.png                      # mắt lam ngọc (mặc định)
python scripts/calibrate_owl.py prof owl-prof.png --variant point owl-prof-point.png
```

Bộ ảnh đầu tiên (11/09) sinh với mắt cam nên hiệu chuẩn bằng `--eye amber`; trang vẫn vẽ mắt
lam ngọc đè lên. PNG gốc để trong thư mục này nhưng **gitignore** — chỉ WebP được commit.

Hai lệnh trên ghi `img/owl-face.webp`, `img/owl-prof.webp`, `img/owl-prof-point.webp` và
`owl.json`. Ảnh nào script báo "chỉ tìm thấy 0/1 đĩa hổ phách" là mắt chưa đủ đồng nhất — sinh
lại với prompt nhấn mạnh *solid flat orange discs, no pupil, no reflection*. Mỗi WebP nên dưới
2 MB (script cảnh báo).

| File | Dùng ở đâu | Kích thước gợi ý |
|---|---|---|
| `owl-face.png` | hero nhịp 1 (mặt cận đè tiêu đề), cú góc phải, biểu tượng nav | 2048 × 2048 |
| `owl-prof.png` | hero nhịp 2–3, Giáo sư Lens đậu trên cành | 2048 × 2560 (4:5) |
| `owl-prof-point.png` | cùng tư thế, cánh phải giơ ra "giới thiệu" — trang hoán đổi khi tấm giới thiệu hiện | 2048 × 2560 |
| `branch.png` → tự đổi tên `branch.webp` | cành cây tiền cảnh, parallax | 2400 × 800 |
| `chunk-aware.png` → `chunk-aware.webp` | khung minh họa mục Chunk-aware | 1600 × 1000 |

`branch` và `chunk-aware` không có mắt nên không qua script: tự nén sang WebP (bất kỳ công cụ
nào, chất lượng ~85) và đặt đúng tên.

## Prompt — đính `original.jpg` vào cùng phiên chat làm ảnh tham chiếu

Giữ nguyên nhân vật qua cả bộ. Phong cách: **3D siêu thực như ảnh tham chiếu**.

**owl-face.png** (2048 × 2048, nền trong suốt)

> Use the attached owl photo as the exact character reference: a grey owl with fine white-and-
> grey streaked feathers, a perfectly symmetrical face, dark feathering around the eyes, and
> intense glowing turquoise-cyan eyes. Extreme close-up portrait, face filling the frame,
> hyper-realistic 3D render, real feather detail, dark moody studio lighting. The owl wears thin
> round wire-rim scientist glasses. Both eyes are large, perfectly flat, solid glowing
> turquoise discs (#2ce8d6) with no pupil, no reflection and no iris texture. The edges of the
> head fade into transparency. Transparent background PNG, square.

**owl-prof.png** (2048 × 2560, 4:5)

> Same grey owl character as the reference, full body, perched upright on a bare oak branch,
> wearing thin round wire-rim glasses and a small open white lab coat with a pen in the pocket,
> wings folded, calm confident posture like a professor about to lecture. Eyes are flat solid
> glowing turquoise discs, no pupils. Hyper-realistic 3D render, dark moody lighting, isolated
> subject on a transparent background, portrait 4:5.

**owl-prof-point.png** (2048 × 2560)

> Identical to the previous image in every detail — same owl, glasses, lab coat, branch,
> lighting and framing — except the right wing is raised and extended sideways as if
> presenting something to the viewer. Transparent background PNG.

**branch.png** (2400 × 800)

> A single bare oak branch with a few dry leaves and lichen, seen from the side, entering from
> the left and ending in the middle, dark textured bark, photorealistic, isolated on a
> transparent background, no owl, wide 3:1.

**chunk-aware.png** (1600 × 1000)

> Flat editorial illustration on a near-black background with turquoise and amber accents. A
> short paragraph represented as four horizontal text-like bars stacked vertically; below them
> a rounded speech bubble representing an answer. Dotted beams of light rise from the bubble to
> the bars — most of the light lands on the second bar, which glows; the others stay dim. Clean
> geometric style, no readable text, no people, 16:10.

## Cử chỉ thêm — mỗi cử chỉ một ảnh, cùng tư thế gốc của `owl-prof.png`

Trang đã có sẵn cơ chế khung hình: mỗi biến thể là một ảnh, tên biến thể quyết định lúc nào
dùng. Không có ảnh thì trang tự dùng cử chỉ thay thế (vẫy bằng hai khung base/point, gật, rung).

| Biến thể | Trang dùng khi | Prompt (kèm ảnh `owl-prof.png` làm tham chiếu, giữ y hệt mọi thứ) |
|---|---|---|
| `wave` | chào khi tấm giới thiệu hiện, bấm vào cú | *…except the right wing is raised high above the head, feathers spread open, mid-wave as if greeting someone.* |
| `think` | bộ phát hiện đang chấm, phán quyết nội tại | *…except the right wing is bent so the wingtip touches the chin, head tilted slightly, a pondering pose.* |
| `shock` | phán quyết ngoại lai | *…except both wings are spread wide and the feathers on the head are puffed up, startled.* |
| `happy` | phán quyết trung thực | *…except the right wing rests on the chest and the body leans forward slightly, a small satisfied bow.* |

Mở đầu mỗi prompt: *Identical to the reference image in every detail — same owl, glasses, lab
coat, branch, lighting, framing and flat turquoise eyes —*. Rồi hiệu chuẩn **tất cả biến thể trong
một lệnh** (lệnh này ghi lại toàn bộ danh sách biến thể):

```
python scripts/calibrate_owl.py prof owl-prof.png --variant point owl-prof-point.png     --variant wave owl-prof-wave.png --variant think owl-prof-think.png     --variant shock owl-prof-shock.png --variant happy owl-prof-happy.png
```

Ảnh cú tĩnh cho slide bảo vệ (không dùng trên trang, mắt bình thường có đồng tử):

> Same grey owl professor with round glasses and a white lab coat, glowing turquoise eyes with
> dark pupils, looking straight at the camera, dark background, hyper-realistic 3D render.
