"""Task T25, experiment E06: does the attention land on the chunk holding the evidence?

    python scripts/extract_features.py --config configs/e06_localization_isedsc01.yaml --split dev
    python scripts/run_localization.py --config configs/e06_localization_isedsc01.yaml

The experiment CH1 stands or falls on. Every other result infers the mechanism from a classifier
score; this reads it off directly, by comparing where the model looked against where the gold
evidence actually is.

Two questions, on two disjoint halves of the same split:

* **Localisation**, on the samples that have evidence — SUPPORTED and REFUTED, which normalise to
  ``no`` and ``intrinsic``. Reported as hit@1, hit@3 and MRR against the floor a random ranker
  reaches on the same contexts.
* **Diffuseness**, on the samples that do not — NEI, which normalises to ``extrinsic``. If the
  mechanism is real, attention should spread out when there is nothing in the context to attend
  to, so its entropy over chunks should sit higher than on the other two labels.

Runs on CPU. The GPU work is the extraction; this only reads what it wrote.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_done, shard_path  # noqa: E402
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.stats import describe_effect, mann_whitney  # noqa: E402
from vihallulens.features.localization import summarise  # noqa: E402

# The label every dataset's "no evidence in the context" class normalises to. On ISE-DSC01 this
# is NEI; docs/DATA.md records the mapping, and T13 measured that only 67 % of them are extrinsic
# in the ViHallu sense — which is why this label is treated here as "has no evidence", the thing
# actually known about it, rather than as "extrinsic".
NO_EVIDENCE_LABEL = "extrinsic"


def entropy_per_sample(records) -> np.ndarray:
    """Mean chunk entropy over all heads, one number per sample.

    Averaged over heads rather than read off the best one **on purpose**. Picking the head that
    separates the labels most would be choosing the test statistic after seeing the data, and the
    p-value would no longer mean anything. The average involves no choice.
    """
    return np.asarray(
        [float(np.mean(record["chunk_entropy"])) for record in records], dtype=float
    )


def report_localisation(records, layer_indices, n_heads) -> dict:
    ranks = np.asarray([r["gold_rank"] for r in records], dtype=np.int16)
    ranks = ranks.reshape(len(records), len(layer_indices), n_heads)
    summary = summarise(ranks, np.asarray([r["n_chunks"] for r in records]))

    print()
    print("-" * 80)
    print(f"ĐỊNH VỊ CHÚ Ý — {summary['n_samples']:,} mẫu có bằng chứng, "
          f"trung bình {summary['mean_chunks']:.1f} đoạn mỗi ngữ cảnh")
    print("-" * 80)
    print(f"  {'Chỉ số':<10} {'đầu tốt nhất':>13} {'sàn ngẫu nhiên':>15} "
          f"{'gấp sàn':>9}   {'trung bình mọi đầu':>19}")
    for key in ("hit@1", "hit@3", "mrr"):
        layer, head = summary[f"{key}_head"]
        print(f"  {key:<10} {summary[key]:>13.4f} {summary[f'{key}_floor']:>15.4f} "
              f"{summary[f'{key}_lift']:>8.2f}x   {summary[f'{key}_mean_over_heads']:>19.4f}"
              f"   (lớp {layer_indices[layer]}, đầu {head})")
    print()
    print("  'đầu tốt nhất' chọn trên chính dữ liệu này nên lạc quan theo thiết kế — đọc là")
    print("  'đầu mạnh nhất tìm được', không phải một con số trên tập giữ riêng.")
    return summary


def report_diffuseness(with_evidence, without_evidence) -> dict:
    a = entropy_per_sample(without_evidence)
    b = entropy_per_sample(with_evidence)
    test = mann_whitney(a, b)

    print()
    print("-" * 80)
    print("ĐỘ TẢN CỦA CHÚ Ý KHI KHÔNG CÓ BẰNG CHỨNG")
    print("-" * 80)
    print(f"  entropy trung vị, nhãn không bằng chứng : {test['median_a']:.4f}  "
          f"({test['n_a']:,} mẫu)")
    print(f"  entropy trung vị, hai nhãn có bằng chứng: {test['median_b']:.4f}  "
          f"({test['n_b']:,} mẫu)")
    print(f"  P(tản hơn)                              : {test['probability_superior']:.4f}")
    print(f"  cỡ ảnh hưởng (rank-biserial)            : {test['effect']:+.4f}  "
          f"→ {describe_effect(test['effect'])}")
    print(f"  Mann-Whitney U                          : z = {test['z']:.2f}, "
          f"p = {test['p_value']:.3g}")
    print()
    print("  Với cỡ mẫu này p gần như chắc chắn rất nhỏ, nên **cỡ ảnh hưởng mới là con số**")
    print("  phải đọc. p chỉ nói khác biệt không do ngẫu nhiên, không nói nó có đáng kể không.")
    return test


def main() -> int:
    parser = argparse.ArgumentParser(description="T25/E06: định vị chú ý so với bằng chứng vàng.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--split", default="dev", choices=("train", "dev", "test"))
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    run = extraction_hash(cfg)
    path = shard_path(args.processed_dir, run, cfg.dataset.name, args.split)
    records = sorted(load_done(path).values(), key=lambda record: record["sample_id"])
    if not records:
        print(f"\nThiếu đặc trưng: {path}")
        print(f"Chạy trước: python scripts/extract_features.py --config {args.config} "
              f"--split {args.split}")
        return 1

    layer_indices = records[0]["layer_indices"]
    n_heads = len(records[0]["lookback_total"]) // len(layer_indices)
    with_evidence = [r for r in records if "gold_rank" in r]
    without_evidence = [r for r in records if r["label"] == NO_EVIDENCE_LABEL]
    truncated = sum(1 for r in records if r["truncated"])

    print()
    print("=" * 80)
    print("E06 — ĐỊNH VỊ CHÚ Ý TRÊN NGỮ CẢNH DÀI")
    print("=" * 80)
    print(f"  cấu hình              : {args.config}  (trích {run})")
    print(f"  bộ dữ liệu            : {cfg.dataset.name}/{args.split}, {len(records):,} mẫu")
    cutting = cfg.chunking.strategy
    if cfg.chunking.window_size:
        cutting += f", cửa sổ {cfg.chunking.window_size} bước {cfg.chunking.stride}"
    print(f"  chia đoạn             : {cutting}")
    print(f"  lưới lớp × đầu        : {len(layer_indices)} × {n_heads}")
    print(f"  có bằng chứng định vị được : {len(with_evidence):,}")
    print(f"  nhãn không bằng chứng      : {len(without_evidence):,}")
    print(f"  bị cắt ngữ cảnh            : {truncated:,}/{len(records):,}")

    missing = len(records) - len(with_evidence) - len(without_evidence)
    if missing:
        print(f"  không định vị được bằng chứng : {missing:,}  ← loại khỏi phần định vị")

    if not with_evidence:
        print("\nKhông có mẫu nào định vị được bằng chứng. Kiểm lại cột evidence của bộ dữ liệu.")
        return 1

    summary = report_localisation(with_evidence, layer_indices, n_heads)
    test = (report_diffuseness(with_evidence, without_evidence)
            if len(without_evidence) >= 20 else None)

    verdict = summary["hit@1_lift"] > 1.0
    print()
    print("=" * 80)
    if verdict:
        print(f"  hit@1 vượt sàn ngẫu nhiên {summary['hit@1_lift']:.2f} lần — "
              f"cơ chế có tín hiệu.")
    else:
        print("  hit@1 KHÔNG vượt sàn ngẫu nhiên. Chú ý không rơi vào đoạn bằng chứng.")
        print("  Đây là kết quả bác CH1 và phải được báo cáo đúng như vậy, "
              "không đi tìm cách đọc khác.")
    print("=" * 80)

    extra = {
        "n_localised": len(with_evidence),
        "n_no_evidence": len(without_evidence),
        "n_unlocated": missing,
        "n_truncated": truncated,
        "layer_indices": layer_indices,
        "n_heads": n_heads,
        "best_heads": {k: summary[f"{k}_head"] for k in ("hit@1", "hit@3", "mrr")},
        "entropy_test": test,
        # No per-sample timing on this path: it reads a shard the GPU already wrote, so a number
        # here would be the cost of reading JSON, not the cost of the method.
        "ms_per_sample": None,
        "peak_vram_mb": 0.0,
        "selection_note": "đầu tốt nhất chọn trên chính dữ liệu báo cáo, là cận trên chứ không "
                          "phải kết quả giữ riêng",
    }
    metrics = {k: v for k, v in summary.items() if not isinstance(v, tuple)}
    record = log_result(cfg.run_name, {**cfg.to_dict(), "experiment": "E06"},
                        metrics, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
