"""Append-only experiment log and table export.

Section 3 of ``CLAUDE.md`` rules out hosted trackers: every result lives in
``results/runs.jsonl``, one JSON object per line, committed to the repository. The file is
append-only so a finished run is never rewritten by a later one.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from vihallulens.config import hash_config_dict

DEFAULT_RESULTS_PATH = Path("results/runs.jsonl")

# Section 3 of docs/EXPERIMENTS.md: every method must report these, so a run without them is
# not comparable and is rejected at write time rather than discovered missing at report time.
REQUIRED_EXTRA_KEYS = ("ms_per_sample", "peak_vram_mb")

UNKNOWN_COMMIT = "unknown"


def _git_commit() -> str:
    """Short hash of the current commit, or "unknown" outside a working repository."""
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return UNKNOWN_COMMIT
    return completed.stdout.strip() or UNKNOWN_COMMIT


def log_result(
    run_name: str,
    config: dict[str, Any],
    metrics: dict[str, Any],
    extra: dict[str, Any],
    path: str | Path = DEFAULT_RESULTS_PATH,
) -> dict[str, Any]:
    """Append one run to the results file and return the record that was written.

    ``extra`` must carry ``ms_per_sample`` and ``peak_vram_mb``; a run missing either cannot
    be placed in the accuracy-versus-cost table and is refused here.
    """
    missing = [key for key in REQUIRED_EXTRA_KEYS if key not in extra]
    if missing:
        raise ValueError(
            f"extra is missing required key(s): {', '.join(missing)}. "
            f"Section 3 of docs/EXPERIMENTS.md requires {', '.join(REQUIRED_EXTRA_KEYS)} "
            f"for every method."
        )

    record = {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "run_name": run_name,
        "git_commit": _git_commit(),
        "config_hash": hash_config_dict(config),
        "config": config,
        "metrics": metrics,
        "extra": extra,
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def read_results(path: str | Path = DEFAULT_RESULTS_PATH) -> pd.DataFrame:
    """Read the whole results file into a flat frame, one row per run.

    Nested objects become dotted columns: ``config.dataset.name``, ``metrics.macro_f1``,
    ``extra.ms_per_sample``. Returns an empty frame when the file does not exist yet.
    """
    path = Path(path)
    if not path.is_file():
        return pd.DataFrame()
    with path.open(encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    if not records:
        return pd.DataFrame()
    return pd.json_normalize(records)


def export_table(
    filter: dict[str, Any] | None = None,  # noqa: A002 - name fixed by docs/SPEC.md
    columns: list[str] | None = None,
    path: str | Path = DEFAULT_RESULTS_PATH,
) -> pd.DataFrame:
    """Select runs and columns for pasting into the report.

    ``filter`` matches on exact equality using the dotted column names produced by
    :func:`read_results`, for example ``{"config.dataset.name": "vihallu"}``. ``columns``
    keeps only the listed columns, in the order given. A requested column that no run has
    yet is created empty rather than raising, so a half-filled result table still exports.
    """
    frame = read_results(path)
    if frame.empty:
        return pd.DataFrame(columns=columns) if columns else frame

    for key, value in (filter or {}).items():
        if key not in frame.columns:
            return frame.iloc[0:0][columns] if columns else frame.iloc[0:0]
        frame = frame[frame[key] == value]

    if columns:
        for column in columns:
            if column not in frame.columns:
                frame[column] = pd.NA
        frame = frame[columns]
    return frame.reset_index(drop=True)
