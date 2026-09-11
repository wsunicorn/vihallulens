"""Error analysis of one scored run (task T35).

Two deliverables, both required by ``docs/EXPERIMENTS.md``:

1. **A sample of misclassified test items, each tagged with what went wrong.** The tags here are
   *structural* — computed from measurable properties of the sample and the prediction, not from
   reading the text — so they are reproducible and they are the same for every run of this script.
   Reading the 100 samples and writing what a human sees is the part the two authors do by hand;
   the CSV leaves a column for it.
2. **macro-F1 split by ``meta.prompt_type``.** ViHallu contains prompts with the Vietnamese
   diacritics stripped (``noisy``). Those tokenise into a different token sequence, which moves
   the question's token count and therefore the denominator of every lookback ratio. Without
   the split there is no way to tell "the detector finds hallucinations" from "the detector
   finds noisy prompts".

The model is **refitted here rather than loaded**, because the classifier was never saved — only
its predictions were. Refitting is safe because the whole pipeline is deterministic (seed 42,
same shard, aggregation chosen on dev), and E16 showed it reproduces E02/E03/E07 to the digit.
The script checks that anyway: the refitted predictions must equal the stored ``y_pred`` exactly,
or every number below is about a different model than the one in the tables.

Why structural tags rather than a hand taxonomy baked into code: a taxonomy written after reading
a hundred samples would be a description of *those* hundred, and the next run would need a new
one. Tags like "response copies the context wording but is labelled hallucinated" are hypotheses
about *why* the classifier fails that a reader can confirm or reject sample by sample.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR  # noqa: E402
from run_chunk_aware import load_split, matrix_for, select_aggregation  # noqa: E402
from vihallulens.config import REQUIRED_SPLIT_SEED, extraction_hash, load_config  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.metrics import LABELS, bootstrap_ci, compute_metrics  # noqa: E402
from vihallulens.features.assemble import build_feature_matrix  # noqa: E402
from vihallulens.features.surface import lexical_overlap  # noqa: E402

DEFAULT_OUT = Path("results/error_analysis.csv")

# Thresholds for the structural tags. Round numbers chosen once and stated here rather than
# tuned: the point of a tag is to be the same across runs, not to be optimal for one.
OVERLAP_HIGH = 0.80   # response wording is almost all lifted from the context
OVERLAP_LOW = 0.40    # response shares under half its words with the context
SHORT_RESPONSE = 8    # words; below this the response carries little to attend from
CONFIDENT = 0.70      # top class probability at which a wrong answer is "confidently wrong"
BORDERLINE = 0.10     # gap between the top two probabilities below which the model was unsure

# Primary tag, first match wins. Ordered from "the input itself is unusual" to "the model was
# simply wrong", so that a sample with a structural excuse gets that excuse rather than a verdict
# about confidence. All flags are also written as their own columns, so nothing is lost.
TAG_ORDER = (
    ("prompt_noisy", "prompt bị bỏ dấu"),
    ("mot_doan", "ngữ cảnh chỉ một đoạn — chunk-aware thoái hóa"),
    ("chep_lai_ma_sai", "phản hồi chép lại ngữ cảnh mà vẫn bị gán ảo giác"),
    ("dien_dat_lai", "phản hồi trung thực nhưng diễn đạt khác hẳn ngữ cảnh"),
    ("phan_hoi_ngan", f"phản hồi dưới {SHORT_RESPONSE} từ"),
    ("tu_tin_sai", f"sai mà xác suất lớp đoán ≥ {CONFIDENT:.2f}"),
    ("phan_van", f"hai lớp cao nhất cách nhau < {BORDERLINE:.2f}"),
    ("khac", "không rơi vào mẫu nào ở trên"),
)


def stored_predictions(results_path: Path, run_name: str) -> list | None:
    if not results_path.exists():
        return None
    found = None
    with results_path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                row = json.loads(line)
                if row.get("run_name") == run_name:
                    found = row.get("extra", {}).get("y_pred")
    return found


def refit(cfg, processed_dir: Path, seed: int):
    """The same steps as ``run_chunk_aware.main``, returning what error analysis needs."""
    run = extraction_hash(cfg)
    groups = list(cfg.features.groups)
    records, labels = {}, {}
    for split in ("train", "dev", "test"):
        rows, path, _ = load_split(processed_dir, run, cfg.dataset.name, split)
        if rows is None:
            raise SystemExit(f"thiếu shard {path}")
        records[split] = rows
        labels[split] = np.asarray([row["label"] for row in rows])
    layer_indices = records["train"][0]["layer_indices"]
    n_layers = len(layer_indices)
    n_heads = len(records["train"][0]["lookback_total"]) // n_layers

    x_train = build_feature_matrix(records["train"], groups, n_layers, n_heads)
    best, _ = select_aggregation(x_train, labels["train"], records, groups, n_layers, n_heads,
                                 labels["dev"], seed)
    keep = best["keep"]
    train_m = matrix_for(records["train"], groups, n_layers, n_heads, best["mode"], keep)
    test_m = matrix_for(records["test"], groups, n_layers, n_heads, best["mode"], keep)
    detector = LookbackDetector(
        detector_type=cfg.detector.type, class_weight=cfg.detector.class_weight, seed=seed,
    ).fit(train_m, labels["train"])
    proba = detector.predict_proba(test_m)
    predicted = detector.predict(test_m)
    return records["test"], labels["test"], predicted, proba, list(detector.classes_), best


def tag_row(row: pd.Series) -> tuple[str, dict[str, bool]]:
    """All applicable structural flags, and the first one in priority order as the tag."""
    hallucinated = row["label"] in ("intrinsic", "extrinsic")
    flags = {
        "prompt_noisy": row["prompt_type"] == "noisy",
        "mot_doan": row["n_chunks"] == 1,
        "chep_lai_ma_sai": hallucinated and row["lexical_overlap"] >= OVERLAP_HIGH,
        "dien_dat_lai": row["label"] == "no" and row["lexical_overlap"] <= OVERLAP_LOW,
        "phan_hoi_ngan": row["response_words"] < SHORT_RESPONSE,
        "tu_tin_sai": row["confidence"] >= CONFIDENT,
        "phan_van": row["margin"] < BORDERLINE,
    }
    flags["khac"] = not any(flags.values())
    tag = next(name for name, _ in TAG_ORDER if flags[name])
    return tag, flags


def stratified_errors(errors: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    """``n`` wrong samples, spread over confusion pairs in proportion to how often each occurs.

    Proportional rather than equal per pair: a pair that happens 90 times deserves more of the
    hundred than one that happens twice, or the sample misrepresents where the errors are.
    Largest-remainder rounding so the shares sum to exactly ``n``.
    """
    if len(errors) <= n:
        return errors
    counts = errors["cap_nham"].value_counts()
    raw = counts / counts.sum() * n
    take = raw.astype(int)
    for pair in (raw - take).sort_values(ascending=False).index[: n - take.sum()]:
        take[pair] += 1
    rng = np.random.default_rng(seed)
    parts = []
    for pair, k in take.items():
        pool = errors[errors["cap_nham"] == pair]
        parts.append(pool.iloc[rng.choice(len(pool), size=int(k), replace=False)])
    return pd.concat(parts).sort_values(["cap_nham", "sample_id"])


def group_metrics(frame: pd.DataFrame, mask: np.ndarray, seed: int) -> dict:
    y, p = frame["label"].to_numpy()[mask], frame["pred"].to_numpy()[mask]
    metrics = compute_metrics(y, p)
    metrics.update(bootstrap_ci(y, p, seed=seed))
    metrics["n"] = int(mask.sum())
    return metrics


def draw(errors: pd.DataFrame, sample: pd.DataFrame, run_name: str, out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    pairs = errors["cap_nham"].value_counts()
    axes[0].barh(pairs.index[::-1], pairs.values[::-1], color="#4c72b0")
    axes[0].set_title(f"Mọi mẫu sai trên tập test ({len(errors)})")
    axes[0].set_xlabel("số mẫu")
    for i, v in enumerate(pairs.values[::-1]):
        axes[0].text(v + 0.5, i, str(v), va="center", fontsize=9)

    tags = sample["nhan_loi"].value_counts()
    axes[1].barh(tags.index[::-1], tags.values[::-1], color="#dd8452")
    axes[1].set_title(f"Nhãn cấu trúc của {len(sample)} mẫu được lấy")
    axes[1].set_xlabel("số mẫu")
    for i, v in enumerate(tags.values[::-1]):
        axes[1].text(v + 0.3, i, str(v), va="center", fontsize=9)

    fig.suptitle(f"Phân tích sai sót — {run_name}", fontsize=12)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="T35: phân tích sai sót của một lượt chấm.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--reference-run", required=True,
                        help="run_name trong runs.jsonl có y_pred để đối chiếu bản khớp lại")
    parser.add_argument("--n", type=int, default=100, help="số mẫu sai đưa vào CSV")
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    seed = REQUIRED_SPLIT_SEED

    print()
    print("=" * 80)
    print(f"T35 — PHÂN TÍCH SAI SÓT: {args.reference_run}")
    print("=" * 80)
    started = time.perf_counter()
    records, labels, predicted, proba, classes, best = refit(cfg, args.processed_dir, seed)
    print(f"  khớp lại mô hình      : {best['label']}, {best['n_features']:,} chiều "
          f"({time.perf_counter() - started:.0f} giây)")

    # -- the reproduction check: refit must equal what the tables were built from ---------
    stored = stored_predictions(args.results_path, args.reference_run)
    if stored is None:
        raise SystemExit(f"không thấy y_pred của {args.reference_run} trong {args.results_path}")
    agree = int(np.sum(np.asarray(stored) == predicted))
    print(f"  đối chiếu y_pred đã lưu: {agree}/{len(predicted)} trùng"
          + ("" if agree == len(predicted) else "  !! KHÁC — mọi số dưới đây về mô hình khác"))
    if agree != len(predicted):
        return 1

    # -- join predictions with the text and metadata -------------------------------------
    text = load_dataset(cfg.dataset.name, "test", args.interim_dir).set_index("sample_id")
    frame = pd.DataFrame({
        "sample_id": [r["sample_id"] for r in records],
        "label": labels,
        "pred": predicted,
        "n_chunks": [r["n_chunks"] for r in records],
    })
    for i, name in enumerate(classes):
        frame[f"p_{name}"] = proba[:, i]
    top2 = np.sort(proba, axis=1)[:, -2:]
    frame["confidence"] = top2[:, 1]
    frame["margin"] = top2[:, 1] - top2[:, 0]
    frame = frame.join(text[["question", "response", "context", "meta"]], on="sample_id")
    meta = frame["meta"].map(lambda m: json.loads(m) if isinstance(m, str) else (m or {}))
    frame["prompt_type"] = meta.map(lambda m: m.get("prompt_type", "unknown"))
    frame["context_words"] = frame["context"].map(lambda s: len(str(s).split()))
    frame["response_words"] = frame["response"].map(lambda s: len(str(s).split()))
    frame["lexical_overlap"] = [
        lexical_overlap(str(r), str(c))
        for r, c in zip(frame["response"], frame["context"], strict=True)
    ]
    frame["dung"] = frame["label"] == frame["pred"]
    frame["cap_nham"] = frame["label"] + "→" + frame["pred"]

    errors = frame[~frame["dung"]].copy()
    tagged = [tag_row(row) for _, row in errors.iterrows()]
    errors["nhan_loi"] = [t for t, _ in tagged]
    for name, _ in TAG_ORDER:
        errors[f"co_{name}"] = [f[name] for _, f in tagged]

    print(f"  tập test              : {len(frame):,} mẫu, sai {len(errors):,} "
          f"({len(errors) / len(frame) * 100:.1f} %)")

    # -- confusion pairs over ALL errors ---------------------------------------------------
    print()
    print("-" * 80)
    print("CẶP NHẦM — trên toàn bộ mẫu sai của tập test")
    print("-" * 80)
    for pair, count in errors["cap_nham"].value_counts().items():
        true_label = pair.split("→")[0]
        base = int((frame["label"] == true_label).sum())
        print(f"  {pair:<24} {count:>4}   ({count / base * 100:>4.1f} % số mẫu {true_label})")

    # -- structural flags over ALL errors (each sample can carry several) -----------------
    print()
    print("-" * 80)
    print("NHÃN CẤU TRÚC — mỗi mẫu có thể mang nhiều nhãn; cột 'chính' lấy nhãn đầu theo thứ tự")
    print("-" * 80)
    print(f"  {'nhãn':<18}{'có mặt':>8}{'chính':>8}   nghĩa")
    for name, meaning in TAG_ORDER:
        present = int(errors[f"co_{name}"].sum())
        primary = int((errors["nhan_loi"] == name).sum())
        print(f"  {name:<18}{present:>8}{primary:>8}   {meaning}")

    # -- the 100-sample CSV -----------------------------------------------------------------
    sample = stratified_errors(errors, args.n, seed)
    columns = ["sample_id", "label", "pred", "cap_nham", "nhan_loi"] \
        + [f"co_{n}" for n, _ in TAG_ORDER] \
        + ["confidence", "margin"] + [f"p_{c}" for c in LABELS if f"p_{c}" in sample] \
        + ["n_chunks", "context_words", "response_words", "lexical_overlap", "prompt_type",
           "question", "response", "context"]
    out = sample[columns].copy()
    out["ghi_chu_tay"] = ""   # for the reading pass — what a human sees that the tags do not
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False, encoding="utf-8-sig")
    print()
    print(f"  Đã ghi {args.out} — {len(out)} dòng, lấy theo tỷ lệ cặp nhầm, seed {seed}")

    # -- prompt_type split, the requirement from docs/EXPERIMENTS.md ------------------------
    print()
    print("-" * 80)
    print("TÁCH THEO meta.prompt_type — yêu cầu ở docs/EXPERIMENTS.md cho mọi thí nghiệm ViHallu")
    print("-" * 80)
    noisy = (frame["prompt_type"] == "noisy").to_numpy()
    rows = {"noisy": group_metrics(frame, noisy, seed),
            "còn lại": group_metrics(frame, ~noisy, seed)}
    print(f"  {'nhóm':<10}{'n':>6}{'macro-F1':>10}{'KTC 95 %':>20}{'sai':>8}{'tỷ lệ sai':>11}")
    for name, m in rows.items():
        mask = noisy if name == "noisy" else ~noisy
        wrong = int((~frame["dung"].to_numpy()[mask]).sum())
        print(f"  {name:<10}{m['n']:>6}{m['macro_f1']:>10.4f}"
              f"  [{m['macro_f1_lo']:.4f}, {m['macro_f1_hi']:.4f}]{wrong:>8}"
              f"{wrong / m['n'] * 100:>10.1f} %")
    gap = rows["noisy"]["macro_f1"] - rows["còn lại"]["macro_f1"]
    print(f"  chênh noisy − còn lại : {gap:+.4f}")
    if rows["noisy"]["n"] < 50:
        print(f"  Nhóm noisy chỉ có {rows['noisy']['n']} mẫu; khoảng tin cậy rộng là hệ quả trực "
              "tiếp, đừng đọc con số điểm mà không nhìn khoảng.")

    summary_path = args.out.with_suffix(".json")
    summary_path.write_text(json.dumps({
        "run_name": args.reference_run,
        "n_test": int(len(frame)),
        "n_errors": int(len(errors)),
        "confusion_pairs": errors["cap_nham"].value_counts().to_dict(),
        "tags_present": {n: int(errors[f"co_{n}"].sum()) for n, _ in TAG_ORDER},
        "tags_primary": errors["nhan_loi"].value_counts().to_dict(),
        "prompt_type": {k: {kk: (float(vv) if isinstance(vv, (int, float)) else vv)
                            for kk, vv in v.items()} for k, v in rows.items()},
        "n_sampled": int(len(out)),
        "seed": seed,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Đã ghi {summary_path}")

    png = args.out.with_suffix(".png")
    draw(errors, sample, args.reference_run, png)
    print(f"  Đã vẽ {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
