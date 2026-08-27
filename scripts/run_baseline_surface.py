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
from vihallulens.evaluation.metrics import LABELS, compute_metrics, summarise_runs  # noqa: E402
from vihallulens.features.surface import FEATURE_NAMES, surface_features  # noqa: E402

RUN_NAME = "e01_surface_baseline"
N_SEEDS = 5


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


def run_once(x_train, y_train, x_test, y_test, seed: int, bootstrap: bool) -> tuple[dict, float]:
    """One fit and one evaluation. Returns the metrics and the milliseconds per test sample."""
    if bootstrap:
        # Varying only ``random_state`` would change nothing: lbfgs on a convex problem is
        # deterministic, and five identical numbers would make the standard deviation section 3
        # of docs/EXPERIMENTS.md asks for meaningless. Resampling the training set with
        # replacement measures something real instead — how much the result depends on which
        # samples happened to be in the training set.
        rng = np.random.default_rng(seed)
        picked = rng.integers(0, len(x_train), size=len(x_train))
        x_train, y_train = x_train[picked], y_train[picked]

    detector = LookbackDetector(seed=seed).fit(x_train, y_train)
    started = time.perf_counter()
    predicted = detector.predict(x_test)
    proba = detector.predict_proba(x_test)
    elapsed_ms = (time.perf_counter() - started) * 1000
    # detector.classes_ is the column order of proba; sklearn sorts alphabetically and that is
    # not the reporting order. Passing it is what keeps the ECE honest.
    metrics = compute_metrics(y_test, predicted, proba, proba_labels=detector.classes_)
    return metrics, elapsed_ms / len(x_test)


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

    # The headline number comes from training on the whole training set once. The five
    # bootstrap runs below say how much that number could have moved.
    point, ms_per_sample = run_once(x_train, y_train, x_test, y_test, REQUIRED_SPLIT_SEED,
                                    bootstrap=False)
    repeats = [
        run_once(x_train, y_train, x_test, y_test, REQUIRED_SPLIT_SEED + offset,
                 bootstrap=True)[0]
        for offset in range(N_SEEDS)
    ]
    spread = summarise_runs(repeats)

    print()
    print("-" * 80)
    print(f"KẾT QUẢ TRÊN TẬP TEST — {len(y_test):,} mẫu")
    print("-" * 80)
    print(f"  {'Chỉ số':<14} {'Giá trị':>9} {'± lệch chuẩn':>14}")
    for key in ("macro_f1", "accuracy", *[f"f1_{label}" for label in LABELS], "ece"):
        print(f"  {key:<14} {point[key]:>9.4f} {spread[f'{key}_std']:>14.4f}")

    detector = LookbackDetector(seed=REQUIRED_SPLIT_SEED).fit(x_train, y_train)
    print()
    print(f"  Tham số phải huấn luyện : {detector.n_params_trainable}")
    print(f"  Thời gian suy luận      : {ms_per_sample:.4f} ms/mẫu")
    print("  Độ lệch chuẩn đo bằng 5 lần lấy mẫu lặp lại tập huấn luyện, vì lbfgs tất định")
    print("  nên đổi riêng hạt giống sẽ cho ra năm con số y hệt nhau.")

    config = {
        "experiment": "E01",
        "dataset": {"name": args.dataset, "split_seed": REQUIRED_SPLIT_SEED},
        "features": {"groups": ["surface"], "names": list(FEATURE_NAMES)},
        "detector": {"type": "logistic_regression", "class_weight": "balanced",
                     "standardize": True},
    }
    metrics = {**point, **{f"{key}_std": spread[f"{key}_std"] for key in point}}
    extra = {
        "ms_per_sample": ms_per_sample,
        # Runs on the CPU: two features and a linear model need no GPU at all, which is itself
        # part of what makes this the floor.
        "peak_vram_mb": 0.0,
        "n_params_trainable": detector.n_params_trainable,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "n_seeds": N_SEEDS,
        "std_method": "bootstrap tập huấn luyện",
    }
    record = log_result(RUN_NAME, config, metrics, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
