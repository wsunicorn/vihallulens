"""The statistics behind the paired comparisons."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_paired_tests as t  # noqa: E402

RNG = np.random.default_rng(0)
TRUTH = RNG.choice(t.LABELS, 120).tolist()


def noisy(rate: float, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    flip = rng.random(len(TRUTH)) < rate
    return [rng.choice(t.LABELS) if f else y for f, y in zip(flip, TRUTH, strict=True)]


def test_vectorised_macro_f1_matches_sklearn():
    pred = noisy(0.4, 1)
    codes = t.encode(TRUTH)[None, :], t.encode(pred)[None, :]
    assert t.macro_f1_rows(*codes)[0] == pytest.approx(t.macro_f1(TRUTH, pred))


def test_absent_class_counts_as_zero_like_sklearn():
    truth, pred = ["no"] * 4, ["no", "no", "intrinsic", "no"]
    got = t.macro_f1_rows(t.encode(truth)[None, :], t.encode(pred)[None, :])[0]
    assert got == pytest.approx(t.macro_f1(truth, pred))


def test_identical_predictions_differ_by_zero():
    pred = noisy(0.3, 2)
    out = t.paired_difference(TRUTH, [pred], [pred], rounds=1000)
    assert out["delta"] == out["lo"] == out["hi"] == 0


def test_clear_winner_has_interval_above_zero():
    out = t.paired_difference(TRUTH, [noisy(0.05, 3)], [noisy(0.7, 4)], rounds=1000)
    assert out["lo"] > 0 and out["p_bootstrap"] < 0.05


def test_seeds_are_averaged():
    a, b, c = noisy(0.2, 5), noisy(0.3, 6), noisy(0.4, 7)
    out = t.paired_difference(TRUTH, [a, b], [c], rounds=500)
    want = (t.macro_f1(TRUTH, a) + t.macro_f1(TRUTH, b)) / 2 - t.macro_f1(TRUTH, c)
    assert out["delta"] == pytest.approx(want)


def test_mcnemar_counts_lone_hits():
    out = t.mcnemar_exact(["no"] * 6, ["no"] * 6, ["no", "intrinsic"] + ["no"] * 4)
    assert (out["only_a"], out["only_b"], out["p"]) == (1, 0, 1.0)
    assert t.mcnemar_exact(["no"] * 8, ["no"] * 8, ["extrinsic"] * 8)["p"] < 0.01


def test_holm_adjusts_and_stays_monotone():
    assert t.holm([0.01, 0.04, 0.03]) == pytest.approx([0.03, 0.06, 0.06])
    assert t.holm([0.9, 0.8]) == [1.0, 1.0]


def test_predictions_that_do_not_reproduce_their_score_are_refused():
    ids = [f"s{i}" for i in range(len(TRUTH))]
    run = {"config": {"dataset": {"name": "d"}}, "metrics": {"macro_f1": 0.9},
           "extra": {"y_pred": noisy(0.5, 8)}}
    store = t.Predictions({"r": run}, None, {})
    store.truths["d"] = dict(zip(ids, TRUTH, strict=True))
    with pytest.raises(SystemExit, match="Không dùng được"):
        store.get("r")
