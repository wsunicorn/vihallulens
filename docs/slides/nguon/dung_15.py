"""Committee deck in 15 pages plus a thank-you page -> docs/slides/slide_hoi_dong_15.pptx (+ .pdf).

Follows the order the advisor asked for on 05/10/2026 (introduction and problem, motivation and
gaps, related work with the works named in the footer, data, method, system, experiments,
self-assessment, references), with Data before Method as in the thesis. Built like the
internship deck: native shapes, tables and charts that PowerPoint can edit, Times New Roman,
a one-sentence takeaway under every title, part numbers and a part bar, fade transitions,
one click per group, speaker notes. Every number comes from the thesis.

    uv run --no-project --with python-pptx==1.0.2 --with cairosvg==2.7.1 --with pillow \\
        --with pywin32==308 python docs/slides/nguon/dung_15.py [--pdf]

Icons: Lucide 0.441.0 (ISC licence), nguon/icons.
"""
# ruff: noqa: E501  (slide layout and text are data; wrapping them hurts more than it helps)

import io
import re
import shutil
import sys
from pathlib import Path

import cairosvg
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
DECK_DIR = HERE.parent
OUT = DECK_DIR / "slide_hoi_dong_15.pptx"
SUBMIT = DECK_DIR.parents[1] / "UniversityRequirements" / "Reports"
SUBMIT_NAME = "Slide15_KLTN_22635801_22643511_PhatHienAoGiac"

FONT = "Times New Roman"
INK, MUTED, RULE, PAPER, PAPER2, WHITE = "18202E", "5E6675", "D9D3C7", "FAF8F3", "F2EEE5", "FFFFFF"
CTX, CTXS, RES, RESS = "0F7C7C", "D7ECEA", "C27612", "F6E6CC"
OK, OKS, WARN, WARNS, BAD, BADS = "2F8A55", "DCEFE2", "B7860B", "F5EACB", "C0412D", "F6DDD7"
IUH, GOLD, VIOLET, VIOLS = "153898", "F9B200", "6B4FA0", "E9E3F3"
PARTS = ["Giới thiệu", "Cơ sở lý thuyết", "Dữ liệu", "Phương pháp", "Hệ thống", "Thực nghiệm",
         "Tự đánh giá"]
TOTAL = 16
L, C, R = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MID, BOT = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM


def rgb(h):
    return RGBColor.from_string(h)


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
_theme = next(r.target_part for r in prs.slide_master.part.rels.values()
              if r.reltype.endswith("/theme"))
_xml = _theme.blob.decode("utf8")
_xml = re.sub(r'(<a:(?:major|minor)Font>\s*<a:latin typeface=")[^"]*', rf"\g<1>{FONT}", _xml)
_theme._blob = _xml.encode("utf8")


# ------------------------------------------------------------------------------ primitives
def no_style(s):
    st = s._element.find(qn("p:style"))
    if st is not None:
        s._element.remove(st)


def box(sh, x, y, w, h, fill=None, line=None, lw=1.25, r=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
        dash=False):
    s = sh.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    no_style(s)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = min(0.5, r / max(0.01, min(w, h)))
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if line:
        s.line.color.rgb, s.line.width = rgb(line), Pt(lw)
        if dash:
            s.line.dash_style = 4
    else:
        s.line.fill.background()
    return s


def rect(sh, x, y, w, h, fill):
    return box(sh, x, y, w, h, fill, shape=MSO_SHAPE.RECTANGLE)


def _run(p, text, size, color, bold, italic):
    for k, part in enumerate(re.split(r"\*\*", text)):
        if not part:
            continue
        r = p.add_run()
        r.text = part
        f = r.font
        f.size, f.bold, f.italic, f.name = Pt(size), bold or k % 2 == 1, italic, FONT
        f.color.rgb = rgb(color)
        rpr = r._r.get_or_add_rPr()
        for tag in ("a:ea", "a:cs"):
            e = rpr.find(qn(tag))
            if e is None:
                e = etree.SubElement(rpr, qn(tag))
            e.set("typeface", FONT)


def text(sh, x, y, w, h, paras, size=16, color=INK, bold=False, align=L, anchor=TOP, italic=False,
         after=0, bullet=False, spacing=None):
    """paras: a string, or a list of strings / (string, options). **x** is bold."""
    tb = sh.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap, tf.vertical_anchor = True, anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    items = [paras] if isinstance(paras, str) else paras
    for i, it in enumerate(items):
        o = dict(size=size, color=color, bold=bold, align=align, italic=italic, after=after,
                 bullet=bullet)
        if isinstance(it, tuple):
            it, extra = it
            o.update(extra)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment, p.space_after = o["align"], Pt(o["after"])
        if spacing:
            p.line_spacing = spacing
        if o["bullet"]:
            ppr = p._p.get_or_add_pPr()
            ppr.set("marL", "228600")
            ppr.set("indent", "-228600")
            etree.SubElement(ppr, qn("a:buFont")).set("typeface", FONT)
            etree.SubElement(ppr, qn("a:buChar")).set("char", "•")
        _run(p, it, o["size"], o["color"], o["bold"], o["italic"])
    return tb


def line(sh, x1, y1, x2, y2, color=MUTED, w=1.5, head=False, dash=False):
    c = sh.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    no_style(c)
    c.line.color.rgb, c.line.width = rgb(color), Pt(w)
    if dash:
        c.line.dash_style = 4
    if head:
        e = etree.SubElement(c.line._get_or_add_ln(), qn("a:tailEnd"))
        e.set("type", "triangle")
    return c


_icons = {}


def icon(sh, name, x, y, s, color=CTX):
    key = (name, color)
    if key not in _icons:
        svg = (HERE / "icons" / f"{name}.svg").read_text("utf8").replace("currentColor", f"#{color}")
        _icons[key] = cairosvg.svg2png(bytestring=svg.encode(), output_width=192, output_height=192)
    return sh.add_picture(io.BytesIO(_icons[key]), Inches(x), Inches(y), Inches(s), Inches(s))


def picture(sh, path, x, y, w=None, h=None):
    p = Path(path)
    if p.suffix == ".svg":
        data = cairosvg.svg2png(url=str(p), output_width=1600)
    else:
        buf = io.BytesIO()
        Image.open(p).convert("RGBA").save(buf, "PNG")
        data = buf.getvalue()
    return sh.add_picture(io.BytesIO(data), Inches(x), Inches(y),
                          Inches(w) if w else None, Inches(h) if h else None)


def pill(sh, x, y, w, h, label, fill, color=WHITE, size=12):
    box(sh, x, y, w, h, fill, r=h / 2)
    text(sh, x, y, w, h, label, size=size, color=color, bold=True, align=C, anchor=MID)


# ------------------------------------------------------------------------------ slides
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


