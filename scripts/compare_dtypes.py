"""Compare float16 and float32 attention extraction on the same samples.

Task T07 showed that float16 turns layer 27 of Qwen2.5-7B into nan. Two questions follow,
and neither can be answered by staring at one sample:

1. Is it always layer 27, or do other samples overflow elsewhere? Dropping one known-bad
   layer is only a plan if the bad layer is the same one every time.
2. Are the layers that stay finite in float16 actually *correct*? A layer can be finite and
   still be distorted by hidden states that are already close to overflow, and that kind of
   error is invisible without something to compare against.

The script runs both dtypes over the same samples and reports, per layer, how often float16
goes non-finite and how far it drifts from float32 where both are finite.
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

from vihallulens.data.chunking import chunk_by_sentence  # noqa: E402
from vihallulens.data.paths import find_raw_dir  # noqa: E402
from vihallulens.extract.attention import AttentionExtractor  # noqa: E402

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def spread(values: list[int], count: int) -> list[int]:
    """Indices spread evenly across a sorted order, so short and long samples both appear."""
    if len(values) <= count:
        return values
    positions = np.linspace(0, len(values) - 1, count).round().astype(int)
    return [values[position] for position in dict.fromkeys(positions)]


def collect_samples(data_dir: Path, per_dataset: int) -> list[tuple[str, str, str, str]]:
    """Samples from both corpora, spread across the context-length distribution."""
    import pandas as pd

    samples: list[tuple[str, str, str, str]] = []

    vihallu = data_dir / "vihallu_train.csv"
    if vihallu.is_file():
        frame = pd.read_csv(vihallu)
        order = frame["context"].str.split().str.len().sort_values().index.tolist()
        for position in spread(order, per_dataset):
            row = frame.loc[position]
            samples.append(
                ("vihallu", str(row["context"]), str(row["prompt"]), str(row["response"]))
            )

    isedsc = data_dir / "isedsc01_train.json"
    if isedsc.is_file():
        with isedsc.open(encoding="utf-8") as handle:
            records = list(json.load(handle).values())
        order = sorted(
            range(len(records)), key=lambda i: len(str(records[i].get("context", "")).split())
        )
        for position in spread(order, per_dataset):
            record = records[position]
            samples.append(
                ("isedsc01", str(record["context"]), "", str(record.get("claim", "")))
            )
    return samples


def extract_all(extractor, samples, dtype_name: str):
    """Run every sample through one extractor, keeping only what the comparison needs."""
    results = []
    started = time.perf_counter()
    for index, (dataset, context, question, response) in enumerate(samples, start=1):
        features = extractor.extract(context, question, response, chunk_by_sentence(context))
        results.append(
            {
                "dataset": dataset,
                "total": features.lookback_total.astype(np.float32),
                "per_chunk": features.lookback_per_chunk.astype(np.float32),
                "nonfinite": set(features.nonfinite_layers),
                "elapsed_ms": features.elapsed_ms,
                "peak_vram_mb": features.peak_vram_mb,
            }
        )
        print(f"    [{dtype_name}] {index}/{len(samples)}", end="\r")
    print(f"    [{dtype_name}] xong {len(samples)} mẫu trong {time.perf_counter() - started:.0f} s")
    return results


def per_layer_report(low, high, n_layers: int) -> None:
    """How often float16 breaks, and how far it drifts where it does not."""
    print()
    print(f"  {'Lớp':>4} | {'mẫu nan (fp16)':>15} | {'|Δ| trung bình':>15} | {'|Δ| lớn nhất':>13}")
    print(f"  {'-' * 4}-+-{'-' * 15}-+-{'-' * 15}-+-{'-' * 13}")

    worst_clean_layer, worst_clean_value = None, 0.0
    for layer in range(n_layers):
        nan_count = sum(1 for item in low if layer in item["nonfinite"])
        diffs = []
        for a, b in zip(low, high, strict=True):
            if layer in a["nonfinite"]:
                continue
            diff = np.abs(a["total"][layer] - b["total"][layer])
            if np.isfinite(diff).all():
                diffs.append(diff)
        if diffs:
            joined = np.concatenate([d.ravel() for d in diffs])
            mean_diff, max_diff = float(joined.mean()), float(joined.max())
        else:
            mean_diff = max_diff = float("nan")
        if nan_count == 0 and np.isfinite(max_diff) and max_diff > worst_clean_value:
            worst_clean_layer, worst_clean_value = layer, max_diff
        print(
            f"  {layer:>4} | {nan_count:>7}/{len(low):<7} | {mean_diff:>15.5f} | {max_diff:>13.5f}"
        )

    print()
    print(f"  Lớp lệch nhiều nhất trong số các lớp không bao giờ nan: {worst_clean_layer} "
          f"(|Δ| lớn nhất {worst_clean_value:.5f})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare float16 and float32 extraction.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--per-dataset", type=int, default=10)
    parser.add_argument("--max-context-tokens", type=int, default=4096)
    parser.add_argument("--data-dir", type=Path, default=None)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import torch

    data_dir = find_raw_dir(args.data_dir)
    samples = collect_samples(data_dir, args.per_dataset)

    print()
    print("=" * 80)
    print("SO SÁNH float16 VỚI float32")
    print("=" * 80)
    print(f"  dữ liệu   : {data_dir}")
    print(f"  số mẫu    : {len(samples)}")
    lengths = [len(context.split()) for _, context, _, _ in samples]
    print(f"  độ dài    : {min(lengths)} đến {max(lengths)} từ")

    runs = {}
    for dtype_name in ("float32", "float16"):
        extractor = AttentionExtractor(
            args.model,
            max_context_tokens=args.max_context_tokens,
            device="cuda",
            compute_dtype=dtype_name,
        )
        runs[dtype_name] = extract_all(extractor, samples, dtype_name)
        n_layers = len(extractor.layer_indices)
        del extractor
        torch.cuda.empty_cache()

    low, high = runs["float16"], runs["float32"]

    print()
    for dtype_name, results in runs.items():
        mean_ms = float(np.mean([item["elapsed_ms"] for item in results]))
        peak = max(item["peak_vram_mb"] for item in results)
        print(f"  {dtype_name:<9}: {mean_ms:>8.0f} ms mỗi mẫu, VRAM đỉnh {peak:>8.0f} MB")

    broken = sorted({layer for item in low for layer in item["nonfinite"]})
    samples_with_nan = sum(1 for item in low if item["nonfinite"])
    print()
    print(f"  Mẫu có ít nhất một lớp nan ở fp16 : {samples_with_nan}/{len(low)}")
    print(f"  Tập hợp các lớp từng nan          : {broken}")

    per_layer_report(low, high, n_layers)

    clean = [layer for layer in range(n_layers) if layer not in broken]
    diffs = []
    for a, b in zip(low, high, strict=True):
        diff = np.abs(a["total"][clean] - b["total"][clean])
        if np.isfinite(diff).all():
            diffs.append(diff.ravel())
    if diffs:
        joined = np.concatenate(diffs)
        print()
        print(f"  Nếu bỏ các lớp {broken}, còn {len(clean)} lớp:")
        print(f"    |Δ| trung bình : {joined.mean():.5f}")
        print(f"    |Δ| phân vị 99 : {np.percentile(joined, 99):.5f}")
        print(f"    |Δ| lớn nhất   : {joined.max():.5f}")
        print("    lookback_total nằm trong [0, 1] nên sai lệch 0,01 là 1 % thang đo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
