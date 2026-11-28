"""Committee deck -> docs/slides/slide_hoi_dong.pptx (+ .pdf): 18 pages and a thank-you page.

Follows the chapters of the thesis, as the advisor asked (05/10 and 28/11/2026): a talk of about
ten minutes in 10-20 slides, the works each slide relies on named in its footer. Built like the
internship deck: native shapes, tables and charts that PowerPoint can edit, Times New Roman,
a one-sentence takeaway under every title, part numbers and a part bar, fade transitions,
one click per group, speaker notes. Every number comes from the thesis.

    uv run --no-project --with python-pptx==1.0.2 --with cairosvg==2.7.1 --with pillow \\
        --with pywin32==308 python docs/slides/nguon/dung_slide.py [--pdf]

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
OUT = DECK_DIR / "slide_hoi_dong.pptx"
SUBMIT = DECK_DIR.parents[1] / "UniversityRequirements" / "Reports"
SUBMIT_NAME = "Slide_KLTN_22635801_22643511_PhatHienAoGiac"

FONT = "Times New Roman"
INK, MUTED, RULE, PAPER, PAPER2, WHITE = "18202E", "5E6675", "D9D3C7", "FAF8F3", "F2EEE5", "FFFFFF"
CTX, CTXS, RES, RESS = "0F7C7C", "D7ECEA", "C27612", "F6E6CC"
OK, OKS, WARN, WARNS, BAD, BADS = "2F8A55", "DCEFE2", "B7860B", "F5EACB", "C0412D", "F6DDD7"
IUH, GOLD, VIOLET, VIOLS = "153898", "F9B200", "6B4FA0", "E9E3F3"
PARTS = ["Giới thiệu", "Cơ sở lý thuyết", "Dữ liệu", "Phương pháp", "Hệ thống", "Thực nghiệm",
         "Thảo luận", "Kết luận"]
TOTAL = 19
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
        text(sh, 1.75, 0.27, 2.8, 0.3, "Báo cáo khóa luận tốt nghiệp", size=13, color=MUTED)
        nav = sh.add_textbox(Inches(4.45), Inches(0.27), Inches(8.33), Inches(0.3))
        tf = nav.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = R
        for k, name in enumerate(PARTS):
            _run(p, name + ("   " if k < len(PARTS) - 1 else ""), 12,
                 IUH if k == part else "8A8F99", k == part, False)
        line(sh, 0.55, 0.72, 12.78, 0.72, RULE, 1)
        text(sh, 0.55, 0.8, 0.85, 0.62, f"{part + 1:02d}", size=34, bold=True, color=IUH, anchor=MID)
        rect(sh, 1.38, 0.88, 0.05, 0.5, GOLD)
        text(sh, 1.55, 0.78, 11.2, 0.5, title, size=28, bold=True, color=INK, anchor=MID)
        text(sh, 1.55, 1.27, 11.2, 0.38, takeaway, size=17, color=CTX, anchor=MID)
        line(sh, 0.55, 7.0, 12.78, 7.0, RULE, 0.75)
        text(sh, 0.55, 7.04, 11.3, 0.4, source, size=11.5, color=MUTED)
        text(sh, 11.9, 7.05, 0.88, 0.3, f"{self.n}/{TOTAL}", size=12, color=MUTED, align=R)

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


NOTES = {
    1: 'Kính chào quý thầy cô. Nhóm em gồm Nguyễn Ngọc Lân và Nguyễn Tấn Minh, dưới sự hướng dẫn của ThS. Trương Vĩnh Linh. Đề tài của nhóm là phát hiện ảo giác cho hệ tăng cường truy xuất tiếng Việt, dựa trên tín hiệu chú ý bên trong mô hình ngôn ngữ.',
    2: 'Hệ RAG tìm tài liệu rồi để mô hình ngôn ngữ trả lời dựa trên tài liệu đó, nhưng câu trả lời vẫn có thể sai theo hai cách. Ảo giác nội tại nói sai điều tài liệu có, như đổi triều Lý thành triều Trần. Ảo giác ngoại lai đưa vào điều tài liệu không nhắc tới, như tháp Eiffel ở hồ Tây. Bên phải là điểm rủi ro hệ thống của nhóm tính cho ba câu.',
    3: 'Bài toán: từ ngữ cảnh, câu hỏi và câu trả lời của bất kỳ hệ RAG nào, xác định một trong ba nhãn. Các cách hiện có đều có hạn chế: mô hình giám khảo chậm và phải gửi dữ liệu ra ngoài, bộ mã hóa phải huấn luyện hàng trăm triệu tham số, đặc trưng bề mặt chỉ đo độ dài và mức trùng từ. Đề tài dùng tín hiệu có sẵn trong lượt đọc của mô hình, với bốn ràng buộc ở dưới.',
    4: 'Nhóm xác định ba khoảng trống: chưa tách chú ý theo từng đoạn tài liệu, chưa so ba hướng tiếp cận trên cùng dữ liệu theo cả độ chính xác lẫn chi phí, và chưa có công trình nào cho tiếng Việt. Từ đó có ba câu hỏi nghiên cứu, kiểm chứng bằng năm giả thuyết từ H1 đến H5.',
    5: 'Bảng này so các hướng đã có theo phần phải huấn luyện, chi phí mỗi lần dùng và hạn chế. Khóa luận thuộc hướng dùng trọng số chú ý, cùng nhánh với Lookback Lens và ReDeEP: chỉ cần một lượt đọc và một bộ phân loại tuyến tính, đổi lại phải dùng mô hình mã nguồn mở.',
    6: 'Phương pháp nền là Lookback Lens. Mỗi đầu chú ý phân bổ chú ý cho tài liệu và cho phần câu trả lời đã viết trước. Tỷ lệ lookback so sánh hai phần đó; trong ví dụ là khoảng 62 phần trăm. Mô hình Qwen2.5-7B cho 756 tỷ lệ như vậy, và một hồi quy logistic dùng chúng để phân loại.',
    7: 'Nhóm dùng bốn bộ dữ liệu tiếng Việt. ViHallu là bộ chính, có câu trả lời do GPT-4o sinh và nhãn ba lớp. ISE-DSC01 có ngữ cảnh dài và đánh dấu sẵn câu bằng chứng. Điểm quan trọng là chia tập theo tài liệu, để tài liệu của tập kiểm tra không xuất hiện lúc huấn luyện.',
    8: 'Đây là đóng góp chính. Hai câu trả lời có thể cùng dành 62 phần trăm chú ý cho tài liệu: câu A tập trung vào câu chứa thông tin, câu B trải đều. Lookback Lens không phân biệt được. Chunk-aware tính tỷ trọng chú ý của từng câu rồi mô tả hình dạng phân bố bằng năm đặc trưng ở bên phải.',
    9: 'Quy trình chỉ cần một lượt đọc: ghép đầu vào, mô hình đọc một lượt, lấy 192 đặc trưng, rồi hồi quy logistic cho nhãn và điểm rủi ro. Giữ ma trận chú ý của cả 28 lớp cần khoảng 26 GB, vượt GPU 16 GB. Forward hook tính đặc trưng ngay tại mỗi lớp rồi bỏ ma trận, nên chỉ cần 8,4 GB.',
    10: 'Hệ thống có bốn tầng, chỉ tầng trích chú ý cần GPU. Bộ phát hiện là một tệp 11,5 KB, nạp lại cho kết quả trùng 700 trên 700 mẫu. Hệ thống dùng được qua thư viện Python, dịch vụ REST hoặc Docker. Trong minh họa, câu trả lời có mệnh đề không có căn cứ được gán ngoại lai, rủi ro 0,997.',
    11: 'Trên 700 mẫu kiểm tra, hướng chú ý đạt 0,745 và 0,757, không khác biệt rõ với PhoBERT 0,749, trong khi chỉ huấn luyện 579 tham số so với 369 triệu. XLM-R cao nhất, 0,776. Gemini làm giám khảo, trên 300 mẫu, đạt 0,753 và cũng không khác biệt rõ với hướng chú ý.',
    12: 'Ở đây nhóm kiểm tra trực tiếp chú ý. Trên ISE-DSC01, đầu chú ý tốt nhất xếp đúng câu bằng chứng lên đầu ở 87,8 phần trăm số mẫu, gấp 14 lần chọn ngẫu nhiên. So với phương pháp cắt bỏ từng đoạn, một đầu chú ý chính xác hơn mà chỉ cần một lượt đọc thay vì gần 11 lượt.',
    13: 'Để kiểm tra quan hệ trực tiếp, nhóm đọc cùng một phát biểu trên hai tài liệu chỉ khác câu bằng chứng. Trên 1.836 cặp, cả bốn đặc trưng thay đổi đúng hướng đã dự đoán trước, ở 71 đến 75 phần trăm số cặp. Tuy nhiên mức thay đổi nhỏ.',
    14: 'Hướng chú ý chỉ cần huấn luyện vài trăm đến vài nghìn tham số. Mô hình đọc 3B nhanh gấp đôi mà điểm chỉ giảm khoảng 0,01. Khi tự kiểm tra câu trả lời của chính mình, thời gian chỉ tăng 3,6 phần trăm. Trên bộ dữ liệu khác, phân loại ba lớp giảm mạnh, nhưng câu hỏi có ảo giác hay không vẫn dùng được.',
    15: 'Giả thuyết chính H2 không được ủng hộ: trong tám cấu hình, không khoảng tin cậy nào nằm hẳn về một phía của 0. Lý do là 99,9 phần trăm tín hiệu của đặc trưng hình dạng đã có trong tỷ lệ gộp. Chú ý cho biết mô hình dựa vào đoạn nào, nhưng không cho biết câu trả lời nói đúng hay sai về đoạn đó.',
    16: 'Tóm lại, H1 và H3 được ủng hộ, H4 được ủng hộ về hướng, H2 không được ủng hộ, H5 chỉ đúng ở bài toán có ảo giác hay không.',
    17: 'Kết quả chính là một bộ phát hiện rất nhỏ nhưng tương đương bộ mã hóa, bằng chứng chú ý chỉ đúng đoạn chứa bằng chứng, và một hệ thống vận hành được. Hướng tiếp theo là phát hiện theo từng đoạn của câu trả lời và kết hợp chú ý với bộ mã hóa.',
    18: 'Đây là các công trình chính mà đề tài dựa vào.',
    19: 'Nhóm em xin cảm ơn quý thầy cô đã lắng nghe, và mong nhận được câu hỏi cùng góp ý của Hội đồng.',
}

pages = []

# 1 ------------------------------------------------------------------------- cover
pg = Page(1, chrome=False, notes=NOTES[1])
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
    text(sh, x + 0.18, 5.27, 2.35, 1.0, [(role, dict(size=12.5, color=MUTED, bold=True)),
                                         (name, dict(size=16.5, bold=True)),
                                         (sub, dict(size=13.5, color=MUTED))])
text(sh, 0.8, 6.75, 6, 0.35, "Thành phố Hồ Chí Minh, tháng 12 năm 2026", size=14.5, color=MUTED)
pages.append(pg)

# 2 ------------------------------------------------------------------------- Ch1: three classes
pg = Page(2, 0, "Ảo giác trong hệ tăng cường truy xuất (RAG)",
          "Câu trả lời có thể trung thực, mâu thuẫn với tài liệu, hoặc chứa thông tin tài liệu không có",
          "Mục 1.1, 2.3 · phân loại ảo giác: Ji và cộng sự (2023), Maynez và cộng sự (2020) · hệ nhãn ba "
          "lớp theo ViHallu: Nguyen và cộng sự (2026) · điểm rủi ro do hệ thống của khóa luận tính",
          notes=NOTES[2])
sh = pg.sh
card(sh, 0.55, 1.85, 4.75, 4.95, CTX)
text(sh, 0.8, 2.02, 4.3, 0.34, "Tài liệu được truy xuất (ngữ cảnh)", size=16, bold=True, color=CTX)
ctx = ["Hà Nội là thủ đô của Việt Nam, nằm bên bờ sông Hồng.",
       "Thành phố có lịch sử hơn một nghìn năm, từng mang tên Thăng Long dưới triều Lý.",
       "Dân số nội thành khoảng tám triệu người.",
       "Khí hậu Hà Nội có bốn mùa rõ rệt, mùa đông có thể xuống dưới mười độ."]
for i, s in enumerate(ctx):
    y = 2.5 + i * 1.05
    box(sh, 0.8, y, 4.3, 0.95, CTXS, r=0.06)
    text(sh, 0.95, y + 0.06, 1.0, 0.25, f"Câu {i + 1}", size=13, bold=True, color=CTX)
    text(sh, 0.95, y + 0.31, 4.05, 0.62, s, size=15)
resp = [("TRUNG THỰC", OK, "Hà Nội từng mang tên Thăng Long dưới triều **Lý**.",
         "Mọi ý đều có trong tài liệu (câu 2)", "0,001"),
        ("ẢO GIÁC NỘI TẠI", WARN, "Hà Nội từng mang tên Thăng Long dưới triều **Trần**, khi dân số đã "
         "lên tới **hai mươi triệu** người.", "Dùng câu 2, câu 3 nhưng nói trái với tài liệu", "0,998"),
        ("ẢO GIÁC NGOẠI LAI", BAD, "Hà Nội nổi tiếng với **tháp Eiffel thu nhỏ ở hồ Tây** và **tuyến "
         "tàu điện ngầm dài nhất Đông Nam Á**.", "Tài liệu không nhắc tới, không có căn cứ", "1,000")]
for i, (lab, col, s, why, risk) in enumerate(resp):
    g = sh if i == 0 else pg.group()
    y = 1.85 + i * 1.68
    box(g, 5.55, y, 7.23, 1.55, WHITE, RULE, 1.25, r=0.1)
    rect(g, 5.55, y + 0.06, 0.08, 1.43, col)
    pill(g, 5.8, y + 0.13, 2.4, 0.36, lab, col, size=13.5)
    text(g, 5.8, y + 0.58, 5.4, 0.62, s, size=16)
    text(g, 5.8, y + 1.13, 5.4, 0.32, why, size=14.5, bold=True, color=col)
    text(g, 11.05, y + 0.14, 1.55, 0.3, "Điểm rủi ro", size=13.5, color=MUTED, align=R)
    text(g, 10.95, y + 0.47, 1.65, 0.6, risk, size=30, bold=True, color=col, align=R)
pages.append(pg)

# 3 ------------------------------------------------------------------------- Ch1: problem, motivation
pg = Page(3, 0, "Phát biểu bài toán và động lực nghiên cứu",
          "Xác định nhãn của câu trả lời từ chính lượt đọc của một mô hình ngôn ngữ, không cần mô hình "
          "giám khảo",
          "Mục 1.2, 1.4 · LLM giám khảo: Zheng và cộng sự (2023) · PhoBERT: Nguyen và Nguyen (2020) · XLM-R: "
          "Conneau và cộng sự (2020) · số liệu chi phí ở Bảng 6.9",
          notes=NOTES[3])
sh = pg.sh
flow = [("Đầu vào", "Ngữ cảnh, câu hỏi và câu trả lời của bất kỳ hệ RAG nào"),
        ("Bộ phát hiện", "Mô hình ngôn ngữ mã nguồn mở đọc một lượt; chỉ một bộ phân loại tuyến tính "
                         "cần huấn luyện"),
        ("Đầu ra", "Nhãn ba lớp, điểm rủi ro và mức chú ý dành cho từng đoạn ngữ cảnh")]
for k, (h, b) in enumerate(flow):
    x = 0.55 + k * 4.12
    box(sh, x, 1.88, 3.85, 1.3, CTXS if k == 1 else WHITE, CTX if k == 1 else RULE, 1.5, r=0.1)
    text(sh, x + 0.2, 1.93, 3.5, 1.2, [(h, dict(size=17, bold=True, color=CTX)), (b, dict(size=15.5))],
         anchor=MID)
    if k < 2:
        line(sh, x + 3.88, 2.53, x + 4.09, 2.53, CTX, 2.25, head=True)
g = pg.group()
text(g, 0.55, 3.4, 12, 0.35, "Hạn chế của các cách làm hiện có", size=16, bold=True)
for k, (ic, h, b, note) in enumerate([
        ("users", "Mô hình ngôn ngữ làm giám khảo", "Mỗi câu trả lời mất khoảng 8,2 giây; dữ liệu phải "
         "gửi ra ngoài hệ thống", "Không cần huấn luyện"),
        ("cpu", "Tinh chỉnh bộ mã hóa", "Phải huấn luyện 369–560 triệu tham số trên dữ liệu có nhãn",
         "Chính xác nhất"),
        ("ruler", "Đặc trưng bề mặt", "Chỉ đo độ dài câu trả lời và mức trùng từ với tài liệu",
         "Gần như không tốn chi phí")]):
    x = 0.55 + k * 4.12
    box(g, x, 3.85, 3.85, 1.8, WHITE, RULE, 1.25, r=0.1)
    icon(g, ic, x + 0.2, 4.0, 0.42, BAD)
    text(g, x + 0.75, 3.98, 3.0, 0.46, h, size=16, bold=True, anchor=MID)
    text(g, x + 0.2, 4.52, 3.55, 0.75, b, size=15)
    text(g, x + 0.2, 5.22, 3.5, 0.35, "Ưu điểm: " + note[0].lower() + note[1:], size=14, color=OK, bold=True)
g = pg.group()
text(g, 0.55, 5.74, 12, 0.32, "Yêu cầu đặt ra cho đề tài", size=16, bold=True)
for k, (ic, t) in enumerate([("users", "Không gọi mô hình giám khảo"), ("lock", "Không tinh chỉnh mô "
                             "hình ngôn ngữ"), ("cpu", "Chạy trên GPU 16 GB"),
                             ("flag", "Tiếng Việt, ba lớp nhãn")]):
    x = 0.55 + k * 3.09
    box(g, x, 6.12, 2.95, 0.68, INK, r=0.12)
    icon(g, ic, x + 0.16, 6.28, 0.36, WHITE)
    text(g, x + 0.62, 6.12, 2.28, 0.68, t, size=14.5, bold=True, color=WHITE, anchor=MID)
pages.append(pg)

# 4 ------------------------------------------------------------------------- Ch1: gaps, questions
pg = Page(4, 0, "Khoảng trống, câu hỏi và giả thuyết nghiên cứu",
          "Ba khoảng trống dẫn tới ba câu hỏi nghiên cứu, được kiểm chứng bằng năm giả thuyết",
          "Mục 1.2–1.3, Bảng 1.1 · Lookback Lens: Chuang và cộng sự (2024) · ViHallu: Nguyen và cộng sự "
          "(2026) · các dự đoán chính được ghi vào kho mã nguồn trước khi chạy thí nghiệm",
          notes=NOTES[4])
sh = pg.sh
cols = [(CTX, "search", "Khoảng trống về phương pháp", "Chưa tách mức chú ý theo từng đoạn ngữ cảnh và "
         "đối chiếu với vị trí của bằng chứng", "Câu hỏi 1", "Tách chú ý theo từng đoạn có giúp phát hiện "
         "tốt hơn, và chú ý có tập trung đúng vào đoạn chứa bằng chứng không?", "H2, H3, H4"),
        (RES, "scale", "Khoảng trống về đánh giá", "Ba hướng tiếp cận chưa được so trên cùng dữ liệu, theo "
         "cả độ chính xác lẫn chi phí", "Câu hỏi 2", "So với tinh chỉnh bộ mã hóa và mô hình giám khảo, "
         "hướng này đạt độ chính xác và tốn chi phí bao nhiêu?", "H1 và phép đo chi phí"),
        (VIOLET, "flag", "Khoảng trống về ngôn ngữ", "Chưa có công trình dùng tín hiệu bên trong mô hình "
         "để phát hiện ảo giác tiếng Việt", "Câu hỏi 3", "Tín hiệu chú ý đóng góp thêm bao nhiêu, và có "
         "dùng được trên bộ dữ liệu khác không?", "H1, H5")]
for k, (col, ic, gk, gs, qk, qs, hs) in enumerate(cols):
    g = sh if k == 0 else pg.group()
    x = 0.55 + k * 4.14
    card(g, x, 1.88, 3.95, 2.0, col)
    icon(g, ic, x + 0.22, 2.1, 0.42, col)
    text(g, x + 0.78, 2.08, 3.05, 0.46, gk, size=15, bold=True, color=col, anchor=MID)
    text(g, x + 0.22, 2.62, 3.6, 1.2, gs, size=16)
    line(g, x + 1.975, 3.95, x + 1.975, 4.3, col, 2.5, head=True)
    box(g, x, 4.38, 3.95, 2.42, WHITE, col, 2, r=0.1)
    text(g, x + 0.22, 4.5, 3.55, 0.34, qk, size=15, bold=True, color=col)
    text(g, x + 0.22, 4.86, 3.6, 1.4, qs, size=16.5)
    text(g, x + 0.22, 6.32, 3.55, 0.34, "Giả thuyết: " + hs, size=15, bold=True, color=MUTED)
pages.append(pg)

# 5 ------------------------------------------------------------------------- Ch2: related work
pg = Page(5, 1, "Các hướng phát hiện ảo giác đã có",
          "Khóa luận thuộc hướng dùng trọng số chú ý: một lượt đọc, chỉ huấn luyện bộ phân loại tuyến tính",
          "Bảng 2.1 · Nguyen và Nguyen (2020) · Conneau và cộng sự (2020) · Zheng và cộng sự (2023) · "
          "Cohen-Wang và cộng sự (2024) · Li và cộng sự (2026) · Chuang và cộng sự (2024) · Sun và cộng sự "
          "(2025) · Ogasa và Arase (2025)",
          notes=NOTES[5])
sh = pg.sh
rows = [("Hướng", "Công trình tiêu biểu", "Phải huấn luyện", "Chi phí mỗi lần dùng", "Hạn chế chính"),
        ("Đặc trưng bề mặt", "—", "Vài tham số", "Gần bằng 0", "Chỉ phản ánh đặc điểm đơn giản của văn bản"),
        ("Tinh chỉnh bộ mã hóa", "PhoBERT, XLM-R", "Hàng trăm triệu tham số", "Một lượt bộ mã hóa",
         "Cần dữ liệu có nhãn; huấn luyện lại khi đổi lĩnh vực"),
        ("Mô hình ngôn ngữ làm giám khảo", "GPT-4, Gemini", "Không", "Một lượt gọi mô hình",
         "Tốn chi phí theo lượt; dữ liệu phải gửi ra ngoài"),
        ("Cắt bỏ từng đoạn ngữ cảnh", "ContextCite, ARC-JSD", "Không hoặc rất ít",
         "Một lượt đọc cho mỗi đoạn", "Chi phí tăng theo số đoạn"),
        ("Trọng số chú ý (khóa luận)", "Lookback Lens, ReDeEP, Ogasa và Arase", "Bộ phân loại tuyến tính",
         "Một lượt đọc", "Cần mô hình mã nguồn mở")]
widths = [2.45, 2.5, 2.55, 2.2, 2.53]
tbl = sh.add_table(len(rows), len(widths), Inches(0.55), Inches(1.9), Inches(sum(widths)),
                   Inches(4.8)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.55 if i == 0 else 0.84)
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MID
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else CTXS if i == len(rows) - 1 else
                                       WHITE if i % 2 else PAPER2)
        cell.text_frame.word_wrap = True
        _run(cell.text_frame.paragraphs[0], v, 16, WHITE if i == 0 else CTX if i == len(rows) - 1
             and j == 0 else INK, i == 0 or i == len(rows) - 1 or j == 0, False)
pages.append(pg)

# 6 ------------------------------------------------------------------------- Ch2: Lookback Lens
pg = Page(6, 1, "Phương pháp nền: Lookback Lens",
          "Mỗi đầu chú ý cho một tỷ lệ chú ý vào ngữ cảnh; các tỷ lệ này là đầu vào của bộ phân loại",
          "Mục 2.1, 2.5, 4.3 · Lookback Lens: Chuang và cộng sự (EMNLP 2024) · Transformer: Vaswani và cộng "
          "sự (2017) · Qwen2.5: Qwen Team (2024) · số trên hình là ví dụ minh họa nguyên lý",
          notes=NOTES[6])
sh = pg.sh
card(sh, 0.55, 1.85, 6.0, 4.95, CTX)
text(sh, 0.8, 2.0, 5.5, 0.34, "Một đầu chú ý, khi đọc từ “1994” của câu trả lời", size=15, bold=True,
     color=CTX)
toks = ["Vịnh", "Hạ Long", "UNESCO", "công nhận", "năm", "1994"]
ws = [0.05, 0.08, 0.30, 0.09, 0.04, 0.04]
for i, (t, w) in enumerate(zip(toks, ws, strict=True)):
    y = 2.45 + i * 0.38
    box(sh, 0.8, y, 1.3, 0.31, WHITE, CTX, 1.25, r=0.05)
    text(sh, 0.8, y, 1.3, 0.31, t, size=14, align=C, anchor=MID)
    line(sh, 2.13, y + 0.15, 2.95, 3.55, CTX, 0.8 + w * 18)
box(sh, 2.95, 3.32, 0.95, 0.46, RESS, RES, 1.75, r=0.06)
text(sh, 2.95, 3.32, 0.95, 0.46, "1994", size=16, bold=True, align=C, anchor=MID)
for i, (t, w) in enumerate(zip(["UNESCO", "công", "nhận", "năm"], [0.06, 0.07, 0.05, 0.07],
                               strict=True)):
    y = 2.83 + i * 0.38
    box(sh, 4.95, y, 1.35, 0.31, WHITE, RES, 1.25, r=0.05)
    text(sh, 4.95, y, 1.35, 0.31, t, size=14, align=C, anchor=MID)
    line(sh, 3.92, 3.55, 4.92, y + 0.15, RES, 0.8 + w * 18)
text(sh, 0.8, 4.76, 1.6, 0.3, "Tài liệu", size=14, bold=True, color=CTX)
text(sh, 4.3, 4.36, 2.2, 0.3, "Câu trả lời đã viết", size=14, bold=True, color=RES, align=R)
g = pg.group()
text(g, 0.8, 5.1, 3.4, 0.3, "Chú ý trung bình mỗi từ của tài liệu", size=14, color=MUTED)
rect(g, 0.8, 5.44, 2.4, 0.24, PAPER2)
rect(g, 0.8, 5.44, 2.0, 0.24, CTX)
text(g, 3.3, 5.38, 0.75, 0.32, "0,10", size=16, bold=True, color=CTX)
text(g, 0.8, 5.78, 3.4, 0.3, "Chú ý trung bình mỗi từ đã viết trước", size=14, color=MUTED)
rect(g, 0.8, 6.12, 2.4, 0.24, PAPER2)
rect(g, 0.8, 6.12, 1.25, 0.24, RES)
text(g, 3.3, 6.06, 0.75, 0.32, "0,06", size=16, bold=True, color=RES)
box(g, 4.15, 5.12, 2.2, 1.5, CTXS, r=0.1)
text(g, 4.25, 5.17, 2.0, 1.4, [("Tỷ lệ lookback", dict(size=14, color=MUTED)),
                                ("0,10 ÷ (0,10 + 0,06)", dict(size=15)),
                                ("≈ 62 %", dict(size=28, bold=True, color=CTX))], align=C, anchor=MID)
g = pg.group()
card(g, 6.8, 1.85, 5.98, 4.95, IUH)
text(g, 7.05, 2.0, 5.5, 0.34, "Mọi đầu chú ý của mô hình đọc", size=15, bold=True, color=IUH)
seed = [11]


def rnd():
    seed[0] = (seed[0] * 9301 + 49297) % 233280
    return seed[0] / 233280


grid = g.add_group_shape().shapes
cw, chh = 0.1, 0.07
for layer in range(27):
    for head in range(28):
        v = 0.25 + 0.5 * rnd() + (0.25 if (head, layer) in ((7, 5), (4, 17)) else 0)
        c = box(grid, 7.05 + head * cw, 2.45 + layer * (chh + 0.012), cw - 0.014, chh, CTX,
                shape=MSO_SHAPE.RECTANGLE)
        fill = c.fill._xPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
        etree.SubElement(fill, qn("a:alpha")).set("val", str(int(min(1, v * 0.9) * 100000)))
text(g, 7.05, 4.67, 3.2, 0.3, "27 lớp × 28 đầu = 756 tỷ lệ", size=15, bold=True)
line(g, 9.95, 3.55, 10.45, 3.55, MUTED, 2.25, head=True)
box(g, 10.5, 3.05, 2.1, 1.0, WHITE, INK, 1.5, r=0.08)
text(g, 10.5, 3.05, 2.1, 1.0, [("Hồi quy logistic", dict(size=15, bold=True)),
                              ("Ba lớp nhãn", dict(size=13.5, color=MUTED))], align=C, anchor=MID)
text(g, 7.05, 5.05, 5.6, 1.72, [
    "**Đầu chú ý**: một thành phần tính chú ý riêng trong mỗi lớp của mô hình.",
    "Bài gốc (tiếng Anh): dùng được khi chuyển từ hỏi đáp sang tóm tắt văn bản.",
    "Khóa luận tái lập cho tiếng Việt với ba lớp nhãn."], size=14.5, bullet=True, after=3)
pages.append(pg)

# 7 ------------------------------------------------------------------------- Ch3: data
pg = Page(7, 2, "Bốn bộ dữ liệu tiếng Việt và cách chia tập",
          "Chia tập theo ngữ cảnh để tài liệu của tập kiểm tra không xuất hiện khi huấn luyện",
          "Chương 3, Bảng 3.1, 3.2, 3.3, 3.5 · ViHallu: Nguyen và cộng sự (2026) · ISE-DSC01: UIT Data "
          "Science Challenge (2023) · ViWikiFC: Le và cộng sự (2024) · ViFactCheck: Tran và cộng sự (2025)",
          notes=NOTES[7])
sh = pg.sh
rows = [("Bộ dữ liệu", "Vai trò trong khóa luận", "Số mẫu", "Cách chia"),
        ("ViHallu", "Bộ chính: câu trả lời do GPT-4o sinh, nhãn ảo giác ba lớp", "7.000",
         "Tự chia 80/10/10 theo ngữ cảnh"),
        ("ISE-DSC01", "Ngữ cảnh dài (trung vị 19 câu); định vị bằng chứng", "36.369",
         "Tự chia 80/10/10 theo ngữ cảnh"),
        ("ViWikiFC", "So với kết quả đã công bố; thí nghiệm can thiệp", "20.919",
         "Chia gốc; trùng tài liệu 100 %"),
        ("ViFactCheck", "Thử trên lĩnh vực tin tức", "7.232", "Chia gốc; trùng tài liệu 99,3 %")]
widths = [1.85, 5.25, 1.25, 3.88]
tbl = sh.add_table(len(rows), len(widths), Inches(0.55), Inches(1.88), Inches(sum(widths)),
                   Inches(2.7)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.48 if i == 0 else 0.55)
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MID
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else CTXS if i == 1 else WHITE if i % 2 else PAPER2)
        p = cell.text_frame.paragraphs[0]
        p.alignment = R if j == 2 else L
        _run(p, v, 15.5, WHITE if i == 0 else BAD if "trùng" in v else INK,
             i == 0 or j == 0 or "trùng" in v, False)
g = pg.group()
card(g, 0.55, 4.75, 6.85, 2.07, CTX)
text(g, 0.8, 4.88, 6.4, 0.34, "Chia theo ngữ cảnh, không chia theo từng câu trả lời", size=16,
     bold=True, color=CTX)
palette = [CTX, RES, VIOLET, OK, WARN, BAD, "2A6FB0", "8A5A44"]
sizes = [3, 2, 4, 3, 2, 3, 4, 2]
for x, w, lab, docs in [(0.8, 3.45, "Huấn luyện 80 %", range(0, 6)), (4.4, 1.35, "Kiểm định 10 %",
                                                                       range(6, 7)),
                        (5.9, 1.35, "Kiểm tra 10 %", range(7, 8))]:
    box(g, x, 5.3, w, 0.55, WHITE, RULE, 1.25, r=0.06)
    text(g, x - 0.05, 5.87, w + 0.1, 0.3, lab, size=13.5, bold=True, color=MUTED, align=C)
    step, dot, gap = 0.17, 0.14, 0.08
    span = sum(sizes[d] for d in docs) * step - (step - dot) + (len(docs) - 1) * gap
    dx = x + (w - span) / 2
    for d in docs:
        for _ in range(sizes[d]):
            box(g, dx, 5.505, dot, dot, palette[d], shape=MSO_SHAPE.OVAL)
            dx += step
        dx += gap
text(g, 0.8, 6.24, 6.45, 0.55, "Mỗi màu là một tài liệu: mọi câu trả lời của nó nằm chung một tập.",
     size=15)
g = pg.group()
card(g, 7.6, 4.75, 5.18, 2.07, RES)
text(g, 7.85, 4.88, 4.8, 0.34, "Kiểm chứng nhãn thủ công", size=16, bold=True, color=RES)
text(g, 7.85, 5.24, 4.8, 0.6, "Nhãn NEI (thiếu thông tin) được xem là ảo giác ngoại lai; hai thành "
     "viên kiểm tra độc lập 100 mẫu:", size=14.5)
for k, (v, t) in enumerate([("67/100", "Cả hai đồng ý là ngoại lai"), ("0,505", "Mức đồng thuận kappa")]):
    text(g, 7.85 + k * 2.45, 5.9, 2.4, 0.9, [(v, dict(size=24, bold=True, color=RES)),
                                             (t, dict(size=14, color=MUTED))])
pages.append(pg)

# 8 ------------------------------------------------------------------------- Ch4: chunk-aware
pg = Page(8, 3, "Phương pháp đề xuất: chunk-aware lookback ratio",
          "Tách tỷ lệ chú ý theo từng đoạn ngữ cảnh để biết chú ý tập trung vào đâu, không chỉ bao nhiêu",
          "Mục 4.4–4.5, Bảng 4.1 · mở rộng từ Lookback Lens: Chuang và cộng sự (2024) · số trên hình là ví "
          "dụ minh họa nguyên lý",
          notes=NOTES[8])
sh = pg.sh
sents = ["Vịnh Hạ Long nằm ở tỉnh Quảng Ninh.", "Vịnh gồm 1.969 hòn đảo lớn nhỏ.",
         "UNESCO công nhận là Di sản thế giới năm 1994.",
         "Năm 2000, vịnh được công nhận lần hai."]
for i, s in enumerate(sents):
    x = 0.55 + i * 1.62
    box(sh, x, 1.85, 1.52, 1.05, CTXS, CTX, 1, r=0.06)
    text(sh, x + 0.08, 1.89, 1.4, 0.25, f"Câu {i + 1}", size=12.5, bold=True, color=CTX)
    text(sh, x + 0.08, 2.13, 1.4, 0.78, s, size=13)
panels = [("A · Trung thực", OK, "“UNESCO công nhận vịnh là Di sản thiên nhiên thế giới năm 1994.”",
           [0.06, 0.09, 0.71, 0.14], "0,65", "71 %", "Tập trung vào một câu"),
          ("B · Ngoại lai", BAD, "“Vịnh Hạ Long mỗi năm đón hơn bảy triệu lượt khách.”",
           [0.24, 0.27, 0.26, 0.23], "1,00", "27 %", "Trải đều trên các câu")]
for k, (name, col, quote, share, ent, mx, verdict) in enumerate(panels):
    g = sh if k == 0 else pg.group()
    y = 3.02 + k * 1.92
    box(g, 0.55, y, 6.4, 1.8, WHITE, RULE, 1.25, r=0.1)
    pill(g, 0.72, y + 0.12, 1.65, 0.34, name, col, size=13.5)
    text(g, 2.5, y + 0.07, 4.4, 0.48, quote, size=13.5, italic=True)
    text(g, 0.72, y + 0.56, 3.1, 0.28, "Lookback Lens: chú ý vào tài liệu", size=13.5, color=MUTED)
    rect(g, 0.72, y + 0.88, 2.0, 0.18, PAPER2)
    rect(g, 0.72, y + 0.88, 2.0 * 0.62, 0.18, CTX)
    text(g, 2.8, y + 0.76, 0.75, 0.38, "62 %", size=16, bold=True)
    base = y + 1.6
    for i, v in enumerate(share):
        bx = 3.85 + i * 0.75
        rect(g, bx, base - v * 0.95, 0.5, v * 0.95, CTX)
        text(g, bx - 0.1, base - v * 0.95 - 0.24, 0.7, 0.22, f"{round(v * 100)} %", size=12.5, align=C)
        text(g, bx - 0.1, base, 0.7, 0.2, f"Câu {i + 1}", size=11.5, color=MUTED, align=C)
    text(g, 0.72, y + 1.12, 3.1, 0.64, [(f"Entropy {ent} · lớn nhất {mx}", dict(size=14.5, bold=True)),
                                       (verdict, dict(size=14.5, bold=True, color=col))])
g = pg.group()
card(g, 7.2, 1.85, 5.58, 4.95, IUH)
text(g, 7.45, 2.0, 5.1, 0.34, "Năm đặc trưng hình dạng của mỗi đầu chú ý", size=16, bold=True,
     color=IUH)
feats = [("MAX", "Tỷ trọng lớn nhất của một đoạn", "Giảm"),
         ("ENT", "Mức phân tán của chú ý (entropy)", "Tăng"),
         ("GINI", "Mức chênh lệch giữa các đoạn", "Giảm"),
         ("GAP", "Chênh lệch giữa hai đoạn đầu", "Giảm"),
         ("DRIFT", "Thay đổi giữa hai từ liên tiếp", "Không dự đoán")]
text(g, 10.6, 2.43, 2.05, 0.3, "Khi mất bằng chứng", size=13.5, bold=True, color=MUTED, align=R)
for i, (f, m, d) in enumerate(feats):
    y = 2.82 + i * 0.6
    line(g, 7.45, y - 0.04, 12.6, y - 0.04, RULE, 0.75)
    text(g, 7.45, y, 1.0, 0.52, f, size=14, bold=True, color=IUH, anchor=MID)
    text(g, 8.35, y, 2.95, 0.52, m, size=14.5, anchor=MID)
    text(g, 11.2, y, 1.45, 0.52, d, size=14, bold=True, color=MUTED if d.startswith("Không") else CTX,
         align=R, anchor=MID)
text(g, 7.45, 5.9, 5.15, 0.85, "Mỗi đầu chú ý cho **6 giá trị**: một tỷ lệ lookback và năm đặc trưng "
     "hình dạng.", size=15.5)
pages.append(pg)

# 9 ------------------------------------------------------------------------- Ch4: pipeline, hook
pg = Page(9, 3, "Quy trình phát hiện và cách trích chú ý tiết kiệm bộ nhớ",
          "Đặc trưng được tính ngay tại từng lớp rồi bỏ ma trận chú ý: bộ nhớ cao nhất 8,4 GB trên GPU 16 GB",
          "Mục 4.1, 4.2, 4.7, 4.8, Bảng 2.2 · Qwen2.5: Qwen Team (2024) · lượng tử hóa 4 bit: Dettmers và "
          "cộng sự (2023) · 8.428 MB đo trên GPU Tesla T4 ở 4.096 token",
          notes=NOTES[9])
sh = pg.sh
steps = [("1", "Ghép đầu vào", "Tài liệu, câu hỏi, câu trả lời theo một mẫu cố định; xác định vị trí "
                                "từng phần"),
         ("2", "Một lượt đọc", "Qwen2.5-7B nén 4 bit đọc toàn bộ; trích chú ý ở 27 lớp"),
         ("3", "192 đặc trưng", "32 đầu chú ý chọn trên tập kiểm định × 6 giá trị"),
         ("4", "Hồi quy logistic", "579 tham số → nhãn ba lớp và điểm rủi ro")]
for k, (n, h, b) in enumerate(steps):
    x = 0.55 + k * 3.1
    box(sh, x, 1.88, 2.8, 1.75, WHITE, RULE, 1.25, r=0.1)
    box(sh, x + 0.18, 2.02, 0.46, 0.46, IUH, shape=MSO_SHAPE.OVAL)
    text(sh, x + 0.18, 2.02, 0.46, 0.46, n, size=16, bold=True, color=WHITE, align=C, anchor=MID)
    text(sh, x + 0.75, 2.0, 2.0, 0.5, h, size=16.5, bold=True, anchor=MID)
    text(sh, x + 0.18, 2.58, 2.52, 1.02, b, size=15)
    if k < 3:
        line(sh, x + 2.83, 2.75, x + 3.07, 2.75, IUH, 2.25, head=True)
g = pg.group()
card(g, 0.55, 3.85, 7.25, 2.95, BAD)
text(g, 0.8, 3.98, 6.8, 0.34, "Bộ nhớ GPU khi đọc 4.096 token (Qwen2.5-7B)", size=16, bold=True)
bars = [("Trọng số mô hình", 5.3, MUTED), ("Ma trận chú ý một lớp", 0.94, CTX),
        ("Giữ cả 28 lớp", 26.3, BAD), ("Dùng forward hook", 8.43, OK)]
x0, x1, vmax = 3.3, 7.0, 28
for i, (lab, v, col) in enumerate(bars):
    y = 4.45 + i * 0.5
    text(g, 0.75, y, 2.45, 0.4, lab, size=15, anchor=MID, align=R)
    rect(g, x0, y + 0.06, (x1 - x0) * v / vmax, 0.28, col)
    text(g, x0 + (x1 - x0) * v / vmax + 0.06, y, 1.0, 0.4, vn(v, 1) + " GB", size=14.5, bold=True,
         color=col, anchor=MID)
x16 = x0 + (x1 - x0) * 16 / vmax
line(g, x16, 4.35, x16, 6.4, BAD, 1.5, dash=True)
text(g, x16 - 1.1, 6.42, 2.2, 0.3, "Giới hạn GPU 16 GB", size=13.5, bold=True, color=BAD, align=C)
g = pg.group()
card(g, 8.0, 3.85, 4.78, 2.95, OK)
text(g, 8.25, 3.98, 4.4, 0.34, "Forward hook", size=16, bold=True, color=OK)
text(g, 8.25, 4.38, 4.35, 2.35, [
    "Một hàm tự chạy ngay khi mỗi lớp tính xong.",
    "Tính đặc trưng từ ma trận chú ý, rồi bỏ ma trận trước khi sang lớp sau.",
    "Mỗi câu trả lời mất khoảng 0,44 giây trên GPU Tesla T4."], size=16, bullet=True, after=6)
pages.append(pg)

# 10 ------------------------------------------------------------------------ Ch5: system
pg = Page(10, 4, "Hệ thống ViHalluLens",
          "Bốn tầng, mỗi tầng chỉ gọi tầng ngay dưới; dùng qua thư viện Python, dịch vụ REST hoặc Docker",
          "Chương 5, Bảng 5.2, 5.3, Hình 5.2–5.4 · truy xuất BM25: Robertson và Zaragoza (2009) · minh họa "
          "chạy trên GPU Tesla T4 ngày 11/09/2026",
          notes=NOTES[10])
sh = pg.sh
layers = [("Tầng 4 · Phục vụ", "Dịch vụ REST, giao diện quan sát, hệ RAG minh họa", VIOLET),
          ("Tầng 3 · Bộ phát hiện", "Hồi quy logistic, điểm rủi ro; tệp 11,5 KB", RES),
          ("Tầng 2 · Đặc trưng", "Tỷ lệ lookback và năm đặc trưng hình dạng (CPU)", CTX),
          ("Tầng 1 · Trích chú ý", "Ghép đầu vào, một lượt đọc, forward hook (GPU)", IUH)]
for i, (h, b, col) in enumerate(layers):
    y = 1.88 + i * 0.95
    box(sh, 0.55, y, 5.3, 0.84, WHITE, col, 1.75, r=0.08)
    text(sh, 0.75, y + 0.04, 4.9, 0.34, h, size=15.5, bold=True, color=col)
    text(sh, 0.75, y + 0.42, 5.0, 0.36, b, size=14.5)
g = pg.group()
for k, (ic, h) in enumerate([("file-json", "Thư viện Python"), ("server", "Dịch vụ REST"),
                             ("layers", "Docker")]):
    x = 0.55 + k * 1.8
    box(g, x, 5.8, 1.7, 1.0, PAPER2, r=0.08)
    icon(g, ic, x + 0.6, 5.88, 0.45, INK)
    text(g, x, 6.36, 1.7, 0.36, h, size=14, bold=True, align=C)
g = pg.group()
picture(g, HERE / "img" / "web-ket-qua.webp", 6.1, 1.88, w=6.68, h=3.84)
for k, (v, t) in enumerate([("11,5 KB", "Tệp bộ phát hiện"), ("700/700", "Dự đoán trùng khi "
                                                                         "nạp lại"),
                            ("860", "Ca kiểm thử tự động")]):
    text(g, 6.1 + k * 2.27, 5.76, 2.2, 0.8, [(v, dict(size=24, bold=True, color=IUH)),
                                             (t, dict(size=14, color=MUTED))])
text(g, 6.1, 6.50, 6.68, 0.3, "Ảnh: câu trả lời thêm chi tiết ngoài tài liệu bị gán **ảo giác ngoại lai**.",
     size=14)
pages.append(pg)

# 11 ------------------------------------------------------------------------ Ch6: classification
pg = Page(11, 5, "Kết quả phân loại trên ViHallu",
          "Hướng chú ý tương đương PhoBERT đã tinh chỉnh, với số tham số ít hơn hàng trăm nghìn lần",
          "Bảng 6.1, Hình 6.1, Bảng E.6 · tập kiểm tra ViHallu 700 mẫu · PhoBERT: Nguyen và Nguyen (2020) · "
          "XLM-R: Conneau và cộng sự (2020) · LLM giám khảo: Zheng và cộng sự (2023) · † Gemini đánh giá "
          "trên 300/700 mẫu",
          notes=NOTES[11])
sh = pg.sh
card(sh, 0.55, 1.85, 8.0, 4.95, IUH)
text(sh, 0.8, 1.98, 7.5, 0.34, "Macro-F1 ba lớp và khoảng tin cậy 95 %", size=16, bold=True)
rowsr = [("Đặc trưng bề mặt", "9 tham số", 0.656, 0.620, 0.689, MUTED),
         ("PhoBERT đã tinh chỉnh", "369 triệu tham số", 0.749, 0.714, 0.778, RES),
         ("XLM-R đã tinh chỉnh", "560 triệu tham số", 0.776, 0.757, 0.818, RES),
         ("Gemini làm giám khảo †", "0 tham số, gọi API", 0.753, 0.702, 0.801, VIOLET),
         ("Lookback Lens", "2.271 tham số", 0.745, 0.711, 0.776, CTX),
         ("Chunk-aware", "579 tham số", 0.757, 0.724, 0.789, CTX)]
x0, x1 = 3.35, 7.4
for t in (0.60, 0.65, 0.70, 0.75, 0.80, 0.85):
    xx = x0 + (t - 0.60) / 0.25 * (x1 - x0)
    line(sh, xx, 2.45, xx, 6.22, "E6E1D6", 0.75)
    text(sh, xx - 0.35, 6.24, 0.7, 0.26, vn(t, 2), size=13, color=MUTED, align=C)
text(sh, x0 - 0.3, 6.47, x1 - x0 + 0.6, 0.3, "Macro-F1 (dự đoán ngẫu nhiên ≈ 0,33)", size=13, color=MUTED,
     align=C)
for i, (name, par, v, lo, hi, col) in enumerate(rowsr):
    y = 2.72 + i * 0.6
    if name == "Chunk-aware":
        box(sh, 0.62, y - 0.29, 7.86, 0.58, CTXS, r=0.05)
    text(sh, 0.8, y - 0.3, 2.55, 0.32, name, size=15, bold=True)
    text(sh, 0.8, y + 0.02, 2.55, 0.27, par, size=13, color=MUTED)
    ci_row(sh, x0, x1, 0.60, 0.85, y, v, lo, hi, col, 15, vn(v))
g = pg.group()
card(g, 8.8, 1.85, 3.98, 4.95, CTX)
text(g, 9.05, 1.98, 3.6, 0.34, "So sánh trên cùng các mẫu", size=16, bold=True, color=CTX)
pairs = [("Chunk-aware so với PhoBERT", "Không khác biệt rõ"),
         ("Chunk-aware so với XLM-R", "Không khác biệt rõ"),
         ("Lookback Lens so với XLM-R", "Thấp hơn 0,031"),
         ("Chunk-aware so với Gemini", "Không khác biệt rõ")]
for i, (h, verdict) in enumerate(pairs):
    y = 2.5 + i * 0.82
    line(g, 9.05, y - 0.06, 12.55, y - 0.06, RULE, 0.75)
    text(g, 9.05, y, 3.65, 0.75, [(h, dict(size=15, bold=True)),
                                  (verdict, dict(size=15, bold=True,
                                                color=OK if verdict.startswith("Không") else RES))])
text(g, 9.05, 5.85, 3.6, 0.9, "“Không khác biệt rõ”: khoảng tin cậy 95 % của hiệu số chứa 0.",
     size=14, color=MUTED)
pages.append(pg)

# 12 ------------------------------------------------------------------------ Ch6: localisation
pg = Page(12, 5, "Chú ý có tập trung vào đúng đoạn chứa bằng chứng không?",
          "Đầu chú ý tốt nhất xếp đúng đoạn bằng chứng lên đầu ở 87,8 % số mẫu, chính xác hơn cắt bỏ "
          "ngữ cảnh",
          "Bảng 6.2, Hình 6.2, 6.9, mục 6.5, 6.8, 6.14.1 · ARC-JSD: Li và cộng sự (2026) · giới hạn của chú "
          "ý khi dùng làm lời giải thích: Jain và Wallace (2019), Wiegreffe và Pinter (2019)",
          notes=NOTES[12])
sh = pg.sh
card(sh, 0.55, 1.85, 6.0, 4.95, CTX)
text(sh, 0.8, 1.98, 5.6, 0.34, "Tỷ lệ xếp đúng câu bằng chứng lên đầu", size=16, bold=True, color=CTX)
text(sh, 0.8, 2.38, 5.6, 0.3, "ISE-DSC01 · 2.376 mẫu · trung bình 22,6 câu mỗi tài liệu", size=14.5,
     color=MUTED)
for i, (lab, v, col) in enumerate([("Đầu chú ý tốt nhất", 0.878, CTX), ("Trung bình 756 đầu", 0.332,
                                                                       "6FB3B0"),
                                   ("Chọn ngẫu nhiên", 0.061, MUTED)]):
    y = 2.85 + i * 0.72
    text(sh, 0.8, y, 2.05, 0.5, lab, size=15.5, anchor=MID)
    rect(sh, 2.85, y + 0.08, 3.1, 0.34, PAPER2)
    rect(sh, 2.85, y + 0.08, 3.1 * v, 0.34, col)
    text(sh, 2.9 + 3.1 * v, y, 0.95, 0.5, vn(v * 100, 1) + " %", size=15.5, bold=True, color=col,
         anchor=MID)
text(sh, 0.8, 5.1, 5.6, 1.65, [
    "Gấp **14,3 lần** chọn ngẫu nhiên; trung bình cả 756 đầu cũng gấp 5,4 lần.",
    "Lặp lại trên ViWikiFC: đầu tốt nhất 85,3 %, trung bình 32,9 %."], size=15.5, bullet=True, after=6)
g = pg.group()
card(g, 6.8, 1.85, 5.98, 4.95, RES)
text(g, 7.05, 1.98, 5.5, 0.34, "So với cắt bỏ từng đoạn ngữ cảnh (300 mẫu)", size=16, bold=True,
     color=RES)
for i, (lab, v, cost, col) in enumerate([("Đầu chú ý tốt nhất", 0.850, "1 lượt đọc", CTX),
                                         ("Đầu chọn trên bộ khác", 0.797, "1 lượt đọc", "6FB3B0"),
                                         ("Cắt bỏ từng đoạn", 0.733, "10,9 lượt đọc", RES)]):
    y = 2.6 + i * 0.78
    text(g, 7.05, y, 2.3, 0.52, lab, size=15.5, anchor=MID)
    rect(g, 9.35, y + 0.08, 2.25, 0.36, PAPER2)
    rect(g, 9.35, y + 0.08, 2.25 * v, 0.36, col)
    text(g, 9.42, y + 0.08, 1.1, 0.36, vn(v * 100, 1) + " %", size=15, bold=True, color=WHITE,
         anchor=MID)
    text(g, 11.65, y, 1.15, 0.52, cost, size=13.5, color=MUTED, anchor=MID)
text(g, 7.05, 5.1, 5.55, 1.65, [
    "Một lượt đọc, chính xác hơn 11,7 điểm phần trăm, có ý nghĩa thống kê.",
    "Chỉ kết luận về định vị bằng chứng, chưa chứng minh mô hình dùng đoạn đó để trả lời."], size=15.5,
     bullet=True, after=6)
pages.append(pg)

# 13 ------------------------------------------------------------------------ Ch6: intervention
pg = Page(13, 5, "Thí nghiệm can thiệp: loại bỏ câu bằng chứng",
          "Khi chỉ thay câu bằng chứng, cả bốn đặc trưng thay đổi đúng hướng đã dự đoán trước khi chạy",
          "Bảng 6.5, Hình 6.3, 6.4 · 1.836 cặp ViWikiFC · kiểm định dấu hạng Wilcoxon, độ lớn hiệu ứng "
          "theo Kerby (2014)",
          notes=NOTES[13])
sh = pg.sh
card(sh, 0.55, 1.85, 5.6, 4.95, IUH)
text(sh, 0.8, 1.98, 5.2, 0.34, "Thiết kế thí nghiệm", size=16, bold=True, color=IUH)
for k, (lab, col, gold) in enumerate([("Tài liệu A: có câu bằng chứng", CTX, True),
                                      ("Tài liệu B: thay câu đó bằng câu cùng chủ đề", RES, False)]):
    y = 2.5 + k * 1.45
    text(sh, 0.8, y, 5.2, 0.32, lab, size=15, bold=True, color=col)
    for i in range(10):
        hit = i == 4
        box(sh, 0.8 + i * 0.5, y + 0.42, 0.42, 0.62,
            (CTX if gold else RES) if hit else PAPER2, (CTX if gold else RES) if hit else RULE, 1, r=0.04)
    text(sh, 0.8 + 4 * 0.5 - 0.4, y + 1.06, 1.22, 0.27, "Bằng chứng" if gold else "Câu thay",
         size=12.5, bold=True, color=col, align=C)
text(sh, 0.8, 5.5, 5.15, 1.25, ["Cùng một phát biểu, cùng chín câu còn lại, cùng thứ tự.",
                                "Hướng thay đổi được ghi vào mã nguồn từ trước."], size=15.5,
     bullet=True, after=4)
g = pg.group()
card(g, 6.4, 1.85, 6.38, 4.95, OK)
text(g, 6.65, 1.98, 5.9, 0.34, "Tỷ lệ cặp thay đổi đúng hướng dự đoán", size=16, bold=True, color=OK)
text(g, 10.8, 2.38, 1.8, 0.3, "Độ lớn hiệu ứng", size=13.5, color=MUTED, align=R)
for i, (lab, v, r_) in enumerate([("ENT tăng", 0.754, "0,716"), ("GINI giảm", 0.745, "0,686"),
                                  ("MAX giảm", 0.724, "0,657"), ("GAP giảm", 0.712, "0,624")]):
    y = 2.8 + i * 0.65
    text(g, 6.65, y, 1.5, 0.48, lab, size=15.5, bold=True, anchor=MID)
    rect(g, 8.15, y + 0.08, 3.0, 0.32, PAPER2)
    rect(g, 8.15, y + 0.08, 3.0 * v, 0.32, OK)
    text(g, 8.22, y + 0.08, 1.1, 0.32, vn(v * 100, 1) + " %", size=14.5, bold=True, color=WHITE,
         anchor=MID)
    text(g, 11.3, y, 1.3, 0.48, r_, size=15.5, align=R, anchor=MID)
line(g, 8.15 + 1.5, 2.72, 8.15 + 1.5, 5.4, MUTED, 1.25, dash=True)
text(g, 9.1, 5.4, 1.1, 0.28, "50 %", size=13, color=MUTED, align=C)
text(g, 6.65, 5.8, 5.95, 0.95, "Đúng hướng **4/4** đặc trưng, độ lớn hiệu ứng ở mức lớn; nhưng mức thay "
     "đổi tuyệt đối nhỏ (khoảng 0,015 trên thang 0–1).", size=15.5)
pages.append(pg)

# 14 ------------------------------------------------------------------------ Ch6: cost, transfer
pg = Page(14, 5, "Chi phí và khả năng dùng trên bộ dữ liệu khác",
          "Mô hình đọc 3B cân bằng chi phí và độ chính xác; phát hiện có ảo giác hay không vẫn dùng được khi đổi bộ dữ liệu",
          "Bảng 6.7, 6.9, 6.10, Hình 6.6, Bảng E.5 · thời gian đo trên GPU Tesla T4 · Gemini đánh giá trên "
          "300 mẫu",
          notes=NOTES[14])
sh = pg.sh
rows = [("Phương pháp", "Macro-F1", "ms/mẫu", "Tham số"),
        ("XLM-R đã tinh chỉnh", "0,776", "25", "560 triệu"),
        ("PhoBERT đã tinh chỉnh", "0,749", "12", "369 triệu"),
        ("Gemini làm giám khảo †", "0,753", "8.194", "0"),
        ("Chunk-aware, mô hình 7B", "0,757", "438", "579"),
        ("Lookback Lens, mô hình 3B", "0,735", "223", "195")]
widths = [2.8, 1.25, 1.05, 1.45]
tbl = sh.add_table(len(rows), len(widths), Inches(0.55), Inches(1.88), Inches(sum(widths)),
                   Inches(3.1)).table
for j, w in enumerate(widths):
    tbl.columns[j].width = Inches(w)
for i, row in enumerate(rows):
    tbl.rows[i].height = Inches(0.5)
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.margin_left = cell.margin_right = Inches(0.1)
        cell.vertical_anchor = MID
        cell.fill.solid()
        cell.fill.fore_color.rgb = rgb(INK if i == 0 else OKS if i == 5 else WHITE if i % 2 else PAPER2)
        p = cell.text_frame.paragraphs[0]
        p.alignment = L if j == 0 else R
        _run(p, v, 15.5, WHITE if i == 0 else INK, i == 0 or i == 5, False)
g = pg.group()
box(g, 0.55, 5.18, 6.55, 1.62, OKS, r=0.1)
text(g, 0.75, 5.27, 6.2, 1.5, [("**Mô hình đọc 3B:** nhanh gấp đôi bản 7B, ít hơn 56 % bộ nhớ, macro-F1 chỉ giảm "
                                "0,010.", dict(size=15)),
                               ("**Tự kiểm tra:** mô hình 3B vừa sinh vừa đọc lại câu trả lời; thời gian chỉ tăng "
                                "**3,6 %**, dữ liệu không phải gửi ra ngoài.", dict(size=15))], after=8)
g = pg.group()
card(g, 7.35, 1.85, 5.43, 4.95, IUH)
text(g, 7.6, 1.98, 5.0, 0.34, "Huấn luyện trên bộ này, dùng trên bộ kia", size=16, bold=True,
     color=IUH)
cd = CategoryChartData()
cd.categories = ["ViHallu → ISE-DSC01", "ISE-DSC01 → ViHallu"]
cd.add_series("Ba lớp", (0.430, 0.554))
cd.add_series("Có ảo giác hay không", (0.631, 0.784))
ch = g.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(7.5), Inches(2.4), Inches(5.15), Inches(3.3),
                 cd).chart
ch.has_legend = True
ch.legend.position, ch.legend.include_in_layout = XL_LEGEND_POSITION.TOP, False
ch.legend.font.size, ch.legend.font.name = Pt(14.5), FONT
ch.font.size, ch.font.name = Pt(14.5), FONT
va = ch.value_axis
va.minimum_scale, va.maximum_scale = 0, 0.9
va.has_major_gridlines = False
va.visible = False
ch.category_axis.tick_labels.font.size = Pt(14)
ch.category_axis.format.line.color.rgb = rgb(RULE)
pl = ch.plots[0]
pl.gap_width, pl.overlap = 70, -10
for ser, col in zip(pl.series, (RES, CTX), strict=True):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = rgb(col)
    for pt, v in zip(ser.points, ser.values, strict=True):
        tf = pt.data_label.text_frame
        tf.text = vn(v)
        r0 = tf.paragraphs[0].runs[0]
        r0.font.size, r0.font.bold, r0.font.name = Pt(15), True, FONT
        pt.data_label.position = XL_LABEL_POSITION.OUTSIDE_END
text(g, 7.6, 5.8, 5.0, 0.95, "Số liệu của Lookback Lens. Hai bộ định nghĩa ảo giác ngoại lai khác nhau, "
     "nên phân loại ba lớp không dùng lại được.", size=14.5)
pages.append(pg)

# 15 ------------------------------------------------------------------------ Ch7: discussion
pg = Page(15, 6, "Thảo luận: định vị đúng nhưng không phân loại tốt hơn",
          "Chunk-aware không tăng điểm phân loại: tín hiệu của nó đã có sẵn trong tỷ lệ chú ý gộp",
          "Mục 7.1–7.3, Hình 7.1, Bảng E.6, 7.2 · so sánh trên cùng mẫu, lấy mẫu lại 10.000 lần, hiệu chỉnh "
          "Holm cho tám phép so sánh · Jain và Wallace (2019), Wiegreffe và Pinter (2019)",
          notes=NOTES[15])
sh = pg.sh
card(sh, 0.55, 1.85, 6.55, 4.95, BAD)
text(sh, 0.8, 1.98, 6.1, 0.34, "Hiệu macro-F1: chunk-aware trừ Lookback Lens", size=16, bold=True,
     color=BAD)
forest = [("ViHallu, Qwen2.5-7B", 0.0116, -0.0233, 0.0453), ("ViHallu, Qwen2.5-3B", -0.0128, -0.0442,
                                                              0.0186),
          ("ViHallu, Qwen2.5-1.5B", 0.0114, -0.0056, 0.0286), ("ViHallu, Sailor2-8B", -0.0258, -0.0570,
                                                                 0.0053),
          ("ISE-DSC01, 29.077 mẫu", 0.0068, -0.0010, 0.0144), ("ISE-DSC01, 5.600 mẫu", 0.0050, -0.0045,
                                                                0.0145),
          ("ViWikiFC", -0.0012, -0.0132, 0.0106), ("ViFactCheck", 0.0226, -0.0029, 0.0478)]
fx0, fx1, lo_v, hi_v = 3.35, 6.85, -0.06, 0.05
zero = fx0 + (0 - lo_v) / (hi_v - lo_v) * (fx1 - fx0)
for t in (-0.04, -0.02, 0.02, 0.04):
    xx = fx0 + (t - lo_v) / (hi_v - lo_v) * (fx1 - fx0)
    line(sh, xx, 2.45, xx, 5.85, "E6E1D6", 0.75)
    text(sh, xx - 0.35, 5.88, 0.7, 0.25, f"{t:+.2f}".replace(".", ","), size=12.5, color=MUTED, align=C)
line(sh, zero, 2.45, zero, 5.85, INK, 1.5)
text(sh, zero - 0.2, 5.88, 0.4, 0.25, "0", size=12.5, color=MUTED, align=C)
for i, (lab, v, lo, hi) in enumerate(forest):
    y = 2.65 + i * 0.4
    text(sh, 0.8, y - 0.18, 2.55, 0.36, lab, size=14.5, anchor=MID)
    ci_row(sh, fx0, fx1, lo_v, hi_v, y, v, lo, hi, CTX if v > 0 else RES)
text(sh, 0.8, 6.2, 6.1, 0.55, "Không khoảng tin cậy nào nằm hẳn một phía của 0.", size=15.5, bold=True)
g = pg.group()
card(g, 7.35, 1.85, 5.43, 4.95, IUH)
text(g, 7.6, 1.98, 5.0, 0.34, "Vì sao không tăng điểm?", size=16, bold=True, color=IUH)
text(g, 7.6, 2.45, 5.0, 3.0, [
    "**Cùng tín hiệu:** 99,9 % thông tin của năm đặc trưng đã có trong tỷ lệ gộp (ISE-DSC01).",
    "**Chú ý cho biết mô hình dựa vào đoạn nào,** không cho biết câu trả lời khẳng định gì về đoạn đó: "
    "câu trả lời đúng và câu trả lời phủ định lại tài liệu cùng dựa vào một đoạn.",
    "**Ranh giới nội tại – ngoại lai** khó ngay cả với người gán nhãn (kappa 0,505)."], size=15.5,
     bullet=True, after=8)
box(g, 7.6, 5.6, 5.0, 1.05, PAPER2, r=0.08)
text(g, 7.75, 5.63, 4.75, 1.0, "Xác suất của chunk-aware đáng tin hơn chủ yếu vì bộ phân loại nhỏ hơn; "
     "hiệu chỉnh xác suất làm hai bên tương đương.", size=14.5, anchor=MID)
pages.append(pg)

# 16 ------------------------------------------------------------------------ Ch8: hypotheses
pg = Page(16, 7, "Kết luận: kiểm định năm giả thuyết",
          "Ba giả thuyết được ủng hộ; giả thuyết chính về chunk-aware không được ủng hộ",
          "Bảng 1.1, 7.1, mục 8.1 · các dự đoán chính được ghi vào kho mã nguồn trước khi chạy thí nghiệm",
          notes=NOTES[16])
sh = pg.sh
hyp = [("H1", "Tỷ lệ chú ý gộp tốt hơn đặc trưng bề mặt, tương đương bộ mã hóa",
        "0,745 so với 0,656; tương đương PhoBERT (0,749)", "Được ủng hộ", OK),
       ("H2", "Chia theo đoạn làm tăng macro-F1, tăng nhiều hơn khi ngữ cảnh dài",
        "Cả tám khoảng tin cậy chứa 0", "Không được ủng hộ", BAD),
       ("H3", "Chú ý tập trung vào đúng đoạn chứa bằng chứng",
        "87,8 %, gấp 14,3 lần ngẫu nhiên", "Được ủng hộ", OK),
       ("H4", "Mất bằng chứng thì chú ý phân tán hơn",
        "Đúng hướng 4/4, mức thay đổi nhỏ", "Ủng hộ về hướng", WARN),
       ("H5", "Giữ hiệu năng khi chuyển sang bộ dữ liệu khác",
        "Ba lớp giảm mạnh; nhị phân 0,63–0,78", "Một phần", WARN)]
text(sh, 1.32, 1.86, 5.0, 0.32, "Giả thuyết", size=14.5, bold=True, color=MUTED)
text(sh, 6.72, 1.86, 3.6, 0.32, "Bằng chứng chính", size=14.5, bold=True, color=MUTED)
text(sh, 10.5, 1.86, 2.25, 0.32, "Kết luận", size=14.5, bold=True, color=MUTED, align=C)
for i, (h, s, e, v, col) in enumerate(hyp):
    g = sh if i == 0 else pg.group()
    y = 2.25 + i * 0.9
    box(g, 0.55, y, 12.23, 0.8, WHITE if i % 2 == 0 else PAPER2, RULE, 0.75, r=0.06)
    box(g, 0.7, y + 0.17, 0.46, 0.46, INK, shape=MSO_SHAPE.OVAL)
    text(g, 0.7, y + 0.17, 0.46, 0.46, h, size=14, bold=True, color=WHITE, align=C, anchor=MID)
    text(g, 1.32, y, 5.2, 0.8, s, size=16, bold=True, anchor=MID)
    text(g, 6.72, y, 3.6, 0.8, e, size=15, color=MUTED, anchor=MID)
    pill(g, 10.42, y + 0.17, 2.2, 0.46, v, col, size=14.5)
pages.append(pg)

# 17 ------------------------------------------------------------------------ Ch8: results, limits
pg = Page(17, 7, "Kết quả đạt được, hạn chế và hướng phát triển",
          "Tín hiệu chú ý đủ để phát hiện ảo giác với rất ít tham số, và chỉ ra được đoạn chứa bằng chứng",
          "Mục 8.1–8.3, mục 7.5",
          notes=NOTES[17])
sh = pg.sh
cols3 = [("Kết quả đạt được", "circle-check", OK, [
    "Bộ phát hiện ba lớp đạt 0,757 với 579 tham số, tương đương PhoBERT",
    "Chú ý định vị đúng bằng chứng 87,8 %, chính xác hơn cắt bỏ ngữ cảnh",
    "Hệ thống hoàn chỉnh: thư viện, REST, Docker, giao diện; 860 ca kiểm thử"]),
         ("Hạn chế", "triangle-alert", BAD, [
             "Chia theo đoạn không làm tăng điểm phân loại",
             "Phân loại ba lớp không dùng lại được trên bộ dữ liệu khác",
             "Nhãn chỉ có ở mức cả câu trả lời",
             "Kịch bản tự kiểm tra mới đo chi phí, chưa đo độ chính xác"]),
         ("Hướng phát triển", "rocket", CTX, [
             "Phát hiện theo từng đoạn của câu trả lời, với nhãn ở mức đoạn",
             "Kết hợp chú ý (tốt ở ảo giác nội tại) với bộ mã hóa (tốt ở ngoại lai)",
             "Chỉ tính các hàng chú ý của câu trả lời để đọc được tài liệu dài hơn"])]
for k, (h, ic, col, items) in enumerate(cols3):
    g = sh if k == 0 else pg.group()
    x = 0.55 + k * 4.14
    card(g, x, 1.88, 3.95, 4.92, col)
    icon(g, ic, x + 0.22, 2.1, 0.42, col)
    text(g, x + 0.78, 2.07, 3.0, 0.48, h, size=19, bold=True, color=col, anchor=MID)
    text(g, x + 0.25, 2.72, 3.55, 4.0, items, size=19, bullet=True, after=14)
pages.append(pg)

# 18 ------------------------------------------------------------------------ references
pg = Page(18, 7, "Tài liệu tham khảo chính",
          "Số trong ngoặc theo danh mục 28 tài liệu của quyển khóa luận",
          "Danh mục đầy đủ ở cuối quyển khóa luận",
          notes=NOTES[18])
sh = pg.sh
refs = [("Phương pháp nền và hướng liên quan", CTX, [
    ("[2]", "Chuang và cộng sự (2024). Lookback Lens. ", "EMNLP 2024"),
    ("[26]", "Vaswani và cộng sự (2017). Attention Is All You Need. ", "NeurIPS 30"),
    ("[20]", "Sun và cộng sự (2025). ReDeEP. ", "ICLR 2025"),
    ("[17]", "Ogasa và Arase (2025). Multi-View Attention Features. ", "arXiv"),
    ("[13]", "Li và cộng sự (2026). ARC-JSD. ", "ICLR 2026")]),
        ("Dữ liệu", RES, [
            ("[15]", "Nguyen và cộng sự (2026). ViHallu Challenge. ", "arXiv:2601.04711"),
            ("[24]", "UIT Data Science Challenge 2023 (ISE-DSC01).", ""),
            ("[11]", "Le và cộng sự (2024). ViWikiFC. ", "arXiv:2405.07615"),
            ("[23]", "Tran và cộng sự (2025). ViFactCheck. ", "AAAI 2025")]),
        ("Phương pháp so sánh", VIOLET, [
            ("[16]", "Nguyen và Nguyen (2020). PhoBERT. ", "Findings of EMNLP 2020"),
            ("[4]", "Conneau và cộng sự (2020). XLM-R. ", "ACL 2020"),
            ("[28]", "Zheng và cộng sự (2023). LLM-as-a-Judge. ", "NeurIPS 36")]),
        ("Mô hình và nền tảng", IUH, [
            ("[18]", "Qwen Team (2024). Qwen2.5 Technical Report. ", "arXiv:2412.15115"),
            ("[12]", "Lewis và cộng sự (2020). Retrieval-Augmented Generation. ", "NeurIPS"),
            ("[9]", "Ji và cộng sự (2023). Survey of Hallucination in NLG. ", "ACM CSUR")])]
pos = [(0.55, 1.88), (0.55, 4.6), (6.8, 1.88), (6.8, 4.0)]
for (h, col, items), (x, y) in zip(refs, pos, strict=True):
    text(sh, x, y, 5.9, 0.34, h.upper(), size=14.5, bold=True, color=col)
    for i, (n, body, venue) in enumerate(items):
        yy = y + 0.45 + i * 0.44
        text(sh, x, yy, 0.6, 0.34, n, size=14, bold=True, color=col)
        tb = text(sh, x + 0.6, yy, 5.6, 0.34, body, size=14)
        if venue:
            _run(tb.text_frame.paragraphs[0], venue, 14, MUTED, False, True)
pages.append(pg)

# 19 ------------------------------------------------------------------------ thanks
pg = Page(19, chrome=False, notes=NOTES[19])
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
