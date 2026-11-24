"""What detection costs when the generating model is also the reading model (E11, self-check).

Table 6.14 prices the detector as a separate reading pass, because the reader and the generator
of the demo are two models. The thesis argues that in a self-check deployment only the hook would
be extra, but that was never measured: Qwen2.5-7B overflows in float16 and cannot generate on a
T4. Qwen2.5-3B has no overflowing layer, so it can play both parts on the same card.

Each sample is answered once, freely, and that answer is then *replayed* under four arms so that
every arm does the same amount of work:

    A  sdpa, no hook                what generation costs today
    B  eager, no hook               the price of switching the optimised attention off
    C  eager, hook while decoding   the price of reading the attention as well
    R  eager, hook, one teacher-forcing pass over the finished answer (no generation)

    C - B  the detection itself      B - A  giving up sdpa      C - A  everything extra
    R      the extra cost when the attention is read in a second pass instead (A + R)

Every arm is run twice per sample, the second time in the opposite order, and the order rotates
between samples, so a card that slows down during the session slows every arm equally.

Only cost is measured. The generated answers have no labels, so nothing here says how accurate
the detector is on them. Predictions are written below, before the run.

Usage:
    python scripts/measure_self_check.py run --out /kaggle/working/e11_self_check.jsonl
    python scripts/measure_self_check.py report --path results/e11_self_check.jsonl
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from functools import partial
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import REQUIRED_SPLIT_SEED  # noqa: E402
from vihallulens.data.chunking import chunk_by_sentence  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.features.chunk_aware import chunk_features  # noqa: E402

DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"
DEFAULT_SAMPLES = 100
MAX_NEW_TOKENS = 160
MAX_PROMPT_TOKENS = 4096
N_WARMUP = 3
ARMS = ("A", "B", "C", "R")
IMPLEMENTATION = {"A": "sdpa", "B": "eager", "C": "eager", "R": "eager"}
BOOTSTRAP_ROUNDS = 2000
MB = 1024**2

# Written before the run. ``report`` prints what came out next to each of them.
PREDICTIONS = {
    "hook_share": "C − B dưới 10 % thời gian sinh A",
    "eager_costs": "B − A dương: tắt sdpa làm sinh chậm hơn",
    "cheaper_than_reread": "C − A nhỏ hơn R: đọc khi sinh ít tốn hơn đọc lại một lượt",
    "same_features": "|Δ| trung bình của lookback_total giữa C và R dưới 0,01",
}


def pick_samples(frame, n: int, seed: int = REQUIRED_SPLIT_SEED):
    """``n`` rows with a question, one per context, independent of row order."""
    frame = frame[frame["question"].fillna("").str.strip() != ""]
    frame = frame.sort_values("sample_id").drop_duplicates("context_id")
    rng = np.random.default_rng(seed)
    picked = rng.choice(len(frame), size=min(n, len(frame)), replace=False)
    return frame.iloc[sorted(picked)]


def arm_order(index: int, round_index: int) -> list[str]:
    """Rotate A, B, C, R by sample; reverse the order in the second round."""
    shift = index % len(ARMS)
    order = list(ARMS[shift:] + ARMS[:shift])
    return order[::-1] if round_index else order


def load_model(model_name: str, dtype_name: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    from vihallulens.revisions import revision_for

    dtype = getattr(torch, dtype_name)
    revision = revision_for(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        revision=revision,
        dtype=dtype,
        attn_implementation="sdpa",
        device_map={"": 0},
        quantization_config=BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=dtype,
            bnb_4bit_use_double_quant=True,
        ),
    )
    return model.eval(), tokenizer


def end_ids(model, tokenizer) -> set[int]:
    eos = model.generation_config.eos_token_id
    ids = set(eos if isinstance(eos, list) else [eos])
    ids.add(tokenizer.eos_token_id)
    return {int(i) for i in ids if i is not None}


def reread(model, prompt, ids, layout):
    """One teacher-forcing pass with the extractor's own reduction, on the same token ids."""
    import torch

    from vihallulens.extract.attention import layer_diagnostics, lookback_from_layer

    layout = layout.to(next(model.parameters()).device)
    parts, finite = [], []

    def hook(module, inputs, output):  # noqa: ARG001 - signature fixed by PyTorch
        finite.append(layer_diagnostics(output[1], layout)[0])
        parts.append(lookback_from_layer(output[1], layout))
        return (output[0], None, *output[2:])

    handles = [layer.self_attn.register_forward_hook(hook) for layer in model.model.layers]
    try:
        with torch.no_grad():
            tensor = torch.tensor([prompt.input_ids + ids], device=layout.query_positions.device)
            model(tensor, use_cache=False, logits_to_keep=1)
    finally:
        for handle in handles:
            handle.remove()
    names = ("per_chunk", "total", "context", "self_mean")
    columns = list(zip(*parts, strict=True))
    stacked = {name: torch.stack(v) for name, v in zip(names, columns, strict=True)}
    return stacked, [i for i, ok in enumerate(finite) if not ok]


