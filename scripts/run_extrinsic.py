"""Task T27, experiment E08: take the evidence away and see whether the signal notices.

    python scripts/build_retrieval_contexts.py --split dev
    python scripts/extract_features.py --config configs/e08_extrinsic_viwikifc.yaml --split dev
    python scripts/run_extrinsic.py --config configs/e08_extrinsic_viwikifc.yaml

Every other experiment here is correlational. A signal is measured, a label somebody else
assigned is compared against it, agreement is reported — and when the two agree, the conclusion
"the mechanism works" is an inference, not an observation. E06 was the closest to direct, but it
still only *observed* where attention fell.

This one **intervenes**. Each claim is paired with itself: the same response, read twice against
two ten-sentence contexts that differ in exactly one sentence. In one, that sentence is the gold
evidence; in the other, a distractor stands in its place. Nothing else moves — not the length,
not the chunk count, not the ordering, not the label of anything a person annotated.

If the chunk-aware signal means what the thesis says it means, removing the evidence should make
the attention distribution flatter: there is no longer anything in the context to concentrate on.
If it does not move, then whatever chunk-aware features are picking up on the other corpora is
not "the model found the evidence".

Reported as a **paired** test, because the two halves are the same sample twice.

Runs on CPU.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_done, shard_path  # noqa: E402
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.stats import describe_effect, wilcoxon  # noqa: E402
from vihallulens.features.chunk_aware import CHUNK_FEATURE_NAMES  # noqa: E402
from vihallulens.features.localization import summarise  # noqa: E402

PRESENT, ABSENT = "present", "absent"

# Which way each feature should move when the evidence is taken away, if the mechanism is real.
# Written down before the numbers are read, so a result that goes the other way cannot quietly be
# re-described as a confirmation.
EXPECTED_DIRECTION = {
    "chunk_entropy": +1,      # nothing to focus on, so the distribution should flatten
    "chunk_max_share": -1,    # no single chunk should dominate any more
    "chunk_gini": -1,         # less inequality between chunks
    "top1_top2_gap": -1,      # the best chunk should stop standing out from the second
    "chunk_drift": 0,         # no prediction: drift is about movement over response tokens
}


def pair_up(records, frame) -> tuple[dict[str, dict], list[str]]:
    """Index the extracted rows by ``(pair_id, condition)`` using the built dataset's metadata."""
    condition = {row["sample_id"]: row["meta"]["condition"] for row in frame.to_dict("records")}
    pair_of = {row["sample_id"]: row["meta"]["pair_id"] for row in frame.to_dict("records")}
    halves: dict[str, dict] = defaultdict(dict)
    for record in records:
        sample = record["sample_id"]
        if sample in condition:
            halves[pair_of[sample]][condition[sample]] = record
    complete = sorted(key for key, value in halves.items() if len(value) == 2)
    return halves, complete


def feature_means(record, name: str) -> float:
    """One number per sample: the feature averaged over all 756 heads.

    Averaged rather than read off the head that separates the conditions best, for the reason
    given in E06 — choosing the statistic after seeing the data makes the p-value meaningless.
    """
    return float(np.mean(record[name]))


def report_intervention(halves, complete) -> dict:
    print()
    print("-" * 80)
    print(f"BỎ BẰNG CHỨNG ĐI THÌ CHÚ Ý CÓ ĐỔI KHÔNG — {len(complete):,} cặp")
    print("-" * 80)
    print(f"  {'đặc trưng':<18}{'có vàng':>10}{'mất vàng':>10}{'đổi':>10}"
          f"{'% cặp đúng hướng':>18}{'cỡ ảnh hưởng':>14}")

    results = {}
    for name in CHUNK_FEATURE_NAMES:
        before = np.asarray([feature_means(halves[k][PRESENT], name) for k in complete])
        after = np.asarray([feature_means(halves[k][ABSENT], name) for k in complete])
        test = wilcoxon(before, after)
        results[name] = test
        expected = EXPECTED_DIRECTION[name]
        # Share of pairs that moved the way the mechanism predicts. For a feature with no
        # prediction the win rate is printed as-is and means nothing on its own.
        aligned = test["win_rate"] if expected >= 0 else 1.0 - test["win_rate"]
        mark = "" if expected == 0 else ("  ✓" if aligned > 0.5 else "  ✗")
        print(f"  {name:<18}{test['median_before']:>10.4f}{test['median_after']:>10.4f}"
              f"{test['median_change']:>+10.4f}{aligned:>17.1%}"
              f"{test['effect']:>+13.4f}{mark}")

    print()
    print("  Cột 'đổi' là trung vị của hiệu từng cặp — phải đọc CÙNG cột phần trăm.")
    print("  Kiểm định theo cặp đo mức nhất quán của HƯỚNG, không đo độ lớn: một dịch chuyển")
    print("  nhỏ tới mức vô nghĩa vẫn cho 100 % cặp đúng hướng nếu nó đều.")
    return results


