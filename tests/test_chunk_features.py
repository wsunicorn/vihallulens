"""The five chunk-aware features — the contribution of the thesis.

Task T21 asks for tests with inputs whose answers are known by hand, and that is what these are:
every expected value below is derivable on paper, so a change in behaviour is a change in the
definition rather than a drift in a number nobody can check.

The two normalisation decisions get the most attention, because they are the same class of
mistake as "sum instead of mean" in the original Lookback Lens formula: getting them wrong
produces a full matrix of plausible values while the classifier quietly learns context length.
"""

import numpy as np
import pytest

from vihallulens.features.chunk_aware import (
    CHUNK_FEATURE_NAMES,
    chunk_drift,
    chunk_entropy,
    chunk_features,
    chunk_gini,
    chunk_max_share,
    chunk_shares,
    feature_names,
    sample_vector,
    top1_top2_gap,
)


def one_step(*weights):
    """A single (layer, head, token) slice carrying the given per-chunk weights."""
    return np.asarray(weights, dtype=np.float64).reshape(1, 1, 1, -1)


def steps(*rows):
    """One layer, one head, several tokens."""
    return np.asarray(rows, dtype=np.float64).reshape(1, 1, len(rows), -1)


# -- normalising to a distribution ---------------------------------------------------------


def test_densities_become_a_distribution():
    """The extractor hands over attention *densities*, which do not sum to one. Every statistic
    here describes the shape of a distribution, so the normalisation happens once, here, rather
    than being assumed independently by four functions."""
    shares = chunk_shares(one_step(2.0, 6.0))
    assert shares.sum(axis=-1) == pytest.approx(1.0)
    assert shares.ravel() == pytest.approx([0.25, 0.75])


def test_scaling_every_chunk_changes_nothing():
    """A head that attends twice as hard everywhere has the same *shape*. If this failed, the
    features would be measuring how much attention went to the context — which is E02's job,
    already done, and not what this module is for."""
    assert chunk_shares(one_step(1.0, 3.0)) == pytest.approx(chunk_shares(one_step(10.0, 30.0)))


def test_a_head_that_looked_at_nothing_is_read_as_uniform():
    """Not nan. Nothing was looked at, so nothing was preferred; every shape statistic then
    reports "maximally spread" instead of poisoning the whole sample."""
    shares = chunk_shares(one_step(0.0, 0.0, 0.0, 0.0))
    assert shares.ravel() == pytest.approx(0.25)


def test_a_wrong_shape_is_rejected():
    with pytest.raises(ValueError, match="lớp, đầu, token, đoạn"):
        chunk_shares(np.zeros((27, 28, 10)))


def test_a_sample_with_no_chunks_is_rejected():
    with pytest.raises(ValueError, match="không có đoạn"):
        chunk_shares(np.zeros((1, 1, 1, 0)))


# -- entropy, and the normalisation that keeps it honest ------------------------------------


def test_all_attention_on_one_chunk_gives_zero_entropy():
    assert chunk_entropy(chunk_shares(one_step(1.0, 0.0, 0.0, 0.0))) == pytest.approx(0.0)


def test_perfectly_even_attention_gives_one():
    assert chunk_entropy(chunk_shares(one_step(1.0, 1.0, 1.0, 1.0))) == pytest.approx(1.0)


def test_entropy_does_not_grow_with_the_number_of_chunks():
    """The decision this test exists for. Raw entropy tops out at ln(n_chunks), so a context cut
    into 23 pieces would outscore one cut into 5 however the attention was spread — and samples
    differ enormously: ViHallu averages 5,3 chunks, ISE-DSC01 22,8, measured at T15. Unnormalised,
    the feature would largely encode context length, exactly the trap the original formula avoids
    by averaging per token instead of summing."""
    for n_chunks in (2, 5, 23, 60):
        even = chunk_shares(one_step(*([1.0] * n_chunks)))
        assert chunk_entropy(even) == pytest.approx(1.0)


