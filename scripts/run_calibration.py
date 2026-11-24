"""Is the calibration gain of E03 due to the features or to the size of the classifier? (T22C)

Section 7.3 of the thesis noticed, after the fact, that in all seven published pairs the side with
fewer trainable parameters had the lower ECE, and said what would settle it: compare the two
feature sets at the same number of parameters, and apply temperature scaling to both.

Every block of the chunk-aware features has one value per attention head, six blocks in all, so
the two feature sets can be given *exactly* the same width:

                     small = 192 columns         full = every head's worth (N columns)
    lookback         the 192 best heads          all N heads
    chunk-aware      the 32 best heads x 6       the N / 6 best heads x 6

Heads are ranked by a model fitted on train only. The temperature is fitted on dev by minimising
the negative log-likelihood. The test split is only scored.

Predictions, written before the first run:

1. at equal size, chunk-aware and lookback have ECE differences whose interval contains 0 on
   ViHallu with Qwen2.5-7B, at both sizes;
2. on ViHallu (5.600 training samples) the small classifier has the lower ECE, for both feature
   sets;
3. temperature scaling brings the full lookback classifier on ViHallu below ECE 0,06.

The macro-F1 columns are there to read the ECE by, not to pick a detector: the widths were chosen
to equalise parameter counts, and no width is selected on the test score. ``dev_macro_f1`` is
printed next to the test score for the same reason.

Usage:
    python scripts/run_calibration.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, shard_path  # noqa: E402
from run_chunk_aware import matrix_for, stratified_sample  # noqa: E402
from run_paired_tests import paired_difference  # noqa: E402
from run_sentence_pooling import load_compact  # noqa: E402
from vihallulens.config import REQUIRED_SPLIT_SEED, extraction_hash, load_config  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.metrics import DEFAULT_ECE_BINS, LABELS  # noqa: E402
from vihallulens.features.assemble import blocks_for, rank_heads  # noqa: E402

LOOKBACK, CHUNK = ["basic"], ["basic", "chunk_aware", "stability"]
SMALL_COLUMNS = 192
ROUNDS = 2000
SETTINGS = (
    ("ViHallu, Qwen2.5-7B", "e03_chunk_sentence_vihallu.yaml", None),
    ("ViHallu, Qwen2.5-3B", "e14_qwen3b_vihallu.yaml", None),
    ("ViHallu, Qwen2.5-1.5B", "e14_qwen15b_vihallu.yaml", None),
    ("ViHallu, Sailor2-8B", "e13_sailor2_vihallu.yaml", None),
    ("ViWikiFC", "e15_chunk_viwikifc.yaml", None),
    ("ViFactCheck", "e17_chunk_vifactcheck.yaml", None),
    ("ISE-DSC01, 5.600 mẫu", "e07_chunk_aware_isedsc01.yaml", 5600),
    ("ISE-DSC01, 29.077 mẫu", "e07_chunk_aware_isedsc01.yaml", None),
)


def temper(proba: np.ndarray, temperature: float) -> np.ndarray:
    """Softmax outputs re-softened by ``temperature``; 1 leaves them alone, above 1 flattens."""
    logits = np.log(np.clip(proba, 1e-12, 1.0)) / temperature
    logits -= logits.max(axis=1, keepdims=True)
    out = np.exp(logits)
    return out / out.sum(axis=1, keepdims=True)


def nll(proba: np.ndarray, truth: np.ndarray) -> float:
    return float(-np.log(np.clip(proba[np.arange(len(truth)), truth], 1e-12, 1.0)).mean())


def fit_temperature(proba: np.ndarray, truth: np.ndarray) -> float:
    from scipy.optimize import minimize_scalar

    found = minimize_scalar(lambda t: nll(temper(proba, float(np.exp(t))), truth),
                            bounds=(np.log(0.05), np.log(20.0)), method="bounded")
    return float(np.exp(found.x))


def ece_parts(proba: np.ndarray, truth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per sample: which confidence bin, and (correct − confidence). ECE is a sum over bins."""
    confidence = proba.max(axis=1)
    edges = np.linspace(0.0, 1.0, DEFAULT_ECE_BINS + 1)
    bins = np.clip(np.searchsorted(edges, confidence, side="left") - 1, 0, DEFAULT_ECE_BINS - 1)
    return bins, (proba.argmax(axis=1) == truth).astype(float) - confidence


