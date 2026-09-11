"""E16: train the detector on one corpus, score it on another (task T34).

Every other table in this thesis trains and tests inside one corpus. This one asks the question
CH3 actually poses — does the attention signal **generalise beyond the distribution it was fitted
on** — by fitting on ViHallu and scoring on ISE-DSC01, then the reverse.

The two corpora could hardly be more different as inputs: ViHallu carries GPT-4o answers to
questions over 5,3-chunk contexts, ISE-DSC01 carries human claims over 22,6-chunk contexts with
no question at all. What they share is the *reading model*. E15 found that with Qwen2.5-7B the
same heads (``l17_h4``, ``l5_h7``) lead the classifier on three unrelated corpora, which is the
only reason a classifier fitted on one of them has any business being applied to another.

Protocol, and the two places it could quietly cheat:

* **The head aggregation is chosen on the source dev split**, exactly as in
  ``run_chunk_aware.py``. The target corpus is touched once, to score. Choosing on the target
  dev — or on a pooled dev — would leak the target's label balance into the model and inflate
  the transfer number.
* **The same fitted model is scored on both test sets.** The source-test score is therefore a
  built-in check: it must reproduce the same-corpus experiment (E03, E07) to the digit, because
  it *is* that experiment. If it does not, the pipeline diverged somewhere and the transfer
  number cannot be trusted either.

The two configs must agree on everything except ``dataset``. That is asserted, not assumed: two
shards extracted with different reading models or different chunkers produce feature vectors of
the same length whose columns mean different things, and the classifier would run happily on
them and return a number.
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
from run_chunk_aware import (  # noqa: E402
    MIXED,
    load_split,
    matrix_for,
    mixed_names,
    select_aggregation,
)
from vihallulens.config import REQUIRED_SPLIT_SEED, extraction_hash, load_config  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import LABELS, bootstrap_ci, compute_metrics  # noqa: E402
from vihallulens.features.assemble import (  # noqa: E402
    blocks_for,
    build_feature_matrix,
    column_names,
)

# Everything that decides what a feature column *means*. Two configs differing in any of these
# produce vectors that line up by index and disagree by content.
MUST_MATCH = ("chunking", "extractor", "features")


def assert_compatible(source, target) -> None:
    """Refuse to transfer between shards whose columns do not mean the same thing."""
    a, b = source.to_dict(), target.to_dict()
    for key in MUST_MATCH:
        if a[key] != b[key]:
            raise SystemExit(
                f"hai cấu hình khác nhau ở '{key}' — cột đặc trưng sẽ trùng chỉ số mà khác "
                f"nghĩa, bộ phân loại vẫn chạy và vẫn trả về một con số.\n"
                f"  nguồn : {a[key]}\n  đích  : {b[key]}"
            )
    if a["dataset"]["name"] == b["dataset"]["name"]:
        raise SystemExit("nguồn và đích là cùng một bộ — đó là run_chunk_aware.py, không phải E16")


def score(detector, matrix, labels, seed: int) -> dict:
    """Mirror ``run_chunk_aware.py`` exactly, including ``proba_labels``.

    sklearn orders ``predict_proba`` columns alphabetically, which is not the reporting order
    ``('no', 'intrinsic', 'extrinsic')``; ``compute_metrics`` refuses to guess and raises unless
    told. Silently accepting the wrong order would have produced a plausible ECE from the wrong
    class's probabilities.
    """
    predicted = detector.predict(matrix)
    proba = detector.predict_proba(matrix)
    metrics = compute_metrics(labels, predicted, proba, proba_labels=detector.classes_)
    metrics.update(bootstrap_ci(labels, predicted, seed=seed))
    return metrics


def same_corpus_reference(results_path: Path, run_name: str) -> float | None:
    """The same-corpus test score already on record, so the reproduction check is explicit."""
    import json

    if not results_path.exists():
        return None
    value = None
    with results_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("run_name") == run_name:
                value = row["metrics"].get("macro_f1")  # last one wins
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="E16: khái quát hóa chéo bộ dữ liệu.")
    parser.add_argument("--source", type=Path, required=True,
                        help="cấu hình của bộ HUẤN LUYỆN — dev của nó chọn cách gộp đầu")
    parser.add_argument("--target", type=Path, required=True,
                        help="cấu hình của bộ ĐÁNH GIÁ — chỉ đụng tới tập test của nó")
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    parser.add_argument("--run-name", default=None)
    parser.add_argument(
        "--reference-run", default=None,
        help="tên lượt cùng bộ trong runs.jsonl để đối chiếu điểm test nguồn; mặc định lấy "
             "run_name trong cấu hình nguồn, nhưng các lượt cũ (E02, E03) ghi dưới tên ngắn hơn",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    source = load_config(args.source)
    target = load_config(args.target)
    assert_compatible(source, target)
    groups = list(source.features.groups)
    seed = REQUIRED_SPLIT_SEED
    run_name = args.run_name or (
        f"e16_{source.dataset.name}_to_{target.dataset.name}_"
        f"{'chunk' if 'chunk_aware' in groups else 'lookback'}"
    )

    # -- load: source train/dev/test, target test only ------------------------------------
    records, labels, dropped_note = {}, {}, []
    wanted = [(source, "train"), (source, "dev"), (source, "test"), (target, "test")]
    for cfg, split in wanted:
        key = f"{cfg.dataset.name}/{split}"
        rows, path, dropped = load_split(args.processed_dir, extraction_hash(cfg),
                                         cfg.dataset.name, split)
        if rows is None:
            print(f"\nThiếu đặc trưng {key}: {path}")
            return 1
        if dropped:
            dropped_note.append(f"{key} bỏ {len(dropped):,} mẫu có nan")
        records[key] = rows
        labels[key] = np.asarray([row["label"] for row in rows])

    src_train, src_dev, src_test = (f"{source.dataset.name}/{s}" for s in ("train", "dev", "test"))
    tgt_test = f"{target.dataset.name}/test"

    layer_indices = records[src_train][0]["layer_indices"]
    n_layers = len(layer_indices)
    n_heads = len(records[src_train][0]["lookback_total"]) // n_layers
    tgt_layers = records[tgt_test][0]["layer_indices"]
    if tgt_layers != layer_indices:
        raise SystemExit(f"hai shard khác lưới lớp: nguồn {layer_indices}, đích {tgt_layers}")

    print()
    print("=" * 80)
    print(f"{run_name.upper()} — KHÁI QUÁT HÓA CHÉO BỘ")
    print("=" * 80)
    print(f"  huấn luyện trên       : {source.dataset.name}  ({args.source})")
    print(f"  đánh giá trên         : {target.dataset.name}  ({args.target})")
    print(f"  nhóm đặc trưng        : {', '.join(groups)}")
    print(f"  lưới lớp × đầu        : {n_layers} × {n_heads}  (trùng nhau ở cả hai shard)")
    for key in (src_train, src_dev, src_test, tgt_test):
        chunks = [row["n_chunks"] for row in records[key]]
        print(f"  {key:<22}: {len(records[key]):>7,} mẫu, trung bình {np.mean(chunks):.1f} đoạn")
    for note in dropped_note:
        print(f"  {note}")

    # -- choose aggregation on SOURCE dev -------------------------------------------------
    print()
    print("-" * 80)
    print(f"CHỌN CÁCH GỘP ĐẦU — trên DEV của {source.dataset.name}, không đụng bộ đích")
    print("-" * 80)
    x_train = build_feature_matrix(records[src_train], groups, n_layers, n_heads)
    started = time.perf_counter()
    src_records = {"train": records[src_train], "dev": records[src_dev]}
    best, trials = select_aggregation(
        x_train, labels[src_train], src_records, groups, n_layers, n_heads, labels[src_dev], seed,
    )
    for trial in trials:
        mark = "  ← chọn" if trial["label"] == best["label"] else ""
        print(f"  {trial['label']:<32} {trial['n_features']:>8,} "
              f"{trial['dev_macro_f1']:>10.4f}{mark}")
    print(f"  ({time.perf_counter() - started:.0f} giây)")

    # -- fit once, score twice ------------------------------------------------------------
    keep = best["keep"]
    matrices = {
        key: matrix_for(records[key], groups, n_layers, n_heads, best["mode"], keep)
        for key in (src_train, src_test, tgt_test)
    }
    detector = LookbackDetector(
        detector_type=source.detector.type,
        class_weight=source.detector.class_weight,
        seed=seed,
    ).fit(matrices[src_train], labels[src_train])

    on_source = score(detector, matrices[src_test], labels[src_test], seed)
    on_target = score(detector, matrices[tgt_test], labels[tgt_test], seed)
    drop = on_source["macro_f1"] - on_target["macro_f1"]

    print()
    print("-" * 80)
    print("CÙNG MỘT MÔ HÌNH, HAI TẬP TEST")
    print("-" * 80)
    print(f"  {'':<24}{'macro-F1':>10}{'KTC 95 %':>20}{'nhị phân':>10}"
          + "".join(f"{lb:>9}" for lb in LABELS) + f"{'ECE':>8}")
    for name, m in ((src_test, on_source), (tgt_test, on_target)):
        print(f"  {name:<24}{m['macro_f1']:>10.4f}"
              f"  [{m['macro_f1_lo']:.4f}, {m['macro_f1_hi']:.4f}]"
              f"{m['binary_macro_f1']:>10.4f}"
              + "".join(f"{m[f'f1_{lb}']:>9.4f}" for lb in LABELS) + f"{m['ece']:>8.4f}")
    print(f"  {'sụt khi đổi bộ':<24}{drop:>+10.4f}")

    # -- the built-in reproduction check --------------------------------------------------
    reference_run = args.reference_run or source.run_name
    reference = same_corpus_reference(args.results_path, reference_run)
    print()
    if reference is None:
        print(f"  Chưa có điểm cùng bộ của {reference_run} trong {args.results_path} "
              "để đối chiếu.")
    else:
        gap = on_source["macro_f1"] - reference
        verdict = "TRÙNG" if abs(gap) < 5e-4 else f"LỆCH {gap:+.4f}"
        print(f"  Đối chiếu điểm cùng bộ : {reference_run} ghi {reference:.4f}, "
              f"lượt này {on_source['macro_f1']:.4f} → {verdict}")
        if abs(gap) >= 5e-4:
            print("    !! Cùng dữ liệu, cùng seed, cùng quy trình mà ra số khác — đường ống đã")
            print("       lệch ở đâu đó, và con số chuyển bộ bên trên KHÔNG đáng tin cho tới khi")
            print("       tìm ra chỗ lệch.")

    # -- what the drop means, in the terms CH3 uses ----------------------------------------
    print()
    print("-" * 80)
    print("ĐỌC THẾ NÀO")
    print("-" * 80)
    print(f"  Bộ đích có mốc riêng của nó: chạy run_chunk_aware.py trên {args.target} cho điểm")
    print("  'huấn luyện và chấm cùng bộ'. Sụt so với mốc ĐÓ mới là giá của việc đổi phân phối;")
    print("  sụt so với điểm nguồn ở trên chỉ nói hai bộ khó khác nhau.")

    names = (mixed_names(groups, layer_indices, n_heads, keep) if best["mode"] == MIXED
             else column_names(blocks_for(groups), layer_indices, n_heads, best["mode"], keep))
    record = log_result(
        run_name,
        {**source.to_dict(), "experiment": "E16",
         "target_dataset": target.to_dict()["dataset"]},
        on_target,
        {
            "source_dataset": source.dataset.name,
            "target_dataset": target.dataset.name,
            "n_train": len(records[src_train]),
            "n_dev": len(records[src_dev]),
            "n_test_source": len(records[src_test]),
            "n_test": len(records[tgt_test]),
            "n_features": len(names),
            "head_aggregation_chosen": best["label"],
            "source_test_metrics": {k: v for k, v in on_source.items()
                                    if isinstance(v, (int, float))},
            "same_corpus_reference": reference,
            "drop_vs_source_test": drop,
            "n_params_trainable": int(detector.n_params_trainable),
            "ms_per_sample": None,
            "peak_vram_mb": 0.0,
            "y_pred": detector.predict(matrices[tgt_test]).tolist(),
            "std_method": "bootstrap trên tập test đích, 2.000 lần, seed 42",
        },
        path=args.results_path,
    )
    print(f"\n  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