def test_half_the_mass_on_half_the_chunks():
    """Two of four chunks share everything: entropy ln(2)/ln(4) = 0,5 exactly."""
    assert chunk_entropy(chunk_shares(one_step(1.0, 1.0, 0.0, 0.0))) == pytest.approx(0.5)


def test_a_single_chunk_scores_zero_not_undefined():
    """ln(1) is 0 and the division would be 0/0. One chunk means one place to look, so the
    spread is as concentrated as it can be. Not a rare case: 15,3 % of ViWikiFC contexts,
    measured at T15."""
    assert chunk_entropy(chunk_shares(one_step(1.0))) == pytest.approx(0.0)


# -- the leading chunk ----------------------------------------------------------------------


def test_max_share_is_the_largest_share():
    assert chunk_max_share(chunk_shares(one_step(1.0, 3.0, 0.0))) == pytest.approx(0.75)


def test_the_gap_separates_one_favourite_from_two():
    """What max_share alone cannot tell apart: attention committed to one piece of evidence,
    and attention split between two plausible ones. Both have the same leader."""
    committed = chunk_shares(one_step(8.0, 1.0, 1.0))
    split = chunk_shares(one_step(8.0, 8.0, 4.0))
    assert chunk_max_share(committed) > chunk_max_share(split)
    assert top1_top2_gap(committed) == pytest.approx(0.7)
    assert top1_top2_gap(split) == pytest.approx(0.0)


def test_the_gap_with_one_chunk_is_the_whole_distribution():
    assert top1_top2_gap(chunk_shares(one_step(1.0))) == pytest.approx(1.0)


# -- Gini ------------------------------------------------------------------------------------


def test_even_attention_has_no_inequality():
    assert chunk_gini(chunk_shares(one_step(1.0, 1.0, 1.0, 1.0))) == pytest.approx(0.0)


def test_all_on_one_chunk_is_maximal_inequality():
    """Uncorrected, the coefficient stops at (n-1)/n and would encode chunk count the same way
    raw entropy does. The small-sample correction puts the maximum at 1 for every n."""
    for n_chunks in (2, 5, 23):
        weights = [0.0] * n_chunks
        weights[0] = 1.0
        assert chunk_gini(chunk_shares(one_step(*weights))) == pytest.approx(1.0)


def test_gini_matches_a_hand_computation():
    """Shares [0, 0, 0.5, 0.5] sorted ascending. Weighted sum 0·1+0·2+0,5·3+0,5·4 = 3,5;
    raw = 2·3,5/4 − 5/4 = 0,5; corrected = 0,5 · 4/3 = 0,6667."""
    assert chunk_gini(chunk_shares(one_step(0.0, 0.0, 1.0, 1.0))) == pytest.approx(2 / 3)


def test_gini_and_entropy_are_not_the_same_measurement():
    """Both measure concentration but weigh it differently: entropy by how many chunks get some
    attention, Gini by how unequally the mass is split. Keeping both is only worth the columns
    if they can disagree."""
    long_tail = chunk_shares(one_step(10.0, 1.0, 1.0, 1.0, 1.0, 1.0))
    two_way = chunk_shares(one_step(1.0, 1.0, 0.0, 0.0, 0.0, 0.0))
    assert chunk_entropy(long_tail) > chunk_entropy(two_way)
    assert chunk_gini(long_tail) < chunk_gini(two_way)


def test_a_single_chunk_has_no_inequality():
    assert chunk_gini(chunk_shares(one_step(1.0))) == pytest.approx(0.0)


# -- drift ------------------------------------------------------------------------------------


def test_a_steady_gaze_does_not_drift():
    steady = chunk_shares(steps([1.0, 0.0], [1.0, 0.0], [1.0, 0.0]))
    assert chunk_drift(steady) == pytest.approx(0.0)


def test_moving_all_the_attention_drifts_by_one():
    """Total variation distance reads directly as the fraction of mass that moved."""
    assert chunk_drift(chunk_shares(steps([1.0, 0.0], [0.0, 1.0]))) == pytest.approx(1.0)


