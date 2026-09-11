"""Task T29, experiment E12: which feature group actually earns its place.

Four cumulative levels, each adding one group to the one above it:

    1. chỉ bề mặt          hai đặc trưng của E01
    2. + lookback gộp      thêm tỷ lệ chú ý gộp, tức E02
    3. + chunk-aware       thêm bốn đại lượng hình dạng, tức đóng góp của đề tài
    4. + ổn định           thêm chunk_drift

So the delta column reads as "what this group added on top of everything above it" — which is
the only reading that answers CH3. A table of four independent runs would not: it would say how
each group does alone, and every group but the first would then be scored without the aggregate
lookback ratio that T22 showed they depend on.

**Costs no GPU.** Every level reads the shard E02 and E03 already used and refits a linear
classifier on a subset of its columns.

    python scripts/run_ablation.py --config configs/e12_ablation_vihallu.yaml

Two design choices worth stating, because both could silently rig the result:

* **Head aggregation is chosen on dev, separately for each level.** A narrow level and a wide
  level do not want the same reduction — forcing the widest level's choice onto level 2 would
  hand it 32 columns where E02 had 756 and understate it. That exact effect cost 0,045 on the
  intrinsic class at T22, so it is not hypothetical.
* **Surface features sit in every level, including level 1.** The question is what attention
  adds *to what you can get for free*, not what attention scores in a vacuum.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR  # noqa: E402
from run_chunk_aware import MIXED, TOPK_GRID, load_split, matrix_for  # noqa: E402
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import (  # noqa: E402
    LABELS,
    bootstrap_ci,
    compute_metrics,
)
from vihallulens.features.assemble import blocks_for, rank_heads  # noqa: E402
from vihallulens.features.surface import FEATURE_NAMES, surface_features  # noqa: E402

# The four rows of Bảng 4 in docs/EXPERIMENTS.md, in order. Each entry is the attention groups
# that level adds to the surface pair; the list is cumulative by construction.
LEVELS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Chỉ bề mặt", ()),
    ("+ lookback gộp", ("basic",)),
    ("+ chunk-aware", ("basic", "chunk_aware")),
    ("+ ổn định", ("basic", "chunk_aware", "stability")),
)


def surface_by_sample_id(dataset: str, split: str, interim_dir: Path) -> dict[str, np.ndarray]:
    """Surface features keyed by sample id.

    Keyed rather than positional because the shard is sorted by sample id while the interim
    parquet keeps its own order, and a silent misalignment here would attach one response's
    length to another's attention — a bug that lowers the score without ever raising an error.
    """
    frame = load_dataset(dataset, split, interim_dir)
    matrix = surface_features(frame)
    return dict(zip(frame["sample_id"].astype(str), matrix, strict=True))


def surface_matrix(records, lookup: dict[str, np.ndarray]) -> np.ndarray:
    """Surface rows lined up with ``records``, failing loudly on any sample the corpus lacks."""
    missing = [record["sample_id"] for record in records
               if str(record["sample_id"]) not in lookup][:3]
    if missing:
        raise ValueError(
            f"không tìm thấy đặc trưng bề mặt cho mẫu {missing}. Shard đặc trưng và file "
            f"interim đang không cùng một lượt chia tập — chạy lại scripts/split_data.py."
        )
    return np.asarray([lookup[str(record["sample_id"])] for record in records], dtype=np.float64)


def level_matrix(records, groups, n_layers, n_heads, mode, keep, surface) -> np.ndarray:
    """``[surface | attention]`` for one level. Level 1 has no attention half."""
    if not groups:
        return surface
    attention = matrix_for(records, list(groups), n_layers, n_heads, mode, keep)
    return np.hstack([surface, attention])


def select_aggregation(records, surface, labels, groups, n_layers, n_heads, seed):
    """Pick the head reduction for one level, scoring candidates on **dev**.

    Returns ``(mode, keep, trials)``. Level 1 has no heads to reduce, so it returns ``all``
    without fitting anything.
    """
    if not groups:
        return "all", None, []

    n_blocks = len(blocks_for(list(groups)))
    full = LookbackDetector(seed=seed).fit(
        level_matrix(records["train"], groups, n_layers, n_heads, "all", None, surface["train"]),
        labels["train"],
    )
    # Drop the two surface columns before ranking: rank_heads expects the weight vector to be
    # exactly blocks × layers × heads, and the surface pair sits in front of it.
    order = rank_heads(full.feature_weights[len(FEATURE_NAMES):], n_blocks, n_layers, n_heads)

    candidates = [("all", None), ("mean_over_heads", None)]
    candidates += [("topk_heads", order[:k]) for k in TOPK_GRID]
    if "basic" in groups and len(groups) > 1:
        candidates += [(MIXED, order[:k]) for k in TOPK_GRID]

    trials = []
    for mode, keep in candidates:
        train = level_matrix(records["train"], groups, n_layers, n_heads, mode, keep,
                             surface["train"])
        dev = level_matrix(records["dev"], groups, n_layers, n_heads, mode, keep, surface["dev"])
        model = LookbackDetector(seed=seed).fit(train, labels["train"])
        scored = compute_metrics(labels["dev"], model.predict(dev))
        trials.append({
            "label": mode if keep is None else f"{mode} k={len(keep)}",
            "mode": mode, "keep": keep, "n_features": int(train.shape[1]),
            "dev_macro_f1": float(scored["macro_f1"]),
        })
        del train, dev, model

    best = min(trials, key=lambda trial: (-trial["dev_macro_f1"], trial["n_features"]))
    return best["mode"], best["keep"], trials


def main() -> int:
    parser = argparse.ArgumentParser(description="E12: ablation nhóm đặc trưng.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    parser.add_argument(
        "--fixed-aggregation", metavar="MODE",
        help="dùng chung một cách gộp đầu cho mọi mức, ví dụ 'topk_heads k=32'. Mặc định để "
             "dev chọn riêng cho từng mức; chạy cả hai rồi so, vì cột chênh của bản mặc định "
             "trộn 'thêm đặc trưng' với 'đổi số cột'.",
    )
    parser.add_argument(
        "--extra-level", metavar="GROUPS", default=None,
        help="chấm THÊM một mức không cộng dồn, ví dụ 'chunk_aware' = bề mặt + chunk-aware, bỏ "
             "lookback gộp. Ghi vào extra['extra_levels'], KHÔNG chèn vào bảng bốn dòng — bảng "
             "đó phải giữ nguyên hình dạng để so được với lượt E12 đã ghi. Nhiều nhóm thì cách "
             "nhau bằng dấu phẩy. Thêm ở T35B để đo thẳng mức chồng lấn tín hiệu.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    run = extraction_hash(cfg)
    seed = cfg.dataset.split_seed
    run_name = cfg.run_name
    if args.fixed_aggregation:
        run_name = f"{run_name}_gopchung"

    records, labels, surface = {}, {}, {}
    for split in ("train", "dev", "test"):
        rows, path, dropped = load_split(args.processed_dir, run, cfg.dataset.name, split)
        if dropped:
            print(f"  bỏ mẫu có nan {split:<9}: {len(dropped):,}")
        if rows is None:
            print(f"\nThiếu đặc trưng của tập {split}: {path}")
            print("Chạy trước: python scripts/extract_features.py "
                  f"--config {args.config} --split {split}")
            return 1
        records[split] = rows
        labels[split] = np.asarray([row["label"] for row in rows])
        surface[split] = surface_matrix(rows, surface_by_sample_id(
            cfg.dataset.name, split, args.interim_dir))

    layer_indices = records["train"][0]["layer_indices"]
    n_layers = len(layer_indices)
    n_heads = len(records["train"][0]["lookback_total"]) // n_layers

    print()
    print("=" * 84)
    print(f"{run_name.upper()} — ABLATION NHÓM ĐẶC TRƯNG")
    print("=" * 84)
    print(f"  cấu hình              : {args.config}  (trích {run}, dùng lại, KHÔNG tốn GPU)")
    print(f"  train / dev / test    : "
          f"{len(records['train']):,} / {len(records['dev']):,} / {len(records['test']):,} mẫu")
    print(f"  lưới lớp × đầu        : {n_layers} × {n_heads}")
    print(f"  đặc trưng bề mặt      : {', '.join(FEATURE_NAMES)} (có ở mọi mức)")

    started = time.perf_counter()
    rows_out = []
    previous = None
    # One head ranking for the whole table when --fixed-aggregation is on, taken from the widest
    # level. Ranking on each level separately would reintroduce the very difference this mode
    # exists to remove.
    shared_order = None
    if args.fixed_aggregation:
        widest = LEVELS[-1][1]
        full = LookbackDetector(seed=seed).fit(
            level_matrix(records["train"], widest, n_layers, n_heads, "all", None,
                         surface["train"]),
            labels["train"],
        )
        shared_order = rank_heads(full.feature_weights[len(FEATURE_NAMES):],
                                  len(blocks_for(list(widest))), n_layers, n_heads)
        del full

    def score_level(name: str, groups: tuple[str, ...]) -> dict:
        """Fit and score one feature set — the same code for the four rows and any extra."""
        if args.fixed_aggregation and groups:
            mode, _, k_text = args.fixed_aggregation.partition(" k=")
            keep = shared_order[:int(k_text)] if k_text else None
            trials = []
        else:
            mode, keep, trials = select_aggregation(
                records, surface, labels, groups, n_layers, n_heads, seed)

        train = level_matrix(records["train"], groups, n_layers, n_heads, mode, keep,
                             surface["train"])
        test = level_matrix(records["test"], groups, n_layers, n_heads, mode, keep,
                            surface["test"])
        model = LookbackDetector(seed=seed).fit(train, labels["train"])
        predicted = model.predict(test)
        scored = compute_metrics(labels["test"], predicted)
        interval = bootstrap_ci(labels["test"], predicted, seed=seed)
        label = mode if keep is None else f"{mode} k={len(keep)}"
        row = {
            "level": name, "groups": list(groups), "aggregation": label,
            "n_features": int(train.shape[1]), "macro_f1": float(scored["macro_f1"]),
            "ci_low": float(interval["macro_f1_lo"]), "ci_high": float(interval["macro_f1_hi"]),
            "binary_macro_f1": float(scored["binary_macro_f1"]),
            "per_class": {lb: float(scored[f"f1_{lb}"]) for lb in LABELS},
            "dev_trials": len(trials),
        }
        print()
        print(f"  {name}")
        if trials:
            print(f"    cách gộp dev chọn : {label}  ({train.shape[1]:,} cột, "
                  f"{len(trials)} ứng viên)")
        elif groups:
            print(f"    cách gộp chung    : {label}  ({train.shape[1]:,} cột)")
        else:
            print(f"    cách gộp          : không có đầu nào để gộp ({train.shape[1]} cột)")
        print(f"    macro-F1 test     : {row['macro_f1']:.4f} [{row['ci_low']:.4f}; "
              f"{row['ci_high']:.4f}]")
        return row

    for name, groups in LEVELS:
        row = score_level(name, groups)
        row["delta"] = None if previous is None else row["macro_f1"] - previous
        previous = row["macro_f1"]
        if row["delta"] is not None:
            print(f"    chênh so mức trên : {row['delta']:+.4f}")
        rows_out.append(row)

    print()
    print("-" * 84)
    print(f"  {'Nhóm đặc trưng':<24}{'macro-F1':>10}{'Chênh':>10}{'Nhị phân':>11}{'Cột':>9}")
    print("-" * 84)
    for row in rows_out:
        delta = "—" if row["delta"] is None else f"{row['delta']:+.4f}"
        print(f"  {row['level']:<24}{row['macro_f1']:>10.4f}{delta:>10}"
              f"{row['binary_macro_f1']:>11.4f}{row['n_features']:>9,}")
    print("-" * 84)

    chunk_gain = rows_out[2]["delta"]
    print()
    print(f"  Nhóm chunk-aware cộng thêm: {chunk_gain:+.4f}")
    print("  Đây là con số trả lời CH3 cho phần đóng góp của đề tài. Nếu nó gần bằng không thì"
          " phải viết thẳng như vậy trong báo cáo.")

    # -- the non-cumulative extra level, kept OUT of rows_out ---------------------------------
    # Bảng 4 stacks groups, so it cannot say whether chunk-aware carries anything the surface
    # pair does not — chunk-aware is only ever scored on top of lookback. Scoring surface +
    # chunk-aware with lookback removed answers that directly, and comparing the three gains
    # puts a number on how much the two attention groups overlap:
    #     overlap = gain(lookback alone) + gain(chunk alone) - gain(both)
    # Zero means additive; positive means they carry the same information; negative would mean
    # they help each other. Written to its own key so the four-row table stays comparable with
    # the E12 rows already in runs.jsonl.
    extra_rows = []
    if args.extra_level:
        groups = tuple(g.strip() for g in args.extra_level.split(",") if g.strip())
        print()
        print("-" * 84)
        print("MỨC PHỤ — không cộng dồn, không chèn vào bảng trên")
        print("-" * 84)
        extra = score_level(f"bề mặt + {' + '.join(groups)}", groups)
        extra_rows.append(extra)
        base = rows_out[0]["macro_f1"]
        gain_extra = extra["macro_f1"] - base
        print(f"    so với chỉ bề mặt : {gain_extra:+.4f}")
        if groups == ("chunk_aware",):
            gain_look = rows_out[1]["macro_f1"] - base
            gain_both = rows_out[2]["macro_f1"] - base
            overlap = gain_look + gain_extra - gain_both
            extra.update({"gain_over_surface": gain_extra,
                          "gain_lookback_over_surface": gain_look,
                          "gain_both_over_surface": gain_both, "overlap": overlap})
            print()
            print(f"  {'':<36}{'cộng thêm vào bề mặt':>22}")
            print(f"  {'lookback gộp một mình':<36}{gain_look:>+22.4f}")
            print(f"  {'chunk-aware một mình':<36}{gain_extra:>+22.4f}")
            print(f"  {'cả hai':<36}{gain_both:>+22.4f}")
            print(f"  {'chồng lấn = riêng + riêng − cả hai':<36}{overlap:>+22.4f}")
            print()
            print("  Đọc: chồng lấn ≈ 0 là hai nhóm cộng được vào nhau; dương là chúng mang cùng"
                  " một thông tin; âm là chúng bổ trợ nhau.")

    elapsed = time.perf_counter() - started
    log_result(
        run_name=run_name, config=cfg.model_dump(), path=args.results_path,
        metrics={"macro_f1": rows_out[-1]["macro_f1"],
                 "binary_macro_f1": rows_out[-1]["binary_macro_f1"],
                 "chunk_aware_gain": chunk_gain},
        # No GPU was used: this experiment refits a linear classifier on shards the reading
        # model produced weeks ago. peak_vram_mb is 0 for that reason, not because it was
        # left unmeasured.
        extra={"ablation": rows_out, "extra_levels": extra_rows,
               "seconds": round(elapsed, 1),
               "ms_per_sample": round(elapsed * 1000 / len(records["test"]), 3),
               "peak_vram_mb": 0, "reused_extraction": run},
    )
    print(f"\n  Đã ghi {args.results_path}  ({elapsed:.1f} giây, 0 giây GPU)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
