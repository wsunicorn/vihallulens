"""Scoring, and the column-order trap that made the first E01 run wrong.

Macro-F1 and the per-class scores are straightforward. Expected calibration error is not: it
reads the probability matrix, and a probability matrix is only meaningful together with the
list saying which class each column belongs to.
"""

import numpy as np
import pytest

from vihallulens.evaluation.metrics import (
    LABELS,
    bootstrap_ci,
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


# -- confidence intervals from resampling the test set ------------------------------------


def test_the_interval_brackets_the_point_estimate():
    from vihallulens.evaluation.metrics import bootstrap_ci

    truth = ["no"] * 40 + ["intrinsic"] * 40 + ["extrinsic"] * 40
    predicted = truth[:100] + ["no"] * 20
    point = compute_metrics(truth, predicted)["macro_f1"]
    spread = bootstrap_ci(truth, predicted, n_resamples=300, seed=42)
    assert spread["macro_f1_lo"] <= point <= spread["macro_f1_hi"]


def test_a_smaller_test_set_gives_a_wider_interval():
    """The whole reason this replaced the seed-based standard deviation: the dominant
    uncertainty comes from how many samples the test set has, not from the classifier."""
    from vihallulens.evaluation.metrics import bootstrap_ci

    truth = ["no", "intrinsic", "extrinsic"] * 40
    predicted = ["no", "intrinsic", "no"] * 40
    small = bootstrap_ci(truth[:30], predicted[:30], n_resamples=300, seed=42)
    large = bootstrap_ci(truth, predicted, n_resamples=300, seed=42)
    assert small["macro_f1_se"] > large["macro_f1_se"]


def test_perfect_predictions_give_a_degenerate_interval():
    from vihallulens.evaluation.metrics import bootstrap_ci

    truth = ["no", "intrinsic", "extrinsic"] * 20
    spread = bootstrap_ci(truth, truth, n_resamples=200, seed=42)
    assert spread["macro_f1_lo"] == pytest.approx(1.0)
    assert spread["macro_f1_se"] == pytest.approx(0.0)


def test_the_interval_is_the_same_on_every_machine():
    from vihallulens.evaluation.metrics import bootstrap_ci

    truth = ["no", "intrinsic", "extrinsic"] * 20
    predicted = ["no", "no", "extrinsic"] * 20
    first = bootstrap_ci(truth, predicted, n_resamples=200, seed=42)
    second = bootstrap_ci(truth, predicted, n_resamples=200, seed=42)
    assert first == second


def test_too_few_resamples_is_rejected():
    from vihallulens.evaluation.metrics import bootstrap_ci

    with pytest.raises(ValueError, match="ít nhất 2 lần"):
        bootstrap_ci(["no"], ["no"], n_resamples=1)


def test_mismatched_lengths_are_rejected_before_resampling():
    from vihallulens.evaluation.metrics import bootstrap_ci

    with pytest.raises(ValueError, match="phần tử"):
        bootstrap_ci(["no", "no"], ["no"])


# -- two kinds of spread, two names --------------------------------------------------------


def test_the_two_spreads_do_not_share_a_key():
    """``summarise_runs`` measures spread across seeds; ``bootstrap_ci`` measures spread of the
    test-set sampling distribution. Different questions, so different names.

    While both used ``_std`` a merged record kept whichever was written last, and at T18 the two
    E09 records went out carrying the bootstrap number under the seed number's name —
    contradicting the table that the very same run had printed to the screen. Two hours of GPU
    quota produced records whose numbers could not be trusted.
    """
    y_true = ["no", "intrinsic", "extrinsic"] * 20
    y_pred = ["no", "intrinsic", "no"] * 20
    across = summarise_runs([{"macro_f1": 0.70}, {"macro_f1": 0.75}])
    spread = bootstrap_ci(y_true, y_pred, n_resamples=50)
    assert not (set(across) & set(spread)), sorted(set(across) & set(spread))


def test_the_bootstrap_reports_a_standard_error():
    y_true = ["no", "intrinsic", "extrinsic"] * 20
    y_pred = ["no", "intrinsic", "no"] * 20
    spread = bootstrap_ci(y_true, y_pred, n_resamples=50)
    assert "macro_f1_se" in spread
    assert "macro_f1_std" not in spread


def test_the_seed_summary_reports_a_standard_deviation():
    across = summarise_runs([{"macro_f1": 0.70}, {"macro_f1": 0.75}])
    assert "macro_f1_std" in across
    assert "macro_f1_se" not in across


# -- the binary view: detection separated from classification -------------------------------


def test_naming_the_wrong_kind_of_hallucination_still_counts_as_detected():
    """The whole point. At T19 three independent judgements — two students on ViWikiFC and
    Gemini on ViHallu — all read intrinsic hallucination as extrinsic. Under three-class
    macro-F1 those samples are simply wrong; under the binary view they are caught, and the gap
    between the two scores is what says the difficulty lives in the boundary."""
    from vihallulens.evaluation.metrics import binary_metrics

    scores = binary_metrics(["intrinsic"] * 10, ["extrinsic"] * 10)
    assert scores["binary_recall"] == pytest.approx(1.0)
    assert scores["binary_accuracy"] == pytest.approx(1.0)


def test_calling_a_truthful_answer_hallucinated_still_counts_as_wrong():
    from vihallulens.evaluation.metrics import binary_metrics

    scores = binary_metrics(["no"] * 10, ["extrinsic"] * 10)
    assert scores["binary_accuracy"] == pytest.approx(0.0)
    assert scores["binary_precision"] == pytest.approx(0.0)


def test_precision_and_recall_are_those_of_the_hallucinated_class():
    """A deployed detector is judged on these two: how much hallucination it catches, and how
    much of its alarm is real."""
    from vihallulens.evaluation.metrics import binary_metrics

    #        true:  no   no   intr extr extr
    #        pred:  extr no   intr no   extr
    scores = binary_metrics(["no", "no", "intrinsic", "extrinsic", "extrinsic"],
                            ["extrinsic", "no", "intrinsic", "no", "extrinsic"])
    assert scores["binary_recall"] == pytest.approx(2 / 3)
    assert scores["binary_precision"] == pytest.approx(2 / 3)


def test_the_binary_scores_ride_along_with_every_computation():
    """Added inside compute_metrics rather than beside it, so every experiment — past scripts
    included — reports the pair without anyone remembering to ask."""
    scores = compute_metrics(["no", "intrinsic", "extrinsic"], ["no", "extrinsic", "extrinsic"])
    wanted = {"binary_macro_f1", "binary_accuracy", "binary_precision", "binary_recall"}
    assert wanted <= set(scores)


def test_the_binary_score_is_never_below_the_three_class_one_on_this_kind_of_error():
    """Collapsing two classes can only forgive confusions between them, never create new ones."""
    truth = ["no"] * 20 + ["intrinsic"] * 20 + ["extrinsic"] * 20
    muddled = ["no"] * 20 + ["extrinsic"] * 20 + ["intrinsic"] * 20
    scores = compute_metrics(truth, muddled)
    assert scores["binary_macro_f1"] > scores["macro_f1"]


def test_collapsing_labels_keeps_the_clean_class_alone():
    from vihallulens.evaluation.metrics import to_binary

    assert list(to_binary(["no", "intrinsic", "extrinsic"])) == ["no", "hallucinated",
                                                                "hallucinated"]
