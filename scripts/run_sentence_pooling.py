"""Task T45C, experiment E18: pool each sentence of the response, then across sentences.

Chapter 7 explains why attention locates the evidence (E06, 87,8 %) yet classifies no better
than it does with three reasons. The second — *averaging over the whole response dilutes one
fabricated clause among faithful ones* — is the only one an experiment can check, and this is
that experiment.

    CFG=configs/e18_sentence_pooling_vihallu.yaml
    python scripts/extract_features.py --config $CFG --split train   # and dev, test
    python scripts/run_sentence_pooling.py

One extraction, four arms, everything else held fixed — same shard, same three feature groups as
E03, same head selection on dev, same detector, same seed:

* ``whole`` — the whole-response vectors E03 uses, re-scored here so the comparison does not
  cross two GPU runs;
* ``mean`` / ``max`` / ``min`` — each block pooled per sentence, then across sentences.

**Read the ceiling first.** 71,6 % of ViHallu training responses are a single sentence (measured
22/10/2026 with the context's own splitter, ``min_words=5``), and there every arm returns the
same vector. Whatever E18 changes, it changes on the other 28 %, so the script also scores the
multi-sentence part of the test set on its own.

**Reproduction check.** The new shard repeats every whole-response field of the E03 shard. When
that shard is on disk the two are compared value by value; any difference means the extraction
itself moved, and every comparison below would mix that in.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, shard_path  # noqa: E402
from run_chunk_aware import matrix_for, select_aggregation  # noqa: E402
from vihallulens.config import REQUIRED_SPLIT_SEED, extraction_hash, load_config  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import LABELS, bootstrap_ci, compute_metrics  # noqa: E402
from vihallulens.features.assemble import blocks_for  # noqa: E402
from vihallulens.features.sentence import (  # noqa: E402
    POOLINGS,
    SENTENCE_PREFIX,
    pooled_view,
)

CONFIG = Path("configs/e18_sentence_pooling_vihallu.yaml")
REFERENCE_CONFIG = Path("configs/e03_chunk_sentence_vihallu.yaml")
WHOLE = "whole"
ARMS = (WHOLE, *POOLINGS)
SPLITS = ("train", "dev", "test")
PAIRED_ROUNDS = 2000
HALLUCINATED = ("intrinsic", "extrinsic")
META_KEYS = ("sample_id", "label", "layer_indices", "n_chunks", "sentence_n_tokens",
             "elapsed_ms", "peak_vram_mb")

# Written before the extraction run (22/10/2026), locked by tests/test_sentence_pooling.py so a
# result that goes the other way cannot quietly be re-described as a confirmation. Both compare
# ``max`` against ``whole`` on the same shard:
#   1. max pooling raises the F1 of the extrinsic class;
#   2. max pooling lowers the number of hallucinated responses predicted as ``no``.
# Macro-F1 is deliberately not predicted: it may well stay inside the interval.
# ``min`` was added the same day, also before the run: on a fabricated sentence the lookback
# ratio goes DOWN, so the max over sentences picks the most grounded one. It is reported as
# exploratory and carries no prediction.
EXPECTED = {
    "max_raises_extrinsic_f1": True,
    "max_reduces_hallucinated_as_no": True,
}


def load_compact(path: Path, blocks) -> tuple[list[dict], list[str]]:
    """A shard's rows with only what E18 reads, as float32 arrays rather than Python lists.

    The ViHallu train shard with per-sentence fields is several hundred megabytes of JSON, and
    reading it back as lists of Python floats would take gigabytes. Returns ``(rows, dropped)``,
    sorted by sample id, where ``dropped`` names rows with a non-finite value in any block read.
    """
    rows: dict[str, dict] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue  # a truncated last line, as in extract_features.load_done
            row = {key: record[key] for key in META_KEYS if key in record}
            for block in blocks:
                row[block] = np.asarray(record[block], dtype=np.float32)
                sentence = f"{SENTENCE_PREFIX}{block}"
                if sentence in record:
                    row[sentence] = np.asarray(record[sentence], dtype=np.float32)
            rows[row["sample_id"]] = row
    clean, dropped = [], []
    for sample_id in sorted(rows):
        row = rows[sample_id]
        finite = all(np.isfinite(value).all() for key, value in row.items()
                     if isinstance(value, np.ndarray))
        (clean if finite else dropped).append(row if finite else sample_id)
    return clean, dropped


def require_sentences(rows, path: Path, blocks) -> None:
    missing = [row["sample_id"] for row in rows
               if any(f"{SENTENCE_PREFIX}{block}" not in row for block in blocks)][:3]
    if missing:
        raise SystemExit(f"{path.name} không có trường theo câu (ví dụ {missing}). "
                         f"Trích bằng {CONFIG}, không phải shard E03 cũ.")


def hallucinated_as_no(y_true, y_pred) -> int:
    """Hallucinated responses the detector let through as clean."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return int((np.isin(y_true, HALLUCINATED) & (y_pred == "no")).sum())


