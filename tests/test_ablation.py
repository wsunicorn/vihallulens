"""Tests for the E12 ablation runner (task T29).

The two things worth locking here are both alignment bugs that would lower the score silently
rather than raise anything: surface rows attached to the wrong sample, and the head ranking
reading the surface columns as though they were attention columns.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_ablation import LEVELS, level_matrix, surface_matrix  # noqa: E402


def test_surface_rows_follow_sample_id_not_row_order():
    """The shard is sorted by sample id; the corpus frame is not. Position must not be trusted."""
    lookup = {
        "a": np.array([10.0, 0.1]),
        "b": np.array([20.0, 0.2]),
        "c": np.array([30.0, 0.3]),
    }
    records = [{"sample_id": "c"}, {"sample_id": "a"}, {"sample_id": "b"}]

    matrix = surface_matrix(records, lookup)

    assert matrix.tolist() == [[30.0, 0.3], [10.0, 0.1], [20.0, 0.2]]


def test_a_sample_missing_from_the_corpus_is_an_error_not_a_silent_gap():
    lookup = {"a": np.array([1.0, 0.5])}
    records = [{"sample_id": "a"}, {"sample_id": "khong_co"}]

    with pytest.raises(ValueError, match="đặc trưng bề mặt"):
        surface_matrix(records, lookup)


def test_first_level_is_surface_only_and_keeps_exactly_two_columns():
    """Level 1 must not touch the attention shard at all — it is the E01 floor."""
    surface = np.arange(6, dtype=float).reshape(3, 2)

    matrix = level_matrix(records=None, groups=(), n_layers=2, n_heads=2,
                          mode="all", keep=None, surface=surface)

    assert matrix.shape == (3, 2)
    assert np.array_equal(matrix, surface)


def test_levels_are_cumulative_so_the_delta_column_means_what_it_says():
    """Each level must contain every group of the level above it, or the deltas are nonsense."""
    for (_, narrower), (_, wider) in zip(LEVELS, LEVELS[1:], strict=False):
        assert set(narrower) <= set(wider)


def test_the_widest_level_is_the_configured_contribution():
    assert LEVELS[-1][1] == ("basic", "chunk_aware", "stability")
    assert LEVELS[0][1] == ()