class Page:
    def __init__(self, n, part=None, title="", takeaway="", source="", notes="", chrome=True):
        self.s = prs.slides.add_slide(BLANK)
        self.n, self.groups = n, []
        bg = self.s.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(PAPER)
        self.s.notes_slide.notes_text_frame.text = notes
        if chrome:
            self.chrome(part, title, takeaway, source)

    @property
    def sh(self):
        return self.s.shapes

    def chrome(self, part, title, takeaway, source):
        sh = self.sh
        rect(sh, 0, 0, 13.333, 0.075, IUH)
        rect(sh, 0, 0.075, 13.333, 0.035, "E9E4D6")
        rect(sh, 0, 0.075, 13.333 * self.n / TOTAL, 0.035, GOLD)
        picture(sh, HERE / "img" / "logo.svg", 0.55, 0.2, h=0.4)
        text(sh, 1.75, 0.27, 3.2, 0.3, "Báo cáo khóa luận tốt nghiệp", size=12, color=MUTED)
        nav = sh.add_textbox(Inches(4.75), Inches(0.27), Inches(8.03), Inches(0.3))
        tf = nav.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = R
        for k, name in enumerate(PARTS):
            _run(p, name + ("    " if k < len(PARTS) - 1 else ""), 12,
                 IUH if k == part else "8A8F99", k == part, False)
        line(sh, 0.55, 0.72, 12.78, 0.72, RULE, 1)
        text(sh, 0.55, 0.8, 0.85, 0.62, f"{part + 1:02d}", size=34, bold=True, color=IUH, anchor=MID)
        rect(sh, 1.38, 0.88, 0.05, 0.5, GOLD)
        text(sh, 1.55, 0.78, 11.2, 0.5, title, size=27, bold=True, color=INK, anchor=MID)
        text(sh, 1.55, 1.27, 11.2, 0.36, takeaway, size=16, color=CTX, anchor=MID)
        line(sh, 0.55, 7.0, 12.78, 7.0, RULE, 0.75)
        text(sh, 0.55, 7.05, 11.3, 0.36, source, size=10.5, color=MUTED)
        text(sh, 11.9, 7.05, 0.88, 0.3, f"{self.n}/{TOTAL}", size=11, color=MUTED, align=R)

    def group(self):
        g = self.s.shapes.add_group_shape()
        self.groups.append(g)
        return g.shapes

    def finish(self):
        root = self.s._element
        tr = etree.fromstring(f'<p:transition xmlns:p="{P_NS}" spd="med"><p:fade/></p:transition>')
        root.find(qn("p:clrMapOvr")).addnext(tr)
        if not self.groups:
            return
        ids = iter(range(3, 10_000))
        pars = ""
        for g in self.groups:
            a, b, c, d, e = (next(ids) for _ in range(5))
            sid = g.shape_id
            pars += (
                f'<p:par><p:cTn id="{a}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
                f'</p:stCondLst><p:childTnLst><p:par><p:cTn id="{b}" fill="hold"><p:stCondLst>'
                f'<p:cond delay="0"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{c}" '
                f'presetID="10" presetClass="entr" presetSubtype="0" fill="hold" '
                f'nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
                f'<p:childTnLst><p:set><p:cBhvr><p:cTn id="{d}" dur="1" fill="hold"><p:stCondLst>'
                f'<p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{sid}"/>'
                f'</p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName>'
                f'</p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
                f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{e}" dur="500"/>'
                f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
                f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst>'
                f'</p:cTn></p:par>')
        tm = (f'<p:timing xmlns:p="{P_NS}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" '
              f'restart="never" nodeType="tmRoot"><p:childTnLst><p:seq concurrent="1" '
              f'nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
              f'{pars}</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0">'
              f'<p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst><p:nextCondLst>'
              f'<p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>'
              f'</p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
        tr.addnext(etree.fromstring(tm))


def card(sh, x, y, w, h, color, fill=WHITE, top=True):
    box(sh, x, y, w, h, fill, RULE, 1.25, r=0.1)
    if top:
        rect(sh, x + 0.06, y, w - 0.12, 0.07, color)


def ci_row(sh, x0, x1, lo_v, hi_v, y, v, lo, hi, color, label_size=13, label=None):
    """One estimate with its 95 % interval on a horizontal scale from lo_v to hi_v."""
    sx = lambda t: x0 + (t - lo_v) / (hi_v - lo_v) * (x1 - x0)  # noqa: E731
    line(sh, sx(lo), y, sx(hi), y, color, 2.25)
    line(sh, sx(lo), y - 0.09, sx(lo), y + 0.09, color, 2)
    line(sh, sx(hi), y - 0.09, sx(hi), y + 0.09, color, 2)
    box(sh, sx(v) - 0.09, y - 0.09, 0.18, 0.18, color, shape=MSO_SHAPE.OVAL)
    if label:
        text(sh, sx(hi) + 0.1, y - 0.16, 0.9, 0.32, label, size=label_size, bold=True, color=color,
             anchor=MID)
    return sx


def vn(v, d=3):
    return f"{v:.{d}f}".replace(".", ",")


pages = []

# 1 ------------------------------------------------------------------------- cover
pg = Page(1, chrome=False, notes=(
    "Kính chào quý thầy cô trong Hội đồng. Nhóm em gồm Nguyễn Ngọc Lân và Nguyễn Tấn Minh, dưới sự "
    "hướng dẫn của ThS. Trương Vĩnh Linh. Đề tài của nhóm là nghiên cứu và xây dựng hệ thống phát hiện "
    "ảo giác cho mô hình ngôn ngữ lớn tăng cường truy xuất tiếng Việt, dựa trên tín hiệu chú ý nội tại. "
    "Ý tưởng chính: khi một mô hình ngôn ngữ đọc lại câu trả lời cùng ngữ cảnh đã truy xuất, cách nó "
    "phân bổ chú ý cho biết câu trả lời có dựa trên ngữ cảnh hay không, mà không cần gọi thêm một mô "
    "hình giám khảo nào. Bài trình bày đi theo bố cục của quyển khóa luận."))
sh = pg.sh
rect(sh, 0, 0, 13.333, 0.11, IUH)
rect(sh, 0, 0.11, 13.333, 0.045, GOLD)
rect(sh, 0, 7.345, 13.333, 0.045, GOLD)
rect(sh, 0, 7.39, 13.333, 0.11, IUH)
picture(sh, HERE / "img" / "owl-prof.webp", 8.45, 0.75, h=6.6)
picture(sh, HERE / "img" / "logo.svg", 0.8, 0.55, h=0.75)
text(sh, 0.8, 1.5, 7.6, 0.75, [("TRƯỜNG ĐẠI HỌC CÔNG NGHIỆP THÀNH PHỐ HỒ CHÍ MINH",
                                 dict(size=15, bold=True, color=IUH)),
                                ("Khoa Công nghệ Thông tin · Ngành Khoa học dữ liệu",
                                 dict(size=14, color=MUTED))])
text(sh, 0.8, 2.45, 7.6, 0.35, "BÁO CÁO KHÓA LUẬN TỐT NGHIỆP", size=16, bold=True, color=CTX)
text(sh, 0.8, 2.85, 7.7, 2.1, "Nghiên cứu và xây dựng hệ thống phát hiện ảo giác cho mô hình ngôn "
     "ngữ lớn tăng cường truy xuất tiếng Việt dựa trên tín hiệu chú ý nội tại", size=29, bold=True,
     color=INK, spacing=1.05)
for k, (role, name, sub) in enumerate([("Sinh viên thực hiện", "Nguyễn Ngọc Lân", "MSSV 22635801"),
                                       ("Sinh viên thực hiện", "Nguyễn Tấn Minh", "MSSV 22643511"),
                                       ("Giảng viên hướng dẫn", "ThS. Trương Vĩnh Linh",
                                        "Khoa Công nghệ Thông tin")]):
    x = 0.8 + k * 2.55
    rect(sh, x, 5.3, 0.05, 0.95, GOLD)
    text(sh, x + 0.18, 5.27, 2.35, 1.0, [(role, dict(size=11, color=MUTED, bold=True)),
                                         (name, dict(size=16, bold=True)),
                                         (sub, dict(size=12, color=MUTED))])
text(sh, 0.8, 6.75, 6, 0.35, "Thành phố Hồ Chí Minh, tháng 12 năm 2026", size=13, color=MUTED)
pages.append(pg)

# 2 ------------------------------------------------------------------------- problem
pg = Page(2, 0, "Bài toán: phát hiện và phân loại ảo giác trong hệ RAG",
          "Câu trả lời của hệ RAG được xếp vào ba lớp: trung thực, ảo giác nội tại, ảo giác ngoại lai",
          "Mục 1.1, 1.4, 2.3 · phân loại ảo giác: Ji và cộng sự (2023), Maynez và cộng sự (2020) · hệ "
          "nhãn ba lớp theo ViHallu: Nguyen và cộng sự (2026) · điểm rủi ro do hệ thống của đề tài tính",
          notes=(
              "Hệ RAG truy xuất tài liệu rồi để mô hình ngôn ngữ trả lời dựa trên tài liệu đó, nhưng câu "
              "trả lời vẫn có thể chứa thông tin không có căn cứ. Theo hệ nhãn của bộ ViHallu, có hai "
              "loại ảo giác. Ảo giác nội tại dùng thông tin có trong ngữ cảnh nhưng nói sai, như đổi "
              "triều Lý thành triều Trần. Ảo giác ngoại lai đưa vào thông tin ngữ cảnh không hề nhắc tới, "
              "như tháp Eiffel ở hồ Tây. Hai loại cần cách xử lý khác nhau: nội tại thì sửa cho khớp tài "
              "liệu, ngoại lai thì bỏ đi hoặc truy xuất thêm. Bên phải là điểm rủi ro mà hệ thống của "
              "nhóm tính cho ba câu này. Bài toán vì vậy là phân loại ba lớp. Đầu vào là ngữ cảnh, câu "
              "hỏi và câu trả lời của bất kỳ hệ RAG nào; đầu ra là nhãn, điểm rủi ro và tỷ trọng chú ý "
              "theo từng đoạn ngữ cảnh. Đề tài đặt bốn ràng buộc ở dưới cùng."))
sh = pg.sh
card(sh, 0.55, 1.85, 4.55, 3.55, CTX)
text(sh, 0.75, 2.02, 4.2, 0.32, "Tài liệu truy xuất (ngữ cảnh)", size=15, bold=True, color=CTX)
ctx = ["Hà Nội là thủ đô của Việt Nam, nằm bên bờ sông Hồng.",
       "Thành phố có lịch sử hơn một nghìn năm, từng mang tên Thăng Long dưới triều Lý.",
       "Dân số nội thành khoảng tám triệu người.",
       "Khí hậu Hà Nội có bốn mùa rõ rệt, mùa đông có thể xuống dưới mười độ."]
for i, s in enumerate(ctx):
    y = 2.42 + i * 0.74
    box(sh, 0.75, y, 4.15, 0.68, CTXS, r=0.06)
    text(sh, 0.85, y + 0.03, 0.6, 0.22, f"Câu {i + 1}", size=10, bold=True, color=CTX)
    text(sh, 0.85, y + 0.22, 3.95, 0.45, s, size=11.5)
resp = [("TRUNG THỰC", OK, OKS, "Hà Nội từng mang tên Thăng Long dưới triều **Lý**.",
         "Mọi ý đều có trong tài liệu (câu 2)", "0,001"),
        ("NỘI TẠI", WARN, WARNS, "Hà Nội từng mang tên Thăng Long dưới triều **Trần**, khi dân số đã "
         "lên tới **hai mươi triệu** người.", "Dựa vào câu 2 và câu 3 nhưng mâu thuẫn với ngữ cảnh",
         "0,998"),
        ("NGOẠI LAI", BAD, BADS, "Hà Nội nổi tiếng với **tháp Eiffel thu nhỏ ở hồ Tây** và **tuyến "
         "tàu điện ngầm dài nhất Đông Nam Á**.", "Ngữ cảnh không nhắc tới, không có căn cứ", "1,000")]
for i, (lab, col, _tint, s, why, risk) in enumerate(resp):
    g = sh if i == 0 else pg.group()
    y = 1.85 + i * 1.2
    box(g, 5.35, y, 7.43, 1.13, WHITE, RULE, 1.25, r=0.1)
    rect(g, 5.35, y + 0.06, 0.08, 1.01, col)
    pill(g, 5.6, y + 0.1, 1.35, 0.28, lab, col, size=11)
    text(g, 7.1, y + 0.1, 4.0, 0.28, why, size=11.5, bold=True, color=col, anchor=MID)
    text(g, 5.6, y + 0.45, 5.6, 0.62, s, size=13.5)
    text(g, 11.3, y + 0.12, 1.35, 0.25, "điểm rủi ro", size=11, color=MUTED, align=R)
    text(g, 11.1, y + 0.36, 1.55, 0.5, risk, size=24, bold=True, color=col, align=R)
g = pg.group()
flow = [("Đầu vào", "Ngữ cảnh, câu hỏi và câu trả lời của bất kỳ hệ RAG nào"),
        ("Bộ phát hiện", "Mô hình ngôn ngữ mở đọc một lượt; chỉ bộ phân loại tuyến tính được huấn luyện"),
        ("Đầu ra", "Nhãn ba lớp, điểm rủi ro = 1 − P(trung thực), tỷ trọng chú ý theo đoạn")]
for k, (h, b) in enumerate(flow):
    x = 0.55 + k * 4.12
    box(g, x, 5.6, 3.85, 0.82, CTXS if k == 1 else WHITE, CTX if k == 1 else RULE, 1.25, r=0.1)
    text(g, x + 0.15, 5.64, 3.6, 0.76, [(h, dict(size=13, bold=True, color=CTX)), (b, dict(size=12.5))],
         anchor=MID)
    if k < 2:
        line(g, x + 3.88, 6.01, x + 4.09, 6.01, CTX, 2, head=True)
for k, (ic, t) in enumerate([("users", "Không gọi LLM giám khảo"), ("lock", "Không tinh chỉnh LLM"), ("cpu", "Một GPU Tesla T4 16 GB"), ("flag", "Tiếng Việt, ba lớp "
                             "nhãn")]):
    x = 0.55 + k * 3.09
    box(g, x, 6.52, 2.95, 0.36, INK, r=0.18)
    icon(g, ic, x + 0.14, 6.57, 0.26, WHITE)
    text(g, x + 0.48, 6.52, 2.4, 0.36, t, size=12, bold=True, color=WHITE, anchor=MID)
pages.append(pg)

# 3 ------------------------------------------------------------------------- motivation, gaps
pg = Page(3, 0, "Động lực, khoảng trống và câu hỏi nghiên cứu",
          "Ba khoảng trống dẫn tới ba câu hỏi nghiên cứu, cụ thể hóa thành năm giả thuyết",
          "Mục 1.2–1.3, Bảng 1.1 · LLM giám khảo: Zheng và cộng sự (2023) · PhoBERT: Nguyen và Nguyen "
          "(2020) · XLM-R: Conneau và cộng sự (2020) · Lookback Lens: Chuang và cộng sự (2024)",
          notes=(
              "Các hướng phát hiện ảo giác phổ biến đều có hạn chế. LLM giám khảo không cần huấn luyện "
              "nhưng tốn khoảng 8,2 giây mỗi mẫu và phải gửi dữ liệu ra ngoài. Tinh chỉnh bộ mã hóa như "
              "PhoBERT, XLM-R chính xác nhưng phải huấn luyện hàng trăm triệu tham số. Đặc trưng bề mặt "
              "gần như không tốn gì nhưng chỉ phản ánh độ dài và mức trùng từ. Từ đó nhóm xác định ba "
              "khoảng trống, trong phạm vi tài liệu đã khảo sát. Thứ nhất, chưa có công trình tách tỷ lệ "
              "chú ý theo từng đoạn ngữ cảnh và đối chiếu với vị trí bằng chứng. Thứ hai, ba hướng chưa "
              "được so trên cùng dữ liệu, cùng cách chia tập, theo cả độ chính xác lẫn chi phí. Thứ ba, "
              "chưa có công trình dùng tín hiệu nội tại cho ảo giác tiếng Việt. Ba khoảng trống tương "
              "ứng ba câu hỏi nghiên cứu, và được cụ thể hóa thành năm giả thuyết H1 đến H5."))
sh = pg.sh
box(sh, 0.55, 1.85, 12.23, 0.78, PAPER2, r=0.1)
text(sh, 0.75, 1.85, 2.0, 0.78, "Hạn chế của các hướng hiện có", size=13, bold=True, color=INK,
     anchor=MID)
for k, (h, b) in enumerate([("LLM giám khảo", "8,2 giây mỗi mẫu; dữ liệu phải gửi ra ngoài"),
                            ("Bộ mã hóa tinh chỉnh", "369–560 triệu tham số phải huấn luyện"),
                            ("Đặc trưng bề mặt", "Chỉ phản ánh độ dài và mức trùng từ")]):
    x = 2.95 + k * 3.28
    text(sh, x, 1.9, 3.15, 0.7, [(h, dict(size=13, bold=True, color=BAD)), (b, dict(size=12.5))],
         anchor=MID)
cols = [(CTX, "search", "Khoảng trống 1 · Phương pháp", "Chưa tách tỷ lệ chú ý theo từng đoạn ngữ cảnh "
         "và đối chiếu với vị trí bằng chứng", "CH1 · Chia theo đoạn", "Chú ý tách theo từng đoạn có giúp "
         "phát hiện tốt hơn tỷ lệ gộp, và có tập trung đúng vào đoạn chứa bằng chứng?", "H2, H3, H4"),
        (RES, "scale", "Khoảng trống 2 · Đánh giá", "Ba hướng chưa được so trên cùng dữ liệu, cùng cách "
         "chia tập, theo cả độ chính xác lẫn chi phí", "CH2 · Độ chính xác và chi phí", "So với bộ mã hóa "
         "tinh chỉnh và LLM giám khảo, hướng nội tại đạt bao nhiêu và tốn bao nhiêu?",
         "H1 và phép đo chi phí"),
        (VIOLET, "flag", "Khoảng trống 3 · Ngôn ngữ", "Chưa có công trình dùng tín hiệu nội tại để phát "
         "hiện ảo giác tiếng Việt", "CH3 · Đóng góp và chuyển giao", "Chú ý thêm được bao nhiêu so với "
         "đặc trưng bề mặt, và có giữ hiệu năng trên bộ dữ liệu khác?", "H1, H5")]
for k, (col, ic, gk, gs, qk, qs, hs) in enumerate(cols):
    g = pg.group()
    x = 0.55 + k * 4.14
    card(g, x, 2.85, 3.95, 1.55, col)
    icon(g, ic, x + 0.2, 3.05, 0.36, col)
    text(g, x + 0.68, 3.05, 3.15, 0.36, gk, size=13, bold=True, color=col, anchor=MID)
    text(g, x + 0.2, 3.5, 3.6, 0.85, gs, size=14)
    line(g, x + 1.975, 4.45, x + 1.975, 4.75, col, 2.25, head=True)
    box(g, x, 4.8, 3.95, 2.0, WHITE, col, 1.75, r=0.1)
    text(g, x + 0.2, 4.92, 3.6, 0.3, qk, size=13, bold=True, color=col)
    text(g, x + 0.2, 5.27, 3.6, 1.0, qs, size=14.5)
    text(g, x + 0.2, 6.38, 3.6, 0.3, "Giả thuyết: " + hs, size=12.5, bold=True, color=MUTED)
pages.append(pg)

# 4 ------------------------------------------------------------------------- related work
pg = Page(4, 1, "Các hướng phát hiện ảo giác đã có",
          "Khóa luận thuộc hướng trọng số chú ý: một lượt đọc, chỉ huấn luyện bộ phân loại tuyến tính",
          "Bảng 2.1 · Nguyen và Nguyen (2020) · Conneau và cộng sự (2020) · Zheng và cộng sự (2023) · "
          "Cohen-Wang và cộng sự (2024) · Li và cộng sự (2026) · Chuang và cộng sự (2024) · Sun và cộng sự "
          "(2025) · Ogasa và Arase (2025) · Ji và cộng sự (2023)",
          notes=(
              "Bảng này đặt các hướng phát hiện ảo giác cạnh nhau theo tín hiệu sử dụng, phần phải huấn "
              "luyện, chi phí khi dùng và hạn chế chính. Đặc trưng bề mặt rẻ nhưng đơn giản. Bộ mã hóa "
              "tinh chỉnh như PhoBERT, XLM-R cần dữ liệu có nhãn và huấn luyện lại khi đổi miền. LLM làm "
              "giám khảo không cần huấn luyện nhưng tốn chi phí theo lượt và phải gửi dữ liệu ra ngoài. "
              "Hướng cắt bỏ ngữ cảnh như ContextCite và ARC-JSD hỏi câu trả lời dựa vào đoạn nào, chi phí "
              "tăng theo số đoạn. Khóa luận thuộc hướng trọng số chú ý, cùng nhánh với Lookback Lens, "
              "ReDeEP và Ogasa và Arase: chỉ cần một lượt đọc và một bộ phân loại tuyến tính, đổi lại cần "
              "mô hình mở. Ảo giác ở đây là ảo giác theo ngữ cảnh, tức câu trả lời không trung thành với "
              "tài liệu, khác với ảo giác về tính xác thực so với thế giới thực."))
sh = pg.sh
rows = [("Hướng", "Tín hiệu", "Công trình tiêu biểu", "Phải huấn luyện", "Chi phí khi dùng",
         "Hạn chế chính"),
        ("Đặc trưng bề mặt", "Độ dài, trùng lặp từ vựng", "—", "Vài tham số", "Gần bằng 0",
         "Chỉ phản ánh đặc điểm đơn giản của văn bản"),
        ("Bộ mã hóa, NLI", "Ngữ cảnh và phản hồi", "PhoBERT, XLM-R", "Hàng trăm triệu tham số",
         "Một lượt bộ mã hóa", "Cần dữ liệu có nhãn; huấn luyện lại khi đổi miền"),
        ("LLM giám khảo", "Văn bản, qua một LLM khác", "LLM-as-a-judge", "Không", "Một lượt gọi LLM",
         "Chi phí theo lượt; dữ liệu phải gửi ra ngoài"),
        ("Cắt bỏ ngữ cảnh", "Đầu ra khi bỏ một đoạn", "ContextCite, ARC-JSD", "Không hoặc rất ít",
         "Một lượt đọc cho mỗi đoạn", "Chi phí tăng theo số đoạn"),
        ("Trọng số chú ý (khóa luận)", "Chú ý của phản hồi vào ngữ cảnh",
         "Lookback Lens, ReDeEP, Ogasa và Arase", "Bộ phân loại tuyến tính", "Một lượt đọc",
         "Cần mô hình mở; không dùng được FlashAttention")]
widths = [2.15, 2.0, 2.25, 1.85, 1.75, 2.23]
tbl = sh.add_table(len(rows), len(widths), Inches(0.55), Inches(1.9), Inches(sum(widths)),
                   Inches(4.0)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.5 if i == 0 else 0.68)
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.margin_top = cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MID
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else CTXS if i == len(rows) - 1 else
                                       WHITE if i % 2 else PAPER2)
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        _run(p, v, 12.5 if i else 12.5, WHITE if i == 0 else CTX if i == len(rows) - 1 and j == 0 else
             INK, i == 0 or i == len(rows) - 1 or j == 0, False)
