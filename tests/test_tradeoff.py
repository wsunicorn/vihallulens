"""Tests for the E11 accuracy-versus-cost table (task T32).

The one thing this table can get catastrophically wrong is reading the cost of the *classifier*
where it means the cost of the *reading model*. Those two numbers live in different files and
differ by five orders of magnitude — 0,003 ms against 437 ms — and both are labelled
``ms_per_sample``. A row that picks the wrong one looks entirely plausible and turns the central
claim of chapter 7 upside down.

So most of what is checked here is the join, not the arithmetic.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_tradeoff import build, doc_cost, latest_by_name, render  # noqa: E402


def feasibility_row(name, hours, n_vihallu, vram, ms_all):
    return {
        "run_name": name,
        "extra": {"peak_vram_mb": vram, "ms_per_sample": ms_all},
        "metrics": {
            "projected_hours": {"vihallu": hours},
            "tier_histogram": {"vihallu": {"0–512": n_vihallu}},
        },
    }


def scored_row(name, macro, ms, vram=0, params=100):
    return {
        "run_name": name,
        "metrics": {"macro_f1": macro, "macro_f1_lo": macro - 0.03, "macro_f1_hi": macro + 0.03},
        "extra": {"ms_per_sample": ms, "peak_vram_mb": vram, "n_params_trainable": params},
    }


@pytest.fixture
def feasibility():
    # One hour for 3.600 samples is exactly 1.000 ms each, so the arithmetic is checkable by eye.
    return latest_by_name([
        feasibility_row("t31_chiphi_7B_lan1", 1.0, 3600, 8328, 726.6),
        feasibility_row("t31_chiphi_7B_lan2", 2.0, 3600, 8328, 741.7),
    ])


def test_doc_cost_averages_the_interleaved_passes(feasibility):
    """Both passes count. Taking only the first would hide exactly the drift they measure."""
    cost = doc_cost(feasibility, "7B")

    assert cost["n_luot"] == 2
    assert cost["ms"] == pytest.approx(1500.0)  # mean of 1.000 and 2.000
    assert cost["vram_mb"] == 8328


def test_doc_cost_reports_the_spread_between_passes(feasibility):
    """The gap between the two passes is the drift figure, so it is carried, not averaged away."""
    cost = doc_cost(feasibility, "7B")

    assert cost["troi_pct"] == pytest.approx((741.7 - 726.6) / 726.6 * 100)


def test_unmeasured_reading_model_stays_unmeasured(feasibility):
    """Sailor2 was extracted but never timed. Borrowing a similar model's number is worse."""
    assert doc_cost(feasibility, "sailor2") is None


def test_attention_row_takes_the_reading_cost_not_the_classifier_cost(feasibility):
    """The whole point of the join: 0,010 ms is the classifier, 1.500 ms is the method."""
    runs = latest_by_name([scored_row("e02_lookback_lens", 0.7451, ms=0.010, vram=0, params=2271)])

    row = next(r for r in build(runs, feasibility) if r["run_name"] == "e02_lookback_lens")

    assert row["ms_moi_mau"] == pytest.approx(1500.0)
    assert row["vram_mb"] == 8328          # not the classifier's 0
    assert row["ms_bo_phan_loai"] == 0.010  # kept, but in its own column


def test_row_without_a_reading_model_keeps_its_own_cost(feasibility):
    """XLM-R has no reading model, so its 25,2 ms is the whole story and must survive."""
    runs = latest_by_name([scored_row("e09_xlmr", 0.7762, ms=25.197, vram=11231, params=559)])

    row = next(r for r in build(runs, feasibility) if r["run_name"] == "e09_xlmr")

    assert row["ms_moi_mau"] == pytest.approx(25.197)
    assert row["vram_mb"] == 11231
    assert row["ms_bo_phan_loai"] is None


def test_marginal_cost_is_zero_only_for_attention_rows(feasibility):
    """The marginal-cost argument applies where a RAG system already pays for the read."""
    runs = latest_by_name([
        scored_row("e02_lookback_lens", 0.7451, ms=0.010),
        scored_row("e09_xlmr", 0.7762, ms=25.197),
    ])

    table = {r["run_name"]: r for r in build(runs, feasibility)}

    assert table["e02_lookback_lens"]["ms_bien"] == 0.0
    assert table["e09_xlmr"]["ms_bien"] == pytest.approx(25.197)


def test_two_rows_sharing_one_extraction_get_one_cost(feasibility):
    """E02 and E03 read the same shard, so they cannot cost different amounts.

    The old Bảng 1 listed 464 ms and 528 ms for these two rows — two numbers for one extraction.
    Deriving both from the same reading model makes that impossible to write again.
    """
    runs = latest_by_name([
        scored_row("e02_lookback_lens", 0.7451, ms=0.010),
        scored_row("e03_chunk_aware", 0.7567, ms=0.003),
    ])

    table = {r["run_name"]: r for r in build(runs, feasibility)}

    assert table["e02_lookback_lens"]["ms_moi_mau"] == table["e03_chunk_aware"]["ms_moi_mau"]


def test_missing_scored_run_is_skipped_not_faked(feasibility):
    """An experiment that has not run yet leaves no row, rather than a row of zeros."""
    table = build(latest_by_name([scored_row("e09_xlmr", 0.7762, ms=25.2)]), feasibility)

    assert [r["run_name"] for r in table] == ["e09_xlmr"]


def test_render_marks_unmeasured_cost_in_words(feasibility):
    """A blank cell reads as zero to a hurried reader; 'chưa đo' cannot."""
    runs = latest_by_name([scored_row("e13_sailor2_vihallu", 0.7120, ms=0.006)])

    text = render(build(runs, feasibility))

    assert "chưa đo" in text
    assert "0.7120" in text


def test_latest_run_wins():
    """Re-scoring an experiment updates the table instead of adding a second row for it."""
    table = latest_by_name([scored_row("e03_chunk_aware", 0.70, 1.0),
                            scored_row("e03_chunk_aware", 0.7567, 2.0)])

    assert table["e03_chunk_aware"]["metrics"]["macro_f1"] == 0.7567
