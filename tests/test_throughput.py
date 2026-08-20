"""The arithmetic behind the task T08 projection.

Everything here runs on the CPU in milliseconds. The GPU measurement itself cannot be tested,
but the step that turns 80 timed samples into "N hours of GPU time" can be, and that is the
step whose result decides the schedule.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from measure_throughput import (  # noqa: E402
    TIER_BOUNDS,
    assign_tier,
    format_duration,
    log_log_slope,
    parse_telemetry,
    pick_tier_samples,
    project_seconds,
    spread,
    throttling_verdict,
    tier_label,
    tiers_without_truncation,
)


def sample(n_tokens: int) -> dict:
    return {"context": "x", "question": "", "response": "y", "n_tokens": n_tokens}


# -- tiers -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("n_tokens", "expected"),
    [(1, 0), (512, 0), (513, 1), (1024, 1), (1025, 2), (2048, 2), (2049, 3), (4096, 3)],
)
def test_tier_boundaries_are_inclusive_at_the_top(n_tokens, expected):
    assert assign_tier(n_tokens) == expected


def test_samples_longer_than_the_budget_fall_into_the_top_tier():
    """They are truncated to the budget before the forward pass, so they cost top-tier price."""
    assert assign_tier(6622) == len(TIER_BOUNDS) - 1


def test_tier_labels_do_not_overlap():
    labels = [tier_label(index) for index in range(len(TIER_BOUNDS))]
    assert labels == ["0–512", "513–1024", "1025–2048", "2049–4096"]


# -- sample selection --------------------------------------------------------------------


def test_spread_keeps_both_ends():
    picked = spread(list(range(100)), 5)
    assert picked[0] == 0
    assert picked[-1] == 99
    assert len(picked) == 5


def test_spread_returns_everything_when_the_pool_is_small():
    assert spread([3, 7], 20) == [3, 7]


def test_spread_is_deterministic():
    assert spread(list(range(57)), 9) == spread(list(range(57)), 9)


def test_picked_samples_stay_inside_their_tier():
    pool = [sample(n) for n in range(1, 4097, 7)]
    chosen = pick_tier_samples(pool, per_tier=5)
    for tier, members in chosen.items():
        assert len(members) == 5
        assert all(assign_tier(item["n_tokens"]) == tier for item in members)


def test_picked_samples_span_the_tier_rather_than_bunching_at_one_end():
    """Timing only the short members of a tier would understate every projection built on it."""
    pool = [sample(n) for n in range(1025, 2049)]
    members = pick_tier_samples(pool, per_tier=20)[2]
    assert min(item["n_tokens"] for item in members) == 1025
    assert max(item["n_tokens"] for item in members) == 2048


def test_an_empty_tier_yields_an_empty_list_rather_than_raising():
    chosen = pick_tier_samples([sample(100)], per_tier=20)
    assert chosen[0] and chosen[1] == [] and chosen[3] == []


# -- projection --------------------------------------------------------------------------


def test_projection_multiplies_counts_by_tier_cost():
    seconds = project_seconds({0: 10, 1: 5}, {0: 1.0, 1: 2.0})
    assert seconds == pytest.approx(20.0)


def test_projection_skips_tiers_that_were_never_timed():
    """A missing tier must not be silently priced at zero-by-multiplication; it is dropped,
    and the script warns about it separately."""
    assert project_seconds({0: 10, 3: 999}, {0: 1.0}) == pytest.approx(10.0)


def test_projection_of_an_empty_corpus_is_zero():
    assert project_seconds({}, {0: 1.0}) == 0.0


# -- scaling exponent --------------------------------------------------------------------


def test_quadratic_cost_gives_an_exponent_near_two():
    lengths = [256.0, 512.0, 1024.0, 2048.0]
    costs = [length**2 for length in lengths]
    assert log_log_slope(lengths, costs) == pytest.approx(2.0, abs=1e-6)


def test_linear_cost_gives_an_exponent_near_one():
    lengths = [256.0, 512.0, 1024.0, 2048.0]
    costs = [3.0 * length for length in lengths]
    assert log_log_slope(lengths, costs) == pytest.approx(1.0, abs=1e-6)


def test_truncated_tiers_are_kept_out_of_the_fit():
    """A truncated sample runs at the token budget, not at the length that sorted it into a
    tier, so fitting cost against that length describes a run that never happened. Measured at
    T08: including them turned a clean k = 1.00 into a meaningless 0.85."""
    summaries = {
        0: {"n_truncated": 0, "mean_tokens": 371.0, "median_ms": 389.0},
        3: {"n_truncated": 20, "mean_tokens": 2492.0, "median_ms": 2080.0},
    }
    assert sorted(tiers_without_truncation(summaries)) == [0]


def test_a_tier_with_one_truncated_sample_is_still_dropped():
    summaries = {0: {"n_truncated": 1, "mean_tokens": 371.0, "median_ms": 389.0}}
    assert tiers_without_truncation(summaries) == {}


def test_a_single_tier_cannot_give_a_slope():
    assert log_log_slope([512.0], [100.0]) != log_log_slope([512.0], [100.0])  # nan != nan


# -- formatting --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0, "0 giờ 00 phút"), (90, "0 giờ 01 phút"), (3600, "1 giờ 00 phút"), (7380, "2 giờ 03 phút")],
)
def test_duration_is_reported_in_hours_and_minutes(seconds, expected):
    assert format_duration(seconds) == expected


# -- GPU telemetry -----------------------------------------------------------------------


def reading(clock_ratio: float, temperature: float) -> dict:
    return {"clock_ratio": clock_ratio, "temperature_c": temperature}


def test_telemetry_row_is_parsed_into_numbers():
    item = parse_telemetry("62, 1440, 1590, 98")
    assert item["temperature_c"] == 62
    assert item["sm_clock_mhz"] == 1440
    assert item["clock_ratio"] == pytest.approx(1440 / 1590)


def test_a_field_the_card_does_not_expose_yields_nothing():
    """nvidia-smi answers "[N/A]" instead of failing, so success is not proof of a reading."""
    assert parse_telemetry("[N/A], 1440, 1590, 98") is None


def test_a_row_with_the_wrong_number_of_fields_yields_nothing():
    assert parse_telemetry("62, 1440") is None


def test_a_falling_clock_with_rising_heat_is_reported_as_throttling():
    throttled, reason = throttling_verdict([reading(1.0, 45.0), reading(0.88, 78.0)])
    assert throttled
    assert "nhiệt" in reason


def test_an_idle_but_steady_clock_is_not_throttling():
    """A card at rest down-clocks on purpose. Judging one low reading as throttling would flag
    every session; only the trend across the session carries information."""
    throttled, _ = throttling_verdict([reading(0.71, 44.0), reading(0.71, 46.0)])
    assert not throttled


def test_heat_without_a_clock_drop_is_reported_but_not_flagged():
    throttled, reason = throttling_verdict([reading(1.0, 40.0), reading(1.0, 70.0)])
    assert not throttled
    assert "chưa tụt" in reason


def test_a_single_reading_cannot_support_a_verdict():
    throttled, reason = throttling_verdict([reading(1.0, 45.0)])
    assert not throttled
    assert "không đủ" in reason
