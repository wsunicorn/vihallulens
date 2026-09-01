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


# -- the paired test E08 needs -------------------------------------------------------------------


def test_every_pair_moving_up_gives_the_maximum_effect():
    from vihallulens.evaluation.stats import wilcoxon

    base = np.random.default_rng(0).normal(0, 1, 200)
    out = wilcoxon(base, base + 0.5)
    assert out["win_rate"] == 1.0
    assert out["effect"] == pytest.approx(1.0)


def test_the_effect_is_signed_for_pairs_too():
    """A drop has to report as a drop, or E08 could announce its hypothesis confirmed while the
    attention actually became *less* diffuse."""
    from vihallulens.evaluation.stats import wilcoxon

    base = np.random.default_rng(0).normal(0, 1, 200)
    assert wilcoxon(base, base - 0.5)["effect"] == pytest.approx(-1.0)


def test_a_uniform_but_trivial_shift_still_maxes_the_effect_size():
    """The trap this pins down. A paired test measures how *consistently* pairs move, not how
    far, so a shift of a fiftieth of a standard deviation reports win_rate 1,0 and effect 1,0.
    The report must therefore print median_change beside them, and the write-up must read both."""
    from vihallulens.evaluation.stats import wilcoxon

    base = np.random.default_rng(0).normal(0, 1, 500)
    out = wilcoxon(base, base + 0.02)
    assert out["win_rate"] == 1.0
    assert out["effect"] == pytest.approx(1.0)
    assert out["median_change"] == pytest.approx(0.02, abs=1e-9)


def test_pure_noise_moves_about_half_the_pairs():
    from vihallulens.evaluation.stats import wilcoxon

    rng = np.random.default_rng(1)
    base = rng.normal(0, 1, 2000)
    out = wilcoxon(base, base + rng.normal(0, 1, 2000))
    assert 0.45 < out["win_rate"] < 0.55
    assert describe_effect(out["effect"]) == "không đáng kể"


def test_mismatched_pair_counts_are_refused():
    """Two arrays of different length are not pairs, and silently zipping them would compare
    unrelated samples while looking perfectly healthy."""
    from vihallulens.evaluation.stats import wilcoxon

    with pytest.raises(ValueError, match="cùng số cặp"):
        wilcoxon(np.arange(50.0), np.arange(40.0))


def test_ties_are_dropped_and_counted():
    from vihallulens.evaluation.stats import wilcoxon

    base = np.arange(100.0)
    after = base.copy()
    after[:60] += 1.0
    out = wilcoxon(base, after)
    assert out["n_pairs"] == 100
    assert out["n_tied"] == 40
    assert out["win_rate"] == 1.0
