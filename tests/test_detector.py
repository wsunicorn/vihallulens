"""The classifier that sits on top of every feature set from E01 onward."""

import numpy as np
import pytest

from vihallulens.detect.detector import LookbackDetector


def toy(n: int = 60):
    """Two features that separate three classes, enough to fit and predict on."""
    rng = np.random.default_rng(0)
    x = np.vstack([
        rng.normal([0, 0], 0.3, size=(n, 2)),
        rng.normal([4, 0], 0.3, size=(n, 2)),
        rng.normal([0, 4], 0.3, size=(n, 2)),
    ])
    y = np.array(["no"] * n + ["intrinsic"] * n + ["extrinsic"] * n)
    return x, y


# -- fitting ------------------------------------------------------------------------------


def test_a_fitted_detector_separates_well_separated_classes():
    x, y = toy()
    detector = LookbackDetector().fit(x, y)
    assert (detector.predict(x) == y).mean() > 0.95


def test_fit_returns_the_detector_so_calls_can_be_chained():
    x, y = toy()
    assert isinstance(LookbackDetector().fit(x, y), LookbackDetector)


def test_predicting_before_fitting_is_refused():
    with pytest.raises(RuntimeError, match="chưa huấn luyện"):
        LookbackDetector().predict(np.zeros((2, 2)))


def test_mismatched_row_counts_are_rejected():
    with pytest.raises(ValueError, match="dòng"):
        LookbackDetector().fit(np.zeros((3, 2)), np.array(["no", "no"]))


def test_a_single_class_cannot_be_trained_on():
    with pytest.raises(ValueError, match="ít nhất hai lớp"):
        LookbackDetector().fit(np.zeros((4, 2)), np.array(["no"] * 4))


@pytest.mark.parametrize("bad", ["magic", "random_forest"])
def test_an_unknown_detector_type_is_rejected(bad):
    with pytest.raises(ValueError, match="không biết loại"):
        LookbackDetector(detector_type=bad)


def test_an_unknown_class_weight_is_rejected():
    with pytest.raises(ValueError, match="không biết class_weight"):
        LookbackDetector(class_weight="inverse")


# -- probabilities -------------------------------------------------------------------------


def test_probabilities_have_one_column_per_class_and_sum_to_one():
    x, y = toy()
    detector = LookbackDetector().fit(x, y)
    proba = detector.predict_proba(x)
    assert proba.shape == (len(x), 3)
    assert np.allclose(proba.sum(axis=1), 1.0)


def test_the_highest_probability_column_is_the_predicted_class():
    """The invariant compute_metrics leans on to catch a mismatched column order."""
    x, y = toy()
    detector = LookbackDetector().fit(x, y)
    from_proba = detector.classes_[detector.predict_proba(x).argmax(axis=1)]
    assert (from_proba == detector.predict(x)).all()


def test_classes_come_back_sorted_not_in_the_order_they_appeared():
    """Worth pinning down, because it is exactly what makes the column order differ from the
    reporting order used elsewhere in the project."""
    x, y = toy()
    detector = LookbackDetector().fit(x, y)
    assert list(detector.classes_) == ["extrinsic", "intrinsic", "no"]


def test_a_model_without_probabilities_says_so_instead_of_faking_them():
    """LinearSVC returns distances from the boundary. A softmax over distances would look like
    a probability without being one, and the ECE built on it would be meaningless."""
    x, y = toy()
    detector = LookbackDetector(detector_type="linear_svc").fit(x, y)
    with pytest.raises(NotImplementedError, match="không cho xác suất"):
        detector.predict_proba(x)


# -- scaling ------------------------------------------------------------------------------


def test_features_on_wildly_different_scales_are_still_learned():
    """Response length is counted in words and lexical overlap lies in [0, 1] — about forty
    times apart. Without standardising, the regularisation penalty falls almost entirely on
    the smaller-scale feature."""
    x, y = toy()
    x = x * np.array([1.0, 1000.0])
    assert (LookbackDetector(standardize=True).fit(x, y).predict(x) == y).mean() > 0.95


def test_scaling_can_be_switched_off():
    x, y = toy()
    detector = LookbackDetector(standardize=False).fit(x, y)
    assert (detector.predict(x) == y).mean() > 0.95


# -- cost reporting -------------------------------------------------------------------------


def test_the_parameter_count_is_the_coefficients_plus_the_intercepts():
    """Three classes and two features: six coefficients and three intercepts. The point of the
    cost column in experiment E11 is that this is a handful of numbers, not a fine-tuned
    encoder."""
    x, y = toy()
    assert LookbackDetector().fit(x, y).n_params_trainable == 9


def test_counting_parameters_before_fitting_is_refused():
    with pytest.raises(RuntimeError, match="chưa huấn luyện"):
        _ = LookbackDetector().n_params_trainable


# -- persistence ----------------------------------------------------------------------------


def test_a_saved_detector_predicts_the_same_after_loading(tmp_path):
    x, y = toy()
    detector = LookbackDetector().fit(x, y)
    path = detector.save(tmp_path / "detector.pkl")
    assert (LookbackDetector.load(path).predict(x) == detector.predict(x)).all()


def test_loading_a_missing_file_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError):
        LookbackDetector.load(tmp_path / "khong_ton_tai.pkl")


def test_saving_creates_the_directory_if_it_is_missing(tmp_path):
    x, y = toy()
    path = LookbackDetector().fit(x, y).save(tmp_path / "chua_co" / "detector.pkl")
    assert path.is_file()
