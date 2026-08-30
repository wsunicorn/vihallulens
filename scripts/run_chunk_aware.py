"""Tasks T22 and T23, experiments E03 and E04: the chunk-aware detector.

The experiment the whole thesis is for. E02 reproduced Lookback Lens and reached macro-F1 0,7465
by asking one question of the attention map — how much of it went to the context. This asks a
second one: how that attention was spread across the pieces of the context.

    CFG=configs/e03_chunk_sentence_vihallu.yaml
    python scripts/extract_features.py --config $CFG --split train
    python scripts/extract_features.py --config $CFG --split dev
    python scripts/extract_features.py --config $CFG --split test
    python scripts/run_chunk_aware.py --config $CFG

**Head aggregation is chosen on the dev split, never on test.** Six feature families over 27
layers and 28 heads is 4.536 columns against 5.600 training rows, so some reduction is needed —
but picking the reduction that scores best on test would report a number that cannot be
reproduced by anyone who did not already know the answer. Section 4 of docs/EXPERIMENTS.md
requires dev for exactly this.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_done, shard_path  # noqa: E402
from vihallulens.config import REQUIRED_SPLIT_SEED, extraction_hash, load_config  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import (  # noqa: E402
    LABELS,
    bootstrap_ci,
    compute_metrics,
)
from vihallulens.features.assemble import (  # noqa: E402
    GROUP_BLOCKS,
    blocks_for,
    build_feature_matrix,
    column_names,
    rank_heads,
)

# Falls back to the config's own run_name, so the four E04 window runs do not all report
# themselves as E03 in results/runs.jsonl and become impossible to tell apart afterwards.
RUN_NAME = None

# The number to beat, measured at T20. Not E01's 0,6562: chunk-aware and aggregate lookback are
# the same family of method differing only in how the denominator is split, so clearing E01
# would only show that attention helps. Clearing E02 is what shows that *chunking* helps.
E02_MACRO_F1 = 0.7465

# Candidate widths for topk_heads. Small enough to stay far below the 5.600 training rows even
# with six blocks, wide enough to keep more than a handful of heads.
TOPK_GRID = (8, 16, 32, 64)

# A seventh candidate, added after the first E03 run exposed a gap in the search space. Keeping
# k heads shrinks *every* block, including the single narrow one — so the chosen k=32 gave the
# aggregate lookback ratio 32 columns where E02 had 756, and E03 lost 0,045 on the intrinsic
# class that those columns carried.
#
# The search space simply did not contain "keep the cheap block whole and thin the wide ones",
# which means E03 could not be guaranteed to contain E02 as a special case. It can now. The
# candidate is scored on dev like every other one; it is not chosen because it looked good on
# test, and the first run's numbers are reported alongside rather than replaced.
MIXED = "mixed_all_basic_topk_rest"


def load_split(processed_dir: Path, run: str, dataset: str, split: str):
    """Records for one split, sorted by sample id so a resumed extraction gives one matrix."""
    path = shard_path(processed_dir, run, dataset, split)
    if not path.exists():
        return None, path
    records = sorted(load_done(path).values(), key=lambda record: record["sample_id"])
    return records, path


def split_groups(groups) -> tuple[list[str], list[str]]:
    """Separate the aggregate lookback group from the chunk-shape ones."""
    wide = [group for group in groups if group != "basic"]
    return (["basic"] if "basic" in groups else []), wide


def build_mixed(records, groups, n_layers, n_heads, keep):
    """All heads for ``basic``, only the chosen ones for the wide blocks."""
    narrow, wide = split_groups(groups)
    parts = []
    if narrow:
        parts.append(build_feature_matrix(records, narrow, n_layers, n_heads, "all"))
    if wide:
        parts.append(build_feature_matrix(records, wide, n_layers, n_heads, "topk_heads", keep))
    return np.hstack(parts)


def mixed_names(groups, layer_indices, n_heads, keep) -> list[str]:
    narrow, wide = split_groups(groups)
    names = []
    if narrow:
        names += column_names(blocks_for(narrow), layer_indices, n_heads, "all")
    if wide:
        names += column_names(blocks_for(wide), layer_indices, n_heads, "topk_heads", keep)
    return names


def matrix_for(records, groups, n_layers, n_heads, mode, keep):
    """One entry point for every candidate, mixed included."""
    if mode == MIXED:
        return build_mixed(records, groups, n_layers, n_heads, keep)
    return build_feature_matrix(records, groups, n_layers, n_heads, mode, keep)


def select_aggregation(x_train, y_train, records, groups, n_layers, n_heads, y_dev, seed):
    """Choose how to reduce the head axis, scoring every candidate on the **dev** split.

    The ranking of heads comes from a model fitted on train — that is training information used
    on training data, which is allowed. What dev decides is only *how many* to keep, and whether
    to keep individual heads at all rather than averaging them. Test is not consulted.
    """
    n_blocks = len(blocks_for(groups))
    full = LookbackDetector(seed=seed).fit(x_train, y_train)
    order = rank_heads(full.feature_weights, n_blocks, n_layers, n_heads)

    candidates = [("all", None), ("mean_over_heads", None),
                  *[("topk_heads", order[:k]) for k in TOPK_GRID]]
    # Only worth trying when there is a narrow block to keep whole and wide ones to thin.
    if len(GROUP_BLOCKS.get("basic", ())) and "basic" in groups and len(groups) > 1:
        candidates += [(MIXED, order[:k]) for k in TOPK_GRID]

    trials = []
    for mode, keep in candidates:
        train_matrix = matrix_for(records["train"], groups, n_layers, n_heads, mode, keep)
        dev_matrix = matrix_for(records["dev"], groups, n_layers, n_heads, mode, keep)
        model = LookbackDetector(seed=seed).fit(train_matrix, y_train)
        score = compute_metrics(y_dev, model.predict(dev_matrix))["macro_f1"]
        label = mode if keep is None else f"{mode} k={len(keep)}"
        trials.append({"mode": mode, "keep": keep, "label": label,
                       "n_features": train_matrix.shape[1], "dev_macro_f1": float(score)})
        del train_matrix, dev_matrix, model

    # Ties go to the narrower matrix. Several widths scoring the same on 700 dev samples is
    # common and says the extra columns bought nothing; taking the widest would then carry
    # overfitting risk into the test score for no measured gain. Making this explicit rather
    # than leaving it to the order the candidates happen to be listed in.
    best = min(trials, key=lambda trial: (-trial["dev_macro_f1"], trial["n_features"]))
    return best, trials


def main() -> int:
    parser = argparse.ArgumentParser(description="E03/E04: bộ phát hiện chunk-aware.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-name", default=RUN_NAME,
                        help="mặc định lấy run_name trong file cấu hình")
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    parser.add_argument(
        "--dev-only", action="store_true",
        help="dừng sau khi chấm dev, không đụng tập test — dùng cho lượt quét E04 của T23",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    run_name = args.run_name or cfg.run_name
    run = extraction_hash(cfg)
    groups = list(cfg.features.groups)

    # T23 sweeps three window sizes and only one of them survives into T24, so the losers
    # never need a test shard: not extracting it saves seven GPU minutes each, and more to
    # the point it makes "the choice was made on dev" a fact about what was computed rather
    # than a promise about what was looked at.
    wanted = ("train", "dev") if args.dev_only else ("train", "dev", "test")
    records, labels = {}, {}
    for split in wanted:
        rows, path = load_split(args.processed_dir, run, cfg.dataset.name, split)
        if rows is None:
            print(f"\nThiếu đặc trưng của tập {split}: {path}")
            print("Chạy trước: python scripts/extract_features.py "
                  f"--config {args.config} --split {split}")
            return 1
        records[split] = rows
        labels[split] = np.asarray([row["label"] for row in rows])

    layer_indices = records["train"][0]["layer_indices"]
    n_layers = len(layer_indices)
    n_heads = len(records["train"][0]["lookback_total"]) // n_layers
    blocks = blocks_for(groups)

    print()
    print("=" * 80)
    print(f"{run_name.upper()} — BỘ PHÁT HIỆN CHUNK-AWARE")
    print("=" * 80)
    print(f"  cấu hình              : {args.config}  (trích {run})")
    cutting = cfg.chunking.strategy
    if cfg.chunking.window_size:
        cutting += f", cửa sổ {cfg.chunking.window_size} bước {cfg.chunking.stride}"
    print(f"  chia đoạn             : {cutting}")
    print(f"  nhóm đặc trưng        : {', '.join(groups)}")
    print(f"  khối                  : {', '.join(blocks)}")
    sizes = " / ".join(f"{len(records[split]):,}" for split in wanted)
    print(f"  {' / '.join(wanted):<22}: {sizes} mẫu")
    if args.dev_only:
        print("  chế độ                : --dev-only, KHÔNG chấm tập test")
    print(f"  lưới lớp × đầu        : {n_layers} × {n_heads}")

    chunks = [row["n_chunks"] for row in records["train"]]
    single = sum(1 for count in chunks if count == 1)
    print(f"  số đoạn mỗi ngữ cảnh  : trung bình {np.mean(chunks):.1f}, "
          f"trung vị {int(np.median(chunks))}, tối đa {max(chunks)}")
    print(f"  ngữ cảnh chỉ 1 đoạn   : {single:,}/{len(chunks):,} "
          f"({single / len(chunks) * 100:.1f} %)   ← chunk-aware thoái hóa thành gộp ở đó")

    x_train = build_feature_matrix(records["train"], groups, n_layers, n_heads)
    print(f"  đặc trưng nếu giữ hết : {x_train.shape[1]:,}")

    # -- choosing the head aggregation, on dev --------------------------------------------
    print()
    print("-" * 80)
    print("CHỌN CÁCH GỘP ĐẦU CHÚ Ý — chấm trên tập DEV, không đụng tập test")
    print("-" * 80)
    started = time.perf_counter()
    best, trials = select_aggregation(
        x_train, labels["train"], records, groups, n_layers, n_heads,
        labels["dev"], REQUIRED_SPLIT_SEED,
    )
    print(f"  {'Cách gộp':<32} {'số chiều':>10} {'macro-F1 dev':>14}")
    for trial in trials:
        mark = "  ← chọn" if trial["label"] == best["label"] else ""
        print(f"  {trial['label']:<32} {trial['n_features']:>10,} "
              f"{trial['dev_macro_f1']:>14.4f}{mark}")
    print(f"  ({time.perf_counter() - started:.0f} giây)")

    if args.dev_only:
        print()
        print("-" * 80)
        print(f"  chọn                  : {best['label']}, {best['n_features']:,} chiều")
        print(f"  macro-F1 trên DEV     : {best['dev_macro_f1']:.4f}")
        print("  Dừng ở đây theo --dev-only. Tập test để dành cho cấu hình thắng ở T24.")
        return 0

    # -- the chosen model, scored once on test --------------------------------------------
    keep = best["keep"]
    matrices = {
        split: matrix_for(records[split], groups, n_layers, n_heads, best["mode"], keep)
        for split in ("train", "test")
    }
    names = (mixed_names(groups, layer_indices, n_heads, keep) if best["mode"] == MIXED
             else column_names(blocks, layer_indices, n_heads, best["mode"], keep))
    detector = LookbackDetector(
        detector_type=cfg.detector.type,
        class_weight=cfg.detector.class_weight,
        seed=REQUIRED_SPLIT_SEED,
    ).fit(matrices["train"], labels["train"])

    began = time.perf_counter()
    predicted = detector.predict(matrices["test"])
    proba = detector.predict_proba(matrices["test"])
    ms_per_sample = (time.perf_counter() - began) * 1000 / len(matrices["test"])
    point = compute_metrics(labels["test"], predicted, proba, proba_labels=detector.classes_)
    interval = bootstrap_ci(labels["test"], predicted, seed=REQUIRED_SPLIT_SEED)

    print()
    print("-" * 80)
    print(f"KẾT QUẢ TRÊN TẬP TEST — {len(matrices['test']):,} mẫu")
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
    print("  Mười đặc trưng bộ phân loại dựa vào nhiều nhất:")
    weights = detector.feature_weights
    for index in np.argsort(weights)[::-1][:10]:
        print(f"    {names[index]:<34} {weights[index]:.4f}")

    # Which family the weight actually sits in. If the contribution is real, the chunk blocks
    # should carry a share of it well above what a null contribution would give them.
    per_block = {}
    for block in blocks:
        columns = [index for index, name in enumerate(names) if name.startswith(f"{block}_l")]
        per_block[block] = float(weights[columns].sum())
    total = sum(per_block.values()) or 1.0
    print()
    print("  Trọng số chia theo khối đặc trưng:")
    for block, value in sorted(per_block.items(), key=lambda item: -item[1]):
        print(f"    {block:<22} {value / total * 100:>5.1f} %")

    config = {**cfg.to_dict(), "experiment": run_name.split("_")[0].upper()}
    extra = {
        "n_train": len(records["train"]),
        "n_dev": len(records["dev"]),
        "n_test": len(records["test"]),
        "n_features": int(matrices["test"].shape[1]),
        "head_aggregation_chosen": best["label"],
        "head_selection_trials": [
            {key: trial[key] for key in ("label", "n_features", "dev_macro_f1")}
            for trial in trials
        ],
        "layer_indices": layer_indices,
        "n_heads": n_heads,
        "mean_chunks": float(np.mean(chunks)),
        "single_chunk_rate": single / len(chunks),
        "weight_share_per_block": {k: v / total for k, v in per_block.items()},
        "top_features": [(names[i], float(weights[i])) for i in np.argsort(weights)[::-1][:20]],
        "ms_per_sample": ms_per_sample,
        "peak_vram_mb": 0.0,
        "n_params_trainable": detector.n_params_trainable,
        "y_pred": list(predicted),
        "std_method": "_lo/_hi/_se từ bootstrap tập test; bộ phân loại tất định nên không có _std",
        "selection_note": "cách gộp đầu chọn trên tập dev, tập test chỉ chấm một lần",
    }
    record = log_result(run_name, config, {**point, **interval}, extra,
                        path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")

    print()
    print("-" * 80)
    print("SO VỚI E02 — mốc thật của phần đóng góp")
    print("-" * 80)
    delta = point["macro_f1"] - E02_MACRO_F1
    print(f"  E02 lookback gộp : {E02_MACRO_F1:.4f}")
    print(f"  {run_name:<17}: {point['macro_f1']:.4f}   ({delta:+.4f})")
    if point["macro_f1"] <= E02_MACRO_F1:
        print()
        print("  CHƯA VƯỢT. Chia theo đoạn chưa đóng góp được gì trên tập này. Đừng trình bày")
        print("  như một cải tiến — kiểm cách chia đoạn và cách gộp đầu trước, rồi mới kết luận.")
        return 2
    print()
    print("  Vượt. Nhưng muốn nói HƠN HẲN thì phải vượt 0,7773 — cận trên khoảng tin cậy của")
    print("  E02 — chứ không phải chỉ vượt điểm của nó.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
