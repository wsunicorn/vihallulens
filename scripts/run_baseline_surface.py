"""Task T17, experiment E01: the trivial baseline that defines the real floor.

Section 4 of docs/EXPERIMENTS.md is blunt about why this runs first. Two features — how long the
response is, and how much of its wording came from the context — and a logistic regression. If
that already scores well, then every more elaborate method, this thesis's own included, has to
prove it beats *this*, not that it beats a number some other paper published.

Usage:
    python scripts/run_baseline_surface.py
    python scripts/run_baseline_surface.py --dataset isedsc01
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import REQUIRED_SPLIT_SEED  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import (  # noqa: E402
    LABELS,
    bootstrap_ci,
    compute_metrics,
)
from vihallulens.features.surface import FEATURE_NAMES, surface_features  # noqa: E402

RUN_NAME = "e01_surface_baseline"


def describe_features(frame: pd.DataFrame, matrix: np.ndarray) -> None:
    """Per-label averages of the two features, to compare with docs/EXPERIMENTS.md."""
    print()
    print(f"  {'Nhãn':<12} {'Số mẫu':>8} {'Độ dài TB':>11} {'Trùng lặp TB':>14}")
    for label in LABELS:
        mask = (frame["label"] == label).to_numpy()
        if not mask.any():
            continue
        print(f"  {label:<12} {int(mask.sum()):>8,} {matrix[mask, 0].mean():>11.1f} "
              f"{matrix[mask, 1].mean():>14.3f}")
    print()
    print("  Mục 4 docs/EXPERIMENTS.md ghi 32,9 / 39,5 / 45,9 từ và 0,815 / 0,650 / 0,545.")


def main() -> int:
    parser = argparse.ArgumentParser(description="E01: baseline tầm thường hai đặc trưng.")
    parser.add_argument("--dataset", default="vihallu")
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print()
    print("=" * 80)
    print("T17 / E01 — BASELINE TẦM THƯỜNG")
    print("=" * 80)
    print(f"  bộ dữ liệu            : {args.dataset}")
    print(f"  đặc trưng             : {', '.join(FEATURE_NAMES)}")

    parts = {split: load_dataset(args.dataset, split, args.interim_dir)
             for split in ("train", "dev", "test")}
    matrices = {split: surface_features(frame) for split, frame in parts.items()}
    for split, frame in parts.items():
        print(f"  {split:<22}: {len(frame):,} mẫu")

    whole = pd.concat(parts.values(), ignore_index=True)
    describe_features(whole, np.vstack(list(matrices.values())))

    x_train, y_train = matrices["train"], parts["train"]["label"].to_numpy()
    x_test, y_test = matrices["test"], parts["test"]["label"].to_numpy()

    detector = LookbackDetector(seed=REQUIRED_SPLIT_SEED).fit(x_train, y_train)
    started = time.perf_counter()
    predicted = detector.predict(x_test)
    proba = detector.predict_proba(x_test)
    ms_per_sample = (time.perf_counter() - started) * 1000 / len(x_test)
    point = compute_metrics(y_test, predicted, proba, proba_labels=detector.classes_)

    # The uncertainty that matters comes from the test set being only 700 samples, not from
    # the classifier. Measured at T17: varying the seed moves macro-F1 by exactly nothing,
    # resampling the training set by ±0,004, resampling the test set by ±0,017.
    spread = bootstrap_ci(y_test, predicted, seed=REQUIRED_SPLIT_SEED)

    print()
    print("-" * 80)
    print(f"KẾT QUẢ TRÊN TẬP TEST — {len(y_test):,} mẫu")
    print("-" * 80)
    print(f"  {'Chỉ số':<14} {'Giá trị':>9} {'± sai số chuẩn':>15}   {'khoảng tin cậy 95 %':>21}")
    for key in ("macro_f1", "accuracy", *[f"f1_{label}" for label in LABELS]):
        print(f"  {key:<14} {point[key]:>9.4f} {spread[f'{key}_se']:>15.4f}   "
              f"[{spread[f'{key}_lo']:.4f}, {spread[f'{key}_hi']:.4f}]")
    print(f"  {'ece':<14} {point['ece']:>9.4f}")

    print()
    print(f"  {'nhị phân':<14} {point['binary_macro_f1']:>9.4f}   "
          f"chỉ hỏi có ảo giác hay không, gộp nội tại và ngoại lai")
    print(f"  {'  bắt được':<14} {point['binary_recall']:>9.4f}   số mẫu có ảo giác bị phát hiện")
    print(f"  {'  báo đúng':<14} {point['binary_precision']:>9.4f}   số lần báo động là thật")

    print()
    print(f"  Tham số phải huấn luyện : {detector.n_params_trainable}")
    print(f"  Thời gian suy luận      : {ms_per_sample:.4f} ms/mẫu")
    print("  Khoảng tin cậy lấy từ 2.000 lần lấy lại mẫu TẬP TEST. Đây mới là biến thiên")
    print("  chi phối: đổi riêng hạt giống bộ phân loại không làm kết quả nhúc nhích, còn")
    print("  lấy lại mẫu tập huấn luyện chỉ cho ±0,004.")
    print(f"  Muốn nói một phương pháp khác hơn hẳn E01 thì phải vượt "
          f"{spread['macro_f1_hi']:.3f}, không phải {point['macro_f1']:.3f}.")

    config = {
        "experiment": "E01",
        "dataset": {"name": args.dataset, "split_seed": REQUIRED_SPLIT_SEED},
        "features": {"groups": ["surface"], "names": list(FEATURE_NAMES)},
        "detector": {"type": "logistic_regression", "class_weight": "balanced",
                     "standardize": True},
    }
    metrics = {**point, **spread}
    extra = {
        "ms_per_sample": ms_per_sample,
        # Runs on the CPU: two features and a linear model need no GPU at all, which is itself
        # part of what makes this the floor.
        "peak_vram_mb": 0.0,
        "n_params_trainable": detector.n_params_trainable,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "n_resamples": 2000,
        "std_method": "bootstrap tập test, 2.000 lần, khoảng tin cậy 95 %",
        # Raw predictions, so a metric thought of later can be computed without running again.
        # T19 needed exactly this and the E09 records did not have it.
        "y_pred": list(predicted),
    }
    record = log_result(RUN_NAME, config, metrics, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