def report_localisation(halves, complete, layer_indices, n_heads) -> dict | None:
    """The same measurement E06 made, on a second corpus and a different context builder."""
    rows = [halves[key][PRESENT] for key in complete if "gold_rank" in halves[key][PRESENT]]
    if len(rows) < 20:
        return None
    ranks = np.asarray([r["gold_rank"] for r in rows], dtype=np.int16)
    ranks = ranks.reshape(len(rows), len(layer_indices), n_heads)
    summary = summarise(ranks, np.asarray([r["n_chunks"] for r in rows]))

    print()
    print("-" * 80)
    print(f"ĐỊNH VỊ TRÊN NỬA CÓ VÀNG — {summary['n_samples']:,} mẫu, "
          f"{summary['mean_chunks']:.1f} đoạn mỗi ngữ cảnh")
    print("-" * 80)
    print(f"  {'Chỉ số':<10}{'đầu tốt nhất':>14}{'sàn':>10}{'gấp sàn':>10}"
          f"{'trung bình mọi đầu':>21}")
    for key in ("hit@1", "hit@3", "mrr"):
        layer, head = summary[f"{key}_head"]
        print(f"  {key:<10}{summary[key]:>14.4f}{summary[f'{key}_floor']:>10.4f}"
              f"{summary[f'{key}_lift']:>9.2f}x{summary[f'{key}_mean_over_heads']:>21.4f}"
              f"   (lớp {layer_indices[layer]}, đầu {head})")
    print()
    print("  Thứ tự mười câu truy xuất đã được XÁO trước khi ghép. Không xáo thì BM25 để câu")
    print("  vàng ở hạng 0 với 94 % claim, và 'luôn chọn đoạn đầu' sẽ trông như một cơ chế.")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="T27/E08: bỏ bằng chứng đi và đo lại chú ý.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--split", default="dev", choices=("train", "dev", "test"))
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
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

    frame = load_dataset(cfg.dataset.name, args.split, args.interim_dir)
    halves, complete = pair_up(records, frame)
    layer_indices = records[0]["layer_indices"]
    n_heads = len(records[0]["lookback_total"]) // len(layer_indices)

    print()
    print("=" * 80)
    print("E08 — BỎ BẰNG CHỨNG ĐI: PHÉP KIỂM CAN THIỆP")
    print("=" * 80)
    print(f"  cấu hình              : {args.config}  (trích {run})")
    print(f"  bộ dữ liệu            : {cfg.dataset.name}/{args.split}, {len(records):,} dòng")
    print(f"  cặp đủ hai vế         : {len(complete):,}/{len(halves):,}")
    print(f"  lưới lớp × đầu        : {len(layer_indices)} × {n_heads}")
    print(f"  bị cắt ngữ cảnh       : {sum(1 for r in records if r['truncated']):,}")

    if len(complete) < 20:
        print("\nKhông đủ cặp đủ hai vế để kiểm định. Kiểm lại lượt trích.")
        return 1

    results = report_intervention(halves, complete)
    localisation = report_localisation(halves, complete, layer_indices, n_heads)

    entropy = results["chunk_entropy"]
    print()
    print("=" * 80)
    if entropy["win_rate"] > 0.5:
        print(f"  Bỏ bằng chứng đi làm chú ý TẢN HƠN ở {entropy['win_rate']:.1%} số cặp "
              f"(trung vị +{entropy['median_change']:.4f}).")
        print("  Cơ chế phản ứng đúng hướng khi can thiệp — đây là bằng chứng nhân quả, không")
        print("  phải tương quan. Nhưng phải đọc kèm độ lớn ở cột 'đổi'.")
    else:
        print(f"  Bỏ bằng chứng đi KHÔNG làm chú ý tản hơn ({entropy['win_rate']:.1%} số cặp).")
        print("  Kết quả này BÁC cách diễn giải rằng đặc trưng hình dạng đo việc mô hình tìm")
        print("  thấy bằng chứng. Phải báo cáo đúng như vậy và đi tìm cách giải thích khác.")
    print("=" * 80)

    metrics = {f"{name}_{key}": value
               for name, test in results.items()
               for key, value in test.items() if isinstance(value, (int, float))}
    extra = {
        "n_pairs": len(complete),
        "n_rows": len(records),
        "layer_indices": layer_indices,
        "n_heads": n_heads,
        "expected_direction": EXPECTED_DIRECTION,
        "entropy_effect_words": describe_effect(entropy["effect"]),
        "localisation": {k: v for k, v in (localisation or {}).items()
                         if not isinstance(v, tuple)},
        "ms_per_sample": None,
        "peak_vram_mb": 0.0,
        "selection_note": "đặc trưng lấy trung bình mọi đầu, "
                          "không chọn đầu nào sau khi thấy dữ liệu",
    }
    record = log_result(cfg.run_name, {**cfg.to_dict(), "experiment": "E08"},
                        metrics, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
