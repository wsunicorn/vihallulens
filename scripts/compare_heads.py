"""Task T30, experiment E13: do two reading models use attention heads in the same places?

E13's macro-F1 column is the easy half. This is the other half, and it is the part that asks a
question nobody has answered for Vietnamese: Sailor2 is Qwen2.5 continued-pretrained on South-
East Asian languages, so if the heads a linear probe leans on sit at the *same* depths and
indices in both, then head position is a property of the architecture and survives heavy
language-specific training. If they move, it is a property of the training data.

    python scripts/compare_heads.py --config-a configs/e03_chunk_sentence_vihallu.yaml \
                                    --config-b configs/e13_sailor2_vihallu.yaml

Costs no GPU: both sides refit a linear classifier on shards already extracted.

**The grids may not match.** Qwen2.5-7B gives 28 layers; Sailor2-8B is an expansion and has
more. When layer counts differ, comparing "layer 5 to layer 5" is comparing different fractions
of the network, so this script refuses the index-wise metrics and reports only the depth profile,
which is defined for both. Silently lining up index 5 with index 5 would produce a number that
looks like an answer and is not one.

Three metrics, and the first is useless without the second:

    overlap@k      how many of the top-k (layer, head) pairs both models share
    kỳ vọng ngẫu nhiên  k² / N — what overlap@k would be for two unrelated rankings
    Spearman       rank correlation over all N pairs, not just the top
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR  # noqa: E402
from run_chunk_aware import load_split  # noqa: E402
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.stats import _rank_with_ties  # noqa: E402
from vihallulens.features.assemble import blocks_for, build_feature_matrix, rank_heads  # noqa: E402

TOP_K = (10, 32, 64)


def head_ranking(config_path: Path, processed_dir: Path, split: str = "train"):
    """Fit on one model's shard and return its head ordering plus the grid it lives on."""
    cfg = load_config(config_path)
    run = extraction_hash(cfg)
    records, path, dropped = load_split(processed_dir, run, cfg.dataset.name, split)
    if records is None:
        raise SystemExit(
            f"Thiếu đặc trưng tập {split} của {cfg.run_name}: {path}\n"
            f"Chạy trước: python scripts/extract_features.py --config {config_path} "
            f"--split {split}"
        )

    groups = list(cfg.features.groups)
    layer_indices = records[0]["layer_indices"]
    n_layers = len(layer_indices)
    n_heads = len(records[0]["lookback_total"]) // n_layers

    labels = np.asarray([row["label"] for row in records])
    matrix = build_feature_matrix(records, groups, n_layers, n_heads, "all")
    model = LookbackDetector(seed=cfg.dataset.split_seed).fit(matrix, labels)
    order = rank_heads(model.feature_weights, len(blocks_for(groups)), n_layers, n_heads)

    # Score per pair, in grid order, so Spearman can run over the whole grid rather than the top.
    per_pair = np.abs(model.feature_weights).reshape(
        len(blocks_for(groups)), n_layers * n_heads).max(axis=0)

    return {
        "run_name": cfg.run_name,
        "model_name": cfg.extractor.model_name,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "layer_indices": list(layer_indices),
        "order": order,
        "score": per_pair,
        "n_samples": len(records),
        "n_dropped": len(dropped),
    }


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Rank correlation, ties averaged. Hand-written to avoid declaring scipy for one number."""
    ranked_a = _rank_with_ties(a)
    ranked_b = _rank_with_ties(b)
    ranked_a = ranked_a - ranked_a.mean()
    ranked_b = ranked_b - ranked_b.mean()
    denominator = np.sqrt((ranked_a**2).sum() * (ranked_b**2).sum())
    return float((ranked_a * ranked_b).sum() / denominator) if denominator else 0.0


def depth_profile(side: dict, k: int) -> dict:
    """Where the top-k heads sit as a fraction of network depth.

    Defined for both models whatever their layer counts, which is exactly why it is the metric
    that survives a grid mismatch. Layer 5 of 28 and layer 6 of 32 are both about 0,19 deep.
    """
    pairs = side["order"][:k]
    layers = pairs // side["n_heads"]
    depth = layers / max(side["n_layers"] - 1, 1)
    return {
        "mean_depth": float(depth.mean()),
        "median_depth": float(np.median(depth)),
        "share_first_third": float((depth < 1 / 3).mean()),
        "share_middle_third": float(((depth >= 1 / 3) & (depth < 2 / 3)).mean()),
        "share_last_third": float((depth >= 2 / 3).mean()),
    }


def name_of(side: dict, flat: int) -> str:
    layer = side["layer_indices"][flat // side["n_heads"]]
    return f"l{layer}_h{flat % side['n_heads']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="E13: so vị trí đầu chú ý giữa hai mô hình đọc.")
    parser.add_argument("--config-a", type=Path, required=True)
    parser.add_argument("--config-b", type=Path, required=True)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--split", default="train", choices=("train", "dev", "test"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    a = head_ranking(args.config_a, args.processed_dir, args.split)
    b = head_ranking(args.config_b, args.processed_dir, args.split)

    print()
    print("=" * 84)
    print("E13 — VỊ TRÍ ĐẦU CHÚ Ý CÓ ÍCH, HAI MÔ HÌNH ĐỌC")
    print("=" * 84)
    for side in (a, b):
        print(f"  {side['run_name']:<32} {side['model_name']}")
        print(f"    lưới lớp × đầu      : {side['n_layers']} × {side['n_heads']} "
              f"= {side['n_layers'] * side['n_heads']:,} cặp   ({side['n_samples']:,} mẫu train)")
        if side["n_dropped"]:
            total = side["n_samples"] + side["n_dropped"]
            print(f"    bỏ mẫu có nan       : {side['n_dropped']:,}/{total:,} "
                  f"({side['n_dropped'] / total * 100:.2f} %)")

    print()
    print("  Mười đầu dẫn đầu mỗi bên:")
    print(f"    {'#':>3}  {'A: ' + a['run_name']:<34}{'B: ' + b['run_name']}")
    for i in range(10):
        left = f"{name_of(a, a['order'][i])}  ({a['score'][a['order'][i]]:.4f})"
        right = f"{name_of(b, b['order'][i])}  ({b['score'][b['order'][i]]:.4f})"
        print(f"    {i + 1:>3}  {left:<34}{right}")

    same_grid = (a["n_layers"], a["n_heads"]) == (b["n_layers"], b["n_heads"])
    print()
    if same_grid:
        total = a["n_layers"] * a["n_heads"]
        print(f"  Hai lưới trùng nhau ({a['n_layers']} × {a['n_heads']}), so được theo chỉ số.")
        print()
        print(f"    {'k':>5}{'trùng nhau':>13}{'kỳ vọng ngẫu nhiên':>22}{'gấp':>8}")
        for k in TOP_K:
            if k > total:
                continue
            shared = len(set(a["order"][:k].tolist()) & set(b["order"][:k].tolist()))
            expected = k * k / total
            ratio = shared / expected if expected else float("nan")
            print(f"    {k:>5}{shared:>10}/{k:<3}{expected:>19.2f}{ratio:>8.2f}×")

        rho = spearman(a["score"], b["score"])
        print()
        print(f"  Tương quan hạng Spearman trên cả {total:,} cặp: {rho:+.4f}")
        print("  Con số này tính trên toàn lưới nên không phụ thuộc việc chọn k, và nó là con số"
              " nên dẫn khi viết báo cáo.")
    else:
        print("  !! HAI LƯỚI KHÁC NHAU — KHÔNG so theo chỉ số !!")
        print(f"     A có {a['n_layers']} lớp, B có {b['n_layers']} lớp. Lớp 5 của một mô hình 28")
        print("     lớp và lớp 5 của một mô hình 32 lớp nằm ở hai độ sâu khác nhau, nên phép")
        print("     trùng chỉ số và Spearman đều vô nghĩa ở đây. Chỉ báo phần độ sâu tương đối.")

    print()
    print("  Phân bố theo độ sâu tương đối (0 = lớp đầu, 1 = lớp cuối):")
    print(f"    {'k':>5}  {'bên':<4}{'TB độ sâu':>12}{'1/3 đầu':>11}"
          f"{'1/3 giữa':>11}{'1/3 cuối':>11}")
    for k in TOP_K:
        for label, side in (("A", a), ("B", b)):
            if k > side["n_layers"] * side["n_heads"]:
                continue
            profile = depth_profile(side, k)
            print(f"    {k:>5}  {label:<4}{profile['mean_depth']:>12.3f}"
                  f"{profile['share_first_third'] * 100:>10.1f}%"
                  f"{profile['share_middle_third'] * 100:>10.1f}%"
                  f"{profile['share_last_third'] * 100:>10.1f}%")

    print()
    print("  Cách đọc: nếu hai bên có phân bố độ sâu giống nhau thì vị trí đầu sao chép là thuộc")
    print("  tính của kiến trúc và sống sót qua việc huấn luyện thêm tiếng Việt. Nếu khác thì nó")
    print("  phụ thuộc dữ liệu huấn luyện. Cả hai đều là kết quả — đừng lược cái thứ hai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
