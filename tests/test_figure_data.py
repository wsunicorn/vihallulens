"""The condensed data behind the result charts."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import build_figure_data as b  # noqa: E402
from run_calibration import ece  # noqa: E402


def test_hit_grid_is_layers_by_heads():
    records = [{"layer_indices": [0, 1], "gold_rank": [0, 1, 2, 0, 0, 3]},
               {"layer_indices": [0, 1], "gold_rank": [0, 0, 2, 1, 0, 3]}]
    assert b.hit_grid(records).tolist() == [[1.0, 0.5, 0.0], [0.5, 1.0, 0.0]]


@pytest.mark.parametrize(("direction", "aligned"), [(1, 0.75), (-1, 0.25)])
def test_histogram_keeps_every_pair_and_reads_the_direction(direction, aligned):
    out = b.change_histogram(np.array([0.02, 0.9, 0.01, -0.03]), direction)
    assert sum(out["counts"]) == 4 and out["outside"] == 1 and out["aligned"] == aligned


def test_reliability_bins_add_up_to_the_ece():
    rng = np.random.default_rng(0)
    proba = rng.dirichlet(np.ones(3), 400)
    truth = rng.integers(0, 3, 400)
    bins = b.reliability(proba, truth)
    assert sum(row["n"] for row in bins) == 400
    total = sum(row["n"] * abs(row["accuracy"] - row["confidence"]) for row in bins) / 400
    assert total == pytest.approx(ece(proba, truth))


def test_a_disagreement_with_the_thesis_stops_the_script():
    b.agree("x", 0.5001, 0.5)
    with pytest.raises(SystemExit, match="quyển ghi"):
        b.agree("x", 0.51, 0.5)
