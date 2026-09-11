# Ảnh cho trang chủ — sinh bằng GPT image, thả vào đây, chạy một lệnh hiệu chuẩn

Trang `index.html` chạy được khi **chưa có ảnh nào**: cú vẽ bằng SVG thay chỗ — chỉ là chỗ
giữ, trông "giả" là đúng. Cái nhìn thật đến từ ảnh GPT image sinh theo **ảnh cú đại bàng tham
chiếu** (cú xám lông đốm, mắt cam rực, nền đen) — kèm ảnh đó vào phiên chat rồi dùng prompt
dưới. Cách ghép ảnh tĩnh với hoạt ảnh: trang **vẽ đè cả mống mắt lẫn đồng tử** lên vùng mắt của
ảnh, nên mắt trong ảnh tốt nhất là **đĩa cam trơn**; có điểm sáng nhỏ hay đồng tử vẫn được
(script đo theo khung bao). `scripts/calibrate_owl.py` tìm hai đĩa cam, ghi tọa độ vào
`static/owl.json`, nén PNG sang WebP.

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

## Prompt — kèm ảnh cú tham chiếu vào cùng phiên chat

Chọn một trong hai phong cách rồi giữ nguyên cho cả bộ: **(A) 3D siêu thực** giống ảnh tham
chiếu, hoặc **(B) cú bông 3D** (plush, lông mềm, dễ thương nhưng vẫn ngầu). Thay `[STYLE]`
bằng câu tương ứng:

- A: *hyper-realistic 3D render, real feather detail, cinematic studio lighting, like the reference photo*
- B: *high-end 3D plush toy render, soft dense felt fur, subtle stitching, cinematic lighting, still fierce*

**owl-face.png** (2048 × 2048, nền trong suốt)

> Use the attached owl photo as the character reference. Extreme close-up portrait of this
> Eurasian eagle-owl, face filling the frame, grey-brown mottled feathers, dark and moody,
> [STYLE]. The owl wears thin round wire-rim scientist glasses. Both eyes are large, perfectly
> flat, solid glowing amber-orange discs with no pupil, no reflection and no iris texture. The
> edges of the head fade out into transparency. Transparent background PNG, square.

**owl-prof.png** (2048 × 2560, 4:5)

> Same owl character as before, full body, perched upright on a bare oak branch, wearing thin
> round wire-rim glasses and a small open white lab coat, wings folded, calm confident posture
> like a professor about to lecture. Eyes are flat solid amber discs, no pupils. [STYLE].
> Isolated subject on a transparent background, portrait 4:5.

**owl-prof-point.png** (2048 × 2560)

> Identical to the previous image in every detail — same owl, glasses, lab coat, branch,
> lighting and framing — except the right wing is raised and extended sideways as if
> presenting something to the viewer. Transparent background PNG.

**branch.png** (2400 × 800)

> A single bare oak branch with a few leaves, seen from the side, entering from the left and
> ending in the middle, dark textured bark, [STYLE], isolated on a transparent background, no
> owl, wide 3:1.

**chunk-aware.png** (1600 × 1000)

> Flat editorial illustration on a near-black background with warm amber accents. A short
> paragraph represented as four horizontal text-like bars stacked vertically; below them a
> rounded speech bubble representing an answer. Dotted beams of amber light rise from the
> bubble to the bars — most of the light lands on the second bar, which glows warm orange; the
> others stay dim. Clean geometric style, no readable text, no people, 16:10.

Ảnh cú tĩnh cho slide bảo vệ (không dùng trên trang, mắt bình thường có đồng tử):

> Same owl professor with round glasses and a white lab coat, warm amber eyes with pupils,
> looking straight at the camera, dark background, [STYLE].
