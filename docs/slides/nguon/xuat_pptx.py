"""Export the committee deck to an editable PowerPoint file: slide_hoi_dong.pptx.

Chrome opens ``slide_hoi_dong.html`` with ``?all`` (every diagram in its final state) and
``trich_doi_tuong.js`` reads each slide as drawing primitives in slide pixels. Each primitive
becomes a native shape: boxes, ovals, lines and curves (freeforms), text boxes with their runs,
pictures. Only the photographs and the small line icons are pictures; every word and every bar is
an object that PowerPoint can edit. Slides fade in, and the speaker notes come from the deck.

Fonts: the deck's web fonts are mapped to fonts that every Windows/Office machine has
(serif → Cambria, sans → Segoe UI), so the file looks the same on the presentation computer.

    uv run --no-project --with playwright==1.48.0 --with python-pptx==1.0.2 \\
        --with pillow --with cairosvg==2.7.1 python docs/slides/nguon/xuat_pptx.py \\
        docs/slides/slide_hoi_dong.html docs/slides/slide_hoi_dong.pptx
"""

import base64
import io
import re
import sys
from pathlib import Path

import cairosvg
from lxml import etree
from PIL import Image
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

SRC, OUT = (Path(p).resolve() for p in sys.argv[1:3])
JS = (Path(__file__).parent / "trich_doi_tuong.js").read_text(encoding="utf-8")
PX = 6350  # EMU per slide pixel: 12 192 000 EMU / 1920 px
SERIF, SANS, MONO = "Cambria", "Segoe UI", "Consolas"
WIDEN = 1.05  # text boxes get a little room: the replacement fonts are not metric-identical


def emu(v):
    return Emu(int(round(v * PX)))


def font_of(family):
    f = (family or "").lower()
    if "mono" in f or "consol" in f:
        return MONO
    if "serif" in f and "sans" not in f or "newsreader" in f or "georgia" in f:
        return SERIF
    return SANS


def alpha(el, a):
    """Give the solid fill / line colour of a shape an alpha (0..1)."""
    if a >= 0.995:
        return
    for clr in el.iter(qn("a:srgbClr")):
        for old in clr.findall(qn("a:alpha")):
            clr.remove(old)
        etree.SubElement(clr, qn("a:alpha")).set("val", str(int(max(0, min(1, a)) * 100000)))


def no_style(shape):
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def paint(shape, it):
    fill, stroke = it.get("fill"), it.get("stroke")
    a = it.get("a", 1)
    if fill:
        shape.fill.solid()
        shape.fill.fore_color.rgb = RGBColor.from_string(fill[0][1:])
        alpha(shape.fill._xPr.find(qn("a:solidFill")), a * fill[1] * it.get("fo", 1))
    else:
        shape.fill.background()
    if stroke and it.get("sw", 0) > 0.05:
        shape.line.color.rgb = RGBColor.from_string(stroke[0][1:])
        shape.line.width = emu(it["sw"])
        alpha(shape.line._get_or_add_ln().find(qn("a:solidFill")), a * stroke[1] * it.get("so", 1))
        if it.get("dash"):
            shape.line.dash_style = 4
    else:
        shape.line.fill.background()


def add_rect(sh, it):
    if it["w"] < 0.3 or it["h"] < 0.3:
        return
    r = it.get("r", 0)
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if r > 0.5 else MSO_SHAPE.RECTANGLE
    s = sh.add_shape(kind, emu(it["x"]), emu(it["y"]), emu(it["w"]), emu(it["h"]))
    no_style(s)
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = min(0.5, r / max(1e-6, min(it["w"], it["h"])))
    paint(s, it)


def add_oval(sh, it):
    s = sh.add_shape(MSO_SHAPE.OVAL, emu(it["x"]), emu(it["y"]), emu(it["w"]), emu(it["h"]))
    no_style(s)
    paint(s, it)


def add_poly(sh, it):
    pts = it["pts"]
    if len(pts) < 2:
        return
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    if max(xs) - min(xs) < 0.2 and max(ys) - min(ys) < 0.2:
        return
    fb = sh.build_freeform(emu(pts[0][0]), emu(pts[0][1]), scale=1.0)
    fb.add_line_segments([(emu(x), emu(y)) for x, y in pts[1:]], close=bool(it.get("closed")))
    s = fb.convert_to_shape()
    no_style(s)
    if not it.get("closed"):
        it = dict(it, fill=None)
    paint(s, it)
    ln = s.line._get_or_add_ln()
    ln.set("cap", "rnd")


def png_of(src):
    if src.startswith("data:"):
        raw = base64.b64decode(src.split(",", 1)[1])
    else:
        raw = Path(src.replace("file:///", "")).read_bytes()
    if b"<svg" in raw[:400]:
        return cairosvg.svg2png(bytestring=raw, output_width=1200)
    im = Image.open(io.BytesIO(raw))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def add_pic(sh, it, data):
    p = sh.add_picture(io.BytesIO(data), emu(it["x"]), emu(it["y"]), emu(it["w"]), emu(it["h"]))
    if it.get("a", 1) < 0.99:
        blip = p._element.find(".//" + qn("a:blip"))
        etree.SubElement(blip, qn("a:alphaModFix")).set("amt", str(int(it["a"] * 100000)))
    return p


