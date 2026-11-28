"""Condense the local feature shards into the small files the result charts are drawn from.

    python scripts/build_figure_data.py

The charts of chapters 6 and 7 need things the run logs do not keep: the hit@1 of every attention
head, the change of every E08 pair, and the confidence bins behind an ECE. Those are recomputed
here, on CPU, from the shards in ``data/processed/`` (which are too big to commit), and written to
``results/figures/`` (which is small and committed), so the charts can be redrawn on any machine.

Nothing is fitted or chosen anew. Every file is checked against the number the thesis already
reports for the same quantity, and the script stops if they disagree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_done, shard_path  # noqa: E402
from run_calibration import CHUNK, LOOKBACK, SMALL_COLUMNS, ece, fit_arm  # noqa: E402
from run_extrinsic import ABSENT, EXPECTED_DIRECTION, PRESENT, feature_means, pair_up  # noqa: E402
from run_sentence_pooling import load_compact  # noqa: E402
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.evaluation.metrics import DEFAULT_ECE_BINS  # noqa: E402
from vihallulens.features.assemble import blocks_for  # noqa: E402

E06_CONFIG = "e06_localization_isedsc01.yaml"
E08_CONFIG = "e08_extrinsic_viwikifc.yaml"
E03_CONFIG = "e03_chunk_sentence_vihallu.yaml"
HISTOGRAM_EDGES = np.linspace(-0.15, 0.15, 61)
TOLERANCE = 5e-4


def published(run_name: str, path: Path) -> dict:
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["run_name"] == run_name:
            return row["metrics"]
    raise SystemExit(f"không có bản ghi {run_name} trong {path}")


def agree(what: str, got: float, want: float) -> None:
    if abs(got - want) > TOLERANCE:
        raise SystemExit(f"{what}: tính lại được {got:.4f}, quyển ghi {want:.4f}")
    print(f"  khớp {what}: {got:.4f}")


def hit_grid(records) -> np.ndarray:
    """Share of samples whose gold chunk each head ranks first, as layers × heads."""
    ranks = np.asarray([r["gold_rank"] for r in records], dtype=np.int16)
    return (ranks == 0).mean(axis=0).reshape(len(records[0]["layer_indices"]), -1)


def change_histogram(change: np.ndarray, direction: int) -> dict:
    """Counts per bin; the two open ends are folded into the outer bins so nothing is lost."""
    clipped = np.clip(change, HISTOGRAM_EDGES[0], HISTOGRAM_EDGES[-1])
    counts, _ = np.histogram(clipped, HISTOGRAM_EDGES)
    aligned = float((change * (direction or 1) > 0).mean())
    return {"counts": counts.tolist(), "direction": direction, "median": float(np.median(change)),
            "aligned": aligned, "outside": int((change != clipped).sum())}


def reliability(proba: np.ndarray, truth: np.ndarray) -> list[dict]:
    """Mean confidence, accuracy and size of every non-empty confidence bin."""
    confidence = proba.max(axis=1)
    correct = proba.argmax(axis=1) == truth
    edges = np.linspace(0.0, 1.0, DEFAULT_ECE_BINS + 1)
    bins = np.clip(np.searchsorted(edges, confidence, side="left") - 1, 0, DEFAULT_ECE_BINS - 1)
    rows = []
    for b in range(DEFAULT_ECE_BINS):
        inside = bins == b
        if inside.any():
            rows.append({"lo": float(edges[b]), "hi": float(edges[b + 1]),
                         "n": int(inside.sum()), "confidence": float(confidence[inside].mean()),
                         "accuracy": float(correct[inside].mean())})
    return rows


def shard(config: str, split: str, processed: Path):
    cfg = load_config(Path("configs") / config)
    return cfg, shard_path(processed, extraction_hash(cfg), cfg.dataset.name, split)


def build_heads(processed: Path, interim: Path, runs: Path) -> tuple[dict, dict]:
    _, path = shard(E06_CONFIG, "dev", processed)
    ise = hit_grid([r for r in load_done(path).values() if "gold_rank" in r])
    want = published("e06_localization_isedsc01", runs)
    agree("E06 hit@1 đầu tốt nhất", ise.max(), want["hit@1"])
    agree("E06 hit@1 trung bình", ise.mean(), want["hit@1_mean_over_heads"])

    cfg, path = shard(E08_CONFIG, "dev", processed)
    records = sorted(load_done(path).values(), key=lambda r: r["sample_id"])
    halves, complete = pair_up(records, load_dataset(cfg.dataset.name, "dev", interim))
    wiki = hit_grid([halves[k][PRESENT] for k in complete if "gold_rank" in halves[k][PRESENT]])
    agree("E08 hit@1 đầu tốt nhất", wiki.max(), 0.8529)

    from scipy.stats import spearmanr

    heads = {"isedsc01": {"grid": ise.round(6).tolist(), "floor": want["hit@1_floor"]},
             "viwikifc": {"grid": wiki.round(6).tolist(), "floor": 0.1027},
             "spearman": float(spearmanr(ise.ravel(), wiki.ravel()).statistic)}
    print(f"  tương quan hạng giữa hai lưới: {heads['spearman']:.4f}")

    want = published("e08_extrinsic_viwikifc", runs)
    pairs = {"n_pairs": len(complete), "edges": HISTOGRAM_EDGES.round(6).tolist(), "features": {}}
    for name, direction in EXPECTED_DIRECTION.items():
        change = np.asarray([feature_means(halves[k][ABSENT], name)
                             - feature_means(halves[k][PRESENT], name) for k in complete])
        pairs["features"][name] = change_histogram(change, direction)
        agree(f"E08 {name}", float(np.median(change)), want[f"{name}_median_change"])
    return heads, pairs


def build_reliability(processed: Path, calibration: Path) -> dict:
    records, labels = {}, {}
    for split in ("train", "dev", "test"):
        _, path = shard(E03_CONFIG, split, processed)
        records[split], _ = load_compact(path, blocks_for(CHUNK))
        labels[split] = np.asarray([row["label"] for row in records[split]])
    n_layers = len(records["train"][0]["layer_indices"])
    n_heads = len(records["train"][0]["lookback_total"]) // n_layers
    want = json.loads(calibration.read_text(encoding="utf-8"))["settings"][0]["arms"]
    out = {}
    for arm, groups, keep in (("lookback_full", LOOKBACK, None),
                              ("chunk_small", CHUNK, SMALL_COLUMNS // len(blocks_for(CHUNK)))):
        fitted = fit_arm(records, labels, groups, keep, n_layers, n_heads)
        agree(f"ECE {arm}", ece(fitted["proba"], fitted["truth"]), want[arm]["ece"])
        out[arm] = {"temperature": fitted["summary"]["temperature"],
                    "ece": fitted["summary"]["ece"], "ece_scaled": fitted["summary"]["ece_scaled"],
                    "before": reliability(fitted["proba"], fitted["truth"]),
                    "after": reliability(fitted["scaled"], fitted["truth"])}
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--runs", type=Path, default=Path("results/runs.jsonl"))
    parser.add_argument("--calibration", type=Path, default=Path("results/calibration.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/figures"))
    args = parser.parse_args()

    heads, pairs = build_heads(args.processed_dir, args.interim_dir, args.runs)
    files = {"head_hit1": heads, "e08_changes": pairs,
             "reliability": build_reliability(args.processed_dir, args.calibration)}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        path = args.out_dir / f"{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"đã ghi {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
