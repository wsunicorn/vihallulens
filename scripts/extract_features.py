"""Task T20: run the reading model over a split and save the lookback features.

This is the first script in the project that needs the GPU for real work rather than for a
probe. It reads an experiment declaration from ``configs/``, runs one teacher-forcing pass per
sample, and writes the pooled per-head lookback vectors to ``data/processed/``.

    python scripts/extract_features.py --config configs/e02_lookback_vihallu.yaml --split test

Measured at T08: about 1,05 ms per prompt token on a T4, so ViHallu costs roughly 420 ms a
sample and the whole 7.000 take about 50 minutes.

**Resumable, on purpose.** Fifty minutes is long enough to lose to a dropped session, a quota
limit or a stray Ctrl-C, and re-running from scratch would spend the whole budget again. Every
sample is appended to a shard the moment it is computed, and a re-run skips what is already
there — the same reasoning as the judge cache of T19, for the same reason.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.data.chunking import chunk_context  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.features.chunk_aware import (  # noqa: E402
    CHUNK_FEATURE_NAMES,
    chunk_features,
)
from vihallulens.features.lookback import DENOMINATORS, pool_over_tokens  # noqa: E402

DEFAULT_PROCESSED_DIR = Path("data/processed")
PROGRESS_EVERY = 25

# Every column family one pass writes. Both are computed from the same attention matrix, so
# splitting them into two runs would pay for the reading model twice to learn nothing new.
FEATURE_BLOCKS = tuple(f"lookback_{name}" for name in DENOMINATORS) + CHUNK_FEATURE_NAMES


def shard_path(processed_dir: Path, run: str, dataset: str, split: str) -> Path:
    """One file per (extraction, dataset, split).

    ``run`` is the *extraction* hash, not the whole config: features extracted with a different
    reading model, token budget or chunking are different features, but two experiments that
    differ only in which of those features they feed to the classifier share one extraction.
    Hashing the whole config would spend fifty minutes of GPU again for E03 after E02, for a
    difference the GPU never sees.
    """
    return processed_dir / f"{dataset}_{split}_{run}.jsonl"


def chunking_arguments(chunking, tokenizer) -> dict:
    """Everything :func:`chunk_context` needs, read off the config.

    Written as its own function because of the bug it exists to prevent. Until T23 the caller
    passed only ``strategy`` and ``min_words``, which is all the sentence strategy wants — so
    E02 and E03 ran fine and nothing looked wrong. ``token_window`` needs a tokenizer and a
    window, and without them it raises on the very first sample: a failure that would have cost
    a whole Kaggle session to discover, at the far end of a fifty-minute model load.

    ``chunk_context`` takes ``**kwargs`` and ignores what a strategy does not use, so a missing
    key is silently accepted rather than refused. That is why the mapping lives here, in one
    place a CPU test can check, instead of being spelled out at the call site.
    """
    if chunking.strategy == "token_window":
        return {
            "strategy": "token_window",
            "tokenizer": tokenizer,
            "window_size": chunking.window_size,
            "stride": chunking.stride,
        }
    return {"strategy": chunking.strategy, "min_words": chunking.min_words}


def load_done(path: Path) -> dict[str, dict]:
    """Read back what a previous run already computed, tolerating a truncated last line."""
    done: dict[str, dict] = {}
    if not path.exists():
        return done
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"  bỏ qua dòng hỏng {number} trong {path.name}")
                continue
            done[record["sample_id"]] = record
    return done


def to_record(sample_id: str, label: str, features, elapsed_ms: float) -> dict:
    """One sample's row: the pooled vectors plus everything needed to audit them later.

    Both families are written in one pass. The chunk-aware statistics are computed from the same
    attention matrix as the lookback ratio, so extracting them separately would pay for the
    reading model twice to learn nothing new.
    """
    row = {
        "sample_id": sample_id,
        "label": label,
        "n_chunks": int(features.n_chunks),
        "truncated": bool(features.truncated),
        "n_scored_tokens": int(features.lookback_total.shape[2]),
        "layer_indices": list(features.layer_indices),
        "nonfinite_layers": list(features.nonfinite_layers),
        "row_sum_mean": float(features.row_sum_mean),
        "peak_vram_mb": float(features.peak_vram_mb),
        "elapsed_ms": float(elapsed_ms),
    }
    for name in DENOMINATORS:
        pooled = pool_over_tokens(getattr(features, f"lookback_{name}"))
        row[f"lookback_{name}"] = [round(float(value), 6) for value in pooled.reshape(-1)]
    for name, value in chunk_features(features.lookback_per_chunk).items():
        row[name] = [round(float(item), 6) for item in value.reshape(-1)]
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description="T20: trích đặc trưng lookback cho E02.")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--split", default="test", choices=("train", "dev", "test"))
    parser.add_argument("--limit", type=int, default=None, help="chỉ chạy N mẫu đầu, để thử")
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--processed-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    cfg = load_config(args.config)
    run = extraction_hash(cfg)
    frame = load_dataset(cfg.dataset.name, args.split, args.interim_dir)
    if args.limit:
        frame = frame.head(args.limit)

    args.processed_dir.mkdir(parents=True, exist_ok=True)
    path = shard_path(args.processed_dir, run, cfg.dataset.name, args.split)
    done = load_done(path)

    print()
    print("=" * 80)
    print("T20 — TRÍCH ĐẶC TRƯNG LOOKBACK")
    print("=" * 80)
    print(f"  cấu hình              : {args.config}  (hash {run})")
    print(f"  mô hình đọc           : {cfg.extractor.model_name}")
    print(f"  lượng tử hóa / kiểu số: {cfg.extractor.quantization} / "
          f"{cfg.extractor.compute_dtype}")
    print(f"  bỏ lớp                : {cfg.extractor.exclude_layers or 'không bỏ lớp nào'}")
    print(f"  trần token ngữ cảnh   : {cfg.extractor.max_context_tokens:,}")
    cutting = cfg.chunking.strategy
    if cfg.chunking.window_size:
        cutting += f", cửa sổ {cfg.chunking.window_size} bước {cfg.chunking.stride}"
    print(f"  chia đoạn             : {cutting}")
    print(f"  bộ dữ liệu            : {cfg.dataset.name}/{args.split}, {len(frame):,} mẫu")
    print(f"  khối đặc trưng ghi ra : {', '.join(FEATURE_BLOCKS)}")
    print(f"  đã có sẵn             : {len(done):,} mẫu trong {path.name}")

    todo = [row for row in frame.to_dict("records") if row["sample_id"] not in done]
    if not todo:
        print("  Không còn mẫu nào phải chạy.")
        return 0
    print(f"  còn phải chạy         : {len(todo):,} mẫu")

    from vihallulens.extract.attention import AttentionExtractor

    extractor = AttentionExtractor(
        model_name=cfg.extractor.model_name,
        quantization=cfg.extractor.quantization,
        max_context_tokens=cfg.extractor.max_context_tokens,
        device=cfg.extractor.device,
        exclude_layers=cfg.extractor.exclude_layers,
        compute_dtype=cfg.extractor.compute_dtype,
    )
    # After the extractor, because token_window chunks are cut with the reading model's own
    # tokenizer: the windows are meant to line up with attention positions, and those are the
    # positions this tokenizer produces.
    chunking_kwargs = chunking_arguments(cfg.chunking, extractor.tokenizer)

    started = time.perf_counter()
    written, failed, truncated, nonfinite = 0, 0, 0, 0
    first_error = None
    with path.open("a", encoding="utf-8") as handle:
        for position, row in enumerate(todo, start=1):
            chunks = chunk_context(row["context"], **chunking_kwargs)
            began = time.perf_counter()
            try:
                features = extractor.extract(
                    row["context"], row.get("question", ""), row["response"], chunks
                )
            except Exception as error:  # noqa: BLE001 — one bad sample must not end the run
                failed += 1
                if first_error is None:
                    first_error = f"{row['sample_id']}: {type(error).__name__}: {error}"
                    print(f"\n  LỖI ĐẦU TIÊN — {first_error}")
                continue

            record = to_record(row["sample_id"], row["label"], features,
                               (time.perf_counter() - began) * 1000)
            # Written immediately, not at the end: a run killed at minute forty keeps the forty
            # minutes it already paid for.
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            written += 1
            truncated += int(record["truncated"])
            nonfinite += int(bool(record["nonfinite_layers"]))

            if position % PROGRESS_EVERY == 0 or position == len(todo):
                rate = (time.perf_counter() - started) / position
                left = rate * (len(todo) - position) / 60
                print(f"      {position:>5}/{len(todo)}  {rate * 1000:,.0f} ms/mẫu  "
                      f"còn ~{left:.0f} phút  lỗi {failed}", end="\r")
    print()

    elapsed = time.perf_counter() - started
    print()
    print("-" * 80)
    print(f"  đã ghi thêm           : {written:,} mẫu, tổng {len(done) + written:,}")
    print(f"  lỗi                   : {failed:,}")
    print(f"  bị cắt ngữ cảnh       : {truncated:,}/{written:,}")
    print(f"  có lớp tràn số        : {nonfinite:,}/{written:,}")
    print(f"  thời gian             : {elapsed / 60:.1f} phút, "
          f"{elapsed * 1000 / max(written, 1):,.0f} ms/mẫu")
    print(f"  file                  : {path}")
    if failed:
        print()
        print("  Có mẫu hỏng. Chạy lại đúng lệnh này sẽ thử lại chúng và bỏ qua phần đã xong.")
    return 1 if failed and not written else 0


def load_matrix(path: Path, denominator: str = "total"):
    """Read a shard back as a feature matrix, its labels and its sample ids.

    Rows come out sorted by ``sample_id`` rather than in the order they were written, so a run
    that was interrupted and resumed gives the same matrix as one that ran straight through.
    """
    records = sorted(load_done(path).values(), key=lambda record: record["sample_id"])
    if not records:
        raise ValueError(f"không có mẫu nào trong {path}")
    key = f"lookback_{denominator}"
    widths = {len(record[key]) for record in records}
    if len(widths) > 1:
        raise ValueError(f"số chiều đặc trưng không đồng nhất: {sorted(widths)}")
    matrix = np.asarray([record[key] for record in records], dtype=np.float32)
    labels = np.asarray([record["label"] for record in records])
    ids = [record["sample_id"] for record in records]
    return matrix, labels, ids, records


if __name__ == "__main__":
    raise SystemExit(main())
