"""Is this checkpoint fit to fine-tune, and does it behave like the one beside it?

Written at T18 after InfoXLM-large refused to train at three learning rates while XLM-R-large,
the same size with the same config, trained fine. Answering "why" meant checking four things by
hand; this script does all four on a CPU in a couple of minutes, so the next model swap — the
Sailor2 ablation of E13, or a step down the fallback ladder — costs no GPU quota to vet.

    python scripts/check_checkpoint.py microsoft/infoxlm-large FacebookAI/xlm-roberta-large

What it reports, and what a bad answer looks like:

1. Weight loading. Body weights missing from the checkpoint means part of the network is a
   random draw wearing a famous name.
2. Activation range. float16 tops out at 65.504 and the T4 has no bfloat16, so a model whose
   activations run hot has nowhere to go. This is what cost T07 a run.
3. Spread of the pooled vector across samples. The classification head reads one vector per
   sample; if that vector barely changes between samples, the head has nothing to learn from.
4. Config. Printed side by side when more than one checkpoint is given.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.detect.encoder import build_pairs  # noqa: E402
from vihallulens.detect.loading_report import describe  # noqa: E402
from vihallulens.evaluation.metrics import LABELS  # noqa: E402

FP16_MAX = 65504.0
DEFAULT_SAMPLES = 16


def cosine_spread(vectors) -> float:
    """Average cosine distance between distinct samples.

    Zero means every input maps to the same direction. Pretrained transformers are famously
    anisotropic so the number is small for all of them; it is the comparison between two models
    that carries information, not the absolute value.
    """
    unit = torch.nn.functional.normalize(vectors, dim=-1)
    similarity = unit @ unit.T
    off_diagonal = similarity[~torch.eye(len(vectors), dtype=bool)]
    return 1.0 - float(off_diagonal.mean())


def inspect(name: str, left, right, max_length: int) -> dict:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(name)
    model, info = AutoModelForSequenceClassification.from_pretrained(
        name, num_labels=len(LABELS), output_loading_info=True
    )
    ok, message = describe(info)
    model.eval()

    batch = tokenizer(left, right, truncation=True, max_length=max_length,
                      padding="max_length", return_tensors="pt")
    with torch.no_grad():
        out = model(**batch, output_hidden_states=True)

    peaks = [float(state.abs().max()) for state in out.hidden_states]
    hottest = max(range(len(peaks)), key=lambda index: peaks[index])
    last = out.hidden_states[-1]
    result = {
        "load_ok": ok,
        "load_message": message,
        "peak_activation": peaks[hottest],
        "peak_layer": hottest,
        "n_layers": len(peaks) - 1,
        "cls_spread": cosine_spread(last[:, 0]),
        "cls_norm": float(last[:, 0].norm(dim=-1).mean()),
        "mean_spread": cosine_spread(last.mean(dim=1)),
        "logit_range": float(out.logits.abs().max()),
    }
    del model
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Soi một checkpoint trước khi tốn quota GPU.")
    parser.add_argument("names", nargs="+", help="tên trên HuggingFace Hub")
    parser.add_argument("--dataset", default="vihallu")
    parser.add_argument("--split", default="test")
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    frame = load_dataset(args.dataset, args.split, args.interim_dir).head(args.samples)
    left, right = build_pairs(frame, segment=False)

    print()
    print("=" * 80)
    print("SOI CHECKPOINT")
    print("=" * 80)
    print(f"  dữ liệu thử   : {args.dataset}/{args.split}, {len(frame)} mẫu đầu")
    print(f"  độ dài tối đa : {args.max_length} token")

    findings = {}
    for name in args.names:
        print(f"\n  --- {name} ---")
        found = inspect(name, left, right, args.max_length)
        findings[name] = found
        flag = "" if found["load_ok"] else "   *** DỪNG LẠI ***"
        print(f"  nạp trọng số     : {found['load_message']}{flag}")
        share = found["peak_activation"] / FP16_MAX * 100
        print(f"  đỉnh activation  : {found['peak_activation']:,.1f} ở lớp "
              f"{found['peak_layer']}/{found['n_layers']} — {share:.2f} % trần float16")
        print(f"  vector CLS       : giãn cách {found['cls_spread']:.4f}, "
              f"độ dài {found['cls_norm']:.1f}")
        print(f"  nếu gộp trung bình: giãn cách {found['mean_spread']:.4f}")

    print()
    print("-" * 80)
    print("ĐỌC THẾ NÀO")
    print("-" * 80)
    print("  nạp trọng số     : thiếu trọng số THÂN là hỏng; thiếu đầu phân loại là bình thường")
    print(f"  đỉnh activation  : quá {FP16_MAX * 0.5:,.0f} thì float16 trên T4 rất rủi ro")
    print("  giãn cách CLS    : nhỏ hơn hẳn mô hình đối chứng nghĩa là đầu phân loại gần như")
    print("                     nhận cùng một vector cho mọi mẫu, không có gì để học")

    bad = [name for name, found in findings.items() if not found["load_ok"]]
    if bad:
        print()
        print(f"  KHÔNG DÙNG ĐƯỢC: {bad}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
