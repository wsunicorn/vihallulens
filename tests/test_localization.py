"""Locating the gold evidence chunk from the attention distribution. Experiment E06.

This is the experiment CH1 rests on, so the arithmetic under it is worth pinning down hard: a
silently optimistic rank, or a floor computed from the wrong number of chunks, would turn "the
mechanism works" into a claim nobody could reproduce.
"""

import numpy as np
import pytest

from vihallulens.features.localization import (
    best_head,
    gold_rank,
    hit_at,
    mean_shares,
    random_floor,
    reciprocal_rank,
    summarise,
)

LAYERS, HEADS = 2, 3


def shares_with_peak(peak: int, n_chunks: int = 5) -> np.ndarray:
    """A (layers, heads, chunks) grid where every head puts most of its mass on ``peak``."""
    grid = np.full((LAYERS, HEADS, n_chunks), 0.1, dtype=np.float32)
    grid[:, :, peak] = 0.6
    return grid


# -- pooling over tokens -------------------------------------------------------------------------


def test_each_token_is_normalised_before_averaging():
    """A token that sends more attention to the context must not count for more than the others.
    Here token 0 carries ten times the mass of token 1 but points at chunk 0, while token 1
    points at chunk 1; after normalising, the two cancel."""
    per_chunk = np.zeros((1, 1, 2, 2), dtype=np.float32)
    per_chunk[0, 0, 0] = [10.0, 0.0]
    per_chunk[0, 0, 1] = [0.0, 1.0]
    out = mean_shares(per_chunk)
    assert out[0, 0] == pytest.approx([0.5, 0.5])


def test_pooling_drops_the_token_axis():
    out = mean_shares(np.random.default_rng(0).random((LAYERS, HEADS, 7, 4)).astype(np.float32))
    assert out.shape == (LAYERS, HEADS, 4)
    assert out.sum(axis=2) == pytest.approx(1.0, abs=1e-5)


def test_a_three_dimensional_array_is_refused():
    with pytest.raises(ValueError, match="4 chiều"):
        mean_shares(np.zeros((LAYERS, HEADS, 4)))


# -- ranking the gold chunk ----------------------------------------------------------------------


def test_the_most_attended_chunk_gets_rank_zero():
    assert (gold_rank(shares_with_peak(2), gold=2) == 0).all()


def test_a_chunk_beaten_by_two_others_gets_rank_two():
    grid = np.zeros((1, 1, 4), dtype=np.float32)
    grid[0, 0] = [0.4, 0.3, 0.2, 0.1]
    assert gold_rank(grid, gold=2)[0, 0] == 2


def test_ties_count_against_the_gold_chunk():
    """A head that spreads its attention perfectly evenly expressed no preference, and must not
    be credited with hit@1. float16 makes exact ties common enough that the rule matters, and
    understating the mechanism is the error to prefer."""
    flat = np.full((1, 1, 4), 0.25, dtype=np.float32)
    assert gold_rank(flat, gold=0)[0, 0] == 3


def test_a_gold_index_outside_the_chunk_list_is_refused():
    """The failure this guards against is truncation dropping chunks and the caller still holding
    an index from the original list — which would score a different chunk and never complain."""
    with pytest.raises(ValueError, match="nằm ngoài"):
        gold_rank(shares_with_peak(1, n_chunks=4), gold=9)


# -- the floor a random ranker reaches -----------------------------------------------------------


def test_the_floor_follows_the_number_of_chunks():
    assert random_floor(20, 1) == pytest.approx(0.05)
    assert random_floor(20, 3) == pytest.approx(0.15)


def test_the_floor_cannot_exceed_one():
    """With two chunks, a top-three ranking contains everything, so a random ranker always hits.
    Reporting 1.5 here would make the lift ratio meaningless."""
    assert random_floor(2, 3) == 1.0


# -- aggregating across samples ------------------------------------------------------------------


def test_hit_at_counts_a_rank_below_k():
    ranks = np.array([[[0, 1, 5]], [[2, 3, 0]]])  # (samples=2, layers=1, heads=3)
    assert hit_at(ranks, 1).ravel() == pytest.approx([0.5, 0.0, 0.5])
    # Rank 3 is the fourth chunk, so it misses hit@3 — the boundary worth stating once.
    assert hit_at(ranks, 3).ravel() == pytest.approx([1.0, 0.5, 0.5])


def test_reciprocal_rank_scores_the_top_chunk_one():
    assert reciprocal_rank(np.array([[[0, 1, 3]]])).ravel() == pytest.approx([1.0, 0.5, 0.25])


def test_best_head_returns_its_position_not_the_model_layer():
    """Layer 27 is excluded, so grid position and model layer index stop agreeing. The caller
    holds layer_indices and does the translation; returning a model index here would be wrong
    exactly once, in the place hardest to notice."""
    grid = np.zeros((LAYERS, HEADS))
    grid[1, 2] = 0.9
    assert best_head(grid) == (1, 2, 0.9)


# -- the summary Bảng 2 is built from ------------------------------------------------------------


def test_a_perfect_localiser_beats_the_floor_by_the_chunk_count():
    """Twenty chunks, gold always ranked first: hit@1 is 1.0 against a floor of 0.05, so the lift
    is 20. The lift is the number Bảng 2 leans on, because hit@1 alone means nothing without
    knowing how many chunks it was choosing between."""
    ranks = np.zeros((50, LAYERS, HEADS), dtype=int)
    out = summarise(ranks, np.full(50, 20))
    assert out["hit@1"] == 1.0
    assert out["hit@1_floor"] == pytest.approx(0.05)
    assert out["hit@1_lift"] == pytest.approx(20.0)
    assert out["mrr"] == 1.0


def test_the_floor_is_averaged_per_sample_not_from_the_average_chunk_count():
    """Contexts run from 3 to 63 chunks on ISE-DSC01. 1/mean(n) and mean(1/n) differ by a lot at
    that spread, and using the first would quietly flatter the result."""
    counts = np.array([2, 100])
    out = summarise(np.zeros((2, LAYERS, HEADS), dtype=int), counts)
    assert out["hit@1_floor"] == pytest.approx((0.5 + 0.01) / 2)
    assert out["hit@1_floor"] != pytest.approx(1 / counts.mean())


def test_the_summary_reports_both_the_best_head_and_the_head_average():
    """Two different questions: does the signal exist anywhere (best head), and is it broad or
    one specialised circuit (average). Lookback Lens found the latter."""
    ranks = np.full((10, LAYERS, HEADS), 4, dtype=int)
    ranks[:, 0, 0] = 0
    out = summarise(ranks, np.full(10, 10))
    assert out["hit@1"] == 1.0
    assert out["hit@1_head"] == (0, 0)
    assert out["hit@1_mean_over_heads"] == pytest.approx(1 / (LAYERS * HEADS))


def test_the_summary_refuses_a_two_dimensional_rank_array():
    with pytest.raises(ValueError, match="3 chiều"):
        summarise(np.zeros((10, LAYERS)), np.full(10, 5))