def extrinsic_f1(y_true, y_pred) -> float:
    return float(f1_score(y_true, y_pred, labels=["extrinsic"], average=None, zero_division=0)[0])


def macro_f1(y_true, y_pred) -> float:
    return float(f1_score(y_true, y_pred, labels=list(LABELS), average="macro", zero_division=0))


def paired_bootstrap(y_true, pred_a, pred_b, metric, rounds: int = PAIRED_ROUNDS,
                     seed: int = REQUIRED_SPLIT_SEED) -> dict:
    """``metric(b) - metric(a)`` with a 95 % interval from resampling the test set **jointly**.

    Two intervals computed separately overlap far more often than the difference between the
    methods is uncertain, because both arms are scored on the same 700 samples. Resampling the
    pairs keeps that shared part out of the interval.
    """
    y_true, pred_a, pred_b = map(np.asarray, (y_true, pred_a, pred_b))
    rng = np.random.default_rng(seed)
    deltas = np.empty(rounds)
    for i in range(rounds):
        index = rng.integers(0, len(y_true), len(y_true))
        deltas[i] = metric(y_true[index], pred_b[index]) - metric(y_true[index], pred_a[index])
    return {"delta": metric(y_true, pred_b) - metric(y_true, pred_a),
            "lo": float(np.percentile(deltas, 2.5)), "hi": float(np.percentile(deltas, 97.5))}


def check_prediction(y_true, whole_pred, max_pred) -> dict:
    """Whether each locked expectation held, from the point estimates."""
    return {
        "max_raises_extrinsic_f1":
            extrinsic_f1(y_true, max_pred) > extrinsic_f1(y_true, whole_pred),
        "max_reduces_hallucinated_as_no":
            hallucinated_as_no(y_true, max_pred) < hallucinated_as_no(y_true, whole_pred),
    }


def compare_with_reference(new_rows, old_rows, blocks) -> dict:
    """Largest absolute difference per block between two shards, over their shared samples."""
    old = {row["sample_id"]: row for row in old_rows}
    shared = [row for row in new_rows if row["sample_id"] in old]
    out = {"n_shared": len(shared), "n_new": len(new_rows), "n_old": len(old_rows)}
    for block in blocks:
        diffs = [float(np.max(np.abs(row[block] - old[row["sample_id"]][block])))
                 for row in shared]
        out[block] = max(diffs) if diffs else None
    return out


def view(rows, arm: str, blocks):
    return rows if arm == WHOLE else [pooled_view(row, arm, blocks) for row in rows]


