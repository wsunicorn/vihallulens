"""Task T45D, experiment E19: attention against context ablation for locating the evidence.

    # once, on CPU, where the E08 shard lives (already done; the selection is committed)
    python scripts/run_attribution.py select --rebuilt-interim <thư mục dựng lại ngữ cảnh E08>
    # on a Kaggle T4, after building the E08 contexts (notebook t45d_e19_cat_bo_t4.ipynb)
    python scripts/run_attribution.py run
    # on CPU, with results/e19_attribution.jsonl downloaded next to the E08 shard
    python scripts/run_attribution.py report

E06 found the strongest attention head points at the gold chunk 87.8 % of the time, and E08
repeated the measurement on ViWikiFC. ContextCite argues attention is often not faithful for
attribution and that ablation is the reliable test. E19 runs ablation (ARC-JSD style, see
``vihallulens.attribution``) on 300 of E08's evidence-present samples and puts its hit@1 next to
the attention heads' **on the same samples**, together with what each costs in forward passes.

The samples are fixed in ``configs/e19_attribution_samples.json`` with a hash of each context:
E08's shard was extracted from contexts built before the BM25 tie fix, and 31 rows rebuild
differently today, so those are excluded and the run refuses a context whose hash differs.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_features import DEFAULT_PROCESSED_DIR, load_done, shard_path  # noqa: E402
from vihallulens.attribution import (  # noqa: E402
    COMPUTE_DTYPE,
    N_SAMPLES,
    PREDICTION,
    SELECTION_SEED,
    context_digest,
    gold_rank_of,
    select_samples,
)
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.data.chunking import (  # noqa: E402
    chunk_context,
    chunking_arguments,
    locate_evidence_chunk,
)
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402

E08_CONFIG = Path("configs/e08_extrinsic_viwikifc.yaml")
SELECTION = Path("configs/e19_attribution_samples.json")
RESULTS = Path("results/e19_attribution.jsonl")
# The head E06 named on ISE-DSC01. Chosen on another corpus, so using it here involves no
# selection on E19's own samples.
E06_HEAD = (14, 6)
BOOTSTRAP_ROUNDS = 10_000
PROGRESS_EVERY = 5


def present_rows(frame) -> dict[str, dict]:
    return {
        row["sample_id"]: row
        for row in frame.to_dict("records")
        if row["meta"]["condition"] == "present"
    }


def gold_chunk_of(row, chunking_kwargs) -> tuple[list, int | None]:
    chunks = chunk_context(row["context"], **chunking_kwargs)
    return chunks, locate_evidence_chunk(chunks, row.get("evidence") or "", row["context"])


# ----------------------------------------------------------------------------------- select


def cmd_select(args) -> int:
    cfg = load_config(E08_CONFIG)
    chunking_kwargs = chunking_arguments(cfg.chunking)
    shard = load_done(shard_path(args.processed_dir, extraction_hash(cfg), cfg.dataset.name, "dev"))
    kaggle = present_rows(load_dataset(cfg.dataset.name, "dev", args.interim_dir))
    rebuilt = present_rows(load_dataset(cfg.dataset.name, "dev", args.rebuilt_interim))

    candidates, reasons = {}, {"ngữ cảnh dựng lại khác": 0, "không có trong shard": 0,
                               "không định vị được vàng": 0, "bị cắt hoặc tràn số": 0}
    for sample_id, row in kaggle.items():
        if rebuilt.get(sample_id, {}).get("context") != row["context"]:
            reasons["ngữ cảnh dựng lại khác"] += 1
            continue
        record = shard.get(sample_id)
        if record is None or "gold_rank" not in record:
            reasons["không có trong shard"] += 1
            continue
        chunks, gold = gold_chunk_of(row, chunking_kwargs)
        if gold is None or gold != record["gold_chunk"] or len(chunks) != record["n_chunks"]:
            reasons["không định vị được vàng"] += 1
            continue
        if record["truncated"] or record["nonfinite_layers"]:
            reasons["bị cắt hoặc tràn số"] += 1
            continue
        candidates[sample_id] = {"sample_id": sample_id,
                                 "context_sha256": context_digest(row["context"]),
                                 "n_chunks": len(chunks), "gold_chunk": gold}

    chosen = select_samples(list(candidates))
    payload = {
        "experiment": "E19",
        "created": date.today().isoformat(),
        "source": f"{cfg.dataset.name}/dev, nửa present, shard {extraction_hash(cfg)}",
        "seed": SELECTION_SEED,
        "n_candidates": len(candidates),
        "excluded": reasons,
        "samples": [candidates[s] for s in chosen],
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  ứng viên  : {len(candidates):,} mẫu present; loại {reasons}")
    print(f"  đã chọn   : {len(chosen)} mẫu, hạt giống {SELECTION_SEED} -> {args.out}")
    return 0


# ----------------------------------------------------------------------------------- run


def cmd_run(args) -> int:
    cfg = load_config(E08_CONFIG)
    chunking_kwargs = chunking_arguments(cfg.chunking)
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))["samples"]
    if args.limit:
        selection = selection[: args.limit]
    rows = present_rows(load_dataset(cfg.dataset.name, "dev", args.interim_dir))

    mismatched = [s["sample_id"] for s in selection
                  if context_digest(rows[s["sample_id"]]["context"]) != s["context_sha256"]]
    if mismatched:
        print(f"  {len(mismatched)} ngữ cảnh dựng lại KHÁC bản E08 đã trích, "
              f"ví dụ {mismatched[:3]}.")
        print("  Dừng: so chú ý với cắt bỏ chỉ có nghĩa trên cùng một ngữ cảnh.")
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(args.out)
    todo = [s for s in selection if s["sample_id"] not in done]

    print()
    print("=" * 80)
    print("E19 — ĐỊNH VỊ BẰNG CẮT BỎ NGỮ CẢNH (ARC-JSD)")
    print("=" * 80)
    print(f"  mô hình đọc           : {cfg.extractor.model_name}, NF4, {COMPUTE_DTYPE}")
    print(f"  mẫu                   : {len(selection)} (đã có {len(done)}, còn {len(todo)})")
    print(f"  lượt đọc dự kiến      : "
          f"{sum(s['n_chunks'] + 1 for s in todo):,} (1 + số đoạn mỗi mẫu)")
    if not todo:
        return 0

    import torch

    from vihallulens.attribution import AblationAttributor

    attributor = AblationAttributor(cfg.extractor.model_name)
    started, failed = time.perf_counter(), 0
    with args.out.open("a", encoding="utf-8") as handle:
        for position, sample in enumerate(todo, start=1):
            row = rows[sample["sample_id"]]
            chunks, gold = gold_chunk_of(row, chunking_kwargs)
            assert gold == sample["gold_chunk"] and len(chunks) == sample["n_chunks"]
            torch.cuda.reset_peak_memory_stats()
            try:
                result = attributor.attribute(row["context"], row.get("question") or "",
                                              row["response"], chunks)
            except Exception as error:  # noqa: BLE001 — one bad sample must not end the run
                failed += 1
                print(f"\n  LỖI {sample['sample_id']}: {type(error).__name__}: {error}")
                continue
            record = {"sample_id": sample["sample_id"], "gold_chunk": gold,
                      "n_chunks": len(chunks), **result,
                      "peak_vram_mb": torch.cuda.max_memory_allocated() / 1024**2}
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            if position % PROGRESS_EVERY == 0 or position == len(todo):
                rate = (time.perf_counter() - started) / position
                print(f"      {position:>4}/{len(todo)}  {rate:,.1f} s/mẫu  "
                      f"còn ~{rate * (len(todo) - position) / 60:.0f} phút  lỗi {failed}", end="\r")
    print()
    print(f"  xong: {len(todo) - failed} mẫu, lỗi {failed}, "
          f"{(time.perf_counter() - started) / 60:.1f} phút -> {args.out}")
    return 0


# ----------------------------------------------------------------------------------- report


def bootstrap(values: np.ndarray, rounds: int = BOOTSTRAP_ROUNDS) -> tuple[float, float]:
    rng = np.random.default_rng(SELECTION_SEED)
    means = rng.choice(values, size=(rounds, len(values)), replace=True).mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summary(ranks: np.ndarray, n_chunks: np.ndarray) -> dict:
    """hit@1, hit@3 and MRR of one ranker, with the bootstrap interval of hit@1."""
    hit1 = (ranks < 1).astype(float)
    low, high = bootstrap(hit1)
    return {"hit@1": float(hit1.mean()), "hit@1_low": low, "hit@1_high": high,
            "hit@3": float((ranks < 3).mean()), "mrr": float((1.0 / (ranks + 1)).mean()),
            "floor@1": float((1.0 / n_chunks).mean())}


def cmd_report(args) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cfg = load_config(E08_CONFIG)
    selection = {s["sample_id"]: s for s in
                 json.loads(SELECTION.read_text(encoding="utf-8"))["samples"]}
    ablation = load_done(args.out)
    shard = load_done(shard_path(args.processed_dir, extraction_hash(cfg), cfg.dataset.name, "dev"))
    ids = sorted(s for s in selection if s in ablation)
    if len(ids) < 20:
        print(f"Mới có {len(ids)} mẫu trong {args.out}; chạy lệnh run trước.")
        return 1

    layers = shard[ids[0]]["layer_indices"]
    n_heads = len(shard[ids[0]]["gold_rank"]) // len(layers)

    def head_ranks(sample_ids):
        return np.asarray([shard[s]["gold_rank"] for s in sample_ids]).reshape(
            len(sample_ids), len(layers), n_heads)

    attention = head_ranks(ids)
    n_chunks = np.asarray([selection[s]["n_chunks"] for s in ids], dtype=float)
    abl_ranks = np.asarray([gold_rank_of(ablation[s]["scores"], selection[s]["gold_chunk"])
                            for s in ids])

    # The best head is chosen on E08's other evidence-present samples, never on these 300.
    held_out = sorted(s for s, r in shard.items()
                      if s.endswith("__present") and "gold_rank" in r and s not in selection)
    hit_by_head = (head_ranks(held_out) < 1).mean(axis=0)
    best_layer, best_head = np.unravel_index(int(hit_by_head.argmax()), hit_by_head.shape)
    e06 = (layers.index(E06_HEAD[0]), E06_HEAD[1])

    rows = {
        "cắt bỏ ngữ cảnh (ARC-JSD)": summary(abl_ranks, n_chunks),
        f"đầu mạnh nhất, chọn trên {len(held_out):,} mẫu khác "
        f"(lớp {layers[best_layer]}, đầu {best_head})":
            summary(attention[:, best_layer, best_head], n_chunks),
        f"đầu E06 chọn trên ISE-DSC01 (lớp {E06_HEAD[0]}, đầu {E06_HEAD[1]})":
            summary(attention[:, e06[0], e06[1]], n_chunks),
    }
    mean_heads = (attention < 1).mean(axis=(1, 2))
    low, high = bootstrap(mean_heads)
    rows[f"trung bình {len(layers) * n_heads} đầu"] = {
        "hit@1": float(mean_heads.mean()), "hit@1_low": low, "hit@1_high": high,
        "hit@3": float((attention < 3).mean()), "mrr": float((1.0 / (attention + 1)).mean()),
        "floor@1": float((1.0 / n_chunks).mean())}

    forwards = float(np.mean([ablation[s]["n_forward"] for s in ids]))
    seconds = float(np.mean([ablation[s]["elapsed_ms"] for s in ids])) / 1000

    print()
    print("=" * 80)
    print(f"E19 — CẮT BỎ NGỮ CẢNH SO VỚI CHÚ Ý, {len(ids)} mẫu ViWikiFC có vàng")
    print("=" * 80)
    print(f"  {'cách định vị':<62}{'hit@1':>8}{'KTC 95 %':>18}{'hit@3':>8}{'MRR':>8}")
    for name, r in rows.items():
        interval = f"[{r['hit@1_low']:.3f}–{r['hit@1_high']:.3f}]"
        print(f"  {name:<62}{r['hit@1']:>8.3f}{interval:>18}{r['hit@3']:>8.3f}{r['mrr']:>8.3f}")
    print(f"  chọn bừa một đoạn: hit@1 {rows['cắt bỏ ngữ cảnh (ARC-JSD)']['floor@1']:.3f}")
    print(f"  chi phí cắt bỏ: {forwards:.1f} lượt đọc/mẫu (chú ý: 1), {seconds:.1f} s/mẫu trên T4")

    ablation_hit = rows["cắt bỏ ngữ cảnh (ARC-JSD)"]["hit@1"]
    best_name = next(name for name in rows if name.startswith("đầu mạnh nhất"))
    best_hit = rows[best_name]["hit@1"]
    outcome = {
        "ablation_hit1_above_best_head": ablation_hit > best_hit,
        "hit1_ratio_below_forward_ratio": ablation_hit / max(best_hit, 1e-9) < forwards,
    }
    print()
    for key, predicted in PREDICTION.items():
        verdict = "ĐÚNG" if outcome[key] == predicted else "SAI"
        print(f"  dự đoán ghi trước — {key}: {verdict}")

    compared = (("ablation", "cắt bỏ ngữ cảnh (ARC-JSD)"), ("best_head", best_name))
    metrics = {f"{key}_{metric}": value
               for key, name in compared for metric, value in rows[name].items()}
    metrics["mean_heads_hit@1"] = rows[f"trung bình {len(layers) * n_heads} đầu"]["hit@1"]
    peak = max((ablation[s].get("peak_vram_mb") or 0.0) for s in ids)
    extra = {"ms_per_sample": seconds * 1000, "peak_vram_mb": float(peak),
             "n_samples": len(ids), "forwards_per_sample": forwards,
             "seconds_per_sample": seconds, "best_head": [int(layers[best_layer]), int(best_head)],
             "best_head_selected_on": len(held_out), "rows": rows,
             "prediction": PREDICTION, "outcome": outcome, "compute_dtype": COMPUTE_DTYPE}
    config = {**cfg.to_dict(), "run_name": "e19_attribution_viwikifc", "experiment": "E19",
              "n_samples": N_SAMPLES, "selection_seed": SELECTION_SEED}
    record = log_result("e19_attribution_viwikifc", config, metrics, extra, path=args.results_path)
    print(f"\n  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="T45D/E19: định vị bằng cắt bỏ ngữ cảnh.")
    parser.add_argument("command", choices=("select", "run", "report"))
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--rebuilt-interim", type=Path, help="select: ngữ cảnh E08 dựng lại")
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None, help="run: chỉ chạy N mẫu đầu")
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()
    if args.command == "select":
        args.out = args.out or SELECTION
        return cmd_select(args)
    args.out = args.out or RESULTS
    return cmd_run(args) if args.command == "run" else cmd_report(args)


if __name__ == "__main__":
    raise SystemExit(main())