g = pg.group()
for k, (h, b, col) in enumerate([
        ("Ảo giác theo ngữ cảnh", "Câu trả lời không trung thành với tài liệu được cung cấp, khác ảo "
         "giác về tính xác thực so với thế giới thực. Đề tài chỉ xét loại này.", CTX),
        ("Định vị so với truy nguồn", "Hướng cắt bỏ hỏi câu trả lời dựa vào đoạn nào; khóa luận đối "
         "chiếu trực tiếp với ARC-JSD ở trang 11.", RES)]):
    x = 0.55 + k * 6.17
    box(g, x, 6.05, 6.0, 0.8, WHITE, RULE, 1.25, r=0.1)
    rect(g, x, 6.05, 0.07, 0.8, col)
    text(g, x + 0.2, 6.08, 5.7, 0.75, [(h, dict(size=13, bold=True, color=col)), (b, dict(size=12))],
         anchor=MID)
pages.append(pg)

# 5 ------------------------------------------------------------------------- Lookback Lens
pg = Page(5, 1, "Phương pháp nền: Lookback Lens",
          "Mỗi đầu chú ý cho một tỷ lệ lookback; 756 tỷ lệ là đầu vào của một hồi quy logistic",
          "Mục 2.5, 4.3 · Lookback Lens: Chuang và cộng sự (EMNLP 2024) · Transformer: Vaswani và cộng sự "
          "(2017) · Qwen2.5: Qwen Team (2024) · số trên hình là ví dụ minh họa nguyên lý",
          notes=(
              "Phương pháp nền là Lookback Lens, công bố tại EMNLP 2024. Khi mô hình xử lý một token của "
              "câu trả lời, mỗi đầu chú ý chia trọng số cho hai phần: ngữ cảnh, và phần câu trả lời đứng "
              "trước. Lấy chú ý trung bình trên mỗi token của từng phần rồi so sánh, ta được tỷ lệ "
              "lookback: tỷ lệ càng cao, mô hình càng dựa vào ngữ cảnh. Trong ví dụ, 0,10 so với 0,06 cho "
              "khoảng 62 phần trăm. Lấy trung bình trên các token của câu trả lời, riêng cho từng đầu, mô "
              "hình đọc Qwen2.5-7B cho 27 lớp nhân 28 đầu, tức 756 tỷ lệ, vì lớp cuối bị loại do tràn số "
              "ở float16. Một hồi quy logistic nhận 756 giá trị này. Bài gốc trên tiếng Anh cho thấy bộ "
              "phát hiện này chuyển được từ hỏi đáp sang tóm tắt tốt hơn bộ phân loại dùng trạng thái "
              "ẩn. Nhóm em tái lập phương pháp này trên tiếng Việt, với bài toán ba lớp."))
sh = pg.sh
card(sh, 0.55, 1.85, 6.0, 4.95, CTX)
text(sh, 0.8, 2.02, 5.5, 0.3, "Một đầu chú ý, khi đọc token “1994” của câu trả lời", size=14,
     bold=True, color=CTX)
toks = ["Vịnh", "Hạ Long", "UNESCO", "công nhận", "năm", "1994"]
ws = [0.05, 0.08, 0.30, 0.09, 0.04, 0.04]
for i, (t, w) in enumerate(zip(toks, ws, strict=True)):
    y = 2.45 + i * 0.38
    box(sh, 0.8, y, 1.25, 0.3, WHITE, CTX, 1.25, r=0.05)
    text(sh, 0.8, y, 1.25, 0.3, t, size=11.5, align=C, anchor=MID)
    line(sh, 2.08, y + 0.15, 2.95, 3.55, CTX, 0.8 + w * 18)
box(sh, 2.95, 3.33, 0.95, 0.44, RESS, RES, 1.75, r=0.06)
text(sh, 2.95, 3.33, 0.95, 0.44, "1994", size=15, bold=True, align=C, anchor=MID)
for i, (t, w) in enumerate(zip(["UNESCO", "công", "nhận", "năm"], [0.06, 0.07, 0.05, 0.07],
                               strict=True)):
    y = 2.83 + i * 0.38
    box(sh, 4.95, y, 1.3, 0.3, WHITE, RES, 1.25, r=0.05)
    text(sh, 4.95, y, 1.3, 0.3, t, size=11.5, align=C, anchor=MID)
    line(sh, 3.92, 3.55, 4.92, y + 0.15, RES, 0.8 + w * 18)
text(sh, 0.8, 4.78, 1.4, 0.25, "ngữ cảnh", size=11, bold=True, color=CTX)
text(sh, 4.95, 4.4, 1.6, 0.25, "phản hồi đứng trước", size=11, bold=True, color=RES)
g = pg.group()
text(g, 0.8, 5.12, 3.0, 0.28, "Chú ý trung bình mỗi token ngữ cảnh", size=12, color=MUTED)
rect(g, 0.8, 5.42, 2.4, 0.22, PAPER2)
rect(g, 0.8, 5.42, 2.0, 0.22, CTX)
text(g, 3.3, 5.36, 0.7, 0.3, "0,10", size=14, bold=True, color=CTX)
text(g, 0.8, 5.75, 3.2, 0.28, "Chú ý trung bình mỗi token phản hồi trước", size=12, color=MUTED)
rect(g, 0.8, 6.05, 2.4, 0.22, PAPER2)
rect(g, 0.8, 6.05, 1.25, 0.22, RES)
text(g, 3.3, 5.99, 0.7, 0.3, "0,06", size=14, bold=True, color=RES)
box(g, 4.15, 5.12, 2.2, 1.45, CTXS, r=0.1)
text(g, 4.25, 5.17, 2.0, 1.38, [("Tỷ lệ lookback", dict(size=12, color=MUTED)),
                                ("0,10 ÷ (0,10 + 0,06)", dict(size=13)),
                                ("≈ 62 %", dict(size=26, bold=True, color=CTX))], align=C, anchor=MID)
g = pg.group()
card(g, 6.8, 1.85, 5.98, 4.95, IUH)
text(g, 7.05, 2.02, 5.5, 0.3, "Mọi đầu chú ý của mô hình đọc", size=14, bold=True, color=IUH)
seed = [11]