def timed(call):
    import torch

    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    value = call()
    torch.cuda.synchronize()
    elapsed = (time.perf_counter() - started) * 1000
    return value, elapsed, torch.cuda.max_memory_allocated() / MB


def to_features(arrays) -> None:
    """The CPU tail of the detector: move the arrays off the card, compute the five shapes."""
    chunk_features(arrays["per_chunk"].cpu().numpy())
    arrays["total"].cpu().numpy().mean(axis=2)


def run_arm(arm: str, model, prompt, ids, layout):
    """Run one arm. Returns the arrays it read (if any) and the arm's diagnostic."""
    from vihallulens.extract.incremental import IncrementalReader, decode

    if arm in ("A", "B"):
        return None, decode(model, prompt.input_ids, 0, set(), forced=ids)[2]
    if arm == "C":
        with IncrementalReader(model, layout) as reader:
            agreed = decode(model, prompt.input_ids, 0, set(), forced=ids)[2]
        arrays = reader.stacked()
        to_features(arrays)
        return arrays, agreed
    arrays, nonfinite = reread(model, prompt, ids, layout)
    to_features(arrays)
    return arrays, nonfinite


def drift(a, b) -> dict:
    """How far the two routes to the same features are apart."""
    out = {}
    for name in ("total", "context", "per_chunk"):
        diff = (a[name].float() - b[name].float()).abs()
        out[name] = {"mean": float(diff.mean()), "max": float(diff.max())}
    pooled = (a["total"].float().mean(-1) - b["total"].float().mean(-1)).abs()
    out["pooled_total"] = {"mean": float(pooled.mean()), "max": float(pooled.max())}
    return out


def pick_dtype(args, frame):
    """Load the model in the first dtype that generates ordinary text."""
    import torch

    from vihallulens.extract.incremental import decode, render_generation_prompt

    candidates = ["float16", "bfloat16"] if args.dtype == "auto" else [args.dtype]
    for candidate in candidates:
        model, tokenizer = load_model(args.model, candidate)
        healthy = True
        for row in frame.head(N_WARMUP).itertuples():
            prompt = render_generation_prompt(tokenizer, row.context, row.question)
            ids, finite, _ = decode(model, prompt.input_ids, 32, end_ids(model, tokenizer))
            text = tokenizer.decode(ids, skip_special_tokens=True)
            print(f"  thử {candidate}: logit hữu hạn = {finite} | {text[:90]!r}", flush=True)
            healthy = healthy and finite and bool(text.strip())
        if healthy:
            return model, tokenizer, candidate
        print(f"  !! {candidate} không sinh được văn bản bình thường", flush=True)
        del model
        gc.collect()
        torch.cuda.empty_cache()
    raise SystemExit(f"{args.model} không sinh được ở {candidates}; dừng lại.")