def test_drift_is_averaged_over_the_response():
    """Three steps, two transitions: one that moves everything and one that moves nothing."""
    walk = steps([1.0, 0.0], [0.0, 1.0], [0.0, 1.0])
    assert chunk_drift(chunk_shares(walk)) == pytest.approx(0.5)


def test_a_response_with_one_scored_token_does_not_drift():
    """No consecutive pair exists, so no movement was observed — which is not the same as
    movement of unknown size, and 0 says the first while nan would say the second."""
    assert chunk_drift(chunk_shares(one_step(1.0, 0.0))) == pytest.approx(0.0)


def test_drift_measures_movement_not_spread():
    """Two responses with identical *average* spread, one steady and one alternating. Every
    other feature here pools over tokens and cannot see the difference."""
    steady = chunk_shares(steps([0.5, 0.5], [0.5, 0.5]))
    swinging = chunk_shares(steps([1.0, 0.0], [0.0, 1.0]))
    assert chunk_entropy(steady).mean() == pytest.approx(1.0)
    assert chunk_drift(steady) == pytest.approx(0.0)
    assert chunk_drift(swinging) == pytest.approx(1.0)


# -- putting one sample together ---------------------------------------------------------------


def test_every_named_feature_is_produced():
    computed = chunk_features(np.random.default_rng(0).random((3, 4, 6, 5)))
    assert set(computed) == set(CHUNK_FEATURE_NAMES)


def test_each_feature_keeps_the_layer_and_head_grid():
    """Per (layer, head), like E02 — one of the paper's findings is that a few specific heads
    carry the signal, so averaging heads together would throw it away."""
    computed = chunk_features(np.random.default_rng(0).random((27, 28, 9, 5)))
    for name, value in computed.items():
        assert value.shape == (27, 28), name


def test_the_flat_vector_has_five_blocks():
    vector = sample_vector(np.random.default_rng(0).random((27, 28, 9, 5)))
    assert vector.shape == (5 * 27 * 28,)


def test_names_line_up_with_the_values():
    per_chunk = np.random.default_rng(1).random((2, 3, 4, 5))
    names = feature_names([0, 1], 3)
    assert len(names) == sample_vector(per_chunk).size
    assert names[0] == "chunk_entropy_l0_h0"
    assert names[-1] == "chunk_drift_l1_h2"


def test_names_use_the_model_s_own_layer_numbers():
    """Same trap as E02: with layer 27 excluded the array has 27 slices but they are layers 0
    to 26, and E13 asks where the useful heads sit."""
    assert feature_names([0, 5, 26], 2)[-1] == "chunk_drift_l26_h1"


def test_one_statistic_occupies_one_contiguous_block():
    """Feature first, then layer, then head — so an ablation over feature groups is a slice
    rather than a gather, which is what E12 will be doing."""
    names = feature_names([0, 1], 3)
    block = names[: 2 * 3]
    assert all(name.startswith("chunk_entropy_") for name in block)


# -- the whole thing stays inside its definitions ------------------------------------------------


def test_every_feature_lands_in_the_unit_interval():
    """All five are shares, normalised entropies, corrected Gini or total variation distances.
    A value outside [0, 1] means a formula is wrong, not that a sample was unusual — the same
    check the E02 script runs before it believes any score."""
    per_chunk = np.random.default_rng(7).random((5, 6, 12, 8)) * 1e-3
    vector = sample_vector(per_chunk)
    assert np.isfinite(vector).all()
    assert vector.min() >= 0.0
    assert vector.max() <= 1.0


def test_a_realistic_sample_produces_no_nan():
    """Sparse attention with whole heads at zero, which is what the real matrices look like."""
    rng = np.random.default_rng(3)
    per_chunk = rng.random((4, 5, 20, 6)) * (rng.random((4, 5, 20, 6)) > 0.8)
    assert np.isfinite(sample_vector(per_chunk)).all()