def ece_from(bins: np.ndarray, gap: np.ndarray) -> float:
    sums = np.bincount(bins, weights=gap, minlength=DEFAULT_ECE_BINS)
    return float(np.abs(sums).sum() / len(gap))


def ece(proba, truth) -> float:
    return ece_from(*ece_parts(proba, truth))


def ece_difference(proba_a, proba_b, truth, rounds: int = ROUNDS,
                   seed: int = REQUIRED_SPLIT_SEED) -> dict:
    """ECE(a) − ECE(b) with an interval from resampling the test set jointly."""
    a, b = ece_parts(proba_a, truth), ece_parts(proba_b, truth)
    rng = np.random.default_rng(seed)
    deltas = np.empty(rounds)
    for i in range(rounds):
        pick = rng.integers(0, len(truth), len(truth))
        deltas[i] = ece_from(a[0][pick], a[1][pick]) - ece_from(b[0][pick], b[1][pick])
    return {"delta": ece_from(*a) - ece_from(*b), "lo": float(np.percentile(deltas, 2.5)),
            "hi": float(np.percentile(deltas, 97.5))}


def arms_for(n_pairs: int) -> dict[str, tuple[list[str], int | None]]:
    """Arm name to (feature groups, heads kept). ``None`` keeps every head."""
    if n_pairs % len(blocks_for(CHUNK)):
        raise ValueError(f"{n_pairs} đầu không chia hết cho {len(blocks_for(CHUNK))} khối")
    n_blocks = len(blocks_for(CHUNK))
    return {"lookback_small": (LOOKBACK, SMALL_COLUMNS), "lookback_full": (LOOKBACK, None),
            "chunk_small": (CHUNK, SMALL_COLUMNS // n_blocks),
            "chunk_full": (CHUNK, n_pairs // n_blocks)}


def fit_arm(records, labels, groups, keep_n, n_layers, n_heads) -> dict:
    n_blocks = len(blocks_for(groups))
    mode, keep = "all", None
    if keep_n is not None:
        every = matrix_for(records["train"], groups, n_layers, n_heads, "all")
        weights = LookbackDetector(seed=REQUIRED_SPLIT_SEED).fit(every, labels["train"])
        keep = rank_heads(weights.feature_weights, n_blocks, n_layers, n_heads)[:keep_n]
        mode = "topk_heads"
        del every
    matrix = {s: matrix_for(records[s], groups, n_layers, n_heads, mode, keep) for s in records}
    model = LookbackDetector(seed=REQUIRED_SPLIT_SEED).fit(matrix["train"], labels["train"])
    lookup = {label: i for i, label in enumerate(model.classes_)}
    truth = {s: np.array([lookup[y] for y in labels[s]]) for s in records}
    dev, test = model.predict_proba(matrix["dev"]), model.predict_proba(matrix["test"])
    temperature = fit_temperature(dev, truth["dev"])
    scaled = temper(test, temperature)
    from sklearn.metrics import f1_score

    predicted = {s: model.predict(matrix[s]) for s in ("dev", "test")}
    return {"proba": test, "scaled": scaled, "truth": truth["test"], "pred": predicted["test"],
            "summary": {
                "dev_macro_f1": float(f1_score(labels["dev"], predicted["dev"],
                                               labels=list(LABELS), average="macro")),
                "n_params": model.n_params_trainable, "n_columns": int(matrix["train"].shape[1]),
                "macro_f1": float(f1_score(labels["test"], predicted["test"],
                                           labels=list(LABELS), average="macro")),
                "ece": ece(test, truth["test"]), "nll": nll(test, truth["test"]),
                "temperature": temperature, "ece_scaled": ece(scaled, truth["test"]),
                "nll_scaled": nll(scaled, truth["test"])}}


def run_setting(name, config, train_sample, processed_dir) -> dict:
    cfg = load_config(Path("configs") / config)
    run = extraction_hash(cfg)
    records, labels = {}, {}
    for split in ("train", "dev", "test"):
        path = shard_path(processed_dir, run, cfg.dataset.name, split)
        records[split], dropped = load_compact(path, blocks_for(CHUNK))
        labels[split] = np.asarray([row["label"] for row in records[split]])
        if dropped:
            print(f"    bỏ {len(dropped)} mẫu {split} có đặc trưng không hữu hạn")
    if train_sample:
        records["train"], labels["train"] = stratified_sample(
            records["train"], labels["train"], train_sample, REQUIRED_SPLIT_SEED)
    n_layers = len(records["train"][0]["layer_indices"])
    n_heads = len(records["train"][0]["lookback_total"]) // n_layers
    fitted = {arm: fit_arm(records, labels, groups, keep_n, n_layers, n_heads)
              for arm, (groups, keep_n) in arms_for(n_layers * n_heads).items()}
    out = {"name": name, "n_test": len(labels["test"]), "n_train": len(labels["train"]),
           "arms": {arm: f["summary"] for arm, f in fitted.items()}, "differences": {}}
    pairs = {"cùng cỡ nhỏ: chunk − lookback": ("chunk_small", "lookback_small"),
             "cùng cỡ đủ: chunk − lookback": ("chunk_full", "lookback_full"),
             "lookback: nhỏ − đủ": ("lookback_small", "lookback_full"),
             "chunk: nhỏ − đủ": ("chunk_small", "chunk_full"),
             "như đã công bố: chunk nhỏ − lookback đủ": ("chunk_small", "lookback_full")}
    for title, (a, b) in pairs.items():
        out["differences"][title] = {
            key: ece_difference(fitted[a][key], fitted[b][key], fitted[a]["truth"])
            for key in ("proba", "scaled")}
        out["differences"][title]["macro_f1"] = paired_difference(
            labels["test"], [fitted[a]["pred"]], [fitted[b]["pred"]])
    return out


def show(setting: dict) -> None:
    print(f"\n{setting['name']} — {setting['n_train']:,} huấn luyện, {setting['n_test']:,} test")
    for arm, s in setting["arms"].items():
        print(f"  {arm:<15} {s['n_params']:>6,} tham số  macro-F1 dev {s['dev_macro_f1']:.4f} "
              f"test {s['macro_f1']:.4f}  "
              f"ECE {s['ece']:.4f} → {s['ece_scaled']:.4f} (T={s['temperature']:.2f})  "
              f"NLL {s['nll']:.3f} → {s['nll_scaled']:.3f}")
    for title, d in setting["differences"].items():
        before, after, f1 = d["proba"], d["scaled"], d["macro_f1"]
        print(f"    {title:<42} {before['delta']:+.4f} [{before['lo']:+.4f}; {before['hi']:+.4f}]"
              f"   sau T: {after['delta']:+.4f} [{after['lo']:+.4f}; {after['hi']:+.4f}]"
              f"   F1 {f1['delta']:+.4f} [{f1['lo']:+.4f}; {f1['hi']:+.4f}]")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--out", type=Path, default=Path("results/calibration.json"))
    parser.add_argument("--only", default=None, help="chỉ chạy các cấu hình có tên chứa chuỗi này")
    args = parser.parse_args()
    done = []
    for name, config, train_sample in SETTINGS:
        if args.only and args.only not in name:
            continue
        started = time.perf_counter()
        setting = run_setting(name, config, train_sample, args.processed_dir)
        show(setting)
        print(f"    ({time.perf_counter() - started:.0f} giây)", flush=True)
        done.append(setting)
    if not args.only:
        args.out.write_text(json.dumps({"settings": done, "rounds": ROUNDS,
                                        "seed": REQUIRED_SPLIT_SEED},
                                       ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nđã ghi {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
