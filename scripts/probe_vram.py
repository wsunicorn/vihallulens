"""Estimate the attention-memory budget and measure Vietnamese token lengths.

Two questions are answered here, both without a GPU:

1. How much memory does one layer's attention matrix take at a given sequence length, and
   how much would keeping every layer take? This is the arithmetic behind section 5 of
   CLAUDE.md and the reason the hook design in T07 is required.
2. How many tokens does a Vietnamese context actually become? Every dataset figure in
   docs/DATA.md is counted in words while the memory budget is counted in tokens, so the
   conversion rate decides how many samples ``max_context_tokens`` truncates.

Usage:
    python scripts/probe_vram.py
    python scripts/probe_vram.py --model Qwen/Qwen2.5-3B-Instruct --seq-len 2048 4096
    python scripts/probe_vram.py --skip-token-stats     # no tokenizer download
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Run against the checkout, not whatever an editable install may or may not have registered.
# See the note in scripts/probe_env.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

BYTES_PER_FP16 = 2
BYTES_PER_NF4 = 0.5
GB = 1000**3  # decimal GB, to match the table in section 5 of CLAUDE.md
VRAM_LIMIT_GB = 16
HEADROOM_GB = 14  # the ceiling task T07 must stay under

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_SEQ_LENS = (1024, 2048, 4096, 8192)
TRUNCATION_THRESHOLDS = (2048, 4096)

# Raw files carrying labels, per section 2 of docs/DATA.md. The three unlabelled test files
# are skipped: the project never uses them.
RAW_SOURCES = {
    "vihallu": ("vihallu_train.csv", "context", "prompt", "response"),
    "isedsc01": ("isedsc01_train.json", "context", None, "claim"),
    "viwikifc": ("viwikifc_train.csv", "context", None, "claim"),
    "vifactcheck": ("vifactcheck_train.parquet", "Context", None, "Statement"),
}


# ---------------------------------------------------------------------------------------
# 1. Memory budget
# ---------------------------------------------------------------------------------------


def model_shape(model_name: str) -> dict[str, int]:
    """Read layer and head counts from the model config; downloads a few KB of JSON only."""
    from transformers import AutoConfig

    cfg = AutoConfig.from_pretrained(model_name)
    hidden = cfg.hidden_size
    n_heads = cfg.num_attention_heads
    return {
        "n_layers": cfg.num_hidden_layers,
        "n_heads": n_heads,
        "n_kv_heads": getattr(cfg, "num_key_value_heads", n_heads) or n_heads,
        "hidden_size": hidden,
        "intermediate_size": cfg.intermediate_size,
        "vocab_size": cfg.vocab_size,
        "head_dim": getattr(cfg, "head_dim", None) or hidden // n_heads,
        "tied_embeddings": bool(getattr(cfg, "tie_word_embeddings", False)),
    }


def parameter_counts(shape: dict[str, int]) -> dict[str, int]:
    """Split the parameter count into the part bitsandbytes quantises and the part it leaves.

    bitsandbytes replaces ``nn.Linear`` layers only. Embeddings, the language-model head and
    the norms stay in fp16, which is why a 7B model does not weigh 7B x 0.5 bytes.
    """
    hidden = shape["hidden_size"]
    inter = shape["intermediate_size"]
    kv_dim = shape["n_kv_heads"] * shape["head_dim"]
    q_dim = shape["n_heads"] * shape["head_dim"]

    per_layer_linear = (
        hidden * q_dim  # q_proj
        + hidden * kv_dim  # k_proj
        + hidden * kv_dim  # v_proj
        + q_dim * hidden  # o_proj
        + hidden * inter  # gate_proj
        + hidden * inter  # up_proj
        + inter * hidden  # down_proj
    )
    per_layer_other = q_dim + 2 * kv_dim + 2 * hidden  # qkv biases plus two RMSNorms

    quantised = per_layer_linear * shape["n_layers"]
    embedding = shape["vocab_size"] * hidden
    kept_fp16 = embedding + per_layer_other * shape["n_layers"] + hidden
    if not shape["tied_embeddings"]:
        kept_fp16 += embedding  # separate lm_head, which bitsandbytes skips by default

    return {"quantised": quantised, "kept_fp16": kept_fp16, "total": quantised + kept_fp16}


def weight_bytes(counts: dict[str, int]) -> dict[str, float]:
    """Weight footprint in bytes, before and after 4-bit quantisation."""
    return {
        "fp16": counts["total"] * BYTES_PER_FP16,
        "nf4": counts["quantised"] * BYTES_PER_NF4 + counts["kept_fp16"] * BYTES_PER_FP16,
    }


def attention_matrix_bytes(n_heads: int, seq_len: int) -> float:
    """One layer's attention matrix in fp16: n_heads x seq_len^2 x 2 bytes."""
    return n_heads * seq_len * seq_len * BYTES_PER_FP16


