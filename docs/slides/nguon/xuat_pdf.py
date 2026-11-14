"""Export the committee deck to PDF: one page per slide, each slide in its final state.

Chrome (through Playwright, ``channel="chrome"``) opens the deck with ``?all`` so every diagram
shows its last step, screenshots each slide at 1920 x 1080, and the shots become 960 x 540 pt
pages. The PDF carries a title only, no creator or producer metadata.

Run through ``dung_lai.py --pdf``, or alone with
``python xuat_pdf.py ../slide_hoi_dong.html ../slide_hoi_dong.pdf`` under the packages named in
the docstring of ``dung_lai.py``.
"""

import io
import sys
from pathlib import Path

import pymupdf
from PIL import Image
from playwright.sync_api import sync_playwright

SRC, OUT = (Path(p).resolve() for p in sys.argv[1:3])

doc = pymupdf.open()
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome")
    pg = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.goto(SRC.as_uri() + "?all#1")
    pg.wait_for_function("document.querySelector('.slide.active') !== null")
    n_slides = pg.evaluate("document.querySelectorAll('.slide').length")
    for n in range(1, n_slides + 1):
        pg.goto(SRC.as_uri() + f"?all&p={n}#{n}")  # the query change forces a fresh load
        active = f"document.querySelectorAll('.slide')[{n - 1}].classList.contains('active')"
        pg.wait_for_function(active)
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        shot = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
        buf = io.BytesIO()
        shot.save(buf, "JPEG", quality=90)
        page = doc.new_page(width=960, height=540)
        page.insert_image(page.rect, stream=buf.getvalue())
    browser.close()

blank = dict.fromkeys(("author", "subject", "keywords", "creator", "producer"), "")
doc.set_metadata({"title": OUT.stem, **blank})
doc.save(OUT, garbage=4, deflate=True)
print(OUT, doc.page_count, "trang", f"{OUT.stat().st_size / 1e6:.1f} MB")
