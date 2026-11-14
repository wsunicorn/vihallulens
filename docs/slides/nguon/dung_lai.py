"""Rebuild the committee deck ``docs/slides/slide_hoi_dong.html`` from source, in one command.

The deck is built in three steps, each an exact string-replacement script that stops if its
source no longer matches:

  1. ``b1_rut_gon_19.py``  — the 32-slide deck of 02/10 (``slide_goc_32.html``) → 19 slides
  2. ``b2_bo_sung.py``     — four slides the advisor's outline asks for (``figs_bo_sung.js``) → 23
  3. ``b3_hoan_thien.py``  — academic titles and wording, agenda, part dividers, E19, stepping → 31

The two intermediate decks go to ``docs/slides/_build/``. ``--pdf`` also writes
``slide_hoi_dong.pdf``, the final state of every slide (``xuat_pdf.py``). The finished deck is
copied to ``UniversityRequirements/Reports/`` next to the thesis, under the submission name.

The deck is kept private like the thesis: the input deck ``slide_goc_32.html`` and every output
are gitignored and live only on the team's machines; the repository holds the build scripts.

The three build steps need only the standard library. The PDF export needs Google Chrome and
``uv run --no-project --with playwright==1.48.0 --with pymupdf==1.25.5 --with pillow``
in front of ``python docs/slides/nguon/dung_lai.py --pdf``.
"""

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK_DIR = HERE.parent
BUILD = DECK_DIR / "_build"
DECK = DECK_DIR / "slide_hoi_dong.html"
SUBMIT = DECK_DIR.parents[1] / "UniversityRequirements" / "Reports"
SUBMIT_NAME = "Slide_KLTN_22635801_22643511_PhatHienAoGiac"


def run(script: str, *args: Path | str) -> None:
    subprocess.run([sys.executable, str(HERE / script), *map(str, args)], check=True)


BUILD.mkdir(exist_ok=True)
run("b1_rut_gon_19.py", HERE / "slide_goc_32.html", BUILD / "slide_rut_gon_19.html")
run(
    "b2_bo_sung.py",
    BUILD / "slide_rut_gon_19.html",
    HERE / "figs_bo_sung.js",
    BUILD / "slide_hoi_dong_23.html",
)
run("b3_hoan_thien.py", BUILD / "slide_hoi_dong_23.html", DECK)
if "--pdf" in sys.argv:
    run("xuat_pdf.py", DECK, DECK.with_suffix(".pdf"))
if SUBMIT.is_dir():
    for out in (DECK, DECK.with_suffix(".pdf")):
        if out.exists():
            shutil.copy2(out, SUBMIT / (SUBMIT_NAME + out.suffix))
            print("chép", out.name, "→", SUBMIT / (SUBMIT_NAME + out.suffix))
