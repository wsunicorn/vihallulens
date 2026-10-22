"""Method and design figures added for the research-oriented version of the report.

Each figure is written as an SVG (or HTML for the pseudo-code) and rasterised with headless
Chrome, like the other concept figures. No figure carries its own title: the caption in the
report is the title.

Figures are drawn on a narrow canvas (PAGE_W) on purpose. A figure printed across the
15,5 cm text column of the report is scaled by 439 pt / canvas width, so on a 900 px canvas
one px of text is 0,49 pt on paper, while a 1.600 px canvas would leave a 15 px label at
4 pt — unreadable. Everything here is therefore laid out top-down rather than left-right.

Text sizes are the named ones below (T_BODY 19,5 px ≈ 9,5 pt; nothing under T_SMALL,
18 px ≈ 8,8 pt). A figure also has to fit one page with its caption: at most ~1.250 px
tall on this canvas.

Run:  python docs/media/src/method_figs.py
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PIL import Image, ImageOps
from svgkit import Canvas, esc, text_block, wrap

OUT = Path(__file__).resolve().parent.parent
# CHROME_PATH overrides the default Windows install, as in shoot_site.mjs
CHROME = os.environ.get("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
MONO = "Consolas, 'DejaVu Sans Mono', monospace"

GREEN = "#2a8c82"
RED = "#b5452f"
ORANGE = "#d98032"
BLUE = "#3b6ea5"
NAVY = "#1f3a5f"
GRAY = "#8a8f98"
MUTED = "#b9c0c9"
INK = "#2b2b31"
SOFT = "#55555c"

TINT_GREEN = "#e4f2e9"
TINT_RED = "#fbe7e1"
TINT_ORANGE = "#fdf0dd"
TINT_BLUE = "#e3edf6"
TINT_GRAY = "#f2f2f4"
TINT_PURPLE = "#efeaf6"
PURPLE = "#7a6a9c"

PAGE_W = 900          # canvas width of every portrait figure, see the module docstring
PT_PER_PX = 439.4 / PAGE_W      # 15,5 cm in points, per canvas pixel — 0,49 pt
# text sizes in canvas px, and what they print at
T_SMALL = 18          # notes, captions inside the figure   ≈ 8,8 pt
T_BODY = 19.5         # running text in boxes               ≈ 9,5 pt
T_LABEL = 20.5        # bold names, short labels            ≈ 10 pt
T_TITLE = 23          # panel titles                        ≈ 11,2 pt


def render(name: str, w: int, h: int, ext: str = "svg", scale: int = 2,
           trim: bool = False) -> None:
    """Screenshot docs/media/<name>.<ext> into <name>.png. With trim, the window may be
    given room to spare: the white rows under the drawing are cut off afterwards."""
    src = OUT / f"{name}.{ext}"
    png = OUT / f"{name}.png"
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         "--default-background-color=ffffff", f"--force-device-scale-factor={scale}",
         f"--window-size={w},{h}", f"--screenshot={png}", src.as_uri()],
        check=True, capture_output=True)
    if trim:
        im = Image.open(png)
        bottom = ImageOps.invert(im.convert("L")).getbbox()[3]
        im.crop((0, 0, im.width, min(im.height, bottom + 18 * scale))).save(png)
    print(f"{png.name} {Image.open(png).size}")


def text_left(c: Canvas, x, y, text, width, size=15, fill=INK, weight="normal",
              style="normal", family=None, line_h=None, balance=False) -> float:
    """Wrapped text anchored on the left; returns the y below the last line."""
    lh = line_h or size * 1.3
    lines = wrap(text, width, size, bold=weight == "bold", balance=balance)
    for k, line in enumerate(lines):
        c.raw_text(x, y + k * lh, line, size, fill=fill, weight=weight, style=style,
                   family=family)
    return y + len(lines) * lh


def header_band(c: Canvas, x, y, w, title, color, tint, hdr=40, radius=9) -> None:
    """The tinted strip with a bold title across the top of a rounded box."""
    c.band(x, y, w, hdr, tint, radius=radius)
    c.add(f'<rect x="{x}" y="{y + hdr - 14}" width="{w}" height="14" fill="{tint}"/>')
    c.raw_text(x + 14, y + hdr / 2 + 1, title, T_LABEL, fill=color, weight="bold")


def card(c: Canvas, x, y, w, h, title, body, color, tint, hdr=40):
    """Rounded card with a coloured header strip and wrapped body text."""
    c.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#ffffff" '
          f'stroke="{color}" stroke-width="1.8"/>')
    header_band(c, x, y, w, title, color, tint, hdr)
    if body:
        c.add(text_block(x + w / 2, y + hdr + (h - hdr) / 2, body, w - 26, font_size=T_BODY,
                         fill=INK))


# =========================================================================
# 1. Research framework: questions -> hypotheses -> experiments -> data
# =========================================================================
def coded_lines(c: Canvas, x, y, code, text, width, size, code_color, lh) -> float:
    """Wrapped text whose first line opens with a bold, coloured code ("H2 …"), the way a
    run-in heading reads; returns the y below the last line."""
    lines = wrap(f"{code} {text}", width, size)
    for k, line in enumerate(lines):
        if k == 0:
            rest = line[len(code):]
            body = (f'<tspan font-weight="bold" fill="{code_color}">{esc(code)}</tspan>'
                    f'{esc(rest)}')
        else:
            body = esc(line)
        c.add(f'<text x="{x:.1f}" y="{y + k * lh:.1f}" font-size="{size:g}" fill="{INK}" '
              f'dominant-baseline="middle" xml:space="preserve">{body}</text>')
    return y + len(lines) * lh


def fig_khung_nghien_cuu() -> None:
    blocks = [
        ("CH1", "Chunk-aware có hơn tỷ lệ lookback gộp không, và chú ý có tập trung đúng "
                "đoạn bằng chứng không?", RED, TINT_RED, [
            ("H2", "Tách theo đoạn làm tăng macro-F1, mức tăng lớn hơn khi ngữ cảnh nhiều đoạn",
             "E03 chunk-aware · E04–E05 chiến lược chia đoạn · E07 ngữ cảnh dài · E12 ablation"),
            ("H3", "Đầu chú ý mạnh nhất tập trung vào đúng đoạn chứa bằng chứng",
             "E06 định vị bằng chứng trên ISE-DSC01 · E08 lặp lại phép đo trên ViWikiFC"),
            ("H4", "Loại bỏ câu bằng chứng làm phân bố chú ý dàn trải hơn theo hướng định trước",
             "E08 can thiệp theo cặp: chỉ loại bỏ câu bằng chứng (1.836 cặp)")]),
        ("CH2", "Hướng nội tại đứng ở đâu trên mặt phẳng độ chính xác – chi phí?",
         BLUE, TINT_BLUE, [
            ("Chi phí", "Đo trực tiếp độ chính xác, thời gian, VRAM và số tham số",
             "E11 bảng đánh đổi · E14 chi phí theo kích thước mô hình đọc"),
            ("H1", "Lookback gộp vượt đặc trưng bề mặt và tương đương bộ mã hóa tinh chỉnh",
             "E01 đặc trưng bề mặt · E02 tái lập Lookback Lens · E09 bộ mã hóa · "
             "E10 LLM giám khảo")]),
        ("CH3", "Chú ý đóng góp thêm bao nhiêu so với đặc trưng bề mặt, và có khái quát hóa không?",
         GREEN, TINT_GREEN, [
            ("H1", "Phần đóng góp riêng của nhóm đặc trưng chú ý, tách khỏi đặc trưng bề mặt",
             "E12 ablation cộng dồn theo nhóm đặc trưng trên ViHallu và ISE-DSC01"),
            ("H5", "Bộ phát hiện giữ được hiệu năng trên bộ dữ liệu khác",
             "E15 ViWikiFC theo cách chia gốc · E16 khái quát hóa chéo bộ dữ liệu")]),
    ]
    m, lw, rw = 30, 360, 444
    w = PAGE_W - 2 * m
    lh = 24
    c = Canvas(width=PAGE_W, height=1400)
    y = 20
    for code, question, color, tint, rows in blocks:
        qw = w - 104
        qlines = wrap(question, qw, T_BODY)
        hh = 18 + len(qlines) * lh
        c.add(f'<rect x="{m}" y="{y}" width="{w}" height="{hh}" rx="10" fill="{tint}" '
              f'stroke="{color}" stroke-width="1.8"/>')
        c.raw_text(m + 16, y + hh / 2, code, T_TITLE, fill=color, weight="bold")
        text_left(c, m + 86, y + 9 + lh / 2, question, qw, T_BODY, fill=INK, line_h=lh)
        y += hh + 10
        for hcode, htext, exp in rows:
            # the bold code runs wider than wrap() reckons: 10 px more margin
            n_left = len(wrap(f"{hcode} {htext}", lw - 44, T_BODY))
            n_right = len(wrap(exp, rw - 30, T_BODY))
            rh = 18 + max(n_left, n_right) * lh
            c.add(f'<rect x="{m}" y="{y}" width="{lw}" height="{rh}" rx="8" fill="#ffffff" '
                  f'stroke="{color}" stroke-width="1.5"/>')
            c.add(f'<rect x="{m}" y="{y}" width="7" height="{rh}" rx="3" fill="{color}"/>')
            coded_lines(c, m + 20, y + rh / 2 - (n_left - 1) * lh / 2, hcode, htext,
                        lw - 44, T_BODY, color, lh)
            rx = PAGE_W - m - rw
            c.add(f'<rect x="{rx}" y="{y}" width="{rw}" height="{rh}" rx="8" fill="{TINT_GRAY}" '
                  f'stroke="#c8c8d0" stroke-width="1.3"/>')
            c.add(text_block(rx + rw / 2, y + rh / 2, exp, rw - 30, font_size=T_BODY, fill=INK))
            c.arrow((m + lw + 3, y + rh / 2), (rx - 4, y + rh / 2), stroke=color, stroke_width=1.5)
            y += rh + 8
        y += 10

    # resources shared by every experiment
    y += 2
    item_h, item_gap = 48, 4
    panel_h = 44 + 4 * (item_h + item_gap) + 8
    for px, title, color, tint, items in (
        (m, "Bộ dữ liệu", NAVY, TINT_BLUE,
         [("ViHallu", "bộ chính, phản hồi do GPT-4o sinh"),
          ("ISE-DSC01", "ngữ cảnh dài, có câu bằng chứng"),
          ("ViWikiFC", "đối chứng ngoài, thí nghiệm can thiệp"),
          ("ViFactCheck", "dự phòng, thí nghiệm chuyển miền")]),
        (m + w / 2 + 10, "Mô hình đọc", PURPLE, TINT_PURPLE,
         [("Qwen2.5-7B-Instruct", "mô hình chính, 27 lớp × 28 đầu"),
          ("Qwen2.5-3B-Instruct", "bậc thang, 36 × 16"),
          ("Qwen2.5-1.5B-Instruct", "bậc thang, 28 × 12"),
          ("Sailor2-8B-SFT", "đổi họ mô hình, 30 × 28")]),
    ):
        pw = w / 2 - 10
        c.add(f'<rect x="{px}" y="{y}" width="{pw}" height="{panel_h}" rx="10" fill="#ffffff" '
              f'stroke="{color}" stroke-width="1.8"/>')
        c.raw_text(px + 16, y + 24, title, T_TITLE, fill=color, weight="bold")
        for k, (name, role) in enumerate(items):
            yy = y + 44 + k * (item_h + item_gap)
            c.band(px + 12, yy, pw - 24, item_h, tint, radius=6)
            c.raw_text(px + 24, yy + 14, name, T_LABEL, fill=color, weight="bold")
            c.raw_text(px + 24, yy + 35, role, T_SMALL, fill=SOFT)
    foot = ("Mỗi giả thuyết được kiểm chứng bằng một nhóm thí nghiệm; mọi thí nghiệm dùng "
            "chung các nguồn lực ở hai khối dưới.")
    n_foot = len(wrap(foot, w, T_SMALL))
    c.add(text_block(PAGE_W / 2, y + panel_h + 18 + n_foot * 12, foot, w, font_size=T_SMALL,
                     fill=SOFT, style="italic"))
    c.height = y + panel_h + 30 + n_foot * 24
    c.save(OUT / "hinh_khung_nghien_cuu.svg")
    render("hinh_khung_nghien_cuu", PAGE_W, int(c.height))


# =========================================================================
# 2. Data pipeline, from raw files to the evaluation splits
# =========================================================================
def fig_quy_trinh_du_lieu() -> None:
    m = 30
    w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1300)
    lh = 26

    # inputs: the four raw files, read only
    c.raw_text(m, 22, "TỆP GỐC (CHỈ ĐỌC)", T_SMALL, fill=SOFT, weight="bold")
    raw = [("ViHallu", "CSV"), ("ISE-DSC01", "JSON"), ("ViWikiFC", "CSV"),
           ("ViFactCheck", "Parquet")]
    bw = (w - 3 * 12) / 4
    for k, (name, fmt) in enumerate(raw):
        x = m + k * (bw + 12)
        c.band(x, 40, bw, 60, TINT_GRAY, radius=7, stroke="#c8c8d0")
        c.raw_text(x + bw / 2, 60, name, T_LABEL, anchor="middle", weight="bold", fill=NAVY)
        c.raw_text(x + bw / 2, 84, fmt, T_SMALL, anchor="middle", fill=SOFT)
    y = 100
    c.arrow((PAGE_W / 2, y + 4), (PAGE_W / 2, y + 26), stroke=INK)
    y += 32

    steps = [
        ("1", "Bộ đọc riêng cho từng bộ", BLUE, TINT_BLUE,
         "Đổi tên trường về lược đồ chung; ánh xạ nhãn SUPPORTED/REFUTED/NEI sang "
         "no/intrinsic/extrinsic", "ba định dạng tệp, bốn bộ tên cột khác nhau"),
        ("2", "Chuẩn hóa và định danh", BLUE, TINT_BLUE,
         "Chuẩn hóa Unicode NFC; sinh sample_id riêng; context_id là SHA-256 của ngữ cảnh",
         "NFC: cùng một chữ có dấu, tránh hai chuỗi byte khác nhau"),
        ("3", "Định vị bằng chứng", BLUE, TINT_BLUE,
         "So khớp nguyên văn câu bằng chứng trong ngữ cảnh để lấy evidence_start, "
         "hoặc −1 nếu không tìm thấy",
         "khớp được 23.783/23.784 mẫu ISE-DSC01 và 20.918/20.919 mẫu ViWikiFC"),
        ("4", "Kiểm tra lược đồ", GREEN, TINT_GREEN,
         "Kiểm tra kiểu dữ liệu, trường bắt buộc và nhãn hợp lệ ngay khi ghi tệp",
         "hàm ghi báo lỗi thay vì ghi ra dữ liệu hỏng"),
        ("5", "Chia tập theo ngữ cảnh", GREEN, TINT_GREEN,
         "ViHallu và ISE-DSC01: 80/10/10 theo context_id, thứ tự lấy từ SHA-256 với hạt "
         "giống 42; ViWikiFC và ViFactCheck giữ cách chia gốc",
         "báo lỗi nếu một context_id rơi vào hai tập"),
        ("6", "Báo cáo rò rỉ", GREEN, TINT_GREEN,
         "Đếm số ngữ cảnh và số dòng của tập đánh giá đã xuất hiện trong tập huấn luyện",
         "tập test gốc của ViWikiFC: 845/845 ngữ cảnh đã có trong tập huấn luyện"),
    ]
    # The six steps run top-down as numbered cards; a line through the numbers carries
    # the flow instead of an arrow between every pair, which the page had no height for.
    tx = m + 66                   # text column, right of the numbered circle
    tw = w - 66 - 18
    gap = 12
    cards = []
    for _num, _title, _color, _tint, body, _note in steps:
        n_body = len(wrap(body, tw, T_BODY))
        h = 80 + n_body * lh          # title, body lines, note, padding
        cards.append((y, h))
        y += h + gap
    first_cy, last_cy = cards[0][0] + 28, cards[-1][0] + 28
    c.add(f'<line x1="{m + 32}" y1="{first_cy}" x2="{m + 32}" y2="{last_cy}" '
          f'stroke="{GRAY}" stroke-width="3"/>')
    for (num, title, color, _tint, body, note), (cy, h) in zip(steps, cards, strict=False):
        c.add(f'<rect x="{m}" y="{cy}" width="{w}" height="{h}" rx="9" fill="#ffffff" '
              f'stroke="{color}" stroke-width="1.6"/>')
        c.add(f'<circle cx="{m + 32}" cy="{cy + 28}" r="18" fill="{color}"/>')
        c.raw_text(m + 32, cy + 29, num, T_LABEL, anchor="middle", fill="#ffffff", weight="bold")
        c.raw_text(tx, cy + 28, title, T_LABEL, fill=color, weight="bold")
        after = text_left(c, tx, cy + 58, body, tw, T_BODY, fill=INK, line_h=lh)
        c.raw_text(tx, after + 2, note, T_SMALL, fill=SOFT, style="italic")
    y -= gap

    # output store
    y += 30
    c.arrow((PAGE_W / 2, y - 26), (PAGE_W / 2, y - 3), stroke=INK)
    c.cylinder(m + w / 2 - 230, y, 460, 84, "data/interim/ — các tập đã chia (.parquet)",
               font_size=T_BODY)
    y += 104
    note = ("Phát hiện khi chuẩn hóa: ISE-DSC01 thiếu 1.598 mẫu so với số công bố · hai bằng "
            "chứng chỉ là dòng trống · một dòng ViWikiFC lỗi ở nguồn · pairID và annotation_id "
            "có giá trị lặp")
    lines = wrap(note, w - 40, T_SMALL)
    c.band(m, y, w, 22 + len(lines) * 24, TINT_ORANGE, radius=8, stroke=ORANGE)
    text_left(c, m + 20, y + 11 + 12, note, w - 40, T_SMALL, fill="#8a5a1f", line_h=24)
    c.height = y + 22 + len(lines) * 24 + 22
    c.save(OUT / "hinh_quy_trinh_du_lieu.svg")
    render("hinh_quy_trinh_du_lieu", PAGE_W, int(c.height))


# =========================================================================
# 3. Row split against group split
# =========================================================================
def fig_chia_theo_nhom() -> None:
    m = 30
    w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=700)
    ctx_color = {"C1": BLUE, "C2": ORANGE, "C3": GREEN, "C4": PURPLE, "C5": RED}
    cw, ch, gap = 110, 50, 16

    def sample(x, y, ctx, leak=False):
        col = ctx_color[ctx]
        c.add(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="6" fill="{col}" '
              f'stroke="{INK if leak else "#ffffff"}" stroke-width="{4 if leak else 1}"/>')
        c.raw_text(x + cw / 2, y + ch / 2, ctx, T_LABEL, anchor="middle", fill="#ffffff",
                   weight="bold")

    panels = [
        ("Chia theo dòng (ngẫu nhiên)", RED,
         [["C1", "C2", "C3", "C1", "C4", "C5", "C3", "C2"], ["C1", "C3", "C4", "C5"]],
         {"C1", "C3", "C4", "C5"},
         "Cùng một ngữ cảnh xuất hiện ở cả hai tập: điểm trên tập kiểm tra đo cả khả năng "
         "ghi nhớ ngữ cảnh đã thấy."),
        ("Chia theo ngữ cảnh (theo nhóm)", GREEN,
         [["C1", "C1", "C1", "C3", "C3", "C3", "C5", "C5"], ["C2", "C2", "C4", "C4"]],
         set(),
         "Mọi mẫu của một ngữ cảnh nằm trọn trong một tập: tập kiểm tra chỉ chứa ngữ cảnh "
         "chưa từng thấy."),
    ]
    y = 26
    for title, color, (train, test), leaks, note in panels:
        c.raw_text(m, y + 12, title, T_TITLE, fill=color, weight="bold")
        mark = "có rò rỉ ngữ cảnh" if leaks else "không rò rỉ"
        c.band(PAGE_W - m - 210, y - 8, 210, 40, TINT_RED if leaks else TINT_GREEN, radius=8,
               stroke=color)
        c.raw_text(PAGE_W - m - 105, y + 12, mark, T_BODY, anchor="middle", fill=color,
                   weight="bold")
        y += 42
        tw = 2 * 18 + 4 * cw + 3 * gap          # training box: four samples a row
        sw = 2 * 18 + 2 * cw + gap              # test box: two a row
        box_h = 44 + 2 * ch + gap + 16
        for bx, bw, label, cells, per_row in ((m, tw, "Tập huấn luyện", train, 4),
                                              (m + w - sw, sw, "Tập kiểm tra", test, 2)):
            c.add(f'<rect x="{bx}" y="{y}" width="{bw}" height="{box_h}" rx="10" '
                  f'fill="{TINT_GRAY}" stroke="#c8c8d0" stroke-width="1.4"/>')
            c.raw_text(bx + 18, y + 24, label, T_LABEL, weight="bold", fill=INK)
            for k, ctx in enumerate(cells):
                sample(bx + 18 + (k % per_row) * (cw + gap), y + 44 + (k // per_row) * (ch + gap),
                       ctx, leak=ctx in leaks)
        y += box_h + 26
        y = text_left(c, m, y, note, w, T_BODY, fill=INK, line_h=27) + 22
    c.raw_text(PAGE_W / 2, y + 6, "Mỗi ô là một mẫu; các ô cùng màu dùng chung một ngữ cảnh.",
               T_BODY, anchor="middle", fill=SOFT, style="italic")
    c.raw_text(PAGE_W / 2, y + 34, "Viền đậm: ngữ cảnh có mẫu ở cả hai tập.", T_BODY,
               anchor="middle", fill=SOFT, style="italic")
    c.height = y + 58
    c.save(OUT / "hinh_chia_theo_nhom.svg")
    render("hinh_chia_theo_nhom", PAGE_W, int(c.height))


# =========================================================================
# 4. Per-layer forward hooks
# =========================================================================
def fig_forward_hook() -> None:
    m = 30
    w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1300)
    line_h = 26                       # line pitch of T_BODY text

    # the prompt entering the reading model
    c.band(m, 24, w, 54, TINT_GRAY, radius=8, stroke="#c8c8d0")
    c.raw_text(PAGE_W / 2, 51, "Prompt đã ghép: ngữ cảnh, câu hỏi và phản hồi — n token, "
               "một lượt truyền xuôi", T_BODY, anchor="middle", fill=INK)
    top = 100                     # both columns start here

    # right column, measured first: the dashed box has to be drawn under its content
    sw = 180                      # stack column
    bx = m + sw + 30
    bw = PAGE_W - m - bx
    ix, iw = bx + 18, bw - 36
    att_body = "Tạo ma trận chú ý A(l) kích thước H × n × n — khoảng 0,94 GB ở n = 4.096 token"
    ch = 40 + len(wrap(att_body, iw - 26, T_BODY)) * line_h + 22
    hook_steps = [
        "① Lấy các hàng của token phản hồi t = 2, …, T",
        "② Tính chú ý trung bình vào tiền tố, ngữ cảnh và phần đã đọc",
        "③ Tính mật độ chú ý của từng đoạn ngữ cảnh",
        "④ Ghi kết quả vào các mảng nhỏ trên CPU",
        "⑤ Trả về (đầu ra, None) — ma trận A(l) được giải phóng",
    ]
    # a step that runs over continues under its text, past the circled number
    step_lines = [wrap(s, iw - 44, T_BODY) for s in hook_steps]
    hh = 40 + sum(len(ls) for ls in step_lines) * line_h + (len(hook_steps) - 1) * 6 + 22
    card_y = top + 48
    hook_y = card_y + ch + 30
    out_y = hook_y + hh + 30
    box_h = out_y + 46 + 20 - top

    c.add(f'<rect x="{bx}" y="{top}" width="{bw}" height="{box_h}" rx="14" fill="#ffffff" '
          f'stroke="{RED}" stroke-width="1.8" stroke-dasharray="7 5"/>')
    c.raw_text(bx + 18, top + 26, "Bên trong lớp l", T_TITLE, fill=RED, weight="bold")
    card(c, ix, card_y, iw, ch, "Khối tự chú ý (cài đặt eager)", att_body, NAVY, TINT_BLUE)
    c.arrow((bx + bw / 2, card_y + ch + 2), (bx + bw / 2, hook_y - 3), stroke=INK)
    c.add(f'<rect x="{ix}" y="{hook_y}" width="{iw}" height="{hh}" rx="9" fill="#ffffff" '
          f'stroke="{RED}" stroke-width="1.6"/>')
    header_band(c, ix, hook_y, iw, "Forward hook của lớp l", RED, TINT_RED)
    yy = hook_y + 40 + 12 + line_h / 2
    for k, lines in enumerate(step_lines):
        for j, line in enumerate(lines):
            c.raw_text(ix + 18 + (0 if j == 0 else 26), yy, line, T_BODY, fill=INK,
                       weight="bold" if k == 4 else "normal")
            yy += line_h
        yy += 6
    c.arrow((bx + bw / 2, hook_y + hh + 2), (bx + bw / 2, out_y - 3), stroke=INK)
    c.band(ix + 40, out_y, iw - 80, 46, TINT_GRAY, radius=8, stroke="#c8c8d0")
    c.raw_text(bx + bw / 2, out_y + 23, "Đầu ra của lớp → lớp l + 1", T_BODY, anchor="middle",
               fill=INK)

    # left column: the stack of layers
    layers = [("Lớp 0", False), ("Lớp 1", False), ("…", False), ("Lớp l", True), ("…", False),
              ("Lớp 26", False), ("Lớp 27\nkhông đọc", None)]
    y = top + 8
    ys = []
    for name, hot in layers:
        h = 30 if name == "…" else (70 if hot is None else 52)
        if name == "…":
            c.raw_text(m + sw / 2, y + 14, "⋮", 26, anchor="middle", fill=SOFT)
        else:
            fill = TINT_RED if hot else ("#f6f6f8" if hot is None else TINT_BLUE)
            stroke = RED if hot else ("#c8c8d0" if hot is None else BLUE)
            c.band(m, y, sw, h, fill, radius=8, stroke=stroke)
            c.add(text_block(m + sw / 2, y + h / 2, name, sw - 16, font_size=T_LABEL,
                             fill=RED if hot else (SOFT if hot is None else NAVY),
                             weight="bold" if hot else "normal",
                             style="italic" if hot is None else "normal"))
        ys.append((y, h))
        y += h + 14
    for (y1, h1), (y2, _) in zip(ys[:-1], ys[1:], strict=False):
        c.arrow((m + sw / 2, y1 + h1), (m + sw / 2, y2 - 2), stroke=GRAY, stroke_width=1.3)
    c.raw_text(m + sw / 2, y + 2, "tràn số ở float16", T_SMALL, anchor="middle", fill=SOFT,
               style="italic")
    ly, lh = ys[3]
    c.arrow((m + sw + 3, ly + lh / 2), (bx - 4, ly + lh / 2), stroke=RED, stroke_width=1.6)

    # two result panels
    y = max(top + box_h, y + 20) + 40
    pw = (w - 24) / 2
    ph = 40 + 3 * 60 + 14
    c.add(f'<rect x="{m}" y="{y}" width="{pw}" height="{ph}" rx="12" fill="#ffffff" '
          f'stroke="{GREEN}" stroke-width="1.6"/>')
    header_band(c, m, y, pw, "Mảng kết quả giữ lại (CPU)", GREEN, TINT_GREEN, radius=12)
    kept = [("Tỷ lệ lookback, hai biến thể", "L × H × (T − 1)"),
            ("Mật độ chú ý theo đoạn", "L × H × (T − 1) × K"),
            ("Ví dụ T = 50, K = 5", "≈ 185 nghìn giá trị cho 756 đầu")]
    for k, (a, b) in enumerate(kept):
        yy = y + 64 + k * 60
        c.raw_text(m + 18, yy, a, T_BODY, fill=INK, weight="bold")
        c.raw_text(m + 18, yy + 25, b, T_SMALL, fill=SOFT, family=MONO)

    px = m + pw + 24
    c.add(f'<rect x="{px}" y="{y}" width="{pw}" height="{ph}" rx="12" fill="{TINT_ORANGE}" '
          f'stroke="{ORANGE}" stroke-width="1.6"/>')
    c.raw_text(px + 16, y + 24, "Bộ nhớ ma trận chú ý, n = 4.096", T_LABEL, fill="#8a5a1f",
               weight="bold")
    for k, (a, b, col) in enumerate((("Giữ cả 28 lớp cùng lúc", "26 GB", RED),
                                     ("Một lớp tại một thời điểm", "0,94 GB", GREEN))):
        yy = y + 64 + k * 36
        c.raw_text(px + 18, yy, a, T_BODY, fill=INK)
        c.raw_text(px + pw - 18, yy, b, T_LABEL, anchor="end", fill=col, weight="bold")
    text_left(c, px + 18, y + 64 + 2 * 36 + 8, "VRAM đỉnh đo được ở ngưỡng 4.096 token: "
              "8.428 MB — dưới giới hạn 16 GB của Tesla T4", pw - 36, T_SMALL, fill="#8a5a1f",
              line_h=24)
    c.arrow((bx + bw / 2, out_y + 46), (m + pw / 2, y - 4),
            via=[(bx + bw / 2, y - 22), (m + pw / 2, y - 22)], stroke=GREEN, stroke_width=1.6)

    y += ph + 20
    note = ("Năm đặc trưng hình dạng được tính sau lượt truyền xuôi, trên CPU, từ mảng mật độ "
            "đã lưu — có thể bổ sung đặc trưng mới mà không phải chạy lại GPU.")
    lines = wrap(note, w - 40, T_BODY)
    c.band(m, y, w, 24 + len(lines) * line_h, TINT_GRAY, radius=8, stroke="#c8c8d0")
    text_left(c, m + 20, y + 12 + line_h / 2, note, w - 40, T_BODY, fill=INK, line_h=line_h)
    c.height = y + 24 + len(lines) * line_h + 20
    c.save(OUT / "hinh_forward_hook.svg")
    render("hinh_forward_hook", PAGE_W, int(c.height))


# =========================================================================
# 5. Paired intervention design (E08)
# =========================================================================
def fig_thiet_ke_can_thiep() -> None:
    m = 30
    w = PAGE_W - 2 * m
    c = Canvas(width=PAGE_W, height=1200)
    lh = 26

    # the claim that both readings share
    c.band(m, 24, w, 72, TINT_BLUE, radius=10, stroke=BLUE)
    c.raw_text(m + 18, 46, "Cùng một phát biểu", T_LABEL, fill=NAVY, weight="bold")
    c.raw_text(m + 18, 74, "được đọc hai lần, trên hai ngữ cảnh chỉ khác nhau đúng một câu",
               T_BODY, fill=INK)

    cell_w, cg, ch = (w - 9 * 7) / 10, 7, 62
    y = 128
    for title, gold in (("Bản có bằng chứng", True), ("Bản mất bằng chứng", False)):
        color = GREEN if gold else RED
        c.raw_text(m, y, title, T_LABEL, fill=color, weight="bold")
        y += 20
        for k in range(10):
            x = m + k * (cell_w + cg)
            hot = k == 3
            fill, stroke = (("#eaf5ef" if gold else TINT_GRAY), color) if hot else \
                           ("#ffffff", "#c8c8d0")
            c.band(x, y, cell_w, ch, fill, radius=6, stroke=stroke)
            c.raw_text(x + cell_w / 2, y + 21, f"câu {k + 1}", T_SMALL, anchor="middle",
                       fill=color if hot else INK, weight="bold" if hot else "normal")
            if hot:
                c.raw_text(x + cell_w / 2, y + 44, "vàng" if gold else "nhiễu", T_SMALL,
                           anchor="middle", fill=color, weight="bold")
        y += ch + 34
    y = text_left(c, m, y - 8, "Giữ nguyên: phát biểu, chín câu còn lại, thứ tự, độ dài và số "
                  "đoạn. Câu vàng được thay bằng câu nhiễu kế tiếp trong danh sách truy xuất, "
                  "nên nhãn của bản mất bằng chứng là ảo giác ngoại lai theo cấu tạo — không "
                  "cần người gán nhãn.", w, T_SMALL, fill=SOFT, style="italic", line_h=24)

    # both versions go through the same reader
    y += 8
    c.arrow((PAGE_W / 2, y), (PAGE_W / 2, y + 24), stroke=INK)
    y += 28
    c.band(m + w / 2 - 250, y, 500, 52, TINT_GRAY, radius=10, stroke="#c8c8d0")
    c.raw_text(PAGE_W / 2, y + 26, "Mô hình đọc Qwen2.5-7B — trích đặc trưng", T_LABEL,
               anchor="middle", fill=INK, weight="bold")
    y += 52
    c.arrow((PAGE_W / 2, y + 2), (PAGE_W / 2, y + 26), stroke=INK)
    y += 30

    # directions written down before the run
    ph = 138
    c.add(f'<rect x="{m}" y="{y}" width="{w}" height="{ph}" rx="12" fill="#ffffff" '
          f'stroke="{NAVY}" stroke-width="1.6"/>')
    header_band(c, m, y, w, "Hướng thay đổi dự đoán, ghi cố định trước khi chạy", NAVY,
                TINT_BLUE, radius=12)
    preds = [("ENT", "tăng ↑", GREEN), ("GINI", "giảm ↓", RED), ("MAX", "giảm ↓", RED),
             ("GAP", "giảm ↓", RED), ("DRIFT", "không dự đoán", GRAY)]
    cw = (w - 40) / 5
    for k, (name, d, col) in enumerate(preds):
        cx = m + 20 + cw * (k + 0.5)
        c.raw_text(cx, y + 72, name, T_TITLE, anchor="middle", fill=INK, weight="bold")
        c.raw_text(cx, y + 108, d, T_LABEL, anchor="middle", fill=col, weight="bold")
    y += ph + 20

    note = ("Mỗi cặp cho một hiệu số Δ = bản mất bằng chứng − bản có bằng chứng; kiểm định dấu "
            "hạng Wilcoxon và cỡ ảnh hưởng rank-biserial trên 1.836 cặp.")
    lines = wrap(note, w - 40, T_BODY)
    c.band(m, y, w, 24 + len(lines) * lh, TINT_ORANGE, radius=10, stroke=ORANGE)
    text_left(c, m + 20, y + 12 + lh / 2, note, w - 40, T_BODY, fill="#8a5a1f", line_h=lh)
    c.height = y + 24 + len(lines) * lh + 20
    c.save(OUT / "hinh_thiet_ke_can_thiep.svg")
    render("hinh_thiet_ke_can_thiep", PAGE_W, int(c.height))


# =========================================================================
# 6. Pseudo-code of the extraction algorithm
# =========================================================================
ALGO_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
body { margin: 0; background: #ffffff; font-family: 'Times New Roman', serif; color: #1f2328; }
.box { width: 1010px; margin: 18px 22px; border-top: 2.4px solid #1f2328; border-bottom: 2.4px solid
#1f2328; }
.head { font-size: 28px; padding: 10px 6px; border-bottom: 1.4px solid #1f2328; }
.head b { font-weight: bold; }
.io { font-size: 25px; padding: 8px 6px 4px 6px; line-height: 1.45; }
ol { margin: 4px 0 12px 0; padding-left: 58px; font-size: 25px; line-height: 1.55; }
li { padding-left: 6px; }
li::marker { color: #6b7280; font-size: 22px; }
.kw { font-weight: bold; }
.cm { color: #6b7280; font-style: italic; }
.in1 { margin-left: 30px; } .in2 { margin-left: 60px; }
.m { font-style: italic; }
</style></head><body><div class="box">
<div class="head"><b>Thuật toán.</b> Trích đặc trưng chunk-aware bằng forward hook</div>
<div class="io"><span class="kw">Đầu vào:</span> mô hình đọc với tập lớp được đọc 𝓛 (đã bỏ các lớp
tràn số); ngữ cảnh <span class="m">c</span>, câu hỏi <span class="m">q</span> (có thể rỗng), phản
hồi <span class="m">y</span>; chiến lược chia đoạn<br>
<span class="kw">Đầu ra:</span> LR<sub>total</sub>, LR<sub>context</sub> ∈ ℝ<sup>|𝓛|×H×(T−1)</sup>;
mật độ theo đoạn D ∈ ℝ<sup>|𝓛|×H×(T−1)×K</sup>; năm đặc trưng hình dạng</div>
<ol>
<li><span class="m">p</span> ← ghép <span class="m">c</span>, <span class="m">q</span>, <span
class="m">y</span> theo chat template của mô hình đọc</li>
<li><span class="m">C</span>, <span class="m">R</span> ← vị trí token của vùng ngữ cảnh và vùng phản
hồi <span class="cm">▷ tìm chuỗi trong p, ánh xạ qua bảng vị trí ký tự</span></li>
<li><span class="m">C</span><sub>1</sub>, …, <span class="m">C<sub>K</sub></span> ← chia <span
class="m">c</span> thành đoạn, ánh xạ sang token</li>
<li><span class="kw">với mỗi</span> lớp <span class="m">l</span> ∈ 𝓛 <span class="kw">thực
hiện</span> đăng ký hook<sub><span class="m">l</span></sub></li>
<li>chạy mô hình đọc trên <span class="m">p</span> đúng một lượt truyền xuôi <span class="cm">▷
teacher forcing, cài đặt chú ý eager</span></li>
<li><span class="kw">hàm</span> hook<sub><span class="m">l</span></sub>(đầu ra của khối chú ý):</li>
<li class="in1"><span class="m">A</span> ← trọng số chú ý của lớp <span class="m">l</span> <span
class="cm">▷ H × n × n, chỉ tồn tại trong lớp này</span></li>
<li class="in1"><span class="kw">với mỗi</span> đầu <span class="m">h</span> và token phản hồi <span
class="m">t</span> = 2, …, <span class="m">T</span> <span class="kw">thực hiện</span></li>
<li class="in2">tính <span class="m">A<sub>X</sub></span>(<span class="m">t</span>), <span
class="m">A<sub>C</sub></span>(<span class="m">t</span>), <span
class="m">A</span><sub>new</sub>(<span class="m">t</span>) và LR<sub>total</sub>,
LR<sub>context</sub> theo công thức lookback</li>
<li class="in2">D[<span class="m">l</span>, <span class="m">h</span>, <span class="m">t</span>,
<span class="m">k</span>] ← mật độ chú ý của đoạn <span class="m">C<sub>k</sub></span>, với <span
class="m">k</span> = 1, …, <span class="m">K</span></li>
<li class="in1"><span class="kw">trả về</span> (đầu ra chú ý, None) <span class="cm">▷ không tích
lũy A; A được giải phóng trước lớp kế tiếp</span></li>
<li>gỡ mọi hook</li>
<li><span class="m">s</span> ← chuẩn hóa D thành tỷ trọng theo đoạn; tính MAX, ENT, GINI, GAP, DRIFT
trên CPU</li>
<li><span class="kw">trả về</span> LR<sub>total</sub>, LR<sub>context</sub>, D và năm đặc trưng hình
dạng</li>
</ol></div></body></html>"""


def fig_thuat_toan() -> None:
    (OUT / "hinh_thuat_toan.html").write_text(ALGO_HTML, encoding="utf-8")
    # printed 15,5 cm wide: 25 px of text lands at ~10,4 pt
    render("hinh_thuat_toan", 1056, 1100, ext="html", trim=True)


if __name__ == "__main__":
    fig_khung_nghien_cuu()
    fig_quy_trinh_du_lieu()
    fig_chia_theo_nhom()
    fig_forward_hook()
    fig_thiet_ke_can_thiep()
    fig_thuat_toan()