def rnd():
    seed[0] = (seed[0] * 9301 + 49297) % 233280
    return seed[0] / 233280


grid = g.add_group_shape().shapes
cw, chh = 0.105, 0.075
for layer in range(27):
    for head in range(28):
        v = 0.25 + 0.5 * rnd() + (0.25 if (head, layer) in ((7, 5), (4, 17)) else 0)
        c = box(grid, 7.05 + head * cw, 2.45 + layer * (chh + 0.013), cw - 0.015, chh, CTX,
                shape=MSO_SHAPE.RECTANGLE)
        fill = c.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
        etree.SubElement(fill, qn("a:alpha")).set("val", str(int(min(1, v * 0.9) * 100000)))
text(g, 7.05, 4.88, 3.0, 0.3, "27 lớp × 28 đầu = 756 tỷ lệ", size=12.5, bold=True)
line(g, 10.1, 3.62, 10.55, 3.62, MUTED, 2, head=True)
box(g, 10.6, 3.2, 1.95, 0.85, WHITE, INK, 1.5, r=0.08)
text(g, 10.6, 3.2, 1.95, 0.85, [("Hồi quy logistic", dict(size=13, bold=True)),
                                ("trung thực · nội tại · ngoại lai", dict(size=10.5, color=MUTED))],
     align=C, anchor=MID)
text(g, 7.05, 5.3, 5.55, 1.45, [
    "Lớp 27 của Qwen2.5-7B bị loại vì tràn số ở float16; 27 lớp còn lại khớp float32.",
    "Bài gốc (tiếng Anh): huấn luyện trên hỏi đáp, kiểm tra trên tóm tắt, AUROC 85,3 so với tối đa "
    "83,6 của bộ phân loại trạng thái ẩn.",
    "Khóa luận tái lập trên tiếng Việt, ba lớp nhãn."], size=12.5, bullet=True, after=3)
pages.append(pg)

# 6 ------------------------------------------------------------------------- data
pg = Page(6, 2, "Dữ liệu: bốn bộ tiếng Việt và cách chia tập",
          "Chia tập theo ngữ cảnh để tránh rò rỉ; rò rỉ ở tập test gốc được đo và nêu kèm kết quả",
          "Mục 3.1–3.4, Bảng 3.1, 3.2, 3.4, 3.5 · ViHallu: Nguyen và cộng sự (2026) · ISE-DSC01: UIT Data "
          "Science Challenge (2023) · ViWikiFC: Le và cộng sự (2024) · ViFactCheck: Tran và cộng sự (2025) "
          "· nhãn kiểm chứng thông tin theo FEVER: Thorne và cộng sự (2018)",
          notes=(
              "Nhóm dùng bốn bộ dữ liệu tiếng Việt công khai. ViHallu là bộ chính, bảy nghìn mẫu, duy nhất "
              "có câu trả lời do GPT-4o sinh và nhãn ảo giác ba lớp. ISE-DSC01 có ngữ cảnh dài, trung vị "
              "19 câu, và đánh dấu sẵn câu bằng chứng, nên dùng để đo khả năng định vị. ViWikiFC dùng để "
              "so sánh với kết quả đã công bố và cho thí nghiệm loại bỏ câu bằng chứng. ViFactCheck dùng "
              "cho thí nghiệm chuyển sang miền tin tức. Ba bộ kiểm chứng thông tin có nhãn SUPPORTED, "
              "REFUTED, NEI; nhóm ánh xạ sang ba lớp và kiểm chứng thủ công 100 mẫu NEI: 67 mẫu được cả "
              "hai người xác định là ngoại lai, kappa 0,505. Điểm quan trọng là cách chia tập: nhóm chia "
              "theo ngữ cảnh, nên mọi câu trả lời của cùng một tài liệu nằm chung một tập, rò rỉ bằng 0. "
              "Tập test gốc của ViWikiFC dùng lại toàn bộ ngữ cảnh huấn luyện, nhóm đo được và nêu kèm "
              "mọi kết quả trên bộ đó."))
sh = pg.sh
rows = [("Bộ dữ liệu", "Vai trò trong khóa luận", "Số mẫu", "Câu/ngữ cảnh", "Cách chia"),
        ("ViHallu", "Bộ chính: phản hồi do GPT-4o sinh, nhãn ảo giác ba lớp", "7.000", "5",
         "Tự chia 80/10/10 theo ngữ cảnh"),
        ("ISE-DSC01", "Ngữ cảnh dài; đo khả năng định vị câu bằng chứng", "36.369", "19",
         "Tự chia 80/10/10 theo ngữ cảnh"),
        ("ViWikiFC", "So sánh với kết quả đã công bố; thí nghiệm loại bỏ câu bằng chứng", "20.919", "4",
         "Chia gốc; test rò rỉ 100 %"),
        ("ViFactCheck", "Chuyển sang miền tin tức", "7.232", "17", "Chia gốc; test rò rỉ 99,3 %")]
widths = [1.6, 5.3, 1.25, 1.45, 2.63]
tbl = sh.add_table(len(rows), len(widths), Inches(0.55), Inches(1.88), Inches(sum(widths)),
                   Inches(2.4)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.42 if i == 0 else 0.47)
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MID
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else CTXS if i == 1 else
                                       WHITE if i % 2 else PAPER2)
        p = cell.text_frame.paragraphs[0]
        p.alignment = C if j in (2, 3) else L
        _run(p, v, 13, WHITE if i == 0 else BAD if "rò rỉ" in v else INK,
             i == 0 or j == 0 or "rò rỉ" in v, False)
g = pg.group()
card(g, 0.55, 4.5, 6.85, 2.32, CTX)
text(g, 0.8, 4.65, 6.4, 0.3, "Chia theo ngữ cảnh, không chia theo dòng", size=14, bold=True,
     color=CTX)
palette = [CTX, RES, VIOLET, OK, WARN, BAD, "2A6FB0", "8A5A44"]
sizes = [3, 2, 4, 3, 2, 3, 4, 2]
bins = [(0.8, 3.6, "Huấn luyện 80 %", range(0, 6)), (4.6, 1.2, "Dev 10 %", range(6, 7)),
        (5.95, 1.2, "Test 10 %", range(7, 8))]
for x, w, lab, docs in bins:
    box(g, x, 5.05, w, 0.62, WHITE, RULE, 1.25, r=0.06)
    text(g, x, 5.7, w, 0.25, lab, size=11.5, bold=True, color=MUTED, align=C)
    dx = x + 0.12
    for d in docs:
        for _ in range(sizes[d]):
            box(g, dx, 5.27, 0.16, 0.16, palette[d], shape=MSO_SHAPE.OVAL)
            dx += 0.19
        dx += 0.07
text(g, 0.8, 6.02, 6.45, 0.75, "Mỗi màu là một tài liệu: mọi câu trả lời của nó nằm chung một tập. "
     "Ngữ cảnh được sắp theo SHA-256 của (seed 42, mã ngữ cảnh), nên chia giống nhau trên mọi máy; rò "
     "rỉ giữa các tập bằng 0.", size=12.5)
g = pg.group()
card(g, 7.6, 4.5, 5.18, 2.32, RES)
text(g, 7.85, 4.65, 4.8, 0.3, "Ánh xạ nhãn và kiểm chứng thủ công", size=14, bold=True, color=RES)
text(g, 7.85, 5.02, 4.75, 0.75, ["SUPPORTED → trung thực · REFUTED → nội tại · NEI → ngoại lai",
                                 "Hai thành viên gán nhãn độc lập 100 mẫu NEI của ViWikiFC:"],
     size=12.5, after=2)
for k, (v, t) in enumerate([("67/100", "cả hai xác định là ngoại lai"), ("0,505", "hệ số kappa")]):
    x = 7.85 + k * 2.4
    text(g, x, 5.85, 2.3, 0.85, [(v, dict(size=24, bold=True, color=RES)), (t, dict(size=11.5,
                                                                                    color=MUTED))])
pages.append(pg)

# 7 ------------------------------------------------------------------------- chunk-aware
pg = Page(7, 3, "Phương pháp đề xuất: chunk-aware lookback ratio",
          "Tách tỷ lệ chú ý theo từng đoạn ngữ cảnh để đo chú ý tập trung vào đâu, không chỉ bao nhiêu",
          "Mục 4.4–4.5, Bảng 4.1, công thức (4.3)–(4.9) · mở rộng từ Lookback Lens: Chuang và cộng sự "
          "(2024) · số trên hình là ví dụ minh họa nguyên lý",
          notes=(
              "Đây là đóng góp chính của đề tài. Hai câu trả lời có thể cùng dành 62 phần trăm chú ý cho "
              "ngữ cảnh. Câu A lấy thông tin từ câu 3 nên chú ý tập trung vào câu 3; câu B nói điều ngữ "
              "cảnh không có nên chú ý phân bố đều. Lookback Lens gộp cả ngữ cảnh thành một giá trị nên "
              "không phân biệt được hai trường hợp này. Chunk-aware chia ngữ cảnh thành các đoạn, ở đây "
              "là các câu, tính mật độ chú ý trên mỗi token của từng đoạn, rồi chuẩn hóa thành tỷ trọng có "
              "tổng bằng một. Hình dạng của phân bố được mô tả bằng năm đặc trưng ở bên phải: tỷ trọng lớn "
              "nhất, entropy, hệ số Gini, khoảng cách giữa hai đoạn đứng đầu, và mức dịch chuyển giữa hai "
              "token liên tiếp. Mỗi đầu chú ý vì vậy cho sáu giá trị: một tỷ lệ lookback và năm đặc trưng "
              "hình dạng. Hướng thay đổi khi mất bằng chứng được ghi trong mã trước khi chạy thí nghiệm."))
sh = pg.sh
sents = ["Vịnh Hạ Long nằm ở tỉnh Quảng Ninh.", "Vịnh gồm 1.969 hòn đảo lớn nhỏ.",
         "UNESCO công nhận vịnh là Di sản thiên nhiên thế giới năm 1994.",
         "Năm 2000, vịnh được công nhận lần thứ hai về giá trị địa chất."]
for i, s in enumerate(sents):
    x = 0.55 + i * 1.62
    box(sh, x, 1.85, 1.52, 0.95, CTXS, CTX, 1, r=0.06)
    text(sh, x + 0.08, 1.88, 1.4, 0.25, f"Câu {i + 1}", size=10.5, bold=True, color=CTX)
    text(sh, x + 0.08, 2.1, 1.38, 0.7, s, size=10.5)
panels = [("A · trung thực", OK, "“UNESCO công nhận vịnh là Di sản thiên nhiên thế giới năm 1994.”",
           [0.06, 0.09, 0.71, 0.14], "0,65", "71 %", "Tập trung một đoạn"),
          ("B · ngoại lai", BAD, "“Vịnh Hạ Long mỗi năm đón hơn bảy triệu lượt khách.”",
           [0.24, 0.27, 0.26, 0.23], "1,00", "27 %", "Phân bố đều")]
for k, (name, col, quote, share, ent, mx, verdict) in enumerate(panels):
    g = sh if k == 0 else pg.group()
    y = 2.95 + k * 1.95
    box(g, 0.55, y, 6.4, 1.82, WHITE, RULE, 1.25, r=0.1)
    pill(g, 0.72, y + 0.12, 1.55, 0.3, name, col, size=11)
    text(g, 2.4, y + 0.08, 4.45, 0.42, quote, size=11.5, italic=True)
    text(g, 0.72, y + 0.55, 2.6, 0.25, "Lookback Lens · chú ý vào ngữ cảnh", size=10.5, color=MUTED)
    rect(g, 0.72, y + 0.82, 2.1, 0.16, PAPER2)
    rect(g, 0.72, y + 0.82, 2.1 * 0.62, 0.16, CTX)
    text(g, 2.9, y + 0.7, 0.7, 0.35, "62 %", size=15, bold=True)
    base = y + 1.62
    for i, v in enumerate(share):
        bx = 3.75 + i * 0.5
        rect(g, bx, base - v * 1.0, 0.36, v * 1.0, CTX)
        text(g, bx - 0.07, base - v * 1.0 - 0.22, 0.5, 0.2, f"{round(v * 100)} %", size=9.5,
             align=C)
        text(g, bx - 0.07, base + 0.0, 0.5, 0.18, f"Câu {i + 1}", size=8.5, color=MUTED, align=C)
    text(g, 0.72, y + 1.12, 2.9, 0.6, [(f"Entropy {ent} · lớn nhất {mx}", dict(size=12.5, bold=True)),
                                       (verdict, dict(size=12, bold=True, color=col))])
