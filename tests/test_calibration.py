"""Temperature scaling and the paired ECE difference."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_calibration as c  # noqa: E402
from vihallulens.evaluation.metrics import expected_calibration_error  # noqa: E402


def drawn(n=400, sharpness=1.0, seed=0):
    """Probabilities whose labels really are drawn from them, then sharpened."""
    rng = np.random.default_rng(seed)
    proba = rng.dirichlet([1.0, 1.0, 1.0], n)
    truth = np.array([rng.choice(3, p=p) for p in proba])
    return c.temper(proba, 1 / sharpness), truth


def test_temperature_one_changes_nothing():
    proba, _ = drawn()
    np.testing.assert_allclose(c.temper(proba, 1.0), proba, atol=1e-9)


def test_scaling_never_changes_the_prediction():
    proba, _ = drawn()
    for temperature in (0.3, 4.0):
        assert (c.temper(proba, temperature).argmax(1) == proba.argmax(1)).all()


def test_overconfidence_is_found_and_undone():
    proba, truth = drawn(4000, sharpness=3.0)
    temperature = c.fit_temperature(proba, truth)
    assert temperature == pytest.approx(3.0, abs=0.4)
    assert c.ece(c.temper(proba, temperature), truth) < c.ece(proba, truth)


def test_ece_matches_the_library_metric():
    proba, truth = drawn(300, sharpness=2.0)
    names = np.array(["a", "b", "c"])
    want = expected_calibration_error(names[truth], proba, proba_labels=list(names))
    assert c.ece(proba, truth) == pytest.approx(want, abs=1e-12)


def test_difference_of_a_classifier_with_itself_is_zero():
    proba, truth = drawn(200)
    out = c.ece_difference(proba, proba, truth, rounds=50)
    assert out["delta"] == out["lo"] == out["hi"] == 0


def test_arms_have_equal_width_pairwise():
    arms = c.arms_for(756)
    n_blocks = len(c.blocks_for(c.CHUNK))
    assert arms["lookback_small"][1] == arms["chunk_small"][1] * n_blocks == 192
    assert arms["chunk_full"][1] * n_blocks == 756
    with pytest.raises(ValueError, match="chia hết"):
        c.arms_for(757)
