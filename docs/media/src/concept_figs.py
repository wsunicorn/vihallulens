"""Conceptual figures for the theory and method chapters of the report.

Every figure is drawn on a 900 px canvas: printed across the 15,5 cm text column of the
report, one px of text is 0,49 pt on paper. Text uses the sizes named in method_figs.py
(T_BODY 19,5 px ≈ 9,5 pt, nothing under T_SMALL 18 px ≈ 8,8 pt). Laying the same content
out on a 1.500 px canvas would shrink it to half that.

Run:  python docs/media/src/concept_figs.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from method_figs import CHROME, T_BODY, T_LABEL, T_SMALL
from svgkit import Canvas, wrap

OUT = Path(__file__).resolve().parent.parent
MONO = "Consolas, 'DejaVu Sans Mono', monospace"

GREEN = "#2a8c82"
RED = "#b5452f"
ORANGE = "#d98032"
BLUE = "#3b6ea5"
NAVY = "#1f3a5f"
GRAY = "#8a8f98"
MUTED = "#b9c0c9"
INK_DARK = "#2b2b31"

TINT_GREEN = "#e4f2e9"
TINT_RED = "#fbe7e1"
TINT_ORANGE = "#fdf0dd"
TINT_BLUE = "#e3edf6"
TINT_GRAY = "#f2f2f4"

LH = 26                              # line pitch of T_BODY text
LH_S = 24                            # line pitch of T_SMALL text

# The four sentences of the running example; one sentence is one chunk.
SENTENCES = [
    "Vịnh Hạ Long nằm ở tỉnh Quảng Ninh.",
    "Vịnh gồm 1.969 hòn đảo lớn nhỏ.",
    "UNESCO công nhận vịnh là Di sản thiên nhiên thế giới lần đầu năm 1994.",
    "Năm 2000, vịnh được công nhận lần thứ hai về giá trị địa chất, địa mạo.",
]
SENT_W = [286, 262, 470, 470]        # relative lengths, used to draw the context ruler

PAGE_W = 900


def render(name: str, w: int, h: int, scale: int = 2) -> None:
    """Rasterise one generated SVG with headless Chrome."""
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         "--default-background-color=ffffff", f"--force-device-scale-factor={scale}",
         f"--window-size={w},{h}", f"--screenshot={OUT / (name + '.png')}",
         (OUT / f"{name}.svg").as_uri()],
        check=True, capture_output=True)
    print(f"{name}.png ({w * scale}x{h * scale})")


def text_left(c: Canvas, x, y, text, width, size=T_BODY, fill=INK_DARK, weight="normal",
              style="normal", family=None, line_h=None, balance=False) -> float:
    """Wrapped text anchored on the left; returns the y below the last line."""
    lines = wrap(text, width, size, bold=weight == "bold", balance=balance)
    lh = line_h or size * 1.3
    for k, line in enumerate(lines):
        c.raw_text(x, y + k * lh, line, size, fill=fill, weight=weight, style=style,
                   family=family)
    return y + len(lines) * lh


def head(c: Canvas, x, y, w, tint, radius=10, hdr=40) -> None:
    """The tinted strip across the top of a rounded box."""
    c.band(x, y, w, hdr, tint, radius=radius)
    c.add(f'<rect x="{x}" y="{y + hdr - 14}" width="{w}" height="14" fill="{tint}"/>')


# =========================================================================
# A. The three labels, and the attention signature the thesis bets on
# =========================================================================
def lift(c: Canvas, dy: float) -> None:
    """Drop the space an in-figure title used to take: the report caption is the title."""
    c.parts.insert(0, f'<g transform="translate(0,{-dy})">')
    c.parts.append("</g>")
    c.height -= dy


def fig_ba_loai_ao_giac() -> None:
    m = 30
    w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1300)

    # shared context, one row per sentence: these four sentences are the four chunks
    c.raw_text(m, 22, "NGỮ CẢNH TRUY XUẤT — BỐN CÂU, TỨC BỐN ĐOẠN", T_SMALL, fill=GRAY,
               weight="bold")
    y = 40
    for i, s in enumerate(SENTENCES):
        c.band(m, y, w, 36, TINT_GRAY, radius=5, stroke="#c8c8d0")
        c.raw_text(m + 14, y + 19, f"đoạn {i + 1}", T_SMALL, fill=GRAY, weight="bold")
        c.raw_text(m + 100, y + 19, s, T_BODY, fill=INK_DARK)
        y += 40
    y += 10

    cards = [
        ("no", "trung thực", GREEN, TINT_GREEN,
         "Vịnh Hạ Long được UNESCO công nhận là Di sản thiên nhiên thế giới lần đầu năm 1994.",
         "Mọi mệnh đề đều truy được về ngữ cảnh.",
         "Nhọn vào đoạn 3 — đúng đoạn mang mệnh đề.",
         [0.06, 0.09, 0.71, 0.14], 2),
        ("intrinsic", "ảo giác nội tại", ORANGE, TINT_ORANGE,
         "Vịnh Hạ Long được UNESCO công nhận là Di sản thiên nhiên thế giới lần đầu năm 2000.",
         "Ngữ cảnh CÓ nói về năm; mô hình đọc rồi dùng sai câu.",
         "Vẫn nhọn, nhưng nhọn vào đoạn 4 — đọc nhầm câu.",
         [0.05, 0.08, 0.29, 0.58], 3),
        ("extrinsic", "ảo giác ngoại lai", RED, TINT_RED,
         "Vịnh Hạ Long được công nhận năm 1994 và mỗi năm đón hơn bảy triệu lượt khách.",
         "Ngữ cảnh KHÔNG hề nói về lượng khách.",
         "Tản đều — không có đoạn nào để bám vào.",
         [0.24, 0.27, 0.26, 0.23], None),
    ]

    txt_w, chart_w = 470, w - 470 - 24
    for name, vi, color, tint, resp, note, sig, shares, hot in cards:
        rlines = wrap(resp, txt_w - 20, T_BODY)
        nlines = wrap(note, txt_w - 20, T_BODY, bold=True)
        slines = wrap(sig, chart_w - 8, T_SMALL)
        left_h = 40 + 38 + len(rlines) * LH + 10 + len(nlines) * LH + 8
        right_h = 176 + 50 + len(slines) * LH_S
        ch = max(left_h, right_h)
        c.add(f'<rect x="{m}" y="{y}" width="{w}" height="{ch}" rx="10" fill="#ffffff" '
              f'stroke="{color}" stroke-width="1.8"/>')
        head(c, m, y, w, tint)
        c.raw_text(m + 16, y + 21, name, T_LABEL, fill=color, weight="bold", family=MONO)
        c.raw_text(m + w - 16, y + 21, vi, T_LABEL, anchor="end", fill=color)

        c.raw_text(m + 16, y + 58, "PHẢN HỒI CẦN CHẤM", T_SMALL, fill=GRAY, weight="bold")
        yy = text_left(c, m + 16, y + 88, resp, txt_w - 20, T_BODY, line_h=LH)
        text_left(c, m + 16, yy + 8, note, txt_w - 20, T_BODY, fill=color, weight="bold",
                  line_h=LH)

        # the attention signature the thesis bets on
        cx = m + txt_w + 24
        c.raw_text(cx, y + 58, "TỶ TRỌNG CHÚ Ý THEO ĐOẠN", T_SMALL, fill=GRAY, weight="bold")
        bgap = 14
        bw, base = (chart_w - 3 * bgap - 16) / 4, y + 176
        for j, sh in enumerate(shares):
            h = max(4, 115 * sh)
            bxx = cx + 8 + j * (bw + bgap)
            c.band(bxx, base - h, bw, h, color if j == hot else MUTED, radius=3)
            c.raw_text(bxx + bw / 2, base + 18, f"đoạn {j + 1}", T_SMALL, anchor="middle",
                       fill="#55555c")
            c.raw_text(bxx + bw / 2, base - h - 13, f"{sh * 100:.0f} %", T_SMALL,
                       anchor="middle", weight="bold" if j == hot else "normal",
                       fill="#2b2b31")
        c.add(f'<line x1="{cx}" y1="{base}" x2="{m + w - 16}" y2="{base}" '
              f'stroke="#55555c" stroke-width="1.2"/>')
        text_left(c, cx, base + 50, sig, chart_w - 8, T_SMALL, style="italic", fill="#3f3f46",
                  line_h=LH_S, balance=True)
        y += ch + 14

    y += 10
    y = text_left(c, m, y, "Giả thuyết của đề tài: ba hình dạng phân bố này khác nhau đủ để "
                  "tách ba nhãn, trong khi phần văn bản đọc được thì gần như giống nhau.", w,
                  T_BODY, style="italic", line_h=LH)
    c.height = y + 8
    c.save(OUT / "hinh_ba_loai_ao_giac.svg")
    render("hinh_ba_loai_ao_giac", PAGE_W, int(c.height))


# =========================================================================
# B. The prompt template and the token regions measured on it
# =========================================================================
def fig_mau_prompt() -> None:
    m = 30
    inner_w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1000)

    x, y, w = m, 24, inner_w
    lh = 34
    box_h = 12 * lh + 34
    c.add(f'<rect x="{x}" y="{y}" width="{w}" height="{box_h}" rx="8" fill="#fbfbfc" '
          f'stroke="#c8c8d0" stroke-width="1.4"/>')

    lines = [
        ("<|im_start|>system", GRAY, None),
        ("Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp.", "#111111", None),
        ("<|im_end|>", GRAY, None),
        ("<|im_start|>user", GRAY, None),
        ("Ngữ cảnh:", "#111111", None),
        ("{context}", NAVY, "ctx"),
        ("", "#111111", None),
        ("Câu hỏi: {question}", "#8a6a1f", "q"),
        ("<|im_end|>", GRAY, None),
        ("<|im_start|>assistant", GRAY, None),
        ("{response}", RED, "resp"),
        ("<|im_end|>", GRAY, None),
    ]
    ty = y + 34
    for i, (txt, color, tag) in enumerate(lines):
        yy = ty + i * lh
        tint = {"ctx": TINT_BLUE, "resp": TINT_RED, "q": "#f4f0e4"}.get(tag or "")
        if tint:
            c.band(x + 14, yy - 15, w - 28, 30, tint, radius=4)
        c.raw_text(x + 26, yy, txt, T_BODY, fill=color, family=MONO,
                   weight="bold" if tag else "normal")
    y += box_h + 16

    # one call-out per highlighted region, in the same colours as the template
    spots = [
        (NAVY, TINT_BLUE, "Vùng ngữ cảnh {context}",
         "Đúng chuỗi {context}, không gồm dòng tiêu đề “Ngữ cảnh:”. Chunk được chia trên "
         "chính chuỗi này."),
        ("#8a6a1f", "#f4f0e4", "Khối câu hỏi",
         "Ba bộ kiểm chứng thông tin không có câu hỏi thì bỏ hẳn khối này, không in ra "
         "dòng rỗng."),
        (RED, TINT_RED, "Vùng phản hồi {response}",
         "Đúng chuỗi {response}, không gồm token <|im_start|>assistant."),
    ]
    cw = (inner_w - 2 * 14) / 3
    tw = cw - 28
    n_title = max(len(wrap(t, tw, T_BODY, bold=True)) for _, _, t, _ in spots)
    n_body = max(len(wrap(b, tw, T_SMALL)) for *_, b in spots)
    ch = 20 + n_title * LH + 8 + n_body * LH_S + 14
    for k, (color, tint, title, body) in enumerate(spots):
        cx = m + k * (cw + 14)
        c.add(f'<rect x="{cx}" y="{y}" width="{cw}" height="{ch}" rx="8" fill="{tint}" '
              f'stroke="{color}" stroke-width="1.5"/>')
        yy = text_left(c, cx + 14, y + 12 + LH / 2, title, tw, T_BODY, fill=color,
                       weight="bold", line_h=LH)
        # the body follows its own title, however many lines the other titles took
        text_left(c, cx + 14, yy - LH / 2 + 8 + LH_S / 2, body, tw, T_SMALL,
                  fill="#2b2b31", line_h=LH_S)
    y += ch + 16

    rules = [
        "1.  Vị trí hai vùng được tìm bằng cách dò chuỗi trong prompt đã render rồi ánh xạ "
        "sang token qua return_offsets_mapping — không đếm ký tự khung.",
        "2.  Token phản hồi đầu tiên không được chấm vì mẫu số t − 1 bằng 0; trục token của "
        "mọi mảng đặc trưng vì thế có độ dài T − 1.",
    ]
    n_lines = sum(len(wrap(r, inner_w - 44, T_BODY)) for r in rules)
    c.band(m, y, inner_w, 50 + n_lines * LH + 10, TINT_GRAY, radius=8, stroke="#c8c8d0")
    c.raw_text(m + 22, y + 26, "Hai quy tắc quyết định mọi con số phía sau", T_LABEL,
               weight="bold", fill=INK_DARK)
    yy = y + 52 + LH / 2 - 2
    for r in rules:
        yy = text_left(c, m + 22, yy, r, inner_w - 44, T_BODY, line_h=LH)
    c.height = y + 50 + n_lines * LH + 10 + 20
    c.save(OUT / "hinh_mau_prompt.svg")
    render("hinh_mau_prompt", PAGE_W, int(c.height))


# =========================================================================
# C. From the attention matrix to the five shape features
# =========================================================================
def fig_co_che_chunk_aware() -> None:
    m = 30
    w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1000)

    # --- 1. attention matrix -------------------------------------------
    gx, gy, cell = 66, 62, 22
    n_ctx, n_resp = 20, 8
    edges = [0, 4, 9, 13, 20]
    weights = [0.09, 0.62, 0.17, 0.12]

    c.raw_text(gx - 26, 30, "① Ma trận chú ý A(l, h)", T_LABEL, weight="bold")
    for r in range(n_resp):
        for k in range(n_ctx):
            ci = next(i for i in range(4) if edges[i] <= k < edges[i + 1])
            base = weights[ci] / (edges[ci + 1] - edges[ci])
            jitter = 0.55 + 0.9 * (((r * 7 + k * 13) % 11) / 10)
            v = min(1.0, base * jitter * 5.2)
            shade = int(255 - 165 * v)
            c.band(gx + k * cell, gy + r * cell, cell - 2, cell - 2,
                   f"rgb({255 - int(80 * v)},{shade},{int(shade * 0.86)})", radius=2)
    for e in edges[1:-1]:
        c.add(f'<line x1="{gx + e * cell - 1}" y1="{gy - 6}" '
              f'x2="{gx + e * cell - 1}" y2="{gy + n_resp * cell + 6}" '
              f'stroke="{NAVY}" stroke-width="2.2"/>')
    c.add(f'<text x="{gx - 22}" y="{gy + n_resp * cell / 2}" font-size="{T_SMALL}" '
          f'fill="#55555c" text-anchor="middle" dominant-baseline="middle" '
          f'transform="rotate(-90 {gx - 22} {gy + n_resp * cell / 2})">'
          f'token phản hồi</text>')
    c.raw_text(gx + n_ctx * cell / 2, gy + n_resp * cell + 26,
               "token ngữ cảnh, chia thành bốn đoạn", T_SMALL, anchor="middle", fill="#55555c")

    # --- 2. per-chunk share --------------------------------------------
    bx = gx + n_ctx * cell + 62
    c.raw_text(bx - 8, 30, "② Tỷ trọng theo đoạn", T_LABEL, weight="bold")
    bar_w, bar_gap, base_y = 60, 16, gy + n_resp * cell
    for i, wgt in enumerate(weights):
        h = 120 * wgt / max(weights)
        xx = bx + i * (bar_w + bar_gap)
        c.band(xx, base_y - h, bar_w, h, RED if wgt == max(weights) else MUTED, radius=4)
        c.raw_text(xx + bar_w / 2, base_y - h - 14, f"{wgt:.2f}".replace(".", ","),
                   T_SMALL, anchor="middle", weight="bold")
        c.raw_text(xx + bar_w / 2, base_y + 22, f"đoạn {i + 1}", T_SMALL, anchor="middle",
                   fill="#55555c")
    c.add(f'<line x1="{bx - 8}" y1="{base_y}" x2="{bx + 4 * bar_w + 3 * bar_gap + 6}" '
          f'y2="{base_y}" stroke="#55555c" stroke-width="1.3"/>')
    c.arrow((gx + n_ctx * cell + 10, gy + n_resp * cell / 2), (bx - 20, gy + n_resp * cell / 2))

    # --- 3. the five features ------------------------------------------
    fy = gy + n_resp * cell + 64
    rows = [
        ("MAX", "tỷ trọng của đoạn được chú ý nhiều nhất"),
        ("ENT", "entropy chuẩn hóa: phân bố dàn trải hay tập trung"),
        ("GINI", "mức bất bình đẳng giữa các đoạn"),
        ("GAP", "khoảng cách giữa hai đoạn dẫn đầu"),
        ("DRIFT", "mức dịch chuyển của phân bố giữa hai token liên tiếp"),
    ]
    fh = 40 + 12 + len(rows) * 34 + 8
    c.add(f'<rect x="{m}" y="{fy}" width="{w}" height="{fh}" rx="10" fill="#ffffff" '
          f'stroke="{NAVY}" stroke-width="1.7"/>')
    head(c, m, fy, w, TINT_BLUE)
    c.raw_text(m + 16, fy + 21, "③ Năm đặc trưng hình dạng của véc-tơ tỷ trọng", T_LABEL,
               weight="bold", fill=NAVY)
    for i, (name, desc) in enumerate(rows):
        yy = fy + 40 + 12 + 17 + i * 34
        c.raw_text(m + 20, yy, name, T_BODY, family=MONO, fill=RED, weight="bold")
        c.raw_text(m + 130, yy, desc, T_BODY, fill="#55555c")
    c.arrow((PAGE_W / 2, fy - 30), (PAGE_W / 2, fy - 6))

    # --- the contrast this figure exists to make ------------------------
    y = fy + fh + 18
    pw = (w - 20) / 2
    tw = pw - 32
    panels = (
        (m, TINT_ORANGE, ORANGE, "Lookback Lens gốc — lookback gộp",
         "Gộp cả ngữ cảnh thành một khối, chỉ hỏi “nhìn lại bao nhiêu”:",
         "một khối → 1 con số / đầu", "#8a5a1f"),
        (m + pw + 20, TINT_RED, RED, "Đề xuất của khóa luận — chunk-aware",
         "Giữ véc-tơ tỷ trọng theo đoạn rồi mô tả hình dạng của nó:",
         "[0,09 0,62 0,17 0,12]\n→ 5 con số / đầu", RED),
    )
    n_body = max(len(wrap(b, tw, T_BODY)) for _, _, _, _, b, _, _ in panels)
    n_form = max(f.count("\n") + 1 for *_, f, _ in panels)
    ph = 18 + LH + 10 + n_body * LH + 8 + n_form * LH + 14
    for px, tint, stroke, title, body, formula, col in panels:
        c.band(px, y, pw, ph, tint, radius=10, stroke=stroke)
        c.raw_text(px + 16, y + 18 + LH / 2, title, T_LABEL, weight="bold", fill=col)
        yy = text_left(c, px + 16, y + 18 + LH + 10 + LH / 2, body, tw, T_BODY, line_h=LH)
        yy = y + 18 + LH + 10 + n_body * LH + 8 + LH / 2
        for k, part in enumerate(formula.split("\n")):
            c.raw_text(px + 16, yy + k * LH, part, T_BODY, family=MONO, weight="bold",
                       fill=INK_DARK)
    c.height = y + ph + 20
    c.save(OUT / "hinh_co_che_chunk_aware.svg")
    render("hinh_co_che_chunk_aware", PAGE_W, int(c.height))


# =========================================================================
# D. The chunking strategies compared in the experiments, and the control
# =========================================================================
def fig_hai_cach_chia_chunk() -> None:
    m = 30
    inner_w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1000)
    widths = [w * inner_w / sum(SENT_W) for w in SENT_W]      # the four sentences fill the row
    rh = 30                                             # height of a ruler or chunk row

    # the running example, written out once
    c.raw_text(m, 22, "NGỮ CẢNH VÍ DỤ", T_SMALL, fill=GRAY, weight="bold")
    y = 50
    for i, s in enumerate(SENTENCES):
        c.raw_text(m, y, f"câu {i + 1}", T_SMALL, fill=GRAY, weight="bold")
        c.raw_text(m + 70, y, s, T_BODY, fill=INK_DARK)
        y += 28
    y += 16

    def ruler(yy: float) -> None:
        """The same context drawn as four sentence-long segments."""
        xx = m
        for i, w in enumerate(widths):
            c.band(xx, yy, w - 4, rh, "#f4f4f6", radius=4, stroke="#d8d8de")
            c.raw_text(xx + (w - 4) / 2, yy + rh / 2, f"câu {i + 1}", T_SMALL, anchor="middle",
                       fill="#6b7280")
            xx += w

    def note_after(yy: float, text: str) -> float:
        return text_left(c, m, yy, text, inner_w, T_SMALL, fill="#3f3f46", line_h=LH_S) + 20

    # --- (a) sentence chunking -----------------------------------------
    c.raw_text(m, y, "(a) Chia theo câu — gộp câu ngắn hơn 5 từ vào câu trước", T_LABEL,
               weight="bold", fill=GREEN)
    ruler(y + 20)
    xx = m
    for i, w in enumerate(widths):
        c.band(xx, y + 20 + rh + 6, w - 4, rh, TINT_GREEN, radius=4, stroke=GREEN)
        c.raw_text(xx + (w - 4) / 2, y + 20 + rh + 6 + rh / 2, f"đoạn {i + 1}", T_SMALL,
                   anchor="middle", fill=GREEN)
        xx += w
    y = note_after(y + 20 + 2 * rh + 6 + 26, "Ranh giới trùng ranh giới câu · không chồng lấn · "
                   "trung bình 5,29 đoạn mỗi ngữ cảnh trên ViHallu")

    # --- (b) sliding token windows --------------------------------------
    c.raw_text(m, y, "(b) Cửa sổ token trượt — 128 token, bước 64 (chồng lấn một nửa)", T_LABEL,
               weight="bold", fill=BLUE)
    ruler(y + 20)
    win_w, stride = inner_w * 0.32, inner_w * 0.16
    for i in range(5):
        x = m + i * stride
        ww = min(win_w, m + inner_w - x)
        if ww <= 0:
            break
        yy = y + 20 + rh + 6 + (i % 2) * (rh + 4)
        c.band(x, yy, ww, rh, TINT_BLUE, radius=4, stroke=BLUE)
        c.raw_text(x + ww / 2, yy + rh / 2, f"cửa sổ {i + 1}", T_SMALL, anchor="middle",
                   fill=NAVY)
    y = note_after(y + 20 + 3 * rh + 10 + 26, "Ranh giới cắt ngang câu · chồng lấn · trung bình "
                   "3,29 đoạn (cấu hình 64/32 và 256/128 tương tự)")

    # --- (c) the control: tiling windows --------------------------------
    c.raw_text(m, y, "(c) Cấu hình đối chứng — cửa sổ 48 token, bước 48 (không chồng lấn)",
               T_LABEL, weight="bold", fill=ORANGE)
    ruler(y + 20)
    n_tiles = 6
    tile = inner_w / n_tiles
    for i in range(n_tiles):
        c.band(m + i * tile + 2, y + 20 + rh + 6, tile - 6, rh, TINT_ORANGE, radius=4,
               stroke=ORANGE)
        c.raw_text(m + i * tile + tile / 2, y + 20 + rh + 6 + rh / 2, f"đoạn {i + 1}", T_SMALL,
                   anchor="middle", fill="#8a5a1f")
    y = note_after(y + 20 + 2 * rh + 6 + 26, "Ranh giới cắt ngang câu · không chồng lấn · "
                   "trung bình 5,56 đoạn — gần bằng cách chia theo câu") - 4

    note = ("Cấu hình (c) giống (a) về chồng lấn và độ phân giải, chỉ khác một yếu tố: ranh "
            "giới đoạn có trùng ranh giới câu hay không.")
    n = len(wrap(note, inner_w - 40, T_BODY, bold=True))
    c.band(m, y, inner_w, 24 + n * LH, TINT_GRAY, radius=8, stroke="#c8c8d0")
    text_left(c, m + 20, y + 12 + LH / 2, note, inner_w - 40, T_BODY, weight="bold", fill=INK_DARK,
              line_h=LH)
    c.height = y + 24 + n * LH + 20
    c.save(OUT / "hinh_hai_cach_chia_chunk.svg")
    render("hinh_hai_cach_chia_chunk", PAGE_W, int(c.height))


if __name__ == "__main__":
    fig_ba_loai_ao_giac()
    fig_mau_prompt()
    fig_co_che_chunk_aware()
    fig_hai_cach_chia_chunk()