g = pg.group()
card(g, 7.2, 1.85, 5.58, 4.95, IUH)
text(g, 7.45, 2.0, 5.1, 0.3, "Từ ma trận chú ý đến năm đặc trưng", size=14, bold=True, color=IUH)
text(g, 7.45, 2.38, 5.15, 1.15, [
    "**Mật độ** của đoạn k: chú ý trung bình trên mỗi token của đoạn, so với mẫu số của tỷ lệ "
    "lookback.",
    "**Tỷ trọng** sₖ = mật độ của đoạn k chia cho tổng mật độ các đoạn; Σ sₖ = 1."], size=12.5, after=3)
feats = [("MAX", "Tỷ trọng của đoạn được chú ý nhiều nhất", "giảm"),
         ("ENT", "Entropy chuẩn hóa: mức phân tán của phân bố", "tăng"),
         ("GINI", "Hệ số Gini: mức chênh lệch giữa các đoạn", "giảm"),
         ("GAP", "Khoảng cách giữa hai đoạn đứng đầu", "giảm"),
         ("DRIFT", "Mức dịch chuyển giữa hai token liên tiếp", "không dự đoán")]
text(g, 7.45, 3.55, 1.0, 0.25, "Đặc trưng", size=11, bold=True, color=MUTED)
text(g, 8.4, 3.55, 2.9, 0.25, "Ý nghĩa", size=11, bold=True, color=MUTED)
text(g, 11.3, 3.55, 1.35, 0.25, "Khi mất bằng chứng", size=11, bold=True, color=MUTED, align=R)
for i, (f, m, d) in enumerate(feats):
    y = 3.85 + i * 0.44
    line(g, 7.45, y - 0.04, 12.6, y - 0.04, RULE, 0.75)
    text(g, 7.45, y, 0.95, 0.4, f, size=13, bold=True, color=IUH, anchor=MID)
    text(g, 8.4, y, 2.95, 0.4, m, size=11.5, anchor=MID)
    text(g, 11.3, y, 1.3, 0.4, d.capitalize(), size=12, bold=True,
         color=MUTED if d.startswith("không") else CTX, align=R, anchor=MID)
text(g, 7.45, 6.12, 5.15, 0.6, "Mỗi đầu chú ý cho **6 giá trị**: một tỷ lệ lookback và năm đặc trưng "
     "hình dạng. Hướng thay đổi được ghi trong mã trước khi chạy.", size=12.5)
pages.append(pg)

# 8 ------------------------------------------------------------------------- pipeline, hook
pg = Page(8, 3, "Quy trình một lượt đọc và trích chú ý bằng forward hook",
          "Đặc trưng được tính tại từng lớp rồi giải phóng ma trận: bộ nhớ đỉnh 8,4 GB trên GPU 16 GB",
          "Mục 4.1, 4.2, 4.7, 4.8, Bảng 2.2, 4.2 · Qwen2.5: Qwen Team (2024) · lượng tử hóa NF4: Dettmers "
          "và cộng sự (2023) · đỉnh 8.428 MB đo trên Tesla T4 ở ngưỡng 4.096 token",
          notes=(
              "Toàn bộ quy trình chỉ cần một lượt đọc, mô hình không sinh thêm token nào. Bước một, ghép "
              "ngữ cảnh, câu hỏi và câu trả lời vào mẫu prompt cố định từ ngày 19/08, rồi xác định vị trí "
              "vùng ngữ cảnh và vùng phản hồi. Bước hai, Qwen2.5-7B lượng tử hóa 4 bit đọc một lượt; tại "
              "27 lớp, forward hook tính chú ý theo đoạn. Bước ba, giữ 32 đầu được chọn trên tập dev, mỗi "
              "đầu sáu giá trị, tổng 192 đặc trưng. Bước bốn, hồi quy logistic 579 tham số cho nhãn và "
              "điểm rủi ro. Rủi ro kỹ thuật lớn nhất là bộ nhớ: muốn đọc trọng số chú ý phải tắt các cài "
              "đặt tối ưu như FlashAttention. Ở 4.096 token, ma trận chú ý của một lớp đã chiếm 0,94 GB; "
              "giữ cả 28 lớp cần khoảng 26 GB, vượt 16 GB của T4. Forward hook tính đặc trưng ngay khi một "
              "lớp xong rồi bỏ ma trận, nên đỉnh đo thực tế chỉ 8.428 MB."))
sh = pg.sh
steps = [("1", "Ghép prompt", "Mẫu hội thoại cố định từ 19/08; xác định vùng ngữ cảnh và vùng phản hồi"),
         ("2", "Một lượt đọc", "Qwen2.5-7B, 4 bit NF4, float16, bỏ lớp 27; hook ở 27 lớp"),
         ("3", "192 đặc trưng", "32 đầu chọn trên tập dev × 6 giá trị mỗi đầu"),
         ("4", "Hồi quy logistic", "579 tham số → nhãn ba lớp và điểm rủi ro")]
for k, (n, h, b) in enumerate(steps):
    x = 0.55 + k * 3.1
    box(sh, x, 1.88, 2.8, 1.6, WHITE, RULE, 1.25, r=0.1)
    box(sh, x + 0.18, 2.02, 0.42, 0.42, IUH, shape=MSO_SHAPE.OVAL)
    text(sh, x + 0.18, 2.02, 0.42, 0.42, n, size=15, bold=True, color=WHITE, align=C, anchor=MID)
    text(sh, x + 0.72, 2.02, 2.0, 0.42, h, size=15, bold=True, anchor=MID)
    text(sh, x + 0.18, 2.55, 2.5, 0.9, b, size=12.5)
    if k < 3:
        line(sh, x + 2.83, 2.68, x + 3.07, 2.68, IUH, 2, head=True)
g = pg.group()
card(g, 0.55, 3.7, 7.25, 3.1, BAD)
text(g, 0.8, 3.85, 6.8, 0.3, "Bộ nhớ ma trận chú ý ở 4.096 token (Qwen2.5-7B)", size=14, bold=True)
bars = [("Trọng số 4 bit", 5.3, MUTED), ("Một lớp chú ý", 0.94, CTX),
        ("Giữ cả 28 lớp (cách thông thường)", 26.3, BAD), ("Forward hook: đỉnh đo được", 8.43, OK)]
x0, x1, vmax = 3.35, 7.4, 28
for i, (lab, v, col) in enumerate(bars):
    y = 4.3 + i * 0.5
    text(g, 0.8, y, 2.5, 0.38, lab, size=12, anchor=MID, align=R)
    rect(g, x0, y + 0.06, (x1 - x0) * v / vmax, 0.26, col)
    text(g, x0 + (x1 - x0) * v / vmax + 0.06, y, 0.9, 0.38, vn(v, 1) + " GB", size=12, bold=True,
         color=col, anchor=MID)
x16 = x0 + (x1 - x0) * 16 / vmax
line(g, x16, 4.2, x16, 6.3, BAD, 1.5, dash=True)
text(g, x16 - 0.6, 6.3, 1.4, 0.3, "Giới hạn T4 16 GB", size=11, bold=True, color=BAD, align=C)
g = pg.group()
card(g, 8.0, 3.7, 4.78, 3.1, OK)
text(g, 8.25, 3.85, 4.4, 0.3, "Forward hook", size=14, bold=True, color=OK)
text(g, 8.25, 4.22, 4.35, 2.55, [
    "Hàm tự chạy ngay khi một lớp tính xong: cộng chú ý theo đoạn, rồi trả về rỗng thay cho ma trận.",
    "Không lớp nào phải giữ ma trận của lớp trước.",
    "Thời gian gần tuyến tính theo độ dài: khoảng 1,05 ms mỗi token; 437,6 ms mỗi mẫu ViHallu.",
    "Tràn số đo riêng từng mô hình: 7B bỏ lớp 27, 1.5B phải dùng bfloat16."], size=12.5, bullet=True,
     after=4)
pages.append(pg)

# 9 ------------------------------------------------------------------------- system
pg = Page(9, 4, "Hệ thống ViHalluLens",
          "Bốn tầng, tầng trên chỉ gọi tầng dưới; dùng qua thư viện Python, dịch vụ REST hoặc Docker",
          "Chương 5, Bảng 5.2, 5.3, Hình 5.2–5.4 · truy xuất BM25: Robertson và Zaragoza (2009) · minh họa "
          "chạy trên GPU Tesla T4 của Kaggle ngày 11/09/2026",
          notes=(
              "Hệ thống gồm bốn tầng, tầng trên chỉ gọi tầng ngay dưới. Tầng trích chú ý cần GPU; ba tầng "
              "còn lại chạy trên CPU trong vài mili giây, nên đặc trưng chỉ phải trích một lần rồi dùng lại "
              "cho nhiều thí nghiệm. Bộ phát hiện đã khớp chỉ là một tệp 11,5 KB; nạp lại và đánh giá 700 "
              "mẫu test cho kết quả trùng 700 trên 700 với lúc thí nghiệm. Có ba cách dùng: gọi thư viện "
              "Python, gọi dịch vụ REST, hoặc chạy cả hệ thống bằng Docker, kèm giao diện web tô màu ngữ "
              "cảnh theo tỷ trọng chú ý. Bộ kiểm thử có 860 ca tự động. Nhóm cũng dựng một hệ RAG minh "
              "họa: Qwen2.5-3B sinh câu trả lời, Qwen2.5-7B đọc lại để phát hiện. Câu trả lời về Hồ Hoàn "
              "Kiếm có một mệnh đề không có trong tài liệu, và hệ thống gán nhãn ngoại lai với điểm rủi ro "
              "0,997."))
sh = pg.sh
layers = [("Tầng 4 · Phục vụ", "serve/", "Dịch vụ REST, giao diện quan sát, hệ RAG minh họa", VIOLET),
          ("Tầng 3 · Bộ phát hiện", "detect/", "Hồi quy logistic, điểm rủi ro, tệp 11,5 KB", RES),
          ("Tầng 2 · Đặc trưng", "features/", "Tỷ lệ lookback và năm đặc trưng hình dạng (CPU)", CTX),
          ("Tầng 1 · Trích chú ý", "extract/", "Mẫu prompt, một lượt đọc, forward hook (GPU)", IUH)]
for i, (h, pkg, b, col) in enumerate(layers):
    y = 1.9 + i * 0.95
    box(sh, 0.55, y, 5.2, 0.82, WHITE, col, 1.75, r=0.08)
    text(sh, 0.75, y + 0.06, 3.4, 0.3, h, size=13.5, bold=True, color=col)
    text(sh, 4.3, y + 0.06, 1.3, 0.3, pkg, size=11, color=MUTED, align=R)
    text(sh, 0.75, y + 0.4, 4.9, 0.36, b, size=12.5)
    if i < 3:
        line(sh, 3.15, y + 0.84, 3.15, y + 0.93, MUTED, 1.25)
g = pg.group()
for k, (ic, h, b) in enumerate([("file-json", "Thư viện Python", "detector.score(...)"),
                                ("server", "Dịch vụ REST", "POST /score, GET /health"),
                                ("layers", "Docker", "docker compose up --build")]):
    y = 5.8 + k * 0.0
    x = 0.55 + k * 1.75
    box(g, x, 5.8, 1.65, 1.0, PAPER2, r=0.08)
    icon(g, ic, x + 0.12, 5.9, 0.3, INK)
    text(g, x + 0.48, 5.88, 1.15, 0.35, h, size=11.5, bold=True, anchor=MID)
    text(g, x + 0.12, 6.27, 1.48, 0.5, b, size=9.5, color=MUTED)
