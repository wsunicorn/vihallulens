"""Scoring, and the column-order trap that made the first E01 run wrong.

Macro-F1 and the per-class scores are straightforward. Expected calibration error is not: it
reads the probability matrix, and a probability matrix is only meaningful together with the
list saying which class each column belongs to.
"""

import numpy as np
import pytest

from vihallulens.evaluation.metrics import (
    LABELS,
    compute_metrics,
    expected_calibration_error,
    summarise_runs,
)

# -- the basics ---------------------------------------------------------------------------


def test_perfect_predictions_score_one():
    truth = ["no", "intrinsic", "extrinsic"]
    metrics = compute_metrics(truth, truth)
    assert metrics["macro_f1"] == pytest.approx(1.0)
    assert metrics["accuracy"] == pytest.approx(1.0)


def test_every_class_gets_its_own_score():
    truth = ["no", "intrinsic", "extrinsic"]
    metrics = compute_metrics(truth, truth)
    assert set(metrics) >= {"f1_no", "f1_intrinsic", "f1_extrinsic"}


def test_macro_f1_does_not_let_a_missed_class_hide():
    """The whole reason section 3 of docs/EXPERIMENTS.md makes it the headline: a detector that
    gives up on the rarest class must not be able to shelter behind the common ones."""
    truth = ["no"] * 8 + ["extrinsic"] * 2
    lazy = ["no"] * 10
    metrics = compute_metrics(truth, lazy)
    assert metrics["accuracy"] == pytest.approx(0.8)
    assert metrics["macro_f1"] < 0.4


def test_a_class_absent_from_both_scores_zero_rather_than_raising():
    metrics = compute_metrics(["no", "no"], ["no", "no"])
    assert metrics["f1_intrinsic"] == 0.0


def test_mismatched_lengths_are_rejected():
    with pytest.raises(ValueError, match="phần tử"):
        compute_metrics(["no", "no"], ["no"])


def test_scoring_nothing_is_rejected():
    with pytest.raises(ValueError, match="không có mẫu"):
        compute_metrics([], [])


def test_no_probabilities_means_no_ece():
    assert "ece" not in compute_metrics(["no"], ["no"])


# -- the column-order trap ----------------------------------------------------------------


def test_probability_columns_paired_with_the_wrong_names_are_rejected():
    """The bug that made the first E01 run report an ECE of 0,42. scikit-learn sorts classes
    alphabetically — extrinsic, intrinsic, no — while this project reports in the order no,
    intrinsic, extrinsic. Assuming they matched went unnoticed because every other metric
    still looked perfectly reasonable."""
    truth = ["no", "no"]
    predicted = ["no", "no"]
    # Columns are in sklearn order, so the last column is "no" — but no proba_labels is given.
    proba = np.array([[0.1, 0.2, 0.7], [0.1, 0.2, 0.7]])
    with pytest.raises(ValueError, match="không khớp tên lớp"):
        compute_metrics(truth, predicted, proba)


def test_the_error_says_how_to_fix_it():
    proba = np.array([[0.1, 0.2, 0.7]])
    with pytest.raises(ValueError) as caught:
        compute_metrics(["no"], ["no"], proba)
    assert "proba_labels" in str(caught.value)


def test_giving_the_real_column_order_works():
    truth = ["no", "no"]
    predicted = ["no", "no"]
    proba = np.array([[0.1, 0.2, 0.7], [0.1, 0.2, 0.7]])
    metrics = compute_metrics(
        truth, predicted, proba, proba_labels=("extrinsic", "intrinsic", "no")
    )
    assert "ece" in metrics


def test_columns_already_in_reporting_order_need_no_extra_argument():
    proba = np.array([[0.7, 0.2, 0.1]])
    assert "ece" in compute_metrics(["no"], ["no"], proba)


def test_a_probability_matrix_of_the_wrong_width_is_rejected():
    with pytest.raises(ValueError, match="y_proba phải có dạng"):
        expected_calibration_error(["no"], np.array([[0.5, 0.5]]))


# -- calibration --------------------------------------------------------------------------


def test_a_perfectly_confident_and_perfectly_right_model_has_no_error():
    truth = ["no", "intrinsic"]
    proba = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    assert expected_calibration_error(truth, proba, proba_labels=LABELS) == pytest.approx(0.0)


def test_a_confidently_wrong_model_scores_near_one():
    truth = ["intrinsic", "intrinsic"]
    proba = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    assert expected_calibration_error(truth, proba, proba_labels=LABELS) == pytest.approx(1.0)


def test_confidence_matching_accuracy_gives_a_small_error():
    """Eight of ten right, all at 80 % confidence: the model knows what it knows."""
    truth = ["no"] * 8 + ["intrinsic"] * 2
    proba = np.array([[0.8, 0.1, 0.1]] * 10)
    assert expected_calibration_error(truth, proba, proba_labels=LABELS) == pytest.approx(0.0)


def test_full_confidence_is_not_dropped_by_the_binning():
    """Right-closed bins, so a probability of exactly 1.0 lands in the last bin instead of
    falling outside every one of them and being silently ignored."""
    truth = ["intrinsic"]
    proba = np.array([[1.0, 0.0, 0.0]])
    assert expected_calibration_error(truth, proba, proba_labels=LABELS) == pytest.approx(1.0)


# -- summarising repeats ------------------------------------------------------------------


def test_the_mean_keeps_the_plain_name_and_the_spread_gets_a_suffix():
    summary = summarise_runs([{"macro_f1": 0.6}, {"macro_f1": 0.8}])
    assert summary["macro_f1"] == pytest.approx(0.7)
    assert summary["macro_f1_std"] == pytest.approx(0.1414, abs=1e-3)


def test_a_single_run_has_no_spread():
    summary = summarise_runs([{"macro_f1": 0.6}])
    assert summary["macro_f1"] == pytest.approx(0.6)
    assert summary["macro_f1_std"] == 0.0


def test_summarising_nothing_is_rejected():
    with pytest.raises(ValueError, match="không có lần chạy"):
        summarise_runs([])
