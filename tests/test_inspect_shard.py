"""Tests for the shard diagnosis added at T30.

The T30 Sailor2 run wrote 7.000 records with zero errors and then failed its integrity check on
"huu han False". This module exists so the next such failure arrives with numbers attached
instead of a boolean.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from inspect_shard import BOUNDED, inspect  # noqa: E402


def record(sample_id, nonfinite=(), total=None, drift=None):
    return {
        "sample_id": sample_id,
        "layer_indices": [0, 1, 2],
        "nonfinite_layers": list(nonfinite),
        "lookback_total": total if total is not None else [0.5] * 6,
        "chunk_drift": drift if drift is not None else [0.1] * 6,
    }


def test_counts_samples_and_layers_separately():
    """One sample breaking two layers is one sample, two layer hits."""
    report = inspect([
        record("a", nonfinite=[30, 31]),
        record("b"),
        record("c", nonfinite=[31]),
    ])

    assert report["n_records"] == 3
    assert report["affected"] == 2
    assert dict(report["layer_counts"]) == {30: 1, 31: 2}


def test_a_clean_shard_reports_nothing_broken():
    report = inspect([record("a"), record("b")])

    assert report["affected"] == 0
    assert not report["layer_counts"]
    assert report["blocks"]["lookback_total"]["n_nonfinite"] == 0


def test_nonfinite_values_are_counted_per_value_and_per_row():
    total = [0.5, np.nan, 0.5, np.inf, 0.5, 0.5]
    report = inspect([record("a", total=total), record("b")])

    entry = report["blocks"]["lookback_total"]
    assert entry["n_nonfinite"] == 2
    assert entry["rows_with_nonfinite"] == 1


def test_out_of_range_is_reported_for_bounded_blocks():
    """lookback_total is a ratio; anything outside [0, 1] means the arithmetic went wrong."""
    report = inspect([record("a", total=[0.5, 1.5, -0.2, 0.5, 0.5, 0.5])])

    entry = report["blocks"]["lookback_total"]
    assert entry["n_out_of_range"] == 2
    assert entry["rows_out_of_range"] == 1


def test_chunk_drift_is_never_called_out_of_range():
    """Drift is a change between steps, so negative is normal and must not be flagged."""
    report = inspect([record("a", drift=[-0.4, 0.2, -0.1, 0.0, 0.3, -0.9])])

    assert "chunk_drift" not in BOUNDED
    assert "n_out_of_range" not in report["blocks"]["chunk_drift"]
    assert report["blocks"]["chunk_drift"]["n_nonfinite"] == 0


def test_nonfinite_is_still_caught_in_unbounded_blocks():
    report = inspect([record("a", drift=[-0.4, np.nan, 0.0, 0.0, 0.0, 0.0])])

    assert report["blocks"]["chunk_drift"]["n_nonfinite"] == 1