g = pg.group()
box(g, 6.05, 1.9, 6.73, 3.7, INK, r=0.08)
picture(g, HERE / "img" / "web-hero.webp", 6.95, 1.9, h=3.7)
for k, (v, t) in enumerate([("11,5 KB", "tệp bộ phát hiện"), ("700/700", "dự đoán trùng lúc thí "
                                                                         "nghiệm"),
                            ("860", "ca kiểm thử tự động")]):
    x = 6.05 + k * 2.27
    text(g, x, 5.75, 2.15, 0.8, [(v, dict(size=22, bold=True, color=IUH)), (t, dict(size=11.5,
                                                                                    color=MUTED))])
text(g, 6.05, 6.45, 6.73, 0.4, "Minh họa RAG: Qwen2.5-3B sinh câu trả lời có mệnh đề không có căn cứ; "
     "bộ phát hiện gán **ngoại lai**, rủi ro **0,997**.", size=12)
pages.append(pg)

# 10 ------------------------------------------------------------------------ classification
pg = Page(10, 5, "Kết quả phân loại trên ViHallu",
          "Hướng chú ý tương đương PhoBERT tinh chỉnh với vài trăm đến vài nghìn tham số",
          "Bảng 6.1, Hình 6.1, Bảng E.6 · tập test ViHallu 700 mẫu, khoảng tin cậy 95 % bootstrap · "
          "PhoBERT: Nguyen và Nguyen (2020) · XLM-R: Conneau và cộng sự (2020) · LLM giám khảo: Zheng và "
          "cộng sự (2023) · † Gemini đánh giá trên 300/700 mẫu",
          notes=(
              "Đây là kết quả chính trên 700 mẫu test của ViHallu. Đặc trưng bề mặt đạt 0,656. Hai bộ mã "
              "hóa tinh chỉnh đạt 0,749 với PhoBERT và 0,776 với XLM-R. Hướng chú ý đạt 0,745 với lookback "
              "gộp và 0,757 với chunk-aware. Nhóm so hai phương pháp bằng hiệu ghép cặp trên cùng các mẫu: "
              "hai phương pháp chú ý không phân biệt được với PhoBERT; XLM-R cao hơn lookback gộp 0,031, "
              "vừa đủ để phân biệt, nhưng chưa phân biệt được với chunk-aware. Khác biệt lớn nằm ở số tham "
              "số phải huấn luyện: 579 so với 369 triệu. Gemini làm giám khảo chỉ được đánh giá trên 300 "
              "mẫu: 0,753 với tiêu chí đánh giá đầy đủ và 0,664 với tiêu chí rút gọn; trên đúng 300 mẫu đó, "
              "Gemini với tiêu chí đầy đủ không phân biệt được với hướng chú ý. Nhóm cũng chạy lại tiêu chí "
              "rút gọn vào tháng 11 và được 0,708, tức kết quả của Gemini đổi theo thời gian."))
sh = pg.sh
card(sh, 0.55, 1.85, 7.95, 4.95, IUH)
text(sh, 0.8, 1.98, 7.5, 0.3, "Macro-F1 ba lớp và khoảng tin cậy 95 %", size=14, bold=True)
rowsr = [("Đặc trưng bề mặt (E01)", "9 tham số", 0.656, 0.620, 0.689, MUTED),
         ("PhoBERT-large tinh chỉnh", "369 triệu tham số", 0.749, 0.714, 0.778, RES),
         ("XLM-R-large tinh chỉnh", "560 triệu tham số", 0.776, 0.757, 0.818, RES),
         ("Gemini, tiêu chí đầy đủ †", "0 tham số · gọi API", 0.753, 0.702, 0.801, VIOLET),
         ("Lookback gộp (E02)", "2.271 tham số", 0.745, 0.711, 0.776, CTX),
         ("Chunk-aware (E03)", "579 tham số", 0.757, 0.724, 0.789, CTX)]
x0, x1 = 3.3, 7.5
for t in (0.60, 0.65, 0.70, 0.75, 0.80, 0.85):
    xx = x0 + (t - 0.60) / 0.25 * (x1 - x0)
    line(sh, xx, 2.45, xx, 6.25, "E6E1D6", 0.75)
    text(sh, xx - 0.3, 6.28, 0.6, 0.25, vn(t, 2), size=10.5, color=MUTED, align=C)
text(sh, x0, 6.5, x1 - x0, 0.25, "macro-F1 (0,33 là đoán ngẫu nhiên)", size=10.5, color=MUTED, align=C)
for i, (name, par, v, lo, hi, col) in enumerate(rowsr):
    y = 2.7 + i * 0.6
    if name.startswith("Chunk"):
        box(sh, 0.62, y - 0.29, 7.8, 0.58, CTXS, r=0.05)
    text(sh, 0.8, y - 0.27, 2.45, 0.3, name, size=12.5, bold=True, color=INK)
    text(sh, 0.8, y + 0.01, 2.45, 0.26, par, size=10.5, color=MUTED)
    ci_row(sh, x0, x1, 0.60, 0.85, y, v, lo, hi, col, 12.5, vn(v))
g = pg.group()
card(g, 8.75, 1.85, 4.03, 4.95, CTX)
text(g, 9.0, 1.98, 3.6, 0.55, "Hiệu ghép cặp [KTC 95 %]", size=13.5, bold=True,
     color=CTX)
pairs = [("PhoBERT − chunk-aware", "−0,008 [−0,038; +0,022]", "Chưa phân biệt được"),
         ("XLM-R − chunk-aware", "+0,020 [−0,010; +0,050]", "Chưa phân biệt được"),
         ("XLM-R − lookback gộp", "+0,031 [+0,001; +0,061]", "Vừa đủ phân biệt"),
         ("Gemini đầy đủ − chunk-aware", "+0,015 [−0,043; +0,073]", "Chưa phân biệt được (300 mẫu)")]
for i, (h, v, verdict) in enumerate(pairs):
    y = 2.6 + i * 0.83
    line(g, 9.0, y - 0.06, 12.55, y - 0.06, RULE, 0.75)
    text(g, 9.0, y, 3.6, 0.78, [(h, dict(size=12.5, bold=True)), (v, dict(size=12.5)),
                                (verdict, dict(size=11, color=OK if "Chưa" in verdict else RES,
                                               bold=True))])
text(g, 9.0, 5.95, 3.6, 0.82, "Gemini: 0,664 với tiêu chí rút gọn (08/2026); chạy lại tiêu chí đó "
     "tháng 11 được 0,708.", size=11, color=MUTED)
pages.append(pg)

# 11 ------------------------------------------------------------------------ localisation
pg = Page(11, 5, "Kiểm chứng cơ chế: định vị đoạn chứa bằng chứng",
          "Đầu định vị tốt nhất xếp đúng đoạn bằng chứng lên đầu ở 87,8 % số mẫu, hơn cắt bỏ ngữ cảnh",
          "Bảng 6.2, Hình 6.2, 6.9, mục 6.5, 6.8, 6.14.1 · ARC-JSD: Li và cộng sự (2026) · giới hạn của chú "
          "ý như lời giải thích: Jain và Wallace (2019), Wiegreffe và Pinter (2019)",
          notes=(
              "Đây là phép kiểm chứng cơ chế trực tiếp, không qua bộ phân loại. Với mỗi đầu chú ý, nhóm xếp "
              "các đoạn ngữ cảnh theo tỷ trọng chú ý rồi xem đoạn chứa bằng chứng có đứng đầu không. Trên "
              "2.376 mẫu ISE-DSC01, trung bình 22,6 đoạn mỗi ngữ cảnh, đầu định vị tốt nhất đúng 87,8 phần "
              "trăm, gấp 14,3 lần mức ngẫu nhiên. Vì đây là đầu tốt nhất trong 756 đầu, nhóm báo kèm con số "
              "không qua chọn lọc: trung bình cả 756 đầu đạt 33,2 phần trăm, vẫn gấp 5,4 lần ngẫu nhiên. "
              "Kết quả lặp lại trên bộ thứ hai ViWikiFC. Thí nghiệm E19 so với phương pháp cắt bỏ từng đoạn "
              "ARC-JSD trên 300 mẫu: một đầu chú ý đúng 85 phần trăm với một lượt đọc, cắt bỏ đúng 73,3 "
              "phần trăm với trung bình 10,9 lượt. Kết luận chỉ nói về định vị bằng chứng, không chứng minh "
              "mô hình dùng đoạn đó để tạo ra câu trả lời."))
sh = pg.sh
card(sh, 0.55, 1.85, 6.0, 4.95, CTX)
text(sh, 0.8, 1.98, 5.6, 0.3, "Tỷ lệ xếp đúng đoạn bằng chứng lên đầu (hit@1)", size=14, bold=True,
     color=CTX)
sets = [("ISE-DSC01 · 2.376 mẫu, trung bình 22,6 đoạn", [("Đầu định vị tốt nhất", 0.878, CTX),
                                                          ("Trung bình 756 đầu", 0.332, "6FB3B0"),
                                                          ("Chọn ngẫu nhiên", 0.061, MUTED)]),
        ("ViWikiFC (bộ thứ hai) · trung bình 9,8 đoạn", [("Đầu định vị tốt nhất", 0.853, CTX),
                                                          ("Trung bình 756 đầu", 0.329, "6FB3B0"),
                                                          ("Chọn ngẫu nhiên", 0.103, MUTED)])]
for s_i, (title, bars_) in enumerate(sets):
    g = sh if s_i == 0 else pg.group()
    y0 = 2.45 + s_i * 2.05
    text(g, 0.8, y0, 5.5, 0.28, title, size=12, bold=True, color=MUTED)
    for i, (lab, v, col) in enumerate(bars_):
        y = y0 + 0.36 + i * 0.45
        text(g, 0.8, y, 1.95, 0.36, lab, size=12, anchor=MID)
        rect(g, 2.8, y + 0.06, 3.2, 0.26, PAPER2)
        rect(g, 2.8, y + 0.06, 3.2 * v, 0.26, col)
        text(g, 2.85 + 3.2 * v, y, 0.8, 0.36, vn(v * 100, 1) + " %", size=12, bold=True, color=col,
             anchor=MID)
    if s_i == 0:
        text(g, 0.8, y0 + 1.72, 5.5, 0.28, "Gấp 14,3 lần ngẫu nhiên; con số không qua chọn lọc gấp 5,4 "
             "lần", size=11.5, bold=True, color=CTX)
text(pg.groups[-1].shapes if pg.groups else sh, 0.8, 6.35, 5.5, 0.4, "Thứ hạng 756 đầu trên hai bộ có "
     "tương quan Spearman 0,975.", size=11.5, color=MUTED)
g = pg.group()
card(g, 6.8, 1.85, 5.98, 4.95, RES)
text(g, 7.05, 1.98, 5.5, 0.3, "So với cắt bỏ ngữ cảnh (E19, 300 mẫu ViWikiFC)", size=14, bold=True,
     color=RES)
e19 = [("Đầu định vị tốt nhất", 0.850, "1 lượt đọc", CTX),
       ("Đầu chọn trên ISE-DSC01", 0.797, "1 lượt đọc", "6FB3B0"),
       ("Cắt bỏ từng đoạn (ARC-JSD)", 0.733, "10,9 lượt đọc", RES)]
for i, (lab, v, cost, col) in enumerate(e19):
    y = 2.6 + i * 0.75
    text(g, 7.05, y, 2.3, 0.5, lab, size=12.5, anchor=MID)
    rect(g, 9.4, y + 0.1, 2.3, 0.3, PAPER2)
    rect(g, 9.4, y + 0.1, 2.3 * v, 0.3, col)
    text(g, 9.45, y + 0.1, 1.0, 0.3, vn(v * 100, 1) + " %", size=12, bold=True, color=WHITE,
         anchor=MID)
    text(g, 11.75, y, 1.0, 0.5, cost, size=11, color=MUTED, anchor=MID)
text(g, 7.05, 4.95, 5.5, 1.8, [
    "Hiệu ghép cặp +0,117 [+0,077; +0,160]; đầu chọn trên bộ khác vẫn hơn +0,063 [+0,017; +0,110].",
    "Dự đoán ghi trước là cắt bỏ chính xác hơn; kết quả ngược lại.",
    "Kết luận chỉ về định vị bằng chứng, không chứng minh mô hình dùng đoạn đó."], size=12,
     bullet=True, after=3)
