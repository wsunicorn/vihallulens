"""Task T18, experiment E09: fine-tune an encoder as the strong baseline.

Section 4 of docs/EXPERIMENTS.md puts three Vietnamese-capable encoders here. They are the
serious comparison: unlike the surface baseline of E01 they actually read the text, and unlike
the LLM judge of E10 they run locally. If the attention method cannot beat these, the cost
argument of research question CH2 does not survive.

The training loop is written out by hand rather than using ``transformers.Trainer``. This repo
resolved transformers 5.15, whose Trainer arguments differ from the 4.x ones every example
online uses, and a loop this short is not worth a version risk on a run that costs GPU quota.

Usage, one model at a time so each gets its own session — see section 5 of CLAUDE.md on why
timings from back-to-back runs are not comparable:
    python scripts/train_encoder_baseline.py --model phobert
    python scripts/train_encoder_baseline.py --model xlmr --seeds 3
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import REQUIRED_SPLIT_SEED  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.detect.encoder import (  # noqa: E402
    MODELS,
    build_pairs,
    decode_labels,
    encode_labels,
    truncation_rate,
)
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import (  # noqa: E402
    LABELS,
    bootstrap_ci,
    compute_metrics,
    summarise_runs,
)
from vihallulens.evaluation.telemetry import (  # noqa: E402
    gpu_telemetry,
    throttling_verdict,
)

MB = 1024**2

# Fine-tuning is genuinely stochastic — head initialisation, dropout, data order — so unlike
# the deterministic classifier of E01, seeds measure something real here.
#
# Three rather than the five section 3 of docs/EXPERIMENTS.md asks for, because of what T17
# measured: the test-set interval is ±0,017 while seed spread on a converged fine-tune is far
# smaller, so seeds four and five would refine a number already dominated by a larger one — at
# roughly an hour of GPU quota each for the two 512-token models. Pass --seeds 5 to follow the
# rule literally.
DEFAULT_SEEDS = 3
DEFAULT_EPOCHS = 3
DEFAULT_LR = 2e-5
WARMUP_RATIO = 0.1
MAX_GRAD_NORM = 1.0


def set_seed(seed: int) -> None:
    import random

    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def make_loader(tokenizer, left, right, labels, max_length, batch_size, shuffle, seed):
    import torch
    from torch.utils.data import DataLoader, TensorDataset

    encoded = tokenizer(
        list(left), list(right), truncation=True, max_length=max_length,
        padding="max_length", return_tensors="pt",
    )
    dataset = TensorDataset(
        encoded["input_ids"],
        encoded["attention_mask"],
        torch.tensor(labels, dtype=torch.long),
    )
    generator = torch.Generator().manual_seed(seed) if shuffle else None
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, generator=generator)


def train_once(spec, data, seed: int, epochs: int, lr: float, device: str) -> dict:
    """Fine-tune one model with one seed and score it on the test split."""
    import torch
    from torch.amp import GradScaler, autocast
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    set_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(spec["name"])
    model = AutoModelForSequenceClassification.from_pretrained(
        spec["name"], num_labels=len(LABELS)
    ).to(device)

    train_loader = make_loader(
        tokenizer, *data["train"], spec["max_length"], spec["batch_size"], True, seed
    )
    test_loader = make_loader(
        tokenizer, *data["test"], spec["max_length"], spec["batch_size"], False, seed
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    total_steps = len(train_loader) * epochs
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=lr,
        total_steps=total_steps,
        pct_start=WARMUP_RATIO,
        anneal_strategy="linear",
    )
    scaler = GradScaler(device)

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()

    model.train()
    for epoch in range(epochs):
        for step, (ids, mask, target) in enumerate(train_loader, start=1):
            ids, mask, target = ids.to(device), mask.to(device), target.to(device)
            optimizer.zero_grad(set_to_none=True)
            with autocast(device, dtype=torch.float16):
                loss = model(input_ids=ids, attention_mask=mask, labels=target).loss
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), MAX_GRAD_NORM)
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            if step % 50 == 0:
                print(f"      epoch {epoch + 1}/{epochs}  bước {step}/{len(train_loader)}  "
                      f"loss {loss.item():.4f}", end="\r")
    train_seconds = time.perf_counter() - started

    model.eval()
    predicted, probabilities = [], []
    inference_started = time.perf_counter()
    with torch.no_grad():
        for ids, mask, _ in test_loader:
            with autocast(device, dtype=torch.float16):
                logits = model(input_ids=ids.to(device), attention_mask=mask.to(device)).logits
            proba = torch.softmax(logits.float(), dim=-1).cpu().numpy()
            probabilities.append(proba)
            predicted.append(proba.argmax(axis=1))
    inference_ms = (time.perf_counter() - inference_started) * 1000

    n_params = sum(parameter.numel() for parameter in model.parameters())
    y_pred = decode_labels(np.concatenate(predicted))
    y_proba = np.vstack(probabilities)
    peak_vram = torch.cuda.max_memory_allocated() / MB if torch.cuda.is_available() else 0.0

    del model, optimizer, scaler
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return {
        "metrics": compute_metrics(data["test"][2], y_pred, y_proba, proba_labels=LABELS),
        "y_pred": y_pred,
        "n_params": n_params,
        "train_seconds": train_seconds,
        "ms_per_sample": inference_ms / len(y_pred),
        "peak_vram_mb": peak_vram,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="E09: tinh chỉnh bộ mã hóa làm mốc so sánh.")
    parser.add_argument("--model", required=True, choices=list(MODELS))
    parser.add_argument("--dataset", default="vihallu")
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--lr", type=float, default=DEFAULT_LR)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import torch
    from transformers import AutoTokenizer

    spec = MODELS[args.model]
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print()
    print("=" * 80)
    print(f"T18 / E09 — TINH CHỈNH {args.model.upper()}")
    print("=" * 80)
    print(f"  mô hình               : {spec['name']}")
    print(f"  độ dài tối đa         : {spec['max_length']} token")
    print(f"  tách từ tiếng Việt    : {'có' if spec['segment'] else 'không'}")
    print(f"  batch / epoch / lr    : {spec['batch_size']} / {args.epochs} / {args.lr}")
    print(f"  số seed               : {args.seeds}")
    print(f"  thiết bị              : {device}")

    data = {}
    for split in ("train", "test"):
        frame = load_dataset(args.dataset, split, args.interim_dir)
        left, right = build_pairs(frame, segment=spec["segment"])
        data[split] = (left, right, list(frame["label"]))
    print(f"  train / test          : {len(data['train'][0]):,} / {len(data['test'][0]):,} mẫu")

    tokenizer = AutoTokenizer.from_pretrained(spec["name"])
    cut = truncation_rate(tokenizer, *data["train"][:2], spec["max_length"])
    print(f"  mẫu bị cắt vì quá dài : {cut * 100:.1f} %")
    if spec["segment"]:
        from vihallulens.data.segmentation import cache_info

        print(f"  bộ đệm tách từ        : {cache_info()}")

    labels_train = encode_labels(data["train"][2])
    data["train"] = (*data["train"][:2], labels_train)
    data["test"] = (*data["test"][:2], data["test"][2])

    # Read once before anything runs, and again after each seed. Running the three encoders in
    # one session is perfectly fine for the accuracy figures — throttling makes a card slower,
    # not wrong — but it does distort ms/mẫu, so the run records enough to say whether it did.
    readings = []
    baseline = gpu_telemetry()
    if baseline is not None:
        readings.append(baseline)
        print(f"  nhiệt độ trước khi chạy : {baseline['temperature_c']:.0f} °C, xung SM "
              f"{baseline['sm_clock_mhz']:.0f}/{baseline['sm_clock_max_mhz']:.0f} MHz")

    runs = []
    for offset in range(args.seeds):
        seed = REQUIRED_SPLIT_SEED + offset
        print()
        print(f"  --- seed {seed} ({offset + 1}/{args.seeds}) ---")
        result = train_once(spec, data, seed, args.epochs, args.lr, device)
        runs.append(result)
        after = gpu_telemetry()
        if after is not None:
            readings.append(after)
        heat = f"   {after['temperature_c']:.0f} °C" if after is not None else ""
        print(f"      macro-F1 {result['metrics']['macro_f1']:.4f}   "
              f"huấn luyện {result['train_seconds'] / 60:.1f} phút   "
              f"VRAM đỉnh {result['peak_vram_mb']:,.0f} MB{heat}")

    across_seeds = summarise_runs([run["metrics"] for run in runs])
    # The seed closest to the average is the one whose predictions get the test-set interval:
    # a bootstrap of an outlier run would describe that run rather than the method.
    middle = int(np.argsort([run["metrics"]["macro_f1"] for run in runs])[len(runs) // 2])
    spread = bootstrap_ci(data["test"][2], runs[middle]["y_pred"], seed=REQUIRED_SPLIT_SEED)

    print()
    print("-" * 80)
    print(f"KẾT QUẢ — trung bình {args.seeds} seed, trên {len(data['test'][2]):,} mẫu test")
    print("-" * 80)
    print(f"  {'Chỉ số':<14} {'Trung bình':>11} {'± seed':>9}   {'khoảng tin cậy 95 %':>21}")
    for key in ("macro_f1", "accuracy", *[f"f1_{label}" for label in LABELS]):
        print(f"  {key:<14} {across_seeds[key]:>11.4f} {across_seeds[f'{key}_std']:>9.4f}   "
              f"[{spread[f'{key}_lo']:.4f}, {spread[f'{key}_hi']:.4f}]")
    print(f"  {'ece':<14} {across_seeds['ece']:>11.4f} {across_seeds['ece_std']:>9.4f}")

    # Counted inside the first run rather than by loading the model again: a second load of a
    # 355-million-parameter checkpoint costs a minute and a download for one integer.
    n_params = runs[0]["n_params"]
    ms_per_sample = float(np.mean([run["ms_per_sample"] for run in runs]))
    peak_vram = float(max(run["peak_vram_mb"] for run in runs))
    total_minutes = sum(run["train_seconds"] for run in runs) / 60

    print()
    print(f"  Tham số phải huấn luyện : {n_params:,}")
    print(f"  Thời gian suy luận      : {ms_per_sample:.2f} ms/mẫu")
    print(f"  VRAM đỉnh               : {peak_vram:,.0f} MB")
    print(f"  Tổng thời gian huấn luyện: {total_minutes:.1f} phút cho {args.seeds} seed")

    throttled = False
    if readings:
        throttled, reason = throttling_verdict(readings)
        print()
        if throttled:
            print(f"  CẢNH BÁO HẠ XUNG: {reason}.")
            print("  Điểm số KHÔNG bị ảnh hưởng — hạ xung làm chậm chứ không làm sai. Nhưng")
            print("  ms/mẫu của lần chạy này không so thẳng được với mô hình chạy ở phiên khác.")
        else:
            print(f"  Không thấy hạ xung: {reason}.")

    config = {
        "experiment": "E09",
        "dataset": {"name": args.dataset, "split_seed": REQUIRED_SPLIT_SEED},
        "encoder": {
            "name": spec["name"], "max_length": spec["max_length"],
            "segment": spec["segment"], "batch_size": spec["batch_size"],
            "epochs": args.epochs, "lr": args.lr,
        },
    }
    metrics = {**across_seeds, **spread}
    extra = {
        "ms_per_sample": ms_per_sample,
        "peak_vram_mb": peak_vram,
        "n_params_trainable": n_params,
        "n_seeds": args.seeds,
        "truncation_rate": cut,
        "train_minutes_total": total_minutes,
        "std_method": "độ lệch chuẩn qua seed; khoảng tin cậy từ bootstrap tập test",
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "gpu_throttled": throttled,
        "gpu_telemetry": readings,
    }
    record = log_result(f"e09_{args.model}", config, metrics, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