def print_memory_report(model_name: str, shape: dict, seq_lens: list[int]) -> None:
    counts = parameter_counts(shape)
    weights = weight_bytes(counts)
    n_layers = shape["n_layers"]

    print()
    print("=" * 80)
    print(f"NGÂN SÁCH BỘ NHỚ — {model_name}")
    print("=" * 80)
    print(f"  Số lớp                : {n_layers}")
    print(f"  Số đầu chú ý          : {shape['n_heads']}  (KV heads: {shape['n_kv_heads']})")
    print(f"  hidden_size           : {shape['hidden_size']}")
    print(f"  Tổng tham số          : {counts['total'] / 1e9:.2f} B")
    print(f"    lượng tử hóa được   : {counts['quantised'] / 1e9:.2f} B  (nn.Linear → NF4)")
    print(f"    giữ fp16            : {counts['kept_fp16'] / 1e9:.2f} B  (embedding, head, norm)")
    print(f"  Trọng số fp16         : {weights['fp16'] / GB:.2f} GB")
    print(f"  Trọng số sau NF4      : {weights['nf4'] / GB:.2f} GB   ← mức nạp lên GPU")
    print()

    label = f"Cả {n_layers} lớp"
    print(
        f"  {'Độ dài chuỗi':>13} | {'Một lớp':>9} | {label:>11} | "
        f"{'Đỉnh ước tính':>13} | Kết luận"
    )
    print(f"  {'-' * 13}-+-{'-' * 9}-+-{'-' * 11}-+-{'-' * 13}-+-{'-' * 24}")
    for seq_len in seq_lens:
        one = attention_matrix_bytes(shape["n_heads"], seq_len)
        every = one * n_layers
        peak = weights["nf4"] + one
        verdict = "vừa, nhờ hook" if peak < HEADROOM_GB * GB else "TRÀN dù có hook"
        if every >= HEADROOM_GB * GB:
            verdict += " / ngây thơ: TRÀN"
        print(
            f"  {seq_len:>13,} | {one / GB:>6.2f} GB | {every / GB:>8.2f} GB | "
            f"{peak / GB:>10.2f} GB | {verdict}"
        )

    print()
    print("  Cột 'một lớp' là mức thiết kế hook giữ lại; cột 'cả N lớp' là hậu quả của")
    print("  output_attentions=True dùng ngây thơ. 'Đỉnh ước tính' = trọng số + một lớp, chưa")
    print("  kể bản sao tạm khi softmax, KV cache và activation, nên cộng thêm khoảng 2–3 GB.")
    print(f"  Ngưỡng an toàn đặt ở {HEADROOM_GB} GB trên card {VRAM_LIMIT_GB} GB.")


# ---------------------------------------------------------------------------------------
# 2. Token length of Vietnamese text
# ---------------------------------------------------------------------------------------


def load_raw(data_dir: Path, name: str) -> list[dict[str, str]]:
    """Minimal reader for one labelled raw file. Tasks T09-T12 replace this with real loaders."""
    import pandas as pd

    filename, ctx_col, q_col, resp_col = RAW_SOURCES[name]
    path = data_dir / filename
    if not path.is_file():
        return []

    if path.suffix == ".csv":
        frame = pd.read_csv(path)
    elif path.suffix == ".parquet":
        frame = pd.read_parquet(path)
    else:
        with path.open(encoding="utf-8") as handle:
            frame = pd.DataFrame(list(json.load(handle).values()))

    rows = []
    for record in frame.to_dict("records"):
        rows.append(
            {
                "context": str(record.get(ctx_col) or ""),
                "question": str(record.get(q_col) or "") if q_col else "",
                "response": str(record.get(resp_col) or ""),
            }
        )
    return rows


def _token_lengths(tokenizer, texts: list[str], batch: int = 512) -> list[int]:
    """Token count of each text, batched so a long corpus does not build one huge list."""
    lengths: list[int] = []
    for start in range(0, len(texts), batch):
        encoded = tokenizer(texts[start : start + batch], add_special_tokens=False)
        lengths.extend(len(ids) for ids in encoded["input_ids"])
    return lengths


