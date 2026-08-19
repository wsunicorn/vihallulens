"""Load the reading model in 4-bit NF4 on a single GPU and report the VRAM it costs.

This is task T06: it answers one question only, "does the model fit and how much room is
left", so that task T07 knows how large an attention budget it may spend. No attention
hook lives here; T07 moves this loading code into ``vihallulens.extract.AttentionExtractor``.

The settings are the ones fixed in section 3 of CLAUDE.md and section 2.2 of docs/SPEC.md:
NF4 quantisation, float16 compute, and ``attn_implementation="eager"`` because the whole
project depends on attention matrices being materialised.

Usage, on a Kaggle T4:
    python scripts/probe_load_model.py
    python scripts/probe_load_model.py --model Qwen/Qwen2.5-3B-Instruct
"""

from __future__ import annotations

import argparse
import sys
import time

MB = 1024**2
DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"

# Section 3 of docs/EXPERIMENTS.md reports VRAM in MB; T06 passes if loading stays under this.
LOAD_BUDGET_MB = 7 * 1024


def build_quantisation_config(quantization: str):
    """BitsAndBytes config for NF4, or None when quantisation is switched off."""
    import torch
    from transformers import BitsAndBytesConfig

    if quantization == "none":
        return None
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )


def load_model(model_name: str, quantization: str):
    """Load the model with eager attention, tolerating the dtype argument rename in v5.

    ``torch_dtype`` became ``dtype`` in transformers 5. Both spellings are attempted so this
    script works whichever version the Kaggle image ships.
    """
    import torch
    from transformers import AutoModelForCausalLM

    kwargs = {
        "quantization_config": build_quantisation_config(quantization),
        "attn_implementation": "eager",
        "device_map": {"": 0},
    }
    try:
        return AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16, **kwargs)
    except TypeError:
        return AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, **kwargs)


def report_environment() -> bool:
    """Print device information. Returns False when no CUDA device is available."""
    import torch

    print(f"  torch                 : {torch.__version__}")
    try:
        import transformers

        print(f"  transformers          : {transformers.__version__}")
    except ImportError:  # pragma: no cover - transformers is a hard dependency
        pass

    if not torch.cuda.is_available():
        print("  GPU                   : KHÔNG CÓ — task T06 phải chạy trên Kaggle T4")
        return False

    name = torch.cuda.get_device_name(0)
    major, minor = torch.cuda.get_device_capability(0)
    total = torch.cuda.get_device_properties(0).total_memory / MB
    print(f"  GPU                   : {name}")
    print(f"  Compute capability    : {major}.{minor}")
    print(f"  VRAM tổng             : {total:,.0f} MB")
    if major < 7 or (major == 7 and minor < 5):
        print(
            "  CẢNH BÁO: bitsandbytes NF4 khuyến nghị compute capability 7.5 trở lên.\n"
            "            Card này thấp hơn (P100 là 6.0) — xem cảnh báo ở mục 2 của CLAUDE.md."
        )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Load the reading model in 4-bit and report VRAM.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--quantization", default="nf4", choices=["nf4", "none"])
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import torch

    print()
    print("=" * 80)
    print(f"NẠP MÔ HÌNH 4-BIT — {args.model}")
    print("=" * 80)
    if not report_environment():
        return 1

    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    model = load_model(args.model, args.quantization)
    elapsed = time.perf_counter() - started

    allocated = torch.cuda.memory_allocated() / MB
    reserved = torch.cuda.memory_reserved() / MB
    peak = torch.cuda.max_memory_allocated() / MB

    config = model.config
    print()
    print(f"  Thời gian nạp         : {elapsed:,.1f} giây")
    print(f"  Lượng tử hóa          : {args.quantization}")
    print(f"  attn_implementation   : {getattr(config, '_attn_implementation', 'không rõ')}")
    print(f"  Số lớp / số đầu       : {config.num_hidden_layers} / {config.num_attention_heads}")
    print(f"  dtype tham số         : {next(model.parameters()).dtype}")
    print()
    print(f"  VRAM đang cấp phát    : {allocated:,.0f} MB")
    print(f"  VRAM đã đặt chỗ       : {reserved:,.0f} MB")
    print(f"  VRAM đỉnh khi nạp     : {peak:,.0f} MB")
    total_mb = torch.cuda.get_device_properties(0).total_memory / MB
    print(f"  VRAM còn trống        : {total_mb - reserved:,.0f} MB   ← ngân sách cho attention")

    ok = allocated < LOAD_BUDGET_MB
    print()
    print(f"  Tiêu chí T06 (< {LOAD_BUDGET_MB:,} MB): {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    if getattr(config, "_attn_implementation", None) != "eager":
        print("  CẢNH BÁO: attn_implementation không phải eager — T07 sẽ không lấy được attention.")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