pages.append(pg)

# 12 ------------------------------------------------------------------------ intervention, null
pg = Page(12, 5, "Thí nghiệm can thiệp và đóng góp của chunk-aware",
          "Chú ý phản ứng đúng hướng khi mất bằng chứng, nhưng chunk-aware không tăng điểm phân loại",
          "Bảng 6.5, 6.6, E.6, Hình 6.4, 7.1 · 1.836 cặp ViWikiFC · kiểm định dấu hạng Wilcoxon, cỡ ảnh "
          "hưởng rank-biserial: Kerby (2014) · hiệu ghép cặp bootstrap 10.000 lần, hiệu chỉnh Holm",
          notes=(
              "Các kết quả trước mới cho thấy tương quan, nên nhóm làm thí nghiệm can thiệp: cùng một phát "
              "biểu được đọc trên hai ngữ cảnh mười câu chỉ khác nhau ở câu bằng chứng. Trên 1.836 cặp, cả "
              "bốn đặc trưng hình dạng thay đổi đúng hướng đã ghi trước, ở 71 đến 75 phần trăm số cặp, cỡ "
              "ảnh hưởng lớn. Tuy vậy mức thay đổi nhỏ, trung vị chỉ khoảng 0,015. Bên phải là kết quả bất "
              "lợi cho giả thuyết chính H2: hiệu giữa chunk-aware và lookback gộp trong tám cấu hình, mỗi "
              "dòng kèm khoảng tin cậy ghép cặp. Không khoảng nào nằm hẳn về một phía của 0, năm hiệu dương "
              "ba hiệu âm. Nguyên nhân đo được: trên ISE-DSC01, 99,9 phần trăm tín hiệu của đặc trưng hình "
              "dạng đã có sẵn trong tỷ lệ gộp. Như vậy chunk-aware cho biết chú ý tập trung vào đâu, nhưng "
              "không cải thiện phân loại ba lớp."))
sh = pg.sh
card(sh, 0.55, 1.85, 5.6, 4.95, OK)
text(sh, 0.8, 1.98, 5.2, 0.55, "Loại bỏ câu bằng chứng: cặp đổi đúng hướng",
     size=14, bold=True, color=OK)
iv = [("ENT ↑", 0.754, "+0,716"), ("GINI ↓", 0.745, "−0,686"), ("MAX ↓", 0.724, "−0,657"),
      ("GAP ↓", 0.712, "−0,624")]
text(sh, 4.95, 2.55, 1.05, 0.25, "Cỡ ảnh hưởng", size=10.5, color=MUTED, align=R)
for i, (lab, v, r_) in enumerate(iv):
    y = 2.85 + i * 0.55
    text(sh, 0.8, y, 0.9, 0.4, lab, size=13, bold=True, anchor=MID)
    rect(sh, 1.75, y + 0.08, 3.0, 0.26, PAPER2)
    rect(sh, 1.75, y + 0.08, 3.0 * v, 0.26, OK)
    text(sh, 1.8, y + 0.06, 1.0, 0.3, vn(v * 100, 1) + " %", size=11.5, bold=True, color=WHITE,
         anchor=MID)
    text(sh, 4.95, y, 1.05, 0.4, r_, size=12, align=R, anchor=MID)
line(sh, 1.75 + 1.5, 2.75, 1.75 + 1.5, 5.05, MUTED, 1, dash=True)
text(sh, 2.75, 5.05, 1.0, 0.25, "50 %", size=10, color=MUTED, align=C)
text(sh, 0.8, 5.4, 5.2, 1.35, [
    "Hướng ghi trong mã trước khi chạy: **đúng 4/4**.",
    "Độ lớn nhỏ: trung vị thay đổi 0,013–0,016.",
    "Khả năng định vị lặp lại trên bộ thứ hai này."], size=12.5, bullet=True, after=3)
g = pg.group()
card(g, 6.4, 1.85, 6.38, 4.95, BAD)
text(g, 6.65, 1.98, 5.9, 0.3, "Chunk-aware trừ lookback gộp, tám cấu hình", size=14, bold=True,
     color=BAD)
forest = [("ViHallu, Qwen2.5-7B", 0.0116, -0.0233, 0.0453), ("ViHallu, Qwen2.5-3B", -0.0128, -0.0442,
                                                              0.0186),
          ("ViHallu, Qwen2.5-1.5B", 0.0114, -0.0056, 0.0286), ("ViHallu, Sailor2-8B", -0.0258, -0.0570,
                                                                 0.0053),
          ("ISE-DSC01, 29.077 mẫu", 0.0068, -0.0010, 0.0144), ("ISE-DSC01, 5.600 mẫu", 0.0050, -0.0045,
                                                                0.0145),
          ("ViWikiFC", -0.0012, -0.0132, 0.0106), ("ViFactCheck", 0.0226, -0.0029, 0.0478)]
fx0, fx1, lo_v, hi_v = 9.0, 12.55, -0.06, 0.05
zero = fx0 + (0 - lo_v) / (hi_v - lo_v) * (fx1 - fx0)
line(g, zero, 2.42, zero, 5.75, INK, 1.25)
for t in (-0.04, -0.02, 0.02, 0.04):
    xx = fx0 + (t - lo_v) / (hi_v - lo_v) * (fx1 - fx0)
    line(g, xx, 2.42, xx, 5.75, "E6E1D6", 0.75)
    text(g, xx - 0.35, 5.78, 0.7, 0.22, f"{t:+.2f}".replace(".", ","), size=9.5, color=MUTED, align=C)
text(g, zero - 0.2, 5.78, 0.4, 0.22, "0", size=9.5, color=MUTED, align=C)
for i, (lab, v, lo, hi) in enumerate(forest):
    y = 2.6 + i * 0.39
    text(g, 6.65, y - 0.17, 2.3, 0.34, lab, size=11.5, anchor=MID)
    ci_row(g, fx0, fx1, lo_v, hi_v, y, v, lo, hi, CTX if v > 0 else RES)
text(g, 6.65, 6.05, 5.95, 0.7, "Không khoảng tin cậy nào nằm hẳn một phía của 0 (p sau Holm ≥ 0,67). "
     "Trên ISE-DSC01, **99,9 %** tín hiệu hình dạng đã có trong tỷ lệ gộp.", size=12.5)
pages.append(pg)

# 13 ------------------------------------------------------------------------ cost, transfer
pg = Page(13, 5, "Chi phí và khả năng chuyển giao giữa các bộ dữ liệu",
          "Mô hình đọc 3B là điểm cân bằng; quyết định nhị phân chuyển giao được, phân loại ba lớp thì "
          "không",
          "Bảng 6.7, 6.9, 6.10, Hình 6.6, 6.7, Bảng E.5 · thời gian đo xen kẽ trên Tesla T4 · Gemini: tiêu "
          "chí đầy đủ, 300 mẫu · bộ đích được đánh giá trên tập test của nó",
          notes=(
              "Về chi phí, XLM-R tốt hơn cả độ chính xác lẫn tốc độ: 25,2 mili giây mỗi mẫu so với 437,6 "
              "của mô hình đọc 7B. Ưu thế của hướng chú ý là số tham số phải huấn luyện, từ 195 đến 2.271, "
              "và không phải tinh chỉnh mô hình nào. Thu nhỏ mô hình đọc xuống 3B thì nhanh gấp đôi, bộ nhớ "
              "3,7 GB, macro-F1 chỉ giảm khoảng 0,01. Khi chính mô hình 3B vừa sinh vừa đọc lại để tự kiểm "
              "tra, thời gian chỉ tăng 3,6 phần trăm. Gemini mất khoảng 8,2 giây mỗi mẫu. Bên phải là đánh "
              "giá chéo bộ dữ liệu: huấn luyện trên ViHallu rồi đánh giá trên ISE-DSC01, phân loại ba lớp "
              "giảm còn khoảng 0,36 đến 0,43, gần mức ngẫu nhiên; nhưng câu hỏi nhị phân có ảo giác hay "
              "không vẫn đạt 0,63 đến 0,78. Nguyên nhân khả dĩ là hai bộ định nghĩa nhãn ngoại lai khác "
              "nhau."))
sh = pg.sh
rows = [("Phương pháp", "macro-F1", "ms/mẫu", "VRAM (MB)", "Tham số học"),
        ("XLM-R-large", "0,776", "25,2", "11.231", "560 triệu"),
        ("PhoBERT-large", "0,749", "12,3", "9.002", "369 triệu"),
        ("Gemini (tiêu chí đầy đủ) †", "0,753", "8.194", "—", "0"),
        ("Chunk-aware 7B", "0,757", "437,6", "8.328", "579"),
        ("Lookback gộp 7B", "0,745", "437,6", "8.328", "2.271"),
        ("Lookback gộp 3B", "0,735", "222,7", "3.710", "195")]
widths = [2.45, 0.95, 0.95, 1.05, 1.15]
tbl = sh.add_table(len(rows), len(widths), Inches(0.55), Inches(1.88), Inches(sum(widths)),
                   Inches(3.2)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.44)
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.08)
        cell.vertical_anchor = MID
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else OKS if i == 6 else
                                       WHITE if i % 2 else PAPER2)
        p = cell.text_frame.paragraphs[0]
        p.alignment = L if j == 0 else R
        _run(p, v, 12.5, WHITE if i == 0 else INK, i == 0 or i == 6, False)
g = pg.group()
box(g, 0.55, 5.1, 6.55, 1.7, OKS, r=0.1)
text(g, 0.75, 5.18, 6.2, 1.55, [
    ("Tự kiểm tra: mô hình 3B vừa sinh vừa đọc lại", dict(size=13, bold=True, color=OK)),
    ("Đọc lại một lượt thêm 239 ms, **+3,6 %** thời gian sinh (100 mẫu); đọc chú ý ngay khi sinh "
     "tốn hơn (+18,0 %).", dict(size=12.5)),
    ("Ưu thế của hướng chú ý: 195–2.271 tham số, không tinh chỉnh mô hình, dữ liệu không rời hệ thống.",
     dict(size=12.5))], after=3)
g = pg.group()
card(g, 7.35, 1.85, 5.43, 4.95, IUH)
text(g, 7.6, 1.98, 5.0, 0.3, "Huấn luyện trên bộ này, đánh giá trên bộ kia", size=14, bold=True,
     color=IUH)
cd = CategoryChartData()
cd.categories = ["ViHallu → ISE\nlookback", "ViHallu → ISE\nchunk-aware", "ISE → ViHallu\nlookback",
                 "ISE → ViHallu\nchunk-aware"]
cd.add_series("Ba lớp", (0.430, 0.358, 0.554, 0.552))
cd.add_series("Nhị phân", (0.631, 0.664, 0.784, 0.776))
ch = g.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(7.5), Inches(2.35), Inches(5.15),
                 Inches(3.55), cd).chart
ch.has_legend = True
ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False
ch.legend.font.size, ch.legend.font.name = Pt(11), FONT
ch.font.size, ch.font.name = Pt(10.5), FONT
va = ch.value_axis
va.minimum_scale, va.maximum_scale = 0, 0.9
va.has_major_gridlines = False
va.visible = False
ch.category_axis.tick_labels.font.size = Pt(10)
ch.category_axis.format.line.color.rgb = rgb(RULE)
pl = ch.plots[0]
pl.gap_width, pl.overlap = 60, -10
pl.has_data_labels = True
dl = pl.data_labels
dl.font.size, dl.font.bold, dl.font.name = Pt(10.5), True, FONT
dl.number_format, dl.number_format_is_linked = "0.000", False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
for ser, col in zip(pl.series, (RES, CTX), strict=True):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
    for pt, v in zip(ser.points, ser.values, strict=True):
        tf = pt.data_label.text_frame
        tf.text = vn(v)
        r0 = tf.paragraphs[0].runs[0]
        r0.font.size, r0.font.bold, r0.font.name = Pt(10.5), True, FONT
        pt.data_label.position = XL_LABEL_POSITION.OUTSIDE_END
text(g, 7.6, 5.95, 5.0, 0.8, "Ba lớp giảm 0,19–0,43 so với huấn luyện trên chính bộ đích; nhị phân "
     "vẫn đạt 0,63–0,78. Hai bộ định nghĩa nhãn ngoại lai khác nhau.", size=12)