def run_arm(rows, arm, groups, n_layers, n_heads) -> dict:
    """Head selection on dev, one fit on train, one prediction on test — as E03 does."""
    records = {split: view(rows[split], arm, blocks_for(groups)) for split in SPLITS}
    labels = {split: np.asarray([row["label"] for row in rows[split]]) for split in SPLITS}
    x_train = matrix_for(records["train"], groups, n_layers, n_heads, "all")
    best, trials = select_aggregation(x_train, labels["train"], records, groups, n_layers,
                                      n_heads, labels["dev"], REQUIRED_SPLIT_SEED)
    train = matrix_for(records["train"], groups, n_layers, n_heads, best["mode"], best["keep"])
    test = matrix_for(records["test"], groups, n_layers, n_heads, best["mode"], best["keep"])
    detector = LookbackDetector(seed=REQUIRED_SPLIT_SEED).fit(train, labels["train"])
    predicted = detector.predict(test)
    proba = detector.predict_proba(test)
    return {"best": best, "trials": trials, "pred": predicted, "n_features": train.shape[1],
            "point": compute_metrics(labels["test"], predicted, proba,
                                     proba_labels=detector.classes_),
            "interval": bootstrap_ci(labels["test"], predicted, seed=REQUIRED_SPLIT_SEED)}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="T45C/E18: gộp theo từng câu phản hồi.")
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--reference-config", type=Path, default=REFERENCE_CONFIG)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()

    cfg = load_config(args.config)
    if not cfg.extractor.response_sentences:
        raise SystemExit(f"{args.config} chưa bật extractor.response_sentences")
    groups = list(cfg.features.groups)
    blocks = blocks_for(groups)
    run = extraction_hash(cfg)

    print()
    print("=" * 80)
    print("E18 — GỘP THEO TỪNG CÂU PHẢN HỒI")
    print("=" * 80)
    rows = {}
    for split in SPLITS:
        path = shard_path(args.processed_dir, run, cfg.dataset.name, split)
        if not path.exists():
            print(f"  Thiếu {path}. Chạy trước: python scripts/extract_features.py "
                  f"--config {args.config} --split {split}")
            return 1
        rows[split], dropped = load_compact(path, blocks)
        require_sentences(rows[split], path, blocks)
        print(f"  {split:<6}: {len(rows[split]):,} mẫu  ({path.name}"
              f"{f', bỏ {len(dropped)} mẫu có nan' if dropped else ''})")

    # -- does the new shard repeat the old one? ---------------------------------------------
    reference = {}
    old_run = extraction_hash(load_config(args.reference_config))
    print()
    print("-" * 80)
    print(f"KIỂM TÁI LẬP — trường cũ trong shard mới so với shard E03 ({old_run})")
    print("-" * 80)
    for split in SPLITS:
        old_path = shard_path(args.processed_dir, old_run, cfg.dataset.name, split)
        if not old_path.exists():
            print(f"  {split:<6}: không có {old_path.name} trên máy này, bỏ qua")
            continue
        old_rows, _ = load_compact(old_path, blocks)
        reference[split] = compare_with_reference(rows[split], old_rows, blocks)
        worst = max(value for key, value in reference[split].items()
                    if key in blocks and value is not None)
        print(f"  {split:<6}: {reference[split]['n_shared']:,}/{reference[split]['n_old']:,} "
              f"mẫu chung, lệch lớn nhất {worst:.2e}"
              f"{'  — TRÙNG' if worst == 0 else '  — CÓ LỆCH, đọc kết quả dưới đây thận trọng'}")

    # -- the ceiling: how many responses can differ at all ----------------------------------
    n_sentences = {split: np.asarray([len(row["sentence_n_tokens"]) for row in rows[split]])
                   for split in SPLITS}
    multi = n_sentences["test"] >= 2
    print()
    for split in SPLITS:
        share = (n_sentences[split] >= 2).mean() * 100
        print(f"  phản hồi ≥ 2 câu {split:<6}: {share:5.1f} %  "
              f"(trung bình {n_sentences[split].mean():.2f} câu)")
    print("  Ở phần còn lại cả bốn nhánh cho cùng một véc-tơ.")

    layer_indices = rows["train"][0]["layer_indices"]
    n_layers = len(layer_indices)
    n_heads = len(rows["train"][0]["lookback_total"]) // n_layers
    y_test = np.asarray([row["label"] for row in rows["test"]])

    results = {}
    for arm in ARMS:
        started = time.perf_counter()
        results[arm] = run_arm(rows, arm, groups, n_layers, n_heads)
        print(f"  nhánh {arm:<6} chọn {results[arm]['best']['label']:<32} "
              f"({time.perf_counter() - started:.0f} giây)")

    print()
    print("-" * 80)
    print(f"KẾT QUẢ TRÊN TẬP TEST — {len(y_test)} mẫu, "
          f"trong đó {int(multi.sum())} phản hồi ≥ 2 câu")
    print("-" * 80)
    print(f"  {'nhánh':<7}{'macro-F1':>10}{'KTC 95 %':>20}{'F1 extr.':>10}{'F1 intr.':>10}"
          f"{'F1 no':>8}{'ảo giác→no':>12}{'macro ≥2 câu':>14}")
    for arm in ARMS:
        point, interval = results[arm]["point"], results[arm]["interval"]
        pred = results[arm]["pred"]
        band = f"[{interval['macro_f1_lo']:.4f}, {interval['macro_f1_hi']:.4f}]"
        print(f"  {arm:<7}{point['macro_f1']:>10.4f}{band:>20}"
              f"{point['f1_extrinsic']:>10.4f}{point['f1_intrinsic']:>10.4f}"
              f"{point['f1_no']:>8.4f}{hallucinated_as_no(y_test, pred):>12}"
              f"{macro_f1(y_test[multi], pred[multi]):>14.4f}")

    print()
    print("  Ma trận nhầm lẫn (hàng = nhãn thật, cột = dự đoán; no / intrinsic / extrinsic):")
    for arm in ARMS:
        matrix = confusion_matrix(y_test, results[arm]["pred"], labels=list(LABELS))
        print(f"    {arm:<6} " + "  ".join(" ".join(f"{v:>4}" for v in row) for row in matrix))

    whole = results[WHOLE]["pred"]
    print()
    print(f"  Hiệu so với nhánh {WHOLE}, khoảng tin cậy bootstrap ghép cặp {PAIRED_ROUNDS:,} lượt:")
    paired = {}
    for arm in POOLINGS:
        paired[arm] = {"macro_f1": paired_bootstrap(y_test, whole, results[arm]["pred"], macro_f1),
                       "f1_extrinsic": paired_bootstrap(y_test, whole, results[arm]["pred"],
                                                        extrinsic_f1)}
        for name, value in paired[arm].items():
            print(f"    {arm:<5} {name:<13} {value['delta']:+.4f}  "
                  f"[{value['lo']:+.4f}, {value['hi']:+.4f}]")

    verdict = check_prediction(y_test, whole, results["max"]["pred"])
    print()
    print("-" * 80)
    print("DỰ ĐOÁN GHI TRƯỚC KHI CHẠY (max so với whole)")
    print("-" * 80)
    for key, expected in EXPECTED.items():
        print(f"  {key:<34} dự đoán {expected}  thực tế {verdict[key]}"
              f"  {'✓' if verdict[key] == expected else '✗'}")
    print("  Ghi đúng như dữ liệu nói, kể cả khi dự đoán sai.")

    elapsed = [row["elapsed_ms"] for split in SPLITS for row in rows[split]]
    peak = max(row.get("peak_vram_mb", 0.0) for split in SPLITS for row in rows[split])
    for arm in POOLINGS:
        result = results[arm]
        config = cfg.to_dict()
        config["features"] = {**config["features"], "response_pooling": arm}
        config["experiment"] = "E18"
        record = log_result(
            f"e18_sentence_{arm}_vihallu", config,
            {**result["point"], **result["interval"]},
            {
                "n_train": len(rows["train"]), "n_dev": len(rows["dev"]),
                "n_test": len(rows["test"]),
                "n_features": int(result["n_features"]),
                "head_aggregation_chosen": result["best"]["label"],
                "head_selection_trials": [
                    {key: trial[key] for key in ("label", "n_features", "dev_macro_f1")}
                    for trial in result["trials"]
                ],
                "hallucinated_as_no": hallucinated_as_no(y_test, result["pred"]),
                "confusion_matrix": confusion_matrix(
                    y_test, result["pred"], labels=list(LABELS)).tolist(),
                "multi_sentence_test": {"n": int(multi.sum()),
                                        "macro_f1": macro_f1(y_test[multi], result["pred"][multi]),
                                        "f1_extrinsic": extrinsic_f1(y_test[multi],
                                                                     result["pred"][multi])},
                "versus_whole": paired[arm],
                "whole": {"macro_f1": float(results[WHOLE]["point"]["macro_f1"]),
                          "f1_extrinsic": float(results[WHOLE]["point"]["f1_extrinsic"]),
                          "hallucinated_as_no": hallucinated_as_no(y_test, whole),
                          "head_aggregation_chosen": results[WHOLE]["best"]["label"]},
                "expected": EXPECTED if arm == "max" else None,
                "prediction_held": verdict if arm == "max" else None,
                "reference_check": reference,
                "y_pred": list(result["pred"]),
                # The extraction's own cost, read off the shard: the classifier is negligible.
                "ms_per_sample": float(np.mean(elapsed)),
                "peak_vram_mb": float(peak),
                "selection_note": "cách gộp đầu chọn trên dev cho từng nhánh, test chấm một lần",
            },
            path=args.results_path,
        )
        print(f"  Đã ghi {args.results_path} — {record['run_name']} ({record['config_hash']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
