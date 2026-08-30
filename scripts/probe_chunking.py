"""Task T23: how many chunks each cutting strategy actually produces, measured on CPU.

    python scripts/probe_chunking.py --dataset vihallu

Run this **before** spending GPU on E04. A chunk-aware feature is a statistic over the per-chunk
attention vector, so its whole information content is bounded by how many chunks there are: with
one chunk, entropy is 0, max-share is 1 and the drift is 0 no matter what the model did. A window
larger than the contexts therefore turns the thesis's five features into five constants, and the
experiment measures nothing — a result worth knowing for the price of a minute on CPU rather than
an hour on a T4.

The numbers this prints are quoted in the header comments of ``configs/e04_*.yaml`` and in
Bảng 3 of docs/EXPERIMENTS.md, so it is the source they have to be regenerated from.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.data.chunking import chunk_context  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402

# The sweep E05 fixes, plus the sentence strategy E03 already ran, so the comparison is on one
# page. Sentence chunking tiles the context; the windows overlap by half.
STRATEGIES: tuple[tuple[str, dict], ...] = (
    ("câu, min_words=5", {"strategy": "sentence", "min_words": 5}),
    ("cửa sổ 64, bước 32", {"strategy": "token_window", "window_size": 64, "stride": 32}),
    ("cửa sổ 128, bước 64", {"strategy": "token_window", "window_size": 128, "stride": 64}),
    ("cửa sổ 256, bước 128", {"strategy": "token_window", "window_size": 256, "stride": 128}),
)

DEFAULT_TOKENIZER = "Qwen/Qwen2.5-7B-Instruct"


def chunk_counts(contexts, tokenizer, **kwargs) -> np.ndarray:
    return np.asarray(
        [len(chunk_context(text, tokenizer=tokenizer, **kwargs)) for text in contexts]
    )


def describe(counts: np.ndarray) -> dict[str, float]:
    """The five numbers that decide whether a cutting is worth a GPU pass.

    ``một đoạn`` is the one that matters most: it is the share of the dataset on which the
    chunk-aware features carry no information at all.
    """
    return {
        "trung bình": float(counts.mean()),
        "trung vị": float(np.median(counts)),
        "p95": float(np.percentile(counts, 95)),
        "lớn nhất": float(counts.max()),
        "một đoạn": float((counts == 1).mean()),
        "≤ hai đoạn": float((counts <= 2).mean()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="T23: đếm số đoạn theo từng cách chia.")
    parser.add_argument("--dataset", default="vihallu")
    parser.add_argument("--splits", nargs="+", default=["train", "dev", "test"])
    parser.add_argument("--tokenizer", default=DEFAULT_TOKENIZER)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    contexts = [
        text
        for split in args.splits
        for text in load_dataset(args.dataset, split, args.interim_dir)["context"]
    ]

    lengths = np.asarray([len(tokenizer(t, add_special_tokens=False)["input_ids"])
                          for t in contexts])
    print()
    print("=" * 84)
    print(f"T23 — SỐ ĐOẠN THEO TỪNG CÁCH CHIA · {args.dataset} · {len(contexts):,} ngữ cảnh")
    print("=" * 84)
    print(f"  độ dài ngữ cảnh (token, {args.tokenizer}): trung bình {lengths.mean():.0f}, "
          f"trung vị {np.median(lengths):.0f}, p95 {np.percentile(lengths, 95):.0f}, "
          f"lớn nhất {lengths.max():,}")
    print()
    print(f"  {'cách chia':<24}{'TB':>7}{'trung vị':>10}{'p95':>7}{'max':>7}"
          f"{'1 đoạn':>10}{'≤2 đoạn':>10}")
    print("  " + "-" * 75)
    for name, kwargs in STRATEGIES:
        stats = describe(chunk_counts(contexts, tokenizer, **kwargs))
        print(f"  {name:<24}{stats['trung bình']:>7.1f}{stats['trung vị']:>10.0f}"
              f"{stats['p95']:>7.0f}{stats['lớn nhất']:>7.0f}"
              f"{stats['một đoạn']:>9.1%}{stats['≤ hai đoạn']:>10.1%}")
    print()
    print("  Cột '1 đoạn' là phần dữ liệu mà năm đặc trưng hình dạng thành hằng số")
    print("  (0, 1, 0, 1, 0) — ở đó chunk-aware không nói được gì hơn lookback gộp.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
