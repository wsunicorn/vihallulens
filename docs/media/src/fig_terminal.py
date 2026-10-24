"""Terminal figure: the shape of the code base and the test run behind it.

The numbers are counted from the working tree by ``fig_terminal_counts`` and the
pytest line is the run recorded on 18/09/2026 on the personal machine.

Run:  python docs/media/src/fig_terminal.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent.parent / "hinh_terminal_ma_nguon.html"

# Light palette, so the figure prints on paper the way the rest of the report does. The
# tokens are the landing page's own light theme (``data-theme="light"`` in
# ``src/vihallulens/serve/static/index.html``), which the screenshots also use, and every
# ink here stays dark enough to read once the page is photocopied in grey.
BG = "#ffffff"          # --card
BAR = "#f1ebe0"         # --bg2, the title bar
LINE = "#e0d9cc"        # --line, one shade darker so the frame shows on white paper
FG = "#1d1a17"          # --ink
DIM = "#6e675d"         # --muted
GREEN = "#2f7d4f"       # --ok, the prompt and the passing test line
YELLOW = "#8a5a12"      # --warn darkened: amber on white is unreadable
BLUE = "#2c5d8f"        # the tree branches
WIN_W = 760             # terminal window width in CSS px

LINES = [
    ("prompt", "vihallulens $ ", "tree -L 1 --dirsfirst"),
    ("out", ".", ""),
    ("tree", "├── configs/", "21 tệp YAML — mỗi thí nghiệm một tệp"),
    ("tree", "├── data/", "raw · interim · processed (gitignore, trừ MANIFEST.md)"),
    ("tree", "├── docs/", "SPEC · DATA · EXPERIMENTS · REFERENCES"),
    ("tree", "├── models/", "e03_chunk_aware.pkl — 11,5 KB"),
    ("tree", "├── notebooks/", "15 notebook Kaggle, chỉ gọi hàm từ src/"),
    ("tree", "├── results/", "runs.jsonl · tradeoff.csv · error_analysis.json"),
    ("tree", "├── scripts/", "32 điểm vào CLI"),
    ("tree", "├── src/vihallulens/", "43 tệp .py — 5.573 dòng"),
    ("tree", "├── tests/", "40 tệp test — 7.373 dòng"),
    ("tree", "├── CLAUDE.md  TASKS.md  README.md", ""),
    ("tree", "└── Dockerfile  docker-compose.yml  pyproject.toml", ""),
    ("blank", "", ""),
    ("prompt", "vihallulens $ ", "python -m pytest -q      # tập test thuần logic"),
    ("dots", "." * 52, "[ 100% ]"),
    ("ok", "688 passed", " — 0 thất bại, 0 bỏ qua"),
    ("dim", "  6 tệp cần torch/CUDA hoặc pyvi không chạy trên máy này;", ""),
    ("dim", "  chúng được chạy cùng notebook trên Kaggle", ""),
    ("blank", "", ""),
    ("prompt", "kaggle $ ", "curl -s localhost:8000/health | jq -c"),
    ("json", '{"status":"ok","model_loaded":true,"bundle":"models/e03_chunk_aware.pkl",', ""),
    ("json", ' "reading_model":"Qwen/Qwen2.5-7B-Instruct","chunking":"sentence",', ""),
    ("json", ' "device":"cuda","vram_allocated_mb":8328,"requests_served":0}', ""),
    ("blank", "", ""),
    ("prompt", "vihallulens $ ", "docker compose up --build"),
    ("dim", "  ảnh 10,5 GB · trọng số 15 GB tải vào volume", ""),
    ("dim", "  GET /health → ok khi mô hình đã nạp", ""),
    ("blank", "", ""),
    ("dim", "  Khối tree đếm trên cây làm việc ngày 18/09/2026; khối /health", ""),
    ("dim", "  lấy từ phiên Kaggle Tesla T4 ngày 11/09/2026.", ""),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def row(kind: str, a: str, b: str) -> str:
    if kind == "blank":
        return '<div class="l">&nbsp;</div>'
    if kind == "prompt":
        return (f'<div class="l"><span class="p">{esc(a)}</span>'
                f'<span class="c">{esc(b)}</span></div>')
    if kind == "tree":
        # notes start at column 22, just past the longest name ("├── src/vihallulens/"),
        # which keeps every line inside the window at the 17 px face
        pad = "&nbsp;" * max(2, 22 - len(a))
        note = f'<span class="d">{pad}{esc(b)}</span>' if b else ""
        return f'<div class="l"><span class="t">{esc(a)}</span>{note}</div>'
    if kind == "dots":
        return (f'<div class="l"><span class="g">{esc(a)}</span>'
                f'<span class="d">&nbsp;&nbsp;{esc(b)}</span></div>')
    if kind == "ok":
        return (f'<div class="l"><span class="g b">{esc(a)}</span>'
                f'<span class="d">{esc(b)}</span></div>')
    if kind == "json":
        return f'<div class="l"><span class="j">{esc(a)}</span></div>'
    if kind == "dim":
        return f'<div class="l"><span class="d">{esc(a)}</span></div>'
    return f'<div class="l">{esc(a)}</div>'


HTML = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>terminal</title>
<style>
  html,body {{ margin:0; padding:0; background:#ffffff; }}
  .win {{ width:{WIN_W}px; margin:14px; background:{BG}; border-radius:10px;
          border:1px solid {LINE};
          box-shadow:0 8px 24px rgba(60,40,10,.14); overflow:hidden; }}
  .bar {{ height:40px; background:{BAR}; border-bottom:1px solid {LINE};
          display:flex; align-items:center; padding:0 14px; gap:8px; }}
  .dot {{ width:12px; height:12px; border-radius:50%; }}
  .ttl {{ flex:1; text-align:center; color:{DIM}; font:15px/1
          'Segoe UI',system-ui,sans-serif; letter-spacing:.02em; }}
  .body {{ padding:16px 20px 20px; font:17px/1.55 Consolas,'DejaVu Sans Mono',monospace;
           color:{FG}; white-space:pre; }}
  .p {{ color:{GREEN}; }} .c {{ color:{FG}; font-weight:600; }}
  .t {{ color:{BLUE}; }}  .d {{ color:{DIM}; }}
  .g {{ color:{GREEN}; }} .b {{ font-weight:700; }}
  .j {{ color:{YELLOW}; }}
</style></head><body>
<div class="win">
  <div class="bar">
    <span class="dot" style="background:#ff5f57"></span>
    <span class="dot" style="background:#febc2e"></span>
    <span class="dot" style="background:#28c840"></span>
    <span class="ttl">vihallulens — cấu trúc mã nguồn, kiểm thử và dịch vụ</span>
  </div>
  <div class="body">{''.join(row(*r) for r in LINES)}</div>
</div>
</body></html>"""

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from method_figs import render

    OUT.write_text(HTML, encoding="utf-8")
    print(f"wrote {OUT.name}")
    # printed 15,5 cm wide, this page puts 17 px of text at ~9,5 pt
    render(OUT.stem, WIN_W + 28, 1200, ext="html", trim=True)
