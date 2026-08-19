"""Task T07: prove the forward hook extracts attention without exhausting the GPU.

Two modes:

``--tiny``  builds a randomly initialised Qwen2 on the CPU and runs the whole pipeline on it.
            It answers the version question — does the hook receive ``attn_weights`` at all —
            in seconds and without a GPU, which is the first thing T07 must establish.

default     loads the real reading model in 4-bit and runs the two samples the task names: a
            short ViHallu sample and the longest ISE-DSC01 context. This is the run whose log
            goes into the pull request.

Usage:
    python scripts/probe_attention_hook.py --tiny
    python scripts/probe_attention_hook.py                       # on a Kaggle T4
    python scripts/probe_attention_hook.py --max-context-tokens 2048
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.attention import AttentionExtractor

MB = 1024**2
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
PEAK_BUDGET_MB = 14 * 1024  # the ceiling task T07 must stay under

# Temporary splitter, good enough to give the hook something to attribute attention to.
# Task T15 replaces it with the two real strategies from docs/SPEC.md 2.1.
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


def split_sentences(context: str) -> list[Chunk]:
    """Naive sentence split, only so T07 has chunks to work with."""
    chunks: list[Chunk] = []
    cursor = 0
    for piece in SENTENCE_END.split(context):
        if not piece.strip():
            cursor += len(piece)
            continue
        start = context.find(piece, cursor)
        chunks.append(
            Chunk(text=piece, char_start=start, char_end=start + len(piece), index=len(chunks))
        )
        cursor = start + len(piece)
    if not chunks:
        chunks.append(Chunk(text=context, char_start=0, char_end=len(context), index=0))
    return chunks


def build_tiny_extractor(model_name: str) -> AttentionExtractor:
    """A two-layer randomly initialised Qwen2 sharing the real tokenizer."""
    from transformers import AutoTokenizer, Qwen2Config, Qwen2ForCausalLM

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = Qwen2Config(
        vocab_size=len(tokenizer),
        hidden_size=64,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=4,
        num_key_value_heads=2,
        max_position_embeddings=8192,
    )
    model = Qwen2ForCausalLM(config)
    if hasattr(model, "set_attn_implementation"):
        model.set_attn_implementation("eager")
    return AttentionExtractor.from_components(model, tokenizer, max_context_tokens=8192)


def load_samples(data_dir: Path) -> list[tuple[str, str, str, str]]:
    """One short ViHallu sample and the longest ISE-DSC01 context, as task T07 requires."""
    import pandas as pd

    samples: list[tuple[str, str, str, str]] = []

    vihallu = data_dir / "vihallu_train.csv"
    if vihallu.is_file():
        frame = pd.read_csv(vihallu)
        lengths = frame["context"].str.split().str.len()
        row = frame.loc[(lengths - 200).abs().idxmin()]
        samples.append(("ViHallu (~200 từ)", row["context"], str(row["prompt"]), row["response"]))

    isedsc = data_dir / "isedsc01_train.json"
    if isedsc.is_file():
        with isedsc.open(encoding="utf-8") as handle:
            records = list(json.load(handle).values())
        longest = max(records, key=lambda record: len(str(record.get("context", "")).split()))
        samples.append(
            ("ISE-DSC01 (dài nhất)", longest["context"], "", str(longest.get("claim", "")))
        )
    return samples


def run_one(extractor: AttentionExtractor, label: str, context: str, question: str, response: str):
    chunks = split_sentences(context)
    features = extractor.extract(context, question, response, chunks)

    print(f"\n  {label}")
    print(f"    ngữ cảnh              : {len(context.split()):,} từ, {len(chunks)} chunk")
    print(f"    lookback_per_chunk    : {features.lookback_per_chunk.shape}")
    print(f"    lookback_total        : {features.lookback_total.shape}")
    print(f"    self_attention        : {features.self_attention.shape}")
    print(f"    bị cắt ngữ cảnh       : {features.truncated}")
    print(f"    thời gian             : {features.elapsed_ms:,.0f} ms")
    print(f"    VRAM đỉnh             : {features.peak_vram_mb:,.0f} MB")

    values = features.lookback_total.astype("float32")
    print(f"    lookback_total trung bình: {values.mean():.4f}  (min {values.min():.4f}, "
          f"max {values.max():.4f})")
    if not (values.min() >= 0.0 and values.max() <= 1.0001):
        print("    CẢNH BÁO: lookback_total nằm ngoài [0, 1] — công thức sai ở đâu đó.")
    return features


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove the attention hook works and fits in VRAM.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--tiny", action="store_true", help="random small model on the CPU")
    parser.add_argument("--max-context-tokens", type=int, default=4096)
    parser.add_argument("--data-dir", type=Path, default=None)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import transformers

    print()
    print("=" * 80)
    print("T07 — TRÍCH ATTENTION BẰNG FORWARD HOOK")
    print("=" * 80)
    print(f"  transformers          : {transformers.__version__}")
    mode = "tiny (CPU, trọng số ngẫu nhiên)" if args.tiny else args.model
    print(f"  chế độ                : {mode}")

    if args.tiny:
        extractor = build_tiny_extractor(args.model)
        samples = [
            (
                "mẫu tổng hợp",
                "Việt Nam có diện tích 331.212 km2. Thủ đô là Hà Nội. "
                "Thành phố đông dân nhất là Thành phố Hồ Chí Minh.",
                "Thủ đô của Việt Nam là gì?",
                "Thủ đô của Việt Nam là Hà Nội.",
            )
        ]
    else:
        from vihallulens.data.paths import find_raw_dir

        try:
            data_dir = find_raw_dir(args.data_dir)
        except FileNotFoundError as error:
            print(f"  {error}")
            return 1
        print(f"  thư mục dữ liệu       : {data_dir}")

        extractor = AttentionExtractor(
            args.model, max_context_tokens=args.max_context_tokens, device="cuda"
        )
        samples = load_samples(data_dir)
        if not samples:
            print(f"  KHÔNG thấy file dữ liệu nào trong {data_dir}.")
            return 1

    print(f"  số lớp được hook      : {len(extractor.layer_indices)}")

    for label, context, question, response in samples:
        run_one(extractor, label, context, question, response)

    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / MB
        print()
        print(f"  VRAM đỉnh toàn phiên  : {peak:,.0f} MB")
        verdict = "ĐẠT" if peak < PEAK_BUDGET_MB else "KHÔNG ĐẠT"
        print(f"  Tiêu chí T07 (< {PEAK_BUDGET_MB:,} MB): {verdict}")
        return 0 if peak < PEAK_BUDGET_MB else 1

    print("\n  Chạy trên CPU nên không có số VRAM. Tiêu chí 14 GB phải đo trên Kaggle T4.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
