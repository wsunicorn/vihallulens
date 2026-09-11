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


# ---------------------------------------------------------------- T35B: the extra level

def test_levels_table_still_has_exactly_four_cumulative_rows():
    """T35B added ``--extra-level`` as a separate output, not a fifth row.

    Bảng 4 and the two E12 rows already in runs.jsonl are four rows. A fifth row appended to
    LEVELS would make every later run incomparable with them, so the table's shape is locked.
    """
    assert len(LEVELS) == 4
    assert LEVELS[0][1] == ()
    for earlier, later in zip(LEVELS, LEVELS[1:], strict=False):
        assert set(earlier[1]) <= set(later[1]), "các mức phải cộng dồn"


def test_extra_level_matrix_has_surface_and_only_the_named_groups():
    """Surface + chunk_aware, no lookback: 2 surface columns plus four chunk blocks."""
    n_layers, n_heads = 2, 3
    record = {
        "lookback_total": [0.5] * (n_layers * n_heads),
        "lookback_context": [0.4] * (n_layers * n_heads),
        "chunk_entropy": [0.1] * (n_layers * n_heads),
        "chunk_max_share": [0.9] * (n_layers * n_heads),
        "chunk_gini": [0.2] * (n_layers * n_heads),
        "top1_top2_gap": [0.3] * (n_layers * n_heads),
        "chunk_drift": [0.05] * (n_layers * n_heads),
        "self_attention": [0.0] * (n_layers * n_heads),
    }
    surface = np.array([[12.0, 0.7]])

    with_lookback = level_matrix([record], ("basic", "chunk_aware"), n_layers, n_heads,
                                 "all", None, surface)
    without = level_matrix([record], ("chunk_aware",), n_layers, n_heads, "all", None, surface)

    # Removing the basic group removes exactly its blocks' columns and nothing else, and the
    # two surface columns stay at the front where the head ranking expects them.
    from vihallulens.features.assemble import blocks_for

    basic_columns = len(blocks_for(["basic"])) * n_layers * n_heads
    assert with_lookback.shape[1] - without.shape[1] == basic_columns
    assert without.shape[1] == 2 + len(blocks_for(["chunk_aware"])) * n_layers * n_heads
    assert without[0, :2].tolist() == [12.0, 0.7]
