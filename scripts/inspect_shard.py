"""Diagnose a feature shard that failed its integrity check, without touching a GPU.

The T30 Sailor2 run extracted all three splits cleanly — 7.000 samples, zero errors — and then
cell 8 refused them: some values were not finite and some fell outside [0, 1]. "False" is a
correct verdict and a useless one. Three hours of GPU deserve a report that says *which* layers
broke, on *how many* samples, and what the two ways forward cost.

    python scripts/inspect_shard.py --config configs/e13_sailor2_vihallu.yaml

Every extracted record carries ``nonfinite_layers``, the layers whose attention matrix went
non-finite for that sample, so the whole diagnosis is a pass over a file already on disk.

The two ways forward, and the script prints the price of each:

* **Bỏ thêm lớp** — add the offending layers to ``exclude_layers``. Costs a re-extraction,
  because ``exclude_layers`` feeds the extraction hash, and costs those layers for every sample
  including the ones that were fine.
* **Bỏ mẫu** — drop the affected samples at scoring time. Costs nothing but those samples, and
  is only reasonable while they stay a small, reported fraction — the same way the truncation
  rate is reported rather than hidden.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_done, shard_path  # noqa: E402
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.features.chunk_aware import CHUNK_FEATURE_NAMES  # noqa: E402

# Blocks whose definition puts them in [0, 1]. chunk_drift is a change between steps and may be
# negative, so it is checked for finiteness only — calling it out of range would be wrong.
BOUNDED = ("lookback_total", "lookback_context", *[
    name for name in CHUNK_FEATURE_NAMES if name != "chunk_drift"
])
ALL_BLOCKS = ("lookback_total", "lookback_context", *CHUNK_FEATURE_NAMES)


def inspect(records: list[dict]) -> dict:
    """Per-split diagnosis: which layers broke, how often, and how much data they cost."""
    layer_counts: Counter[int] = Counter()
    affected = 0
    for record in records:
        bad = record.get("nonfinite_layers") or []
        if bad:
            affected += 1
            layer_counts.update(int(layer) for layer in bad)

    blocks = {}
    for name in ALL_BLOCKS:
        values = np.asarray([r[name] for r in records if name in r], dtype=np.float64)
        if not values.size:
            continue
        finite = np.isfinite(values)
        entry = {
            "n_values": int(values.size),
            "n_nonfinite": int((~finite).sum()),
            "rows_with_nonfinite": int((~finite).any(axis=1).sum()),
        }
        if name in BOUNDED:
            inside = finite & (values >= 0) & (values <= 1)
            entry["n_out_of_range"] = int((finite & ~inside).sum())
            entry["rows_out_of_range"] = int((finite & ~inside).any(axis=1).sum())
        blocks[name] = entry

    return {
        "n_records": len(records),
        "affected": affected,
        "layer_counts": layer_counts,
        "blocks": blocks,
        "layer_indices": records[0]["layer_indices"] if records else [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Soi shard đặc trưng, không cần GPU.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--splits", nargs="+", default=["train", "dev", "test"])
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    run = extraction_hash(cfg)

    print()
    print("=" * 84)
    print(f"SOI SHARD — {cfg.run_name}")
    print("=" * 84)
    print(f"  mô hình đọc       : {cfg.extractor.model_name}")
    print(f"  đang bỏ lớp       : {list(cfg.extractor.exclude_layers)}")
    print(f"  hash trích        : {run}")

    total_records = 0
    total_affected = 0
    union: Counter[int] = Counter()
    grid = None

    for split in args.splits:
        path = shard_path(args.processed_dir, run, cfg.dataset.name, split)
        if not path.exists():
            print(f"\n  {split:<6}: KHÔNG CÓ FILE — {path}")
            continue
        records = sorted(load_done(path).values(), key=lambda r: r["sample_id"])
        if not records:
            print(f"\n  {split:<6}: FILE RỖNG")
            continue

        report = inspect(records)
        total_records += report["n_records"]
        total_affected += report["affected"]
        union.update(report["layer_counts"])
        n_layers = len(report["layer_indices"])
        n_heads = len(records[0]["lookback_total"]) // n_layers
        grid = (n_layers, n_heads)

        share = report["affected"] / report["n_records"] * 100
        print()
        print(f"  {split.upper()}  {report['n_records']:,} mẫu   lưới {n_layers} × {n_heads}")
        print(f"    mẫu có lớp tràn số : {report['affected']:,}  ({share:.2f} %)")
        if report["layer_counts"]:
            listed = ", ".join(
                f"lớp {layer}: {count:,}"
                for layer, count in sorted(report["layer_counts"].items())
            )
            print(f"    theo lớp           : {listed}")
        for name, entry in report["blocks"].items():
            flags = []
            if entry["n_nonfinite"]:
                flags.append(f"{entry['n_nonfinite']:,} giá trị không hữu hạn "
                             f"trên {entry['rows_with_nonfinite']:,} dòng")
            if entry.get("n_out_of_range"):
                flags.append(f"{entry['n_out_of_range']:,} giá trị ngoài [0,1] "
                             f"trên {entry['rows_out_of_range']:,} dòng")
            if flags:
                print(f"      {name:<18}: {' | '.join(flags)}")

    if not total_records:
        print("\n  Không đọc được shard nào.")
        return 1

    print()
    print("-" * 84)
    if not union:
        print("  Không lớp nào tràn số. Shard sạch.")
        return 0

    share = total_affected / total_records * 100
    already = set(cfg.extractor.exclude_layers)
    extra = sorted(set(union) - already)
    print(f"  Tổng: {total_affected:,}/{total_records:,} mẫu ({share:.2f} %) có ít nhất một lớp"
          " tràn số.")
    print(f"  Các lớp tràn số  : {sorted(union)}")
    print(f"  Đang bỏ sẵn      : {sorted(already)}")
    print(f"  Lớp MỚI phát hiện: {extra}")

    print()
    print("  Hai đường đi, và giá của từng đường:")
    print()
    if extra:
        remaining = (grid[0] - len(extra)) if grid else None
        print(f"  1. BỎ THÊM LỚP {extra}")
        print("     Đổi exclude_layers, tức đổi hash trích, tức PHẢI TRÍCH LẠI toàn bộ.")
        print(f"     Giá: khoảng 3 giờ GPU, và mất {len(extra)} lớp cho MỌI mẫu — kể cả"
              f" {total_records - total_affected:,} mẫu vốn không sao.")
        if remaining:
            print(f"     Còn lại {remaining} lớp để so với 27 lớp của Qwen.")
    print()
    print(f"  2. BỎ {total_affected:,} MẪU HỎNG ({share:.2f} %)")
    print("     Không tốn GPU. Giữ nguyên shard, loại các mẫu đó lúc chấm và BÁO CÁO tỷ lệ,")
    print("     đúng cách đang làm với tỷ lệ cắt ngữ cảnh.")
    if share > 5:
        print("     CẢNH BÁO: trên 5 % là nhiều, đường này không còn rẻ nữa.")
    else:
        print("     Dưới 5 % nên đường này rẻ hơn hẳn đường 1.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
