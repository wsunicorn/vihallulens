"""The one hypothesis test in the thesis, checked against cases with known answers.

E06's conclusion about NEI rests on this function, and it is hand-written rather than imported,
so it needs to be pinned against results that can be worked out independently.
"""

import numpy as np
import pytest

from vihallulens.evaluation.stats import describe_effect, mann_whitney


def test_two_identical_groups_show_no_effect():
    values = np.arange(100, dtype=float)
    out = mann_whitney(values, values)
    assert out["effect"] == pytest.approx(0.0, abs=1e-9)
    assert out["probability_superior"] == pytest.approx(0.5)
    assert out["p_value"] > 0.99


def test_a_group_entirely_above_the_other_gives_effect_one():
    out = mann_whitney(np.arange(50, 100, dtype=float), np.arange(0, 50, dtype=float))
    assert out["effect"] == pytest.approx(1.0)
    assert out["probability_superior"] == pytest.approx(1.0)
    assert out["p_value"] < 1e-9


def test_the_effect_is_signed():
    """A negative effect has to mean ``a`` sits below ``b``, or E06 could report its hypothesis
    confirmed while the data said the opposite."""
    out = mann_whitney(np.arange(0, 50, dtype=float), np.arange(50, 100, dtype=float))
    assert out["effect"] == pytest.approx(-1.0)


def test_a_large_sample_makes_a_trivial_difference_significant():
    """The reason the write-up is required to lead with the effect size. Two groups differing by
    a twentieth of a standard deviation come out significant at this size and mean nothing."""
    rng = np.random.default_rng(0)
    out = mann_whitney(rng.normal(0.05, 1.0, 20000), rng.normal(0.0, 1.0, 20000))
    assert out["p_value"] < 0.05
    assert abs(out["effect"]) < 0.11
    assert describe_effect(out["effect"]) == "không đáng kể"


def test_ties_do_not_break_the_ranking():
    """Entropy is rounded to six decimals before it is stored, so exact ties are common."""
    out = mann_whitney(np.full(60, 0.5), np.full(60, 0.5))
    assert out["effect"] == pytest.approx(0.0)
    assert out["p_value"] == pytest.approx(1.0)


def test_a_group_too_small_for_the_approximation_is_refused():
    with pytest.raises(ValueError, match="ít nhất 20"):
        mann_whitney(np.arange(5.0), np.arange(50.0))


def test_the_u_statistic_matches_a_worked_example():
    """Three values against three, computed by hand: a = [3, 5, 7], b = [1, 2, 6]. Pairs where a
    beats b: 3>1, 3>2, 5>1, 5>2, 7>1, 7>2, 7>6 — seven of nine."""
    a = np.array([3.0, 5.0, 7.0] * 10)
    b = np.array([1.0, 2.0, 6.0] * 10)
    out = mann_whitney(a, b)
    assert out["probability_superior"] == pytest.approx(7 / 9, abs=0.02)


def test_the_medians_come_back_for_the_write_up():
    out = mann_whitney(np.arange(0, 100, dtype=float), np.arange(50, 150, dtype=float))
    assert out["median_a"] == pytest.approx(49.5)
    assert out["median_b"] == pytest.approx(99.5)


@pytest.mark.parametrize(
    ("effect", "word"),
    [(0.05, "không đáng kể"), (0.2, "nhỏ"), (0.35, "vừa"), (0.6, "lớn"), (-0.6, "lớn")],
)
def test_the_effect_is_put_into_words(effect, word):
    assert describe_effect(effect) == word