def add_text(sh, it):
    runs = [r for r in it["runs"] if r.get("br") or r.get("t")]
    while runs and runs[0].get("br"):
        runs.pop(0)
    if not runs:
        return
    # trim the outer spaces of the paragraph
    first = next(r for r in runs if not r.get("br"))
    first["t"] = first["t"].lstrip()
    last = [r for r in runs if not r.get("br")][-1]
    last["t"] = last["t"].rstrip()
    single = it.get("svg") or it.get("lines", 1) == 1
    w = it["w"] * WIDEN + 8 if single else it["w"] + 2
    x = it["x"]
    if it["align"] == "c":
        x -= (w - it["w"]) / 2
    elif it["align"] == "r":
        x -= w - it["w"]
    tb = sh.add_textbox(emu(x), emu(it["y"]), emu(w), emu(max(it["h"], 4)))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = not single
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE if it.get("svg") else MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[it["align"]]
    if it.get("lh"):
        p.line_spacing = Pt(it["lh"] * 0.5)
    if it.get("indent"):
        p._p.get_or_add_pPr().set("indent", str(int(it["indent"] * PX)))
    for r in runs:
        if r.get("br"):
            p = tf.add_paragraph()
            p.alignment = tf.paragraphs[0].alignment
            if it.get("lh"):
                p.line_spacing = Pt(it["lh"] * 0.5)
            continue
        run = p.add_run()
        run.text = r["t"]
        f = run.font
        f.size = Pt(max(4, r["size"] * 0.5))
        f.bold, f.italic = bool(r.get("b")), bool(r.get("i"))
        f.name = font_of(r.get("f"))
        c = r.get("c") or ["#18202E", 1]
        f.color.rgb = RGBColor.from_string(c[0][1:])
        rpr = run._r.get_or_add_rPr()
        a = it.get("a", 1) * c[1]
        if a < 0.995:
            alpha(rpr.find(qn("a:solidFill")), a)
        if r.get("ls"):
            rpr.set("spc", str(int(r["ls"] * 0.5 * 100)))
        if r.get("u"):
            f.underline = True
        for tag in ("a:latin", "a:ea", "a:cs"):  # Vietnamese text uses the same face everywhere
            e = rpr.find(qn(tag))
            if e is None:
                e = etree.SubElement(rpr, qn(tag))
            e.set("typeface", f.name)


def fade(slide):
    ns = "http://schemas.openxmlformats.org/presentationml/2006/main"
    root = slide._element
    tr = etree.fromstring(f'<p:transition xmlns:p="{ns}" spd="med"><p:fade/></p:transition>')
    root.find(qn("p:clrMapOvr")).addnext(tr)


def main():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(1920 * PX), Emu(1080 * PX)
    blank = prs.slide_layouts[6]
    rels = prs.slide_master.part.rels.values()
    th = next(r.target_part for r in rels if r.reltype.endswith("/theme"))
    xml = th.blob.decode("utf8")
    xml = re.sub(r'(<a:majorFont>\s*<a:latin typeface=")[^"]*', rf"\g<1>{SERIF}", xml)
    xml = re.sub(r'(<a:minorFont>\s*<a:latin typeface=")[^"]*', rf"\g<1>{SANS}", xml)
    th._blob = xml.encode("utf8")
    icons = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel="chrome")
        pg = br.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.goto(SRC.as_uri() + "?all#1")
        pg.wait_for_function("document.querySelector('.slide.active') !== null")
        n = pg.evaluate("document.querySelectorAll('.slide').length")
        for k in range(1, n + 1):
            pg.goto(SRC.as_uri() + f"?all&p={k}#{k}")
            active = f"document.querySelectorAll('.slide')[{k - 1}].classList.contains('active')"
            pg.wait_for_function(active)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            data = pg.evaluate(JS)
            s = prs.slides.add_slide(blank)
            sh = s.shapes
            for it in data["items"]:
                kind = it["k"]
                if kind == "bg":
                    if it.get("fill"):
                        s.background.fill.solid()
                        s.background.fill.fore_color.rgb = RGBColor.from_string(it["fill"][0][1:])
                elif kind == "rect":
                    add_rect(sh, it)
                elif kind == "oval":
                    add_oval(sh, it)
                elif kind == "poly":
                    add_poly(sh, it)
                elif kind == "text":
                    add_text(sh, it)
                elif kind == "img":
                    add_pic(sh, it, png_of(it["src"]))
                elif kind == "svgimg":
                    key = it["svg"]
                    if key not in icons:
                        icons[key] = cairosvg.svg2png(bytestring=key.encode(), output_width=192,
                                                      output_height=192)
                    add_pic(sh, it, icons[key])
            notes = data["notes"].split("<br><br><b>Thao tác")[0]
            s.notes_slide.notes_text_frame.text = notes.replace("<b>", "").replace("</b>", "")
            fade(s)
            print(k, len(data["items"]))
        br.close()
    cp = prs.core_properties
    cp.author = cp.last_modified_by = "Nguyễn Ngọc Lân, Nguyễn Tấn Minh"
    cp.title = "Phát hiện ảo giác cho RAG tiếng Việt dựa trên tín hiệu chú ý nội tại"
    cp.comments = cp.subject = cp.keywords = ""
    prs.save(OUT)
    print(OUT, len(prs.slides), "slide", f"{OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