pages.append(pg)

# 14 ------------------------------------------------------------------------ self-assessment
pg = Page(14, 6, "Tự đánh giá: giả thuyết, kết quả đạt được và hạn chế",
          "Ba giả thuyết được ủng hộ; giả thuyết chính về chunk-aware không được ủng hộ",
          "Bảng 1.1, 7.1, Chương 7, mục 8.1–8.3 · dự đoán chính được ghi vào kho mã nguồn trước khi chạy "
          "thí nghiệm",
          notes=(
              "Nhóm em tự đánh giá theo năm giả thuyết. H1 được ủng hộ: tỷ lệ lookback gộp đạt 0,745, cao "
              "hơn đặc trưng bề mặt và tương đương PhoBERT. H2, giả thuyết chính về chunk-aware, không được "
              "ủng hộ: cả tám khoảng tin cậy ghép cặp đều chứa 0. H3 được ủng hộ: định vị đúng 87,8 phần "
              "trăm và chính xác hơn cắt bỏ ngữ cảnh. H4 được ủng hộ về hướng, độ lớn nhỏ. H5 bị bác bỏ ở "
              "bài toán ba lớp, được ủng hộ một phần ở bài toán nhị phân. Về kết quả, nhóm có một bộ phát "
              "hiện tương đương bộ mã hóa với vài trăm tham số, bằng chứng cơ chế, và một hệ thống vận hành "
              "được. Hạn chế: chunk-aware không tăng điểm, ba lớp không chuyển giao, nhãn chỉ có ở mức cả "
              "câu trả lời. Hướng phát triển là phát hiện theo từng đoạn của câu trả lời, kết hợp chú ý với "
              "bộ mã hóa, và chỉ tính các hàng chú ý của phản hồi để đọc ngữ cảnh dài hơn."))
sh = pg.sh
hyp = [("H1", "Lookback gộp cao hơn đặc trưng bề mặt, tương đương bộ mã hóa",
        "0,745 so với 0,656; tương đương PhoBERT 0,749", "Được ủng hộ", OK),
       ("H2", "Chunk-aware tăng macro-F1, tăng nhiều hơn trên ngữ cảnh dài",
        "8/8 khoảng tin cậy chứa 0; 99,9 % tín hiệu trùng tỷ lệ gộp", "Không được ủng hộ", BAD),
       ("H3", "Chú ý xác định đúng đoạn chứa bằng chứng",
        "87,8 %, gấp 14,3 lần ngẫu nhiên; hơn cắt bỏ ngữ cảnh", "Được ủng hộ", OK),
       ("H4", "Mất bằng chứng thì chú ý phân tán hơn",
        "4/4 hướng đúng ở 71–75 % số cặp; độ lớn nhỏ", "Ủng hộ về hướng", WARN),
       ("H5", "Giữ hiệu năng khi đổi bộ dữ liệu",
        "Ba lớp giảm 0,19–0,43; nhị phân 0,63–0,78", "Bác bỏ ở ba lớp", WARN)]
for i, (h, s, e, v, col) in enumerate(hyp):
    y = 1.85 + i * 0.5
    box(sh, 0.55, y, 12.23, 0.44, WHITE if i % 2 == 0 else PAPER2, r=0.05)
    box(sh, 0.65, y + 0.05, 0.34, 0.34, INK, shape=MSO_SHAPE.OVAL)
    text(sh, 0.65, y + 0.05, 0.34, 0.34, h, size=10.5, bold=True, color=WHITE, align=C, anchor=MID)
    text(sh, 1.12, y, 5.0, 0.44, s, size=12.5, bold=True, anchor=MID)
    text(sh, 6.2, y, 4.35, 0.44, e, size=12, color=MUTED, anchor=MID)
    pill(sh, 10.65, y + 0.06, 2.05, 0.32, v, col, size=11)
cols3 = [("Kết quả đạt được", "circle-check", OK, [
    "Bộ phát hiện ba lớp 0,757 với 579 tham số, tương đương PhoBERT",
    "Định vị bằng chứng 87,8 %, hơn cắt bỏ ngữ cảnh với một lượt đọc",
    "Hệ thống: thư viện, REST, Docker, giao diện; 860 ca kiểm thử"]),
         ("Hạn chế", "triangle-alert", BAD, [
             "Chunk-aware không tăng điểm phân loại",
             "Ba lớp không chuyển giao sang bộ dữ liệu khác",
             "Nhãn chỉ ở mức cả câu trả lời; tự kiểm tra chưa đo độ chính xác"]),
         ("Hướng phát triển", "rocket", CTX, [
             "Phát hiện theo từng đoạn câu trả lời, với nhãn mức đoạn",
             "Kết hợp chú ý (tốt ở nội tại) với bộ mã hóa (tốt ở ngoại lai)",
             "Chỉ tính hàng chú ý của phản hồi để đọc ngữ cảnh dài hơn"])]
for k, (h, ic, col, items) in enumerate(cols3):
    g = pg.group()
    x = 0.55 + k * 4.14
    card(g, x, 4.45, 3.95, 2.38, col)
    icon(g, ic, x + 0.18, 4.62, 0.32, col)
    text(g, x + 0.6, 4.6, 3.2, 0.36, h, size=14, bold=True, color=col, anchor=MID)
    text(g, x + 0.2, 5.05, 3.62, 1.75, items, size=12.5, bullet=True, after=4)
pages.append(pg)

# 15 ------------------------------------------------------------------------ references
pg = Page(15, 6, "Tài liệu tham khảo chính",
          "Các công trình đề tài trực tiếp dựa vào; số trong ngoặc theo danh mục 28 tài liệu của quyển",
          "Danh mục đầy đủ ở cuối quyển khóa luận",
          notes=(
              "Đây là các công trình chính mà đề tài dựa vào, đánh số theo danh mục 28 tài liệu của quyển. "
              "Phương pháp nền là Lookback Lens, xây trên cơ chế chú ý của Transformer; ReDeEP và Ogasa và "
              "Arase là hai hướng gần nhất cùng dùng tín hiệu nội tại; ContextCite và ARC-JSD là hướng cắt "
              "bỏ ngữ cảnh mà nhóm đối chiếu ở E19. Dữ liệu gồm ViHallu, ISE-DSC01, ViWikiFC và ViFactCheck. "
              "Các phương pháp so sánh là PhoBERT, XLM-R và LLM giám khảo; SemViQA là kết quả đã công bố "
              "trên ViWikiFC. Mô hình đọc là Qwen2.5."))
sh = pg.sh
refs = [("Phương pháp nền và hướng liên quan", CTX, [
    ("[2]", "Chuang và cộng sự (2024). Lookback Lens. ", "EMNLP 2024"),
    ("[26]", "Vaswani và cộng sự (2017). Attention Is All You Need. ", "NeurIPS 30"),
    ("[20]", "Sun và cộng sự (2025). ReDeEP. ", "ICLR 2025"),
    ("[17]", "Ogasa, Arase (2025). Multi-View Attention Features. ", "arXiv"),
    ("[3]", "Cohen-Wang và cộng sự (2024). ContextCite. ", "NeurIPS 37"),
    ("[13]", "Li và cộng sự (2026). ARC-JSD. ", "ICLR 2026")]),
        ("Dữ liệu", RES, [
            ("[15]", "Nguyen và cộng sự (2026). ViHallu Challenge. ", "arXiv:2601.04711"),
            ("[24]", "UIT Data Science Challenge 2023 (bộ ISE-DSC01).", ""),
            ("[11]", "Le và cộng sự (2024). ViWikiFC. ", "arXiv:2405.07615"),
            ("[23]", "Tran và cộng sự (2025). ViFactCheck. ", "AAAI 2025")]),
        ("Phương pháp so sánh", VIOLET, [
            ("[16]", "Nguyen, Nguyen (2020). PhoBERT. ", "Findings of EMNLP 2020"),
            ("[4]", "Conneau và cộng sự (2020). XLM-R. ", "ACL 2020"),
            ("[28]", "Zheng và cộng sự (2023). LLM-as-a-Judge. ", "NeurIPS 36"),
            ("[22]", "Tran và cộng sự (2025). SemViQA. ", "arXiv:2503.00955")]),
        ("Mô hình và nền tảng", IUH, [
            ("[18]", "Qwen Team (2024). Qwen2.5 Technical Report. ", "arXiv:2412.15115"),
            ("[12]", "Lewis và cộng sự (2020). Retrieval-Augmented Generation. ", "NeurIPS 33"),
            ("[9]", "Ji và cộng sự (2023). Survey of Hallucination in NLG. ", "ACM CSUR")])]
pos = [(0.55, 1.9), (0.55, 4.6), (6.8, 1.9), (6.8, 4.15)]
for (h, col, items), (x, y) in zip(refs, pos, strict=True):
    g = sh if h.startswith("Phương pháp nền") else pg.group()
    text(g, x, y, 5.9, 0.3, h.upper(), size=12, bold=True, color=col)
    for i, (n, body, venue) in enumerate(items):
        yy = y + 0.38 + i * 0.36
        text(g, x, yy, 0.55, 0.32, n, size=12.5, bold=True, color=col)
        tb = text(g, x + 0.58, yy, 5.4, 0.32, body, size=12.5)
        if venue:
            _run(tb.text_frame.paragraphs[0], venue, 12.5, MUTED, False, True)
pages.append(pg)

# 16 ------------------------------------------------------------------------ thanks
pg = Page(16, chrome=False, notes=(
    "Nhóm em xin chân thành cảm ơn quý thầy cô đã lắng nghe, và rất mong nhận được câu hỏi cùng góp ý "
    "của Hội đồng."))
sh = pg.sh
rect(sh, 0, 0, 13.333, 0.11, IUH)
rect(sh, 0, 0.11, 13.333, 0.045, GOLD)
rect(sh, 0, 7.345, 13.333, 0.045, GOLD)
rect(sh, 0, 7.39, 13.333, 0.11, IUH)
picture(sh, HERE / "img" / "owl-prof-wave.webp", 8.6, 0.85, h=6.5)
picture(sh, HERE / "img" / "logo.svg", 0.8, 0.6, h=0.75)
text(sh, 0.8, 2.2, 7.6, 1.6, [("Nhóm em xin chân thành cảm ơn", dict(size=34, bold=True)),
                              ("quý thầy cô đã lắng nghe", dict(size=34, bold=True, color=CTX,
                                                                italic=True))])
text(sh, 0.8, 4.0, 7.6, 0.45, "Rất mong nhận được câu hỏi và góp ý của Hội đồng", size=20,
     color=MUTED)
text(sh, 0.8, 5.25, 7.6, 1.2, [("Nguyễn Ngọc Lân · Nguyễn Tấn Minh", dict(size=17, bold=True)),
                               ("Giảng viên hướng dẫn: ThS. Trương Vĩnh Linh", dict(size=14,
                                                                                   color=MUTED)),
                               ("Mã nguồn: github.com/wsunicorn/vihallulens", dict(size=14,
                                                                                   color=MUTED))])
pages.append(pg)

assert len(pages) == TOTAL
for pg in pages:
    pg.finish()
cp = prs.core_properties
cp.author = cp.last_modified_by = "Nguyễn Ngọc Lân, Nguyễn Tấn Minh"
cp.title = "Phát hiện ảo giác cho RAG tiếng Việt dựa trên tín hiệu chú ý nội tại"
cp.subject = cp.keywords = cp.comments = ""
prs.save(OUT)
print(OUT, len(prs.slides), "trang")

if "--pdf" in sys.argv:
    import win32com.client
    app = win32com.client.DispatchEx("PowerPoint.Application")
    pres = app.Presentations.Open(str(OUT), True, False, False)
    pres.SaveAs(str(OUT.with_suffix(".pdf")), 32)
    pres.Close()
    app.Quit()
    print(OUT.with_suffix(".pdf"))
if SUBMIT.is_dir():
    for out in (OUT, OUT.with_suffix(".pdf")):
        if out.exists():
            shutil.copy2(out, SUBMIT / (SUBMIT_NAME + out.suffix))
