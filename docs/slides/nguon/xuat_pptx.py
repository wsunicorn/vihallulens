"""Export the committee deck to PowerPoint, keeping every slide's animation.

PowerPoint cannot run the deck's GSAP timelines or CSS transitions, so each slide is recorded:
the HTML is driven frame by frame in Chrome (timelines seeked, CSS transitions paused and
stepped), the frames are encoded to an H.264 video, and the video is placed full-slide with
"start automatically", exactly like the HTML where every slide animates on entry without a click.
The video stops on its last frame, which is the slide's final state. Slides change with a fade,
as in the HTML. Speaker notes are copied from ``data-notes``.

What cannot be carried over: hover tooltips and the in-figure buttons (alternate views). The HTML
stays the primary deck; the PPTX is the fallback for a machine that only has PowerPoint.

Run through ``dung_lai.py --pptx`` (the command is in its docstring), or alone with
``python xuat_pptx.py ../slide_hoi_dong.html ../slide_hoi_dong.pptx`` under the same packages.

Needs Google Chrome installed (Playwright drives it through ``channel="chrome"``).
"""

import copy
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
from lxml import etree
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Emu

SRC, OUT = (Path(p).resolve() for p in sys.argv[1:3])
FPS = 25
TAIL = 0.4  # seconds of still final state at the end of each video
CSS_SPAN = 1.7  # longest CSS entrance (.rise r7: .92 s delay + .7 s) plus a margin
START_DELAY, SPEED = 0.35, 1.35  # must match mount(): delayedCall(.35) and tl.timeScale(1.35)

page_src = SRC.read_text(encoding="utf-8")

# Recording hooks, added to a temporary copy only: expose the current timeline and freeze every
# animation the moment a slide is shown, so frames can be rendered at exact times.
HOOK_AT = "    cur = { tl, steps, setStep };\n"
assert page_src.count(HOOK_AT) == 1
rec_src = page_src.replace(HOOK_AT, HOOK_AT + "    window.__cur = cur;\n")
SHOW_AT = "    mount(slides[i]);\n  }\n"
assert rec_src.count(SHOW_AT) == 1
rec_src = rec_src.replace(
    SHOW_AT,
    "    window.__cur = null;\n    mount(slides[i]);\n"
    "    if (Q.has('rec')) { document.getAnimations().forEach(a => a.pause());"
    " if (window.__cur) window.__cur.tl.pause(0); window.__shown = i + 1; }\n  }\n",
)
SEEK_JS = f"""t => {{
  // the slide's own fade-in is left to PowerPoint's fade transition, so it is skipped here
  document.getAnimations().forEach(a => {{ const el = a.effect && a.effect.target;
    a.currentTime = el && el.classList && el.classList.contains('slide') ? 1e6 : t * 1000; }});
  const c = window.__cur;
  if (c) {{
    const lt = Math.max(0, t - {START_DELAY}) * {SPEED};
    c.tl.seek(Math.min(lt, c.tl.duration()), false);
    let k = 0; c.steps.forEach((_, j) => {{ if (c.tl.labels['s' + j] <= lt) k = j; }});
    c.setStep(k);
  }}
}}"""
DURATION_JS = f"""() => {{
  const c = window.__cur;
  return c ? {START_DELAY} + c.tl.duration() / {SPEED} : 0;
}}"""

work = Path(tempfile.mkdtemp(prefix="pptx_"))
rec_html = SRC.parent / "_rec_tmp.html"  # next to the deck so relative paths (img/) resolve
rec_html.write_text(rec_src, encoding="utf-8")
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

