"""Task T20, experiment E02: the faithful reproduction of Lookback Lens.

This is the internal comparison that matters most, because the thesis's contribution is a direct
modification of this method. If chunk-aware beats a *weak* reproduction of it, the comparison
proves nothing.

    python scripts/extract_features.py --config configs/e02_lookback_vihallu.yaml --split train
    python scripts/extract_features.py --config configs/e02_lookback_vihallu.yaml --split test
    python scripts/run_lookback_baseline.py --config configs/e02_lookback_vihallu.yaml

Two differences from the paper that have to be stated whenever the numbers are:

* The paper takes spans from a **sliding window of eight tokens**; ViHallu labels whole
  responses, so a span here is the whole response.
* The paper classifies **binary** and reports **AUROC**; this is three classes and macro-F1.
  The two numbers do not belong side by side.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_matrix, shard_path  # noqa: E402
from vihallulens.config import REQUIRED_SPLIT_SEED, extraction_hash, load_config  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import (  # noqa: E402
    LABELS,
    bootstrap_ci,
    compute_metrics,
)
from vihallulens.features.lookback import E02_DENOMINATOR, feature_names  # noqa: E402

RUN_NAME = "e02_lookback_lens"

# The completion check of T20 in TASKS.md. E01's macro-F1 is the floor a reproduction has to
# clear; below it, the fault is almost certainly in the extraction rather than in the method,
# and reporting the number would be reporting a bug.
E01_MACRO_F1 = 0.6562


def top_heads(detector, names: list[str], n: int = 10) -> list[tuple[str, float]]:
    """The layer-head pairs the classifier leans on hardest.

    One of the paper's findings is that a few heads carry most of the signal, so a reproduction
    that spreads its weight evenly over 756 features has probably reproduced noise. This also
    feeds E13, which asks whether those heads sit in the same places in a different model.
    """
    weights = detector.feature_weights
    order = np.argsort(weights)[::-1][:n]
    return [(names[index], float(weights[index])) for index in order]


def main() -> int:
    parser = argparse.ArgumentParser(description="E02: tái lập Lookback Lens gốc.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--denominator", default=E02_DENOMINATOR, choices=("total", "context"))
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    # The *extraction* hash, matching what extract_features.py names its shards. T22 split this
    # from the full config hash so E02 and E03 could share one GPU pass; this script kept
    # asking for the old name and could no longer find its own features.
    run = extraction_hash(cfg)

    parts = {}
    for split in ("train", "test"):
        path = shard_path(args.processed_dir, run, cfg.dataset.name, split)
        if not path.exists():
            print(f"\nThiếu đặc trưng của tập {split}: {path}")
            print("Chạy trước: python scripts/extract_features.py "
                  f"--config {args.config} --split {split}")
            return 1
        parts[split] = load_matrix(path, args.denominator)

    (x_train, y_train, _, train_rows) = parts["train"]
    (x_test, y_test, _, test_rows) = parts["test"]

    print()
    print("=" * 80)
    print("T20 / E02 — TÁI LẬP LOOKBACK LENS GỐC")
    print("=" * 80)
    print(f"  cấu hình              : {args.config}  (hash {run})")
    print(f"  mẫu số                : lookback_{args.denominator}"
          f"{'  ← đúng công thức bài gốc' if args.denominator == 'total' else ''}")
    print(f"  train / test          : {len(x_train):,} / {len(x_test):,} mẫu")

    layers = train_rows[0]["layer_indices"]
    n_heads = x_train.shape[1] // len(layers)
    names = feature_names(layers, n_heads, args.denominator)
    print(f"  đặc trưng             : {x_train.shape[1]:,} = {len(layers)} lớp × {n_heads} đầu")

    truncated = sum(row["truncated"] for row in train_rows + test_rows)
    nonfinite = sum(bool(row["nonfinite_layers"]) for row in train_rows + test_rows)
    total = len(train_rows) + len(test_rows)
    print(f"  bị cắt ngữ cảnh       : {truncated:,}/{total:,} ({truncated / total * 100:.1f} %)")
    print(f"  có lớp tràn số        : {nonfinite:,}/{total:,}")

    # Three checks before any score is believed. Each catches a way the extraction can be
    # wrong while still producing a full, plausible-looking matrix.
    print()
    print("-" * 80)
    print("KIỂM TRA ĐẶC TRƯNG TRƯỚC KHI TIN CON SỐ")
    print("-" * 80)
    both = np.vstack([x_train, x_test])
    finite = np.isfinite(both)
    inside = (both >= 0.0) & (both <= 1.0) & finite
    print(f"  hữu hạn               : {finite.mean() * 100:.4f} %")
    print(f"  nằm trong [0, 1]      : {inside.mean() * 100:.4f} %"
          "   ← tỷ lệ nên nằm trong khoảng này theo định nghĩa")
    print(f"  trung bình / lệch chuẩn: {both[finite].mean():.4f} / {both[finite].std():.4f}")
    spread = both.std(axis=0)
    print(f"  đặc trưng không đổi   : {int((spread < 1e-8).sum()):,}/{both.shape[1]:,}"
          "   ← nhiều thì có lớp hoặc đầu bị chết")
    if not finite.all():
        print("  CẢNH BÁO: có giá trị không hữu hạn, bộ phân loại sẽ hỏng.")
        return 1

    detector = LookbackDetector(
        detector_type=cfg.detector.type,
        class_weight=cfg.detector.class_weight,
        seed=REQUIRED_SPLIT_SEED,
    ).fit(x_train, y_train)

    started = time.perf_counter()
    predicted = detector.predict(x_test)
    proba = detector.predict_proba(x_test)
    ms_per_sample = (time.perf_counter() - started) * 1000 / len(x_test)
    point = compute_metrics(y_test, predicted, proba, proba_labels=detector.classes_)
    interval = bootstrap_ci(y_test, predicted, seed=REQUIRED_SPLIT_SEED)

    print()
    print("-" * 80)
    print(f"KẾT QUẢ TRÊN TẬP TEST — {len(x_test):,} mẫu")
    print("-" * 80)
    print(f"  {'Chỉ số':<16} {'Giá trị':>9}   {'khoảng tin cậy 95 %':>21}")
    for key in ("macro_f1", "accuracy", *[f"f1_{label}" for label in LABELS]):
        print(f"  {key:<16} {point[key]:>9.4f}   "
              f"[{interval[f'{key}_lo']:.4f}, {interval[f'{key}_hi']:.4f}]")
    print(f"  {'ece':<16} {point['ece']:>9.4f}")
    print()
    print(f"  {'nhị phân':<16} {point['binary_macro_f1']:>9.4f}   "
          f"[{interval['binary_macro_f1_lo']:.4f}, {interval['binary_macro_f1_hi']:.4f}]")
    print(f"  {'  bắt được':<16} {point['binary_recall']:>9.4f}")
    print(f"  {'  báo đúng':<16} {point['binary_precision']:>9.4f}")

    print()
    print("  Mười đầu chú ý bộ phân loại dựa vào nhiều nhất:")
    for name, weight in top_heads(detector, names):
        print(f"    {name:<34} {weight:.4f}")
    print("  Bài gốc thấy tín hiệu dồn vào một số ít đầu. Trọng số trải đều khắp 756 đặc")
    print("  trưng là dấu hiệu đã tái lập nhiễu chứ không phải tín hiệu.")

    config = {**cfg.to_dict(), "experiment": "E02", "denominator": args.denominator}
    extra = {
        "n_train": len(x_train),
        "n_test": len(x_test),
        "n_features": int(x_train.shape[1]),
        "n_layers": len(layers),
        "n_heads": n_heads,
        "layer_indices": layers,
        "truncated_rate": truncated / total,
        "nonfinite_samples": nonfinite,
        "ms_per_sample": ms_per_sample,
        "peak_vram_mb": 0.0,
        "n_params_trainable": detector.n_params_trainable,
        "top_heads": top_heads(detector, names, n=20),
        "y_pred": list(predicted),
        "std_method": "_lo/_hi/_se từ bootstrap tập test; bộ phân loại tất định nên không có _std",
        "span": "toàn bộ phản hồi, khác cửa sổ trượt 8 token của bài gốc",
        "task_difference": "bài gốc phân loại nhị phân và báo AUROC; đây ba lớp và macro-F1",
    }
    record = log_result(RUN_NAME, config, {**point, **interval}, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")

    print()
    print("-" * 80)
    print("TIÊU CHÍ HOÀN THÀNH CỦA T20")
    print("-" * 80)
    if point["macro_f1"] > E01_MACRO_F1:
        print(f"  ĐẠT: {point['macro_f1']:.4f} > {E01_MACRO_F1:.4f} của baseline tầm thường E01.")
        return 0
    print(f"  KHÔNG ĐẠT: {point['macro_f1']:.4f} ≤ {E01_MACRO_F1:.4f} của E01.")
    print("  Theo T20 trong TASKS.md thì DỪNG LẠI rà soát khâu trích đặc trưng, đừng báo cáo")
    print("  con số này. Ba chỗ phải soi trước tiên, theo mục 1 docs/REFERENCES.md:")
    print("    1. Tỷ lệ có phải trung bình theo token không — chia cho N và t-1, không lấy tổng.")
    print("    2. Véc-tơ có nối đủ lớp × đầu rồi mới trung bình qua các bước không.")
    print("    3. Vùng ngữ cảnh và vùng phản hồi có dò đúng vị trí token không.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
