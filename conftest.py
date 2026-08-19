"""Make the package importable from the checkout, with or without an editable install.

Kaggle installs the project with ``pip install -e .`` inside an already running kernel, and
an editable install works through a ``.pth`` file that Python only reads at interpreter
start-up. Pointing at ``src`` here means the tests run against the checked-out code in every
environment, which is also what makes them meaningful.
"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