notes, videos, posters, durations = [], [], [], []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        pg = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        pg.goto(rec_html.as_uri() + "?rec=1#1")
        pg.wait_for_function("window.__shown === 1")
        n_slides = pg.evaluate("document.querySelectorAll('.slide').length")
        if len(sys.argv) > 3:  # optional: only the first k slides, for a quick check
            n_slides = min(n_slides, int(sys.argv[3]))
        for n in range(1, n_slides + 1):
            pg.goto(rec_html.as_uri() + f"?rec={n}#{n}")
            pg.wait_for_function(f"window.__shown === {n}")
            pg.evaluate("document.fonts.ready")
            raw = pg.evaluate(f"document.querySelectorAll('.slide')[{n - 1}].dataset.notes || ''")
            text = re.sub(r"<br\s*/?>", "\n", raw)
            notes.append(html.unescape(re.sub(r"<[^>]+>", "", text)).strip())
            total = max(CSS_SPAN, pg.evaluate(DURATION_JS)) + TAIL
            frames = int(round(total * FPS))
            fdir = work / f"s{n:02d}"
            fdir.mkdir()
            for f in range(frames):
                pg.evaluate(SEEK_JS, f / FPS)
                pg.screenshot(path=str(fdir / f"{f:05d}.png"))
            mp4 = work / f"s{n:02d}.mp4"
            subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error", "-framerate", str(FPS),
                 "-i", str(fdir / "%05d.png"), "-c:v", "libx264", "-preset", "slow",
                 "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)],
                check=True,
            )  # fmt: skip
            poster = work / f"s{n:02d}_poster.png"
            shutil.copy(fdir / "00000.png", poster)
            videos.append(mp4)
            posters.append(poster)
            durations.append(frames / FPS)
            print(f"slide {n:2d}: {frames} khung, {frames / FPS:.1f} s")
        browser.close()
finally:
    rec_html.unlink(missing_ok=True)

# ---------------------------------------------------------------------------------------------
# PowerPoint: one full-slide video per slide, autoplay, fade transition, speaker notes
# ---------------------------------------------------------------------------------------------
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
P = "{" + NS["p"] + "}"


def autoplay_timing(spid: int, ms: int) -> etree._Element:
    """Timing tree for 'start automatically' playback of the video with shape id ``spid``."""
    xml = f"""<p:timing xmlns:p="{NS["p"]}"><p:tnLst><p:par>
<p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>
<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>
<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>
<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>
<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold"
 nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{ms}" fill="hold"/>
<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>
</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>
</p:childTnLst></p:cTn>
<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>
</p:prevCondLst>
<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond>
</p:nextCondLst>
</p:seq>
<p:video><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold" display="0"><p:stCondLst>
<p:cond delay="indefinite"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>
</p:cMediaNode></p:video>
</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"""
    return etree.fromstring(xml)


FADE = etree.fromstring(f'<p:transition xmlns:p="{NS["p"]}" spd="med"><p:fade/></p:transition>')

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
blank = prs.slide_layouts[6]
for mp4, poster, text, dur in zip(videos, posters, notes, durations, strict=True):
    slide = prs.slides.add_slide(blank)
    movie = slide.shapes.add_movie(
        str(mp4), 0, 0, prs.slide_width, prs.slide_height,
        poster_frame_image=str(poster), mime_type="video/mp4",
    )  # fmt: skip
    root = slide._element
    for old in root.findall(P + "timing") + root.findall(P + "transition"):
        root.remove(old)
    # schema order inside p:sld: cSld, clrMapOvr, transition, timing, extLst
    anchor = root.find(P + "clrMapOvr")
    idx = list(root).index(anchor) + 1 if anchor is not None else len(root)
    root.insert(idx, copy.deepcopy(FADE))
    root.insert(idx + 1, autoplay_timing(movie.shape_id, int(dur * 1000)))
    slide.notes_slide.notes_text_frame.text = text

cp = prs.core_properties
cp.title = "Phát hiện ảo giác cho RAG tiếng Việt dựa trên tín hiệu chú ý nội tại"
cp.author = "Nguyễn Ngọc Lân, Nguyễn Tấn Minh"
cp.last_modified_by = "Nguyễn Ngọc Lân"
cp.comments = cp.keywords = cp.subject = cp.category = ""
prs.save(OUT)
shutil.rmtree(work, ignore_errors=True)
print(OUT, len(videos), "slide", f"{OUT.stat().st_size / 1e6:.1f} MB")
