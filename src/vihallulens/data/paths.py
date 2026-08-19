"""Locating the raw data directory.

The same four files sit in different places depending on where the code runs: ``data/raw``
on a laptop, and somewhere under ``/kaggle/input`` in a notebook, where the exact mount point
depends on how the dataset was attached. Rather than hard-coding a guess that breaks on the
other machine, the directory is found by looking for a file that only this dataset has.
"""

from __future__ import annotations

import os
from pathlib import Path

# Present in the dataset and nowhere else, so finding it identifies the directory.
MARKER_FILE = "vihallu_train.csv"

ENV_VAR = "VIHALLULENS_DATA_DIR"
LOCAL_DEFAULT = Path("data/raw")
KAGGLE_ROOT = Path("/kaggle/input")

# Kaggle has mounted attached datasets at both of these over time, so try both rather than
# betting on one: /kaggle/input/<slug>/ and /kaggle/input/datasets/<owner>/<slug>/.
KAGGLE_PATTERNS = ("*", "*/*", "datasets/*/*", "*/*/*")


def candidate_dirs() -> list[Path]:
    """Every place worth looking, in priority order."""
    candidates: list[Path] = []
    from_env = os.environ.get(ENV_VAR)
    if from_env:
        candidates.append(Path(from_env))
    candidates.append(LOCAL_DEFAULT)
    if KAGGLE_ROOT.is_dir():
        candidates.append(KAGGLE_ROOT)
        for pattern in KAGGLE_PATTERNS:
            candidates.extend(sorted(path for path in KAGGLE_ROOT.glob(pattern) if path.is_dir()))
    return candidates


def find_raw_dir(explicit: str | Path | None = None) -> Path:
    """Return the directory holding the raw files, or raise with the places already tried.

    An explicit path always wins, even without the marker file, so a deliberate pointer at a
    partial copy works. It is never silently replaced by a guess: falling back to some other
    directory would run the experiment on data the caller never asked for.
    """
    if explicit is not None:
        path = Path(explicit)
        if path.is_dir():
            return path
        raise FileNotFoundError(f"the directory given as --data-dir does not exist: {path}")

    candidates = candidate_dirs()
    for candidate in candidates:
        if (candidate / MARKER_FILE).is_file():
            return candidate
    tried = "\n  ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"could not find {MARKER_FILE}. Set {ENV_VAR} or pass --data-dir. Tried:\n  {tried}"
    )