def token_stats(tokenizer, rows: list[dict[str, str]]) -> dict[str, float]:
    """Token statistics over samples, tokenising each distinct context only once."""
    import numpy as np

    contexts = sorted({row["context"] for row in rows})
    ctx_lengths = dict(zip(contexts, _token_lengths(tokenizer, contexts), strict=True))

    others = [f"{row['question']} {row['response']}".strip() for row in rows]
    other_lengths = np.array(_token_lengths(tokenizer, others), dtype=float)

    per_sample_ctx = np.array([ctx_lengths[row["context"]] for row in rows], dtype=float)
    total = per_sample_ctx + other_lengths
    words = np.array([len(row["context"].split()) for row in rows], dtype=float)

    stats = {
        "n_samples": len(rows),
        "n_unique_contexts": len(contexts),
        "tokens_per_word": float(per_sample_ctx.sum() / max(words.sum(), 1.0)),
        "ctx_p50": float(np.percentile(per_sample_ctx, 50)),
        "ctx_p90": float(np.percentile(per_sample_ctx, 90)),
        "ctx_p99": float(np.percentile(per_sample_ctx, 99)),
        "ctx_max": float(per_sample_ctx.max()),
        "total_p50": float(np.percentile(total, 50)),
        "total_p99": float(np.percentile(total, 99)),
        "total_max": float(total.max()),
    }
    for threshold in TRUNCATION_THRESHOLDS:
        stats[f"over_{threshold}"] = float((total > threshold).mean() * 100)
        stats[f"n_over_{threshold}"] = int((total > threshold).sum())
    return stats


def print_token_report(model_name: str, results: dict[str, dict[str, float]]) -> None:
    print()
    print("=" * 80)
    print(f"ĐỘ DÀI TOKEN — tokenizer của {model_name}")
    print("=" * 80)
    print("  Ngữ cảnh, tính trên từng mẫu:")
    print()
    print(
        f"  {'Bộ':<12} {'Mẫu':>7} {'Ngữ cảnh':>9} {'tok/từ':>7} "
        f"{'p50':>6} {'p90':>6} {'p99':>7} {'max':>7}"
    )
    print("  " + "-" * 66)
    for name, stats in results.items():
        print(
            f"  {name:<12} {stats['n_samples']:>7,} {stats['n_unique_contexts']:>9,} "
            f"{stats['tokens_per_word']:>7.2f} {stats['ctx_p50']:>6.0f} "
            f"{stats['ctx_p90']:>6.0f} {stats['ctx_p99']:>7.0f} {stats['ctx_max']:>7.0f}"
        )

    print()
    print("  Ngữ cảnh + câu hỏi + phản hồi, và tỷ lệ mẫu bị cắt theo max_context_tokens")
    print("  (chưa kể phần khung của mẫu prompt sẽ chốt ở T07):")
    print()
    print(
        f"  {'Bộ':<12} {'p50':>7} {'p99':>7} {'max':>8} "
        f"{'vượt 2.048':>18} {'vượt 4.096':>18}"
    )
    print("  " + "-" * 76)
    for name, stats in results.items():
        over_2k = f"{stats['n_over_2048']:,} ({stats['over_2048']:.2f}%)"
        over_4k = f"{stats['n_over_4096']:,} ({stats['over_4096']:.2f}%)"
        print(
            f"  {name:<12} {stats['total_p50']:>7.0f} {stats['total_p99']:>7.0f} "
            f"{stats['total_max']:>8.0f} {over_2k:>18} {over_4k:>18}"
        )


# ---------------------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate attention memory and token lengths.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--seq-len", type=int, nargs="+", default=list(DEFAULT_SEQ_LENS))
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--skip-token-stats", action="store_true")
    args = parser.parse_args()

    # The report is Vietnamese; force UTF-8 so a cp1252 console does not crash on the accents.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    shape = model_shape(args.model)
    print_memory_report(args.model, shape, args.seq_len)

    if args.skip_token_stats:
        return

    from transformers import AutoTokenizer

    from vihallulens.data.paths import find_raw_dir

    try:
        data_dir = find_raw_dir(args.data_dir)
    except FileNotFoundError as error:
        print(f"\n  Bỏ qua phần đo token: {error}")
        return
    print(f"\n  Thư mục dữ liệu       : {data_dir}")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    results = {}
    for name in RAW_SOURCES:
        rows = load_raw(data_dir, name)
        if not rows:
            print(f"  [bỏ qua] không thấy file của {name} trong {data_dir}")
            continue
        results[name] = token_stats(tokenizer, rows)
    if results:
        print_token_report(args.model, results)


if __name__ == "__main__":
    main()
