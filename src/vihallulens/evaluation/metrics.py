"""Scoring a three-class prediction. Signature per section 2.5 of docs/SPEC.md.

Macro-F1 leads, as section 3 of docs/EXPERIMENTS.md fixes. It averages the three per-class F1
scores without weighting by class size, so a detector that gives up on the rarest class cannot
hide behind the two common ones — which is exactly the failure mode to guard against here,
since the rare class is the one the thesis is about.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

# Section 3 of docs/DATA.md. Order fixed so the per-class columns of a results table always
# mean the same thing.
LABELS = ("no", "intrinsic", "extrinsic")

DEFAULT_ECE_BINS = 10


def expected_calibration_error(
    y_true, y_proba, proba_labels=LABELS, n_bins: int = DEFAULT_ECE_BINS
) -> float:
    """How far the model's confidence is from its accuracy, averaged over confidence bins.

    A model that says "80 % sure" should be right about 80 % of the time. ECE bins predictions
    by their confidence and measures the gap between confidence and accuracy inside each bin,
    weighted by how many predictions fall there. Zero is perfect; a confidently wrong model
    scores high.

    It matters here because a hallucination detector that cannot be trusted about *how* sure it
    is cannot be given a threshold, and section 7 of docs/SPEC.md wants the deployed system to
    return a risk score rather than a bare label.

    ``proba_labels`` names the class each **column** of ``y_proba`` belongs to, which is not the
    same thing as the reporting order of the per-class metrics. scikit-learn sorts its classes
    alphabetically, so a three-class model here returns columns ordered extrinsic, intrinsic, no
    — a different order from the ``no, intrinsic, extrinsic`` this project reports in. Measured
    at T17: assuming they matched put the ECE at 0,42 instead of its real value, and nothing
    failed.
    """
    proba = np.asarray(y_proba, dtype=float)
    if proba.ndim != 2 or proba.shape[1] != len(proba_labels):
        raise ValueError(f"y_proba phải có dạng (n, {len(proba_labels)}), nhận {proba.shape}")

    confidence = proba.max(axis=1)
    predicted = np.asarray(proba_labels)[proba.argmax(axis=1)]
    correct = (predicted == np.asarray(y_true)).astype(float)

    # Right-closed bins so that a confidence of exactly 1.0 lands in the last bin rather than
    # falling outside every one of them.
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    error = 0.0
    for low, high in zip(edges[:-1], edges[1:], strict=True):
        inside = (confidence > low) & (confidence <= high)
        if not inside.any():
            continue
        error += inside.mean() * abs(correct[inside].mean() - confidence[inside].mean())
    return float(error)


def compute_metrics(y_true, y_pred, y_proba=None, labels=LABELS, proba_labels=None) -> dict:
    """Macro-F1, accuracy, per-class F1, and ECE when probabilities are supplied.

    ``labels`` is the reporting order of the per-class scores. ``proba_labels`` is the column
    order of ``y_proba``, which is whatever the classifier chose and is usually **not** the
    same — pass ``detector.classes_``. Leaving it out assumes the two agree, and the assumption
    is verified rather than trusted: see the check below.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if len(y_true) != len(y_pred):
        raise ValueError(f"y_true có {len(y_true)} phần tử, y_pred có {len(y_pred)}")
    if len(y_true) == 0:
        raise ValueError("không có mẫu nào để chấm")

    per_class = f1_score(y_true, y_pred, labels=list(labels), average=None, zero_division=0)
    metrics = {
        "macro_f1": float(f1_score(y_true, y_pred, labels=list(labels), average="macro",
                                   zero_division=0)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
    }
    for label, score in zip(labels, per_class, strict=True):
        metrics[f"f1_{label}"] = float(score)

    if y_proba is not None:
        columns = labels if proba_labels is None else proba_labels
        # The class with the highest probability must be the class that was predicted. If it is
        # not, the columns of y_proba have been paired with the wrong names, and every number
        # derived from them is quietly wrong while every other metric still looks fine. This is
        # not hypothetical: it happened at T17 and cost a whole run before being noticed.
        from_proba = np.asarray(columns)[np.asarray(y_proba, dtype=float).argmax(axis=1)]
        disagreements = int((from_proba != y_pred).sum())
        if disagreements:
            raise ValueError(
                f"cột của y_proba không khớp tên lớp: {disagreements}/{len(y_pred)} mẫu có lớp "
                f"xác suất cao nhất khác với y_pred. Truyền proba_labels=detector.classes_ "
                f"(sklearn sắp lớp theo bảng chữ cái, khác thứ tự báo cáo {tuple(labels)})."
            )
        metrics["ece"] = expected_calibration_error(y_true, y_proba, proba_labels=columns)
    return metrics


def summarise_runs(runs: list[dict]) -> dict:
    """Mean and standard deviation of each metric across repeated runs.

    Section 3 of docs/EXPERIMENTS.md requires a standard deviation beside every classifier
    figure. Each metric gains a ``_std`` companion; the mean keeps the plain name so a table
    built from these keys reads the same whether it came from one run or from five.
    """
    if not runs:
        raise ValueError("không có lần chạy nào để tổng hợp")
    summary: dict[str, float] = {}
    for key in runs[0]:
        values = [run[key] for run in runs]
        summary[key] = float(np.mean(values))
        summary[f"{key}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
    return summary
