"""Find the owl's eyes in a generated image and write the pupil rig for the landing page.

The mascot on ``/`` is a raster image (GPT image, see ``serve/static/img/PROMPTS.md``) whose
eyes are drawn as **uniform amber discs with no pupil**; the page overlays moving pupils on top
so the owl follows the pointer. Every generated image puts the eyes somewhere else, so the eye
centres cannot be hard-coded: this script thresholds the amber hue, keeps the two largest
blobs, and writes their centre and radius as fractions of the image size to
``serve/static/owl.json``. It also converts the PNG to a WebP with alpha, capped at
``--max-side`` pixels, which is what the page loads.

    python scripts/calibrate_owl.py face  path/to/owl-face.png          # --eye amber nếu mắt cam
    python scripts/calibrate_owl.py prof  path/to/owl-prof.png \
        --variant point path/to/owl-prof-point.png
    python scripts/calibrate_owl.py --show           # print the current rig

Needs Pillow and numpy (dev extra). Nothing here touches the model or the results.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "vihallulens" / "serve" / "static"
RIG = STATIC / "owl.json"
IMG = STATIC / "img"

# Eye colour as a hue window (fraction of 360°). Feathers are grey/brown, far less saturated.
# A small white highlight inside the eye is fine (bounding box below), a dark pupil is fine too.
EYE_HUES = {
    "cyan": (160 / 360, 200 / 360),   # the turquoise of img/original.jpg (measured median 176°)
    "amber": (12 / 360, 55 / 360),
}
MIN_SAT = 0.5
MIN_VAL = 0.5


def eye_mask(rgba: np.ndarray, eye: str) -> np.ndarray:
    from PIL import Image

    img = Image.fromarray(rgba, "RGBA")
    hsv = np.asarray(img.convert("RGB").convert("HSV"), dtype=np.float32) / 255.0
    alpha = rgba[..., 3] > 128
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    lo, hi = EYE_HUES[eye]
    return alpha & (h >= lo) & (h <= hi) & (s >= MIN_SAT) & (v >= MIN_VAL)


def components(mask: np.ndarray) -> list[tuple[int, float, float, float, float]]:
    """(size, cx, cy, rx, ry) of each 4-connected blob, largest first. Pure numpy flood fill."""
    from collections import deque

    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs, strict=True):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        pts = []
        while q:
            y, x = q.popleft()
            pts.append((y, x))
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(pts) < 200:
            continue
        arr = np.asarray(pts)
        # Centre and radius from the bounding box, not the area: a highlight or a painted pupil
        # punches a hole in the amber blob and would shrink an area-based radius.
        (y0, x0), (y1, x1) = arr.min(axis=0), arr.max(axis=0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = float(x1 - x0 + 1) / 2, float(y1 - y0 + 1) / 2
        out.append((len(pts), float(cx), float(cy), rx, ry))
    out.sort(reverse=True)
    return out


def find_eyes(path: Path, eye: str) -> tuple[list[dict], tuple[int, int]]:
    from PIL import Image

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    scale = 1.0
    if max(w, h) > 1024:  # flood fill in pure Python: work on a smaller copy
        scale = 1024 / max(w, h)
        img = img.resize((round(w * scale), round(h * scale)))
    rgba = np.asarray(img)
    blobs = components(eye_mask(rgba, eye))
    if len(blobs) < 2:
        raise SystemExit(f"chỉ tìm thấy {len(blobs)} đĩa màu {eye} trong {path.name} — mắt phải là "
                         "đĩa màu trơn (xem PROMPTS.md), hoặc thử --eye khác")
    eyes = sorted(blobs[:2], key=lambda b: b[1])  # left eye first
    sw, sh = rgba.shape[1], rgba.shape[0]
    # r stays for older pages; rx/ry (fractions of width and height) let an oval eye be covered
    return [{"cx": round(cx / sw, 4), "cy": round(cy / sh, 4), "r": round(max(rx, ry) / sw, 4),
             "rx": round(rx / sw, 4), "ry": round(ry / sh, 4)}
            for _, cx, cy, rx, ry in eyes], (w, h)


def to_webp(src: Path, dst: Path, max_side: int) -> int:
    from PIL import Image

    img = Image.open(src).convert("RGBA")
    if max(img.size) > max_side:
        k = max_side / max(img.size)
        img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "WEBP", quality=88, method=6)
    return dst.stat().st_size


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Hiệu chuẩn mắt cú cho trang chủ.")
    parser.add_argument("layer", nargs="?", choices=("face", "prof"), help="lớp ảnh")
    parser.add_argument("image", nargs="?", type=Path, help="PNG nền trong suốt")
    parser.add_argument("--variant", nargs=2, metavar=("TEN", "PNG"), action="append", default=[],
                        help="ảnh biến thể cùng tư thế, ví dụ: --variant point owl-prof-point.png")
    parser.add_argument("--eye", choices=tuple(EYE_HUES), default="cyan",
                        help="màu mắt trong ảnh: cyan (theo img/original.jpg) hay amber")
    parser.add_argument("--max-side", type=int, default=1600)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    rig = json.loads(RIG.read_text(encoding="utf-8")) if RIG.exists() else {}
    if args.show or not args.layer:
        print(json.dumps(rig, ensure_ascii=False, indent=2))
        return 0
    if not args.image or not args.image.is_file():
        parser.error("cần đường dẫn ảnh PNG")

    eyes, (w, h) = find_eyes(args.image, args.eye)
    name = f"owl-{args.layer}.webp"
    size = to_webp(args.image, IMG / name, args.max_side)
    entry = {"file": f"img/{name}", "aspect": round(w / h, 4), "eyes": eyes}
    entry["variants"] = {}
    for vname, vpath in args.variant:
        vfile = f"owl-{args.layer}-{vname}.webp"
        vsize = to_webp(Path(vpath), IMG / vfile, args.max_side)
        try:
            veyes, _ = find_eyes(Path(vpath), args.eye)
        except SystemExit:
            veyes = eyes  # same pose, eyes not found: reuse the base positions
            print(f"  {vname}: không tìm thấy mắt, dùng tọa độ ảnh gốc")
        entry["variants"][vname] = {"file": f"img/{vfile}", "eyes": veyes}
        print(f"  {vfile}: {vsize / 1e3:.0f} KB")
    rig[args.layer] = entry
    RIG.write_text(json.dumps(rig, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  {name}: {size / 1e3:.0f} KB, {w}×{h}")
    for i, e in enumerate(eyes):
        print(f"  mắt {i + 1}: tâm ({e['cx']:.3f}, {e['cy']:.3f}) bán kính ngang {e['rx']:.3f} "
              f"dọc {e['ry']:.3f} (tỷ lệ theo bề rộng / bề cao)")
    if size > 2_000_000:
        print("  CẢNH BÁO: ảnh trên 2 MB, hạ --max-side")
    print(f"  ghi {RIG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