def command_run(args) -> int:
    import torch
    import transformers

    from vihallulens.extract.incremental import (
        decode,
        layout_for_tokens,
        render_generation_prompt,
    )

    out = Path(args.out)
    done, has_session = set(), False
    if out.is_file():
        for line in out.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            has_session = has_session or record["kind"] == "session"
            done.add(record.get("sample_id"))

    def write(record: dict) -> None:
        with out.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    frame = pick_samples(load_dataset("vihallu", "test", args.interim_dir), args.samples)
    if args.limit:
        frame = frame.head(args.limit)
    model, tokenizer, dtype_name = pick_dtype(args, frame)
    if not has_session:
        write({"kind": "session", "model": args.model, "compute_dtype": dtype_name,
               "gpu": torch.cuda.get_device_name(0), "torch": torch.__version__,
               "transformers": transformers.__version__, "max_new_tokens": MAX_NEW_TOKENS,
               "predictions": PREDICTIONS})

    eos = end_ids(model, tokenizer)
    warmed = False
    for index, row in enumerate(frame.itertuples()):
        if row.sample_id in done:
            continue
        base = {"kind": "sample", "sample_id": row.sample_id}
        prompt = render_generation_prompt(tokenizer, row.context, row.question)
        if prompt.n_tokens > MAX_PROMPT_TOKENS:
            write({**base, "skipped": "prompt quá dài"})
            continue
        model.set_attn_implementation("sdpa")
        ids, finite, _ = decode(model, prompt.input_ids, MAX_NEW_TOKENS, eos)
        if len(ids) < 2 or not finite:
            write({**base, "skipped": "phản hồi dưới 2 token" if finite else "logit hỏng"})
            continue
        chunks = chunk_by_sentence(row.context)
        layout = layout_for_tokens(prompt, len(ids), chunks)
        if not warmed:  # one untimed pass of each arm, so kernels and caches are warm
            for arm in ARMS:
                model.set_attn_implementation(IMPLEMENTATION[arm])
                run_arm(arm, model, prompt, ids, layout)
            warmed = True
        arms: dict[str, list] = {arm: [] for arm in ARMS}
        kept, agreed, nonfinite = {}, {}, []
        for round_index in range(2):
            for arm in arm_order(index, round_index):
                model.set_attn_implementation(IMPLEMENTATION[arm])  # outside the clock
                (arrays, extra), ms, peak = timed(
                    partial(run_arm, arm, model, prompt, ids, layout)
                )
                arms[arm].append({"ms": ms, "peak_mb": peak})
                if arm == "R":
                    nonfinite = extra
                else:
                    agreed[arm] = extra
                if arrays is not None:
                    kept[arm] = arrays
        write({**base, "prompt_tokens": prompt.n_tokens, "response_tokens": len(ids),
               "n_chunks": len(chunks), "hit_limit": len(ids) == MAX_NEW_TOKENS,
               "agreed": agreed, "nonfinite_layers": nonfinite, "arms": arms,
               "drift": drift(kept["C"], kept["R"]),
               "answer": tokenizer.decode(ids, skip_special_tokens=True)})
        if (index + 1) % 5 == 0:
            print(f"  {index + 1}/{len(frame)} mẫu", flush=True)
    return 0


def load_records(path: Path) -> tuple[dict, list[dict], list[dict]]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    session = next(r for r in rows if r["kind"] == "session")
    samples = [r for r in rows if r["kind"] == "sample"]
    measured = [r for r in samples if "skipped" not in r]
    return session, measured, [r for r in samples if "skipped" in r]


def arm_ms(samples, arm: str, rounds: slice = slice(None)) -> np.ndarray:
    """Mean over the chosen rounds, per sample."""
    return np.array([np.mean([item["ms"] for item in s["arms"][arm][rounds]]) for s in samples])


def paired_ci(values: np.ndarray, rounds: int = BOOTSTRAP_ROUNDS,
              seed: int = REQUIRED_SPLIT_SEED) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(values), size=(rounds, len(values)))
    low, high = np.percentile(values[picks].mean(axis=1), [2.5, 97.5])
    return float(low), float(high)


