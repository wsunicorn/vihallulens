# Ảnh cho trang chủ — sinh bằng GPT image, thả vào đây, chạy một lệnh hiệu chuẩn

Trang `index.html` chạy được khi **chưa có ảnh nào**: cú vẽ bằng SVG thay chỗ. Có ảnh thì
đẹp hơn nhiều, và cách ghép ảnh tĩnh với hoạt ảnh là: mắt trong ảnh phải là **đĩa hổ phách
đồng nhất, không đồng tử, không điểm sáng** — trang vẽ đồng tử đè lên và cho nó dõi theo con
trỏ, chớp, đổi màu theo phán quyết. `scripts/calibrate_owl.py` tự tìm hai đĩa ấy trong ảnh,
ghi tọa độ vào `static/owl.json`, và nén PNG sang WebP.

Giữ **cùng một nhân vật** qua các ảnh: sinh trong cùng phiên chat, tham chiếu ảnh trước.
Nền **trong suốt** (PNG). Sau khi có ảnh:

```
python scripts/calibrate_owl.py face owl-face.png
python scripts/calibrate_owl.py prof owl-prof.png --variant point owl-prof-point.png
```

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

## Prompt

**owl-face.png**

> Ultra close-up portrait of a Eurasian eagle-owl, the face fills the frame, dark charcoal and
> grey feathers with fine detail, dramatic low-key studio lighting, the edges of the head fade
> into transparency. The owl wears thin round wire-rim scientist glasses. Both eyes are large,
> perfectly uniform, flat glowing amber-orange discs with NO pupil, NO reflection, NO iris
> texture — solid orange circles. Photorealistic, cinematic, transparent background PNG.

**owl-prof.png**

> The same eagle-owl character, full body, perched upright on a bare oak branch, wearing thin
> round wire-rim glasses and a small open white lab coat, wings folded, calm confident posture
> like a professor about to lecture. Eyes are uniform flat glowing amber discs with no pupils
> and no reflections. Dark feathers, dramatic side lighting, isolated subject on a transparent
> background, photorealistic, portrait 4:5.

**owl-prof-point.png**

> Identical to the previous image in every detail — same owl, same glasses, same lab coat, same
> branch, same lighting, same framing — except the right wing is raised and extended sideways,
> as if presenting something to the viewer. Transparent background PNG.

**branch.png**

> A single bare oak branch with a few leaves, seen from the side, entering from the left and
> ending in the middle, dark bark with fine texture, photorealistic, isolated on a transparent
> background, no owl, no other objects, wide 3:1.

**chunk-aware.png**

> Flat editorial illustration on a near-black background with warm amber accents. A short
> paragraph represented as four horizontal text-like bars stacked vertically; below them a
> rounded speech bubble representing an answer. Dotted beams of amber light rise from the
> bubble to the bars — most of the light lands on the second bar, which glows warm orange; the
> others stay dim. Clean geometric style, no readable text, no people, 16:10.

Ảnh cú tĩnh cho slide bảo vệ (không dùng trên trang) — cùng nhân vật, mắt có đồng tử bình
thường:

> Portrait of the same eagle-owl professor with round glasses and a white lab coat, warm
> amber eyes with pupils, looking at the camera, dark background, cinematic lighting.
