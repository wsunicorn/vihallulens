"""Tests for the E13 head-position comparison (task T30).

The one that matters most is the grid-mismatch guard. Sailor2-8B is an expansion of Qwen2.5-7B
and very likely has more layers, so the failure mode this file exists to prevent is comparing
layer 5 of a 28-layer model to layer 5 of a 32-layer model and reporting the overlap as though
it meant something.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from compare_heads import depth_profile, name_of, spearman  # noqa: E402


def side(n_layers: int, n_heads: int, order):
    return {
        "n_layers": n_layers,
        "n_heads": n_heads,
        "order": np.asarray(order),
        "layer_indices": list(range(n_layers)),
    }


def test_spearman_is_one_for_identical_orderings():
    values = np.array([0.1, 0.9, 0.5, 0.3])
    assert spearman(values, values) == 1.0


def test_spearman_is_minus_one_for_reversed_orderings():
    values = np.array([1.0, 2.0, 3.0, 4.0])
    assert spearman(values, -values) == -1.0


def test_spearman_handles_ties_without_dividing_by_zero():
    flat = np.array([1.0, 1.0, 1.0, 1.0])
    assert spearman(flat, np.array([1.0, 2.0, 3.0, 4.0])) == 0.0


def test_depth_is_a_fraction_so_two_different_grids_stay_comparable():
    """Layer 5 of 28 and layer 6 of 32 are both about a fifth of the way down."""
    shallow = side(28, 28, [5 * 28 + 0])
    deep = side(33, 28, [6 * 28 + 0])

    a = depth_profile(shallow, k=1)["mean_depth"]
    b = depth_profile(deep, k=1)["mean_depth"]

    assert abs(a - b) < 0.02
    assert 0.0 <= a <= 1.0 and 0.0 <= b <= 1.0


def test_depth_thirds_sum_to_one():
    grid = side(30, 4, list(range(0, 120, 7)))
    profile = depth_profile(grid, k=10)
    total = (profile["share_first_third"] + profile["share_middle_third"]
             + profile["share_last_third"])
    assert abs(total - 1.0) < 1e-9


def test_first_and_last_layer_map_to_zero_and_one():
    grid = side(28, 28, [0])
    assert depth_profile(grid, k=1)["mean_depth"] == 0.0
    last = side(28, 28, [27 * 28])
    assert depth_profile(last, k=1)["mean_depth"] == 1.0


def test_head_name_uses_the_stored_layer_index_not_the_position():
    """Layer 27 is dropped for Qwen, so grid row 27 is model layer 28 — names must not lie."""
    grid = {"n_heads": 4, "n_layers": 3, "layer_indices": [0, 1, 5]}
    assert name_of(grid, 2 * 4 + 3) == "l5_h3"
