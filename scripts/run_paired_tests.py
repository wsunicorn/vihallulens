"""Paired significance tests between methods scored on the same test samples (T22B).

The thesis compared methods by whether their separate 95 % intervals overlap. Two methods scored
on the same samples share most of their sampling noise, so overlapping intervals say little about
the difference. This script resamples the samples jointly, reports the difference with its own
interval, adds McNemar's exact test on correctness, and corrects the family of H2 comparisons
for being eight tests rather than one (Holm).

Nothing is refitted. Every prediction comes from results/runs.jsonl, the file the published
numbers were read from, and each one must reproduce the macro-F1 logged with it before it is used.

Predictions, written before the first run:

* H2 family — the interval of every chunk-aware minus lookback difference contains 0, except
  that Sailor2 and Qwen2.5-3B come out below 0 at the point estimate;
* E03 minus PhoBERT contains 0; XLM-R minus E03 contains 0;
* both attention detectors beat the surface features with an interval above 0.

Usage:
    python scripts/run_paired_tests.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import REQUIRED_SPLIT_SEED  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.evaluation.metrics import LABELS  # noqa: E402

ROUNDS = 10_000
REPRODUCED = 1e-6  # a stored prediction must give back its logged macro-F1 this closely
CONVERGED = 0.5  # encoder seeds below this never left the uniform prediction (Chương 6)

# (name, chunk-aware run, lookback run)
H2_FAMILY = (
    ("ViHallu, Qwen2.5-7B", "e03_chunk_aware", "e02_lookback_lens"),
    ("ViHallu, Qwen2.5-3B", "e14_qwen3b_vihallu", "e14_baseline_lookback_qwen3b"),
    ("ViHallu, Qwen2.5-1.5B", "e14_qwen15b_vihallu", "e14_baseline_lookback_qwen15b"),
    ("ViHallu, Sailor2-8B", "e13_sailor2_vihallu", "e13_baseline_lookback_sailor2"),
    ("ISE-DSC01, 29.077 mẫu huấn luyện", "e07_chunk_aware_isedsc01",
     "e07_baseline_lookback_isedsc01"),
    ("ISE-DSC01, 5.600 mẫu huấn luyện", "e07_chunk_aware_isedsc01_train5600",
     "e07_baseline_lookback_isedsc01_train5600"),
    ("ViWikiFC", "e15_chunk_viwikifc", "e15_baseline_lookback_viwikifc"),
    ("ViFactCheck", "e17_chunk_vifactcheck", "e17_baseline_lookback_vifactcheck"),
)
# (name, a, b): the difference is a minus b
OTHERS = (
    ("Lookback gộp − đặc trưng bề mặt", "e02_lookback_lens", "e01_surface_baseline"),
    ("Chunk-aware − đặc trưng bề mặt", "e03_chunk_aware", "e01_surface_baseline"),
    ("PhoBERT − lookback gộp", "e09_phobert", "e02_lookback_lens"),
    ("PhoBERT − chunk-aware", "e09_phobert", "e03_chunk_aware"),
    ("XLM-R − lookback gộp", "e09_xlmr", "e02_lookback_lens"),
    ("XLM-R − chunk-aware", "e09_xlmr", "e03_chunk_aware"),
    ("Lookback gộp − Gemini (300 mẫu)", "e02_lookback_lens", "e10_gemini_judge"),
    ("Chunk-aware − Gemini (300 mẫu)", "e03_chunk_aware", "e10_gemini_judge"),
)


def macro_f1(y_true, y_pred) -> float:
    return float(f1_score(y_true, y_pred, labels=list(LABELS), average="macro", zero_division=0))


def encode(labels) -> np.ndarray:
    lookup = {label: i for i, label in enumerate(LABELS)}
    return np.array([lookup[label] for label in labels], dtype=np.int64)


def macro_f1_rows(truth: np.ndarray, pred: np.ndarray) -> np.ndarray:
    """macro-F1 of every row of two (rounds, n) code arrays, without a Python loop."""
    k = len(LABELS)
    total = np.zeros(truth.shape[0])
    for c in range(k):
        tp = ((truth == c) & (pred == c)).sum(1)
        denominator = (truth == c).sum(1) + (pred == c).sum(1)
        total += np.where(denominator > 0, 2 * tp / np.maximum(denominator, 1), 0.0)
    return total / k


def paired_difference(truth, preds_a: list, preds_b: list, rounds: int = ROUNDS,
                      seed: int = REQUIRED_SPLIT_SEED) -> dict:
    """macro-F1(a) − macro-F1(b), averaged over each side's seeds, resampled jointly."""
    truth = encode(truth)
    a, b = [encode(p) for p in preds_a], [encode(p) for p in preds_b]
    n = len(truth)

    def score(index):
        row = truth[index]
        return (np.mean([macro_f1_rows(row, p[index]) for p in a], axis=0)
                - np.mean([macro_f1_rows(row, p[index]) for p in b], axis=0))

    rng = np.random.default_rng(seed)
    deltas = np.concatenate([score(rng.integers(0, n, (500, n))) for _ in range(rounds // 500)])
    below = float((deltas <= 0).mean())
    return {"delta": float(score(np.arange(n)[None, :])[0]),
            "lo": float(np.percentile(deltas, 2.5)), "hi": float(np.percentile(deltas, 97.5)),
            "p_bootstrap": float(min(1.0, 2 * min(below, 1 - below)))}


def mcnemar_exact(truth, pred_a, pred_b) -> dict:
    """Exact McNemar on which samples each side gets right; ``only_a`` counts a's lone hits."""
    from scipy.stats import binomtest

    truth, pred_a, pred_b = map(np.asarray, (truth, pred_a, pred_b))
    right_a, right_b = pred_a == truth, pred_b == truth
    only_a, only_b = int((right_a & ~right_b).sum()), int((~right_a & right_b).sum())
    n = only_a + only_b
    p = float(binomtest(only_a, n, 0.5).pvalue) if n else 1.0
    return {"only_a": only_a, "only_b": only_b, "p": p}


def holm(p_values) -> list[float]:
    """Holm step-down adjusted p-values, in the order given."""
    order = np.argsort(p_values)
    adjusted, running, m = [0.0] * len(p_values), 0.0, len(p_values)
    for rank, index in enumerate(order):
        running = max(running, (m - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted


def read_runs(path: Path) -> dict[str, dict]:
    runs = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            runs[record["run_name"]] = record
    return runs


def truth_for(dataset: str, interim_dir) -> dict[str, str]:
    frame = load_dataset(dataset, "test", interim_dir)
    return dict(zip(frame["sample_id"], frame["label"], strict=True))


class Predictions:
    """Stored predictions keyed by sample id, accepted only if they reproduce their own score."""

    def __init__(self, runs: dict, interim_dir, dropped: dict[str, set]):
        self.runs, self.interim_dir, self.dropped = runs, interim_dir, dropped
        self.truths: dict[str, dict] = {}
        self.cache: dict[str, list[dict]] = {}

    def truth(self, dataset: str) -> dict[str, str]:
        if dataset not in self.truths:
            self.truths[dataset] = truth_for(dataset, self.interim_dir)
        return self.truths[dataset]

    def dataset(self, run: str) -> str:
        return self.runs[run]["config"]["dataset"]["name"]

    def get(self, run: str) -> list[dict]:
        """One ``{sample_id: label}`` per converged seed (one for deterministic methods)."""
        if run in self.cache:
            return self.cache[run]
        record, truth = self.runs[run], self.truth(self.dataset(run))
        extra, logged = record["extra"], float(record["metrics"]["macro_f1"])
        if "y_pred_per_seed" in extra:
            rows = extra["y_pred_per_seed"]
            rows = list(rows.values()) if isinstance(rows, dict) else rows
            rows = [row["y_pred"] if isinstance(row, dict) else row for row in rows]
            ids = extra["sample_ids"]
            gold = [truth[i] for i in ids]
            kept = [row for row in rows if macro_f1(gold, row) > CONVERGED]
            found = [dict(zip(ids, row, strict=True)) for row in kept]
            score = float(np.mean([macro_f1(gold, row) for row in kept]))
        else:
            found, score = self._single(run, extra, truth, logged)
        if abs(score - logged) > REPRODUCED:
            raise SystemExit(f"{run}: dự đoán đã lưu cho macro-F1 {score:.6f}, bản ghi là "
                             f"{logged:.6f}. Không dùng được.")
        self.cache[run] = found
        return found

    def _single(self, run, extra, truth, logged):
        """Find which of the two orders in use the stored list follows, and prove it."""
        predicted = extra["y_pred"]
        if "sample_ids" in extra:
            orders = [extra["sample_ids"]]
        else:
            keep = [i for i in truth if i not in self.dropped.get(run, set())]
            orders = [sorted(keep), keep]
        best = None
        for ids in orders:
            if len(ids) != len(predicted):
                continue
            score = macro_f1([truth[i] for i in ids], predicted)
            if best is None or abs(score - logged) < abs(best[1] - logged):
                best = ([dict(zip(ids, predicted, strict=True))], score)
        if best is None:
            raise SystemExit(f"{run}: {len(predicted)} dự đoán nhưng tập test có số mẫu khác")
        return best


def compare(store: Predictions, a: str, b: str) -> dict:
    if store.dataset(a) != store.dataset(b):
        raise ValueError(f"{a} và {b} không cùng bộ dữ liệu")
    truth, side_a, side_b = store.truth(store.dataset(a)), store.get(a), store.get(b)
    ids = sorted(set(side_a[0]) & set(side_b[0]))
    gold = [truth[i] for i in ids]
    preds_a = [[p[i] for i in ids] for p in side_a]
    preds_b = [[p[i] for i in ids] for p in side_b]
    out = {"a": a, "b": b, "n": len(ids),
           "macro_a": float(np.mean([macro_f1(gold, p) for p in preds_a])),
           "macro_b": float(np.mean([macro_f1(gold, p) for p in preds_b])),
           **paired_difference(gold, preds_a, preds_b)}
    if len(preds_a) == len(preds_b) == 1:
        out["mcnemar"] = mcnemar_exact(gold, preds_a[0], preds_b[0])
    return out


def sailor_dropped(processed_dir: Path, runs: dict) -> dict[str, set]:
    """Test samples left out of E13 because their features were not finite."""
    from run_chunk_aware import load_split

    out = {}
    for run in ("e13_sailor2_vihallu", "e13_baseline_lookback_sailor2"):
        config = runs[run]["config"]
        for path in sorted(Path(processed_dir).glob("vihallu_test_*.jsonl")):
            name = path.stem.rsplit("_", 1)[1]
            rows, _, dropped = load_split(processed_dir, name, "vihallu", "test")
            if dropped and len(rows) == runs[run]["extra"]["n_test"]:
                out[run] = {row["sample_id"] for row in dropped}
                break
        if run not in out:
            raise SystemExit(f"không tìm thấy shard test của {config['extractor']['model_name']}")
    return out


def line(name: str, r: dict) -> str:
    text = (f"  {name:<36} n={r['n']:<5} {r['delta']:+.4f} [{r['lo']:+.4f}; {r['hi']:+.4f}]  "
            f"p={r['p_bootstrap']:.4f}")
    if "mcnemar" in r:
        m = r["mcnemar"]
        text += f"  McNemar {m['only_a']}/{m['only_b']} p={m['p']:.4f}"
    return text


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--interim-dir", default=str(DEFAULT_INTERIM_DIR))
    parser.add_argument("--out", type=Path, default=Path("results/paired_tests.json"))
    args = parser.parse_args()

    runs = read_runs(args.results_path)
    store = Predictions(runs, args.interim_dir, sailor_dropped(args.processed_dir, runs))
    family = [{"name": name, **compare(store, a, b)} for name, a, b in H2_FAMILY]
    for row, adjusted in zip(family, holm([r["p_bootstrap"] for r in family]), strict=True):
        row["p_holm"] = adjusted
    others = [{"name": name, **compare(store, a, b)} for name, a, b in OTHERS]

    print("Chunk-aware − lookback gộp (H2), bootstrap ghép cặp 10.000 lần")
    for row in family:
        print(line(row["name"], row), f" p Holm={row['p_holm']:.4f}")
    print("Các cặp khác trên tập test ViHallu")
    for row in others:
        print(line(row["name"], row))
    args.out.write_text(json.dumps({"h2": family, "others": others, "rounds": ROUNDS,
                                    "seed": REQUIRED_SPLIT_SEED}, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"đã ghi {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