def summarise(samples: list[dict]) -> dict:
    ms = {arm: arm_ms(samples, arm) for arm in ARMS}
    base = float(ms["A"].mean())
    contrasts = {"C-B": ms["C"] - ms["B"], "B-A": ms["B"] - ms["A"],
                 "C-A": ms["C"] - ms["A"], "R": ms["R"]}
    tokens = sum(s["response_tokens"] for s in samples)
    out: dict = {
        "n": len(samples),
        "prompt_tokens_mean": float(np.mean([s["prompt_tokens"] for s in samples])),
        "response_tokens_mean": tokens / len(samples),
        "mean_ms": {arm: float(values.mean()) for arm, values in ms.items()},
        "peak_mb": {arm: max(i["peak_mb"] for s in samples for i in s["arms"][arm])
                    for arm in ARMS},
        "contrast": {name: {"ms": float(v.mean()), "ci": paired_ci(v),
                            "share_of_A": float(v.mean()) / base}
                     for name, v in contrasts.items()},
        "round_drift": {arm: float(arm_ms(samples, arm, slice(1, 2)).mean()
                                   / arm_ms(samples, arm, slice(0, 1)).mean() - 1)
                        for arm in ARMS},
        "agreement": {arm: sum(s["agreed"][arm] for s in samples) / tokens for arm in "ABC"},
        "drift_total_mean": float(np.mean([s["drift"]["total"]["mean"] for s in samples])),
        "drift_pooled_mean": float(np.mean([s["drift"]["pooled_total"]["mean"]
                                            for s in samples])),
        "drift_pooled_max": float(max(s["drift"]["pooled_total"]["max"] for s in samples)),
    }
    contrast = out["contrast"]
    out["verdict"] = {
        "hook_share": contrast["C-B"]["share_of_A"] < 0.10,
        "eager_costs": contrast["B-A"]["ci"][0] > 0,
        "cheaper_than_reread": contrast["C-A"]["ms"] < contrast["R"]["ms"],
        "same_features": out["drift_total_mean"] < 0.01,
    }
    return out


def command_report(args) -> int:
    session, samples, skipped = load_records(Path(args.path))
    s = summarise(samples)
    print(f"{session['model']} · {session['compute_dtype']} · {session['gpu']} · "
          f"transformers {session['transformers']}")
    print(f"{s['n']} mẫu, bỏ {len(skipped)}; trung bình {s['prompt_tokens_mean']:.0f} token "
          f"prompt, {s['response_tokens_mean']:.1f} token phản hồi")
    for arm in ARMS:
        print(f"  {arm} ({IMPLEMENTATION[arm]:<5}) {s['mean_ms'][arm]:>9.1f} ms/mẫu · đỉnh "
              f"{s['peak_mb'][arm]:,.0f} MB · lượt 2 so lượt 1 {s['round_drift'][arm]:+.1%}")
    for name, c in s["contrast"].items():
        print(f"  {name:<4} {c['ms']:>8.1f} ms [{c['ci'][0]:.1f}; {c['ci'][1]:.1f}] "
              f"= {c['share_of_A']:.1%} thời gian sinh A")
    print(f"  tỷ lệ token trùng khi phát lại: {s['agreement']}")
    print(f"  |Δ| C–R của lookback_total: từng token {s['drift_total_mean']:.5f}; sau khi lấy "
          f"trung bình {s['drift_pooled_mean']:.5f} (lớn nhất {s['drift_pooled_max']:.5f})")
    for key, text in PREDICTIONS.items():
        print(f"  dự đoán «{text}»: {'ĐÚNG' if s['verdict'][key] else 'SAI'}")
    if args.json:
        Path(args.json).write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--model", default=DEFAULT_MODEL)
    run.add_argument("--dtype", default="auto", choices=("auto", "float16", "bfloat16"))
    run.add_argument("--samples", type=int, default=DEFAULT_SAMPLES)
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--interim-dir", default=str(DEFAULT_INTERIM_DIR))
    run.add_argument("--out", required=True)
    run.set_defaults(func=command_run)
    report = commands.add_parser("report")
    report.add_argument("--path", default="results/e11_self_check.jsonl")
    report.add_argument("--json", default=None)
    report.set_defaults(func=command_report)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
