"""Tests for dropping records whose features are not finite (task T30).

Measured at T30 with Sailor2-8B: 49 of 7.000 ViHallu samples came out with *every* layer
non-finite. Qwen2.5-7B overflows at one layer on every sample, which excluding that layer fixes
for everyone; Sailor2 overflows on every layer for a few samples, which no layer exclusion can
fix. So those rows have to be dropped — and the danger of dropping is that it moves a
denominator without anyone noticing, which is what these tests guard.
"""

from __future__ import annotations

import numpy as np

from vihallulens.features.assemble import drop_nonfinite


def record(sample_id, total, drift=None):
    row = {"sample_id": sample_id, "lookback_total": total}
    if drift is not None:
        row["chunk_drift"] = drift
    return row


def test_clean_records_all_survive():
    records = [record("a", [0.1, 0.2]), record("b", [0.3, 0.4])]

    clean, dropped = drop_nonfinite(records)

    assert len(clean) == 2
    assert dropped == []


def test_nan_and_inf_are_both_dropped():
    records = [
        record("ok", [0.1, 0.2]),
        record("nan", [0.1, np.nan]),
        record("inf", [np.inf, 0.2]),
    ]

    clean, dropped = drop_nonfinite(records)

    assert [r["sample_id"] for r in clean] == ["ok"]
    assert [r["sample_id"] for r in dropped] == ["nan", "inf"]


def test_the_two_halves_always_add_back_to_the_input():
    """The count the caller reports has to be the count that actually left."""
    records = [record(str(i), [0.1, np.nan if i % 3 == 0 else 0.2]) for i in range(30)]

    clean, dropped = drop_nonfinite(records)

    assert len(clean) + len(dropped) == len(records)
    assert {r["sample_id"] for r in clean} | {r["sample_id"] for r in dropped} == {
        str(i) for i in range(30)
    }


def test_order_is_preserved_so_labels_stay_aligned():
    """Labels are built from the same list, so reordering here would mislabel every row."""
    records = [record(str(i), [0.1, 0.2]) for i in range(5)]

    clean, _ = drop_nonfinite(records)

    assert [r["sample_id"] for r in clean] == ["0", "1", "2", "3", "4"]


def test_extra_blocks_are_checked_when_asked():
    """A row can be finite in lookback_total and broken in a chunk statistic."""
    records = [record("a", [0.1, 0.2], drift=[0.0, np.nan])]

    default_clean, default_dropped = drop_nonfinite(records)
    wide_clean, wide_dropped = drop_nonfinite(records, blocks=("lookback_total", "chunk_drift"))

    assert len(default_clean) == 1 and not default_dropped
    assert not wide_clean and len(wide_dropped) == 1


def test_a_record_missing_the_block_is_kept_rather_than_guessed_at():
    """Absence is not corruption; dropping it here would silently shrink other experiments."""
    clean, dropped = drop_nonfinite([{"sample_id": "a"}])

    assert len(clean) == 1
    assert dropped == []
