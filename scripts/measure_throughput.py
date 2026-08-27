"""Task T08: how fast is extraction, and does the whole plan fit the weekly GPU quota?

Task T07 answered "does one sample fit in 16 GB". This one answers the question that decides
the schedule: at 30 Kaggle GPU-hours a week, can the four corpora actually be extracted?

Cost is driven by sequence length, so samples are grouped into length tiers and timed tier by
tier. The tier means are then applied to the real length histogram of each corpus, which turns
a per-sample millisecond figure into hours of GPU time per corpus — the number the plan needs.

Two clocks are reported for every sample and they measure different things:

* ``forward``   — the model call alone, what ``AttentionFeatures.elapsed_ms`` records
* ``end_to_end``— rendering the prompt, fitting it to the budget, the forward pass, and moving
  the features back to the CPU

Projections use ``end_to_end``, because that is what a run actually costs.

Usage:
    python scripts/measure_throughput.py                        # on a Kaggle T4
    python scripts/measure_throughput.py --per-tier 20
    python scripts/measure_throughput.py --model Qwen/Qwen2.5-3B-Instruct
    python scripts/measure_throughput.py --max-context-tokens 2048
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
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.telemetry import (  # noqa: E402
    gpu_telemetry,
    throttling_verdict,
)
from vihallulens.extract.prompt import render_prompt  # noqa: E402

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_RESULTS_PATH = Path("results/feasibility.jsonl")

# Upper bound of each tier, in prompt tokens. Chosen from section 4B of docs/DATA.md: the
# median ViHallu prompt is 308 tokens and the median ISE-DSC01 prompt 796, so the first two
# tiers hold most of the work, while the top tier holds the ISE-DSC01 tail that decides the
# peak memory. The last bound is the token budget itself.
TIER_BOUNDS = (512, 1024, 2048, 4096)

# Kaggle gives 30 GPU-hours a week (section 2 of CLAUDE.md). Extraction may not eat all of
# it: training the classifiers, the encoder baselines of E09 and the ablations all need GPU
# too, so a run costing more than roughly half the quota needs a decision, not a shrug.
WEEKLY_GPU_HOURS = 30.0
COMFORTABLE_SHARE = 0.5

# The two corpora every planned experiment needs: ViHallu carries the main task and ISE-DSC01
# the chunk-aware evidence test. ViWikiFC and ViFactCheck serve E08, E15 and the optional E17,
# so they can be scheduled later or subsampled without touching the core claim.
CORE_CORPORA = ("vihallu", "isedsc01")

# Tier whose upper bound is 2,048, the first fallback budget in section 5 of CLAUDE.md.
CAP_TIER = TIER_BOUNDS.index(2048)

# Every labelled sample in each corpus, from section 4 of docs/DATA.md. Used only to sanity
# check the corpus reader against the numbers already verified at T08B.
EXPECTED_ROWS = {"vihallu": 7000, "isedsc01": 36369, "viwikifc": 20919, "vifactcheck": 7232}


# -- pure logic, tested in tests/test_throughput.py --------------------------------------


def tier_label(index: int, bounds: tuple[int, ...] = TIER_BOUNDS) -> str:
    """Human-readable range of a tier, e.g. ``513–1024``."""
    low = 0 if index == 0 else bounds[index - 1] + 1
    return f"{low}–{bounds[index]}"


def assign_tier(n_tokens: int, bounds: tuple[int, ...] = TIER_BOUNDS) -> int:
    """Which tier a sample of this length is paid for at.

    Anything longer than the last bound is clamped into the top tier rather than dropped: the
    extractor truncates it to the token budget, so it costs exactly what a top-tier sample
    costs. Section 4B of docs/DATA.md counts 14 such samples across all four corpora.
    """
    for index, bound in enumerate(bounds):
        if n_tokens <= bound:
            return index
    return len(bounds) - 1


def spread(values: list[int], count: int) -> list[int]:
    """Pick ``count`` items evenly across a list, keeping both ends.

    Deterministic on purpose: no seed to record, and re-running the measurement on the same
    data times exactly the same samples.
    """
    if len(values) <= count:
        return list(values)
    positions = np.linspace(0, len(values) - 1, count).round().astype(int)
    return [values[position] for position in dict.fromkeys(positions.tolist())]


def pick_tier_samples(pool: list[dict], per_tier: int, bounds=TIER_BOUNDS) -> dict[int, list[dict]]:
    """Group the pool by tier and take an even spread of lengths within each tier.

    Spreading inside the tier matters: taking the 20 shortest members of the 2049–4096 tier
    would time the tier at its cheapest end and understate every projection built on it.
    """
    buckets: dict[int, list[dict]] = {index: [] for index in range(len(bounds))}
    for sample in pool:
        buckets[assign_tier(sample["n_tokens"], bounds)].append(sample)

    chosen: dict[int, list[dict]] = {}
    for index, members in buckets.items():
        members.sort(key=lambda item: item["n_tokens"])
        positions = spread(list(range(len(members))), per_tier)
        chosen[index] = [members[position] for position in positions]
    return chosen


def project_seconds(histogram: dict[int, int], seconds_per_tier: dict[int, float]) -> float:
    """Total GPU seconds for a corpus, given how many of its samples land in each tier.

    A tier with no timing contributes nothing, which is why the caller checks that every
    populated tier was actually measured before trusting the number.
    """
    return sum(
        count * seconds_per_tier[tier]
        for tier, count in histogram.items()
        if tier in seconds_per_tier
    )


def log_log_slope(lengths: list[float], costs: list[float]) -> float:
    """Exponent ``k`` in ``cost ≈ length^k``, fitted on the tier means.

    The point is to see how the cost really grows. The attention matrix grows with the square
    of the length, so ``k`` near 2 would mean attention dominates and halving the token budget
    would buy a fourfold speed-up; ``k`` near 1 means the rest of the network dominates and
    fallback step 1 of section 5 of CLAUDE.md buys much less than it looks like it should.
    """
    if len(lengths) < 2:
        return float("nan")
    x = np.log(np.asarray(lengths, dtype=float))
    y = np.log(np.asarray(costs, dtype=float))
    return float(np.polyfit(x, y, 1)[0])


def tiers_without_truncation(summaries: dict[int, dict]) -> dict[int, dict]:
    """Tiers whose samples all fitted the token budget.

    Only these may be fitted against length. A truncated sample is fed at the budget, not at
    its own length, so pairing the two in a curve fit describes something that never ran.
    """
    return {tier: item for tier, item in summaries.items() if item["n_truncated"] == 0}


def format_duration(seconds: float) -> str:
    """Seconds as hours and minutes, the unit the weekly quota is spent in."""
    hours, remainder = divmod(int(round(seconds)), 3600)
    return f"{hours} giờ {remainder // 60:02d} phút"


# -- corpus reading ----------------------------------------------------------------------


def read_corpus(data_dir: Path, name: str) -> list[tuple[str, str, str]]:
    """Every labelled sample of one corpus as ``(context, question, response)``.

    Column names come from section 2 of docs/DATA.md. Only ViHallu has a question; for the
    three fact-checking corpora the claim plays the part of the response, and the question is
    empty, which the prompt template handles by omitting the block entirely.
    """
    import pandas as pd

    if name == "vihallu":
        frame = pd.read_csv(data_dir / "vihallu_train.csv")
        return [
            (str(row.context), str(row.prompt), str(row.response))
            for row in frame.itertuples(index=False)
        ]

    if name == "isedsc01":
        with (data_dir / "isedsc01_train.json").open(encoding="utf-8") as handle:
            records = json.load(handle)
        return [
            (str(record.get("context", "")), "", str(record.get("claim", "")))
            for record in records.values()
        ]

    if name == "viwikifc":
        samples: list[tuple[str, str, str]] = []
        for split in ("train", "dev", "test"):
            frame = pd.read_csv(data_dir / f"viwikifc_{split}.csv")
            samples += [
                (str(row.context), "", str(row.claim)) for row in frame.itertuples(index=False)
            ]
        return samples

    if name == "vifactcheck":
        samples = []
        for split in ("train", "dev", "test"):
            frame = pd.read_parquet(data_dir / f"vifactcheck_{split}.parquet")
            samples += [
                (str(row.Context), "", str(row.Statement)) for row in frame.itertuples(index=False)
            ]
        return samples

    raise ValueError(f"unknown corpus: {name}")


def scaffold_tokens(tokenizer) -> tuple[int, int]:
    """Tokens the chat template adds on its own, with and without a question block.

    Rendering an empty sample is the only honest way to get this: the template belongs to the
    model, and section 8 of CLAUDE.md forbids reconstructing it by hand.
    """

    def length(question: str) -> int:
        text = render_prompt(tokenizer, "", question, "").text
        return len(tokenizer(text, add_special_tokens=False)["input_ids"])

    return length(""), length("x") - len(tokenizer("x", add_special_tokens=False)["input_ids"])


def token_lengths(tokenizer, samples: list[tuple[str, str, str]], scaffold: tuple[int, int]):
    """Prompt length of every sample, in tokens.

    The three parts are tokenized in one batch and their lengths added, rather than rendering
    the full template 71,520 times. Tokenization is not exactly additive across a boundary, so
    this can be off by a token or two — irrelevant for putting a sample in a 512-wide tier, and
    it turns minutes of work into seconds.
    """
    bare, with_question = scaffold
    flat = [part for sample in samples for part in sample]
    encoded = tokenizer(flat, add_special_tokens=False)["input_ids"]
    lengths = []
    for index in range(0, len(encoded), 3):
        context, question, response = encoded[index : index + 3]
        overhead = with_question if question else bare
        lengths.append(len(context) + len(question) + len(response) + overhead)
    return lengths


# -- measurement -------------------------------------------------------------------------


def time_sample(extractor, sample: dict) -> dict:
    """Extract one sample and record both clocks plus what the run actually saw."""
    started = time.perf_counter()
    context = sample["context"]
    features = extractor.extract(
        context, sample["question"], sample["response"], chunk_by_sentence(context)
    )
    end_to_end_ms = (time.perf_counter() - started) * 1000
    return {
        "n_tokens": sample["n_tokens"],
        "end_to_end_ms": end_to_end_ms,
        "forward_ms": features.elapsed_ms,
        "peak_vram_mb": features.peak_vram_mb,
        "n_chunks": features.n_chunks,
        "truncated": features.truncated,
        "nonfinite": bool(features.nonfinite_layers),
    }


def summarise(timings: list[dict]) -> dict:
    """Tier summary. The median leads, because one stall should not move the projection."""
    end_to_end = np.array([item["end_to_end_ms"] for item in timings])
    forward = np.array([item["forward_ms"] for item in timings])
    return {
        "n_samples": len(timings),
        "mean_tokens": float(np.mean([item["n_tokens"] for item in timings])),
        "median_ms": float(np.median(end_to_end)),
        "mean_ms": float(np.mean(end_to_end)),
        "p90_ms": float(np.percentile(end_to_end, 90)),
        "forward_median_ms": float(np.median(forward)),
        "forward_share": float(np.median(forward) / np.median(end_to_end)),
        "peak_vram_mb": float(max(item["peak_vram_mb"] for item in timings)),
        "mean_chunks": float(np.mean([item["n_chunks"] for item in timings])),
        "n_truncated": int(sum(item["truncated"] for item in timings)),
        "n_nonfinite": int(sum(item["nonfinite"] for item in timings)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure extraction throughput (task T08).")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--per-tier", type=int, default=20, help="samples timed per length tier")
    parser.add_argument("--max-context-tokens", type=int, default=4096)
    parser.add_argument("--compute-dtype", default="float16",
                        choices=["float16", "bfloat16", "float32"])
    parser.add_argument("--exclude-layers", type=int, nargs="*", default=[27])
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--results-path", type=Path, default=DEFAULT_RESULTS_PATH)
    parser.add_argument("--run-name", default=None)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="chỉ nạp tokenizer, dựng phân bố độ dài và chọn mẫu; không nạp mô hình, không đo",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    import torch

    from vihallulens.data.paths import find_raw_dir

    data_dir = find_raw_dir(args.data_dir)
    run_name = args.run_name or f"t08_{args.model.split('/')[-1]}_{args.max_context_tokens}"

    print()
    print("=" * 80)
    print("T08 — ĐO THÔNG LƯỢNG VÀ QUYẾT ĐỊNH BẬC THANG")
    print("=" * 80)
    print(f"  mô hình               : {args.model}")
    print(f"  ngân sách token       : {args.max_context_tokens}")
    print(f"  compute dtype         : {args.compute_dtype}")
    print(f"  lớp bỏ qua            : {args.exclude_layers or 'không bỏ lớp nào'}")
    print(f"  dữ liệu               : {data_dir}")

    # --dry-run exercises every step that does not need a GPU: reading the four corpora,
    # measuring the template overhead, bucketing 71,520 samples and choosing which ones to
    # time. Running it first turns a wasted GPU session into a wasted minute on a laptop.
    started = time.perf_counter()
    if args.dry_run:
        from transformers import AutoTokenizer

        extractor = None
        tokenizer = AutoTokenizer.from_pretrained(args.model)
        print(f"  chế độ                : thử khô, chỉ nạp tokenizer "
              f"({time.perf_counter() - started:.0f} s)")
    else:
        from vihallulens.extract.attention import AttentionExtractor

        extractor = AttentionExtractor(
            args.model,
            max_context_tokens=args.max_context_tokens,
            device="cuda",
            exclude_layers=args.exclude_layers,
            compute_dtype=args.compute_dtype,
        )
        tokenizer = extractor.tokenizer
        print(f"  nạp mô hình           : {time.perf_counter() - started:.0f} s, "
              f"{len(extractor.layer_indices)} lớp được hook")

    # -- length histogram of every corpus -----------------------------------------------
    scaffold = scaffold_tokens(tokenizer)
    print(f"  khung mẫu prompt      : {scaffold[0]} token, "
          f"{scaffold[1]} token khi có câu hỏi")

    print()
    print("-" * 80)
    print("PHÂN BỐ ĐỘ DÀI THEO MỨC — đếm trên toàn bộ mẫu có nhãn")
    print("-" * 80)
    columns = "".join(f"{tier_label(i):>14}" for i in range(len(TIER_BOUNDS)))
    header = f"  {'Bộ':<14}{columns}"
    print(header + f"{'tổng':>10}")
    print("  " + "-" * (len(header) + 8))

    histograms: dict[str, dict[int, int]] = {}
    pool: list[dict] = []
    for name in EXPECTED_ROWS:
        samples = read_corpus(data_dir, name)
        if len(samples) != EXPECTED_ROWS[name]:
            print(f"  CẢNH BÁO: {name} có {len(samples)} mẫu, mục 4 của docs/DATA.md ghi "
                  f"{EXPECTED_ROWS[name]}.")
        lengths = token_lengths(tokenizer, samples, scaffold)
        histogram = dict.fromkeys(range(len(TIER_BOUNDS)), 0)
        for length in lengths:
            histogram[assign_tier(length)] += 1
        histograms[name] = histogram
        counts = "".join(f"{histogram[i]:>14,}" for i in range(len(TIER_BOUNDS)))
        print(f"  {name:<14}{counts}{len(samples):>10,}")

        # ViHallu and ISE-DSC01 alone span 47 to 4,805 words, so they fill every tier; the
        # other two would add nothing but loading time.
        if name in ("vihallu", "isedsc01"):
            pool += [
                {"context": c, "question": q, "response": r, "n_tokens": n, "dataset": name}
                for (c, q, r), n in zip(samples, lengths, strict=True)
            ]

    totals = {
        i: sum(histogram[i] for histogram in histograms.values()) for i in range(len(TIER_BOUNDS))
    }
    print("  " + "-" * (len(header) + 8))
    summed = "".join(f"{totals[i]:>14,}" for i in range(len(TIER_BOUNDS)))
    print(f"  {'tổng':<14}{summed}{sum(totals.values()):>10,}")

    # -- timing ---------------------------------------------------------------------------
    chosen = pick_tier_samples(pool, args.per_tier)

    if args.dry_run:
        print()
        print("-" * 80)
        print("MẪU ĐƯỢC CHỌN ĐỂ ĐO — thử khô, không chạy mô hình")
        print("-" * 80)
        for tier, samples in sorted(chosen.items()):
            if not samples:
                print(f"  {tier_label(tier):>12} : không có mẫu nào rơi vào mức này")
                continue
            lengths = [item["n_tokens"] for item in samples]
            sources = sorted({item["dataset"] for item in samples})
            print(f"  {tier_label(tier):>12} : {len(samples):>2} mẫu, "
                  f"{min(lengths):>5,}–{max(lengths):>5,} token, từ {', '.join(sources)}")
        print()
        print("  Thử khô xong. Bỏ --dry-run và chạy trên GPU để có số thật.")
        return 0

    print()
    print("-" * 80)
    print(f"ĐO THỜI GIAN — {args.per_tier} mẫu mỗi mức")
    print("-" * 80)

    # One discarded run first. The first CUDA call of a process pays for kernel selection and
    # allocator warm-up, and charging that to the shortest tier would distort every tier ratio.
    warm = next(iter(sample for samples in chosen.values() for sample in samples), None)
    if warm is None:
        print("  Không chọn được mẫu nào. Kiểm tra lại thư mục dữ liệu.")
        return 1
    time_sample(extractor, warm)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    # Baseline after the warm-up but before any tier: the state the first tier is measured in.
    readings: list[dict] = []
    baseline = gpu_telemetry()
    if baseline is None:
        print("  nvidia-smi không trả lời được, phiên này không có số nhiệt độ và xung nhịp.")
    else:
        readings.append(baseline)
        print(f"  trước khi đo          : {baseline['temperature_c']:.0f} °C, xung SM "
              f"{baseline['sm_clock_mhz']:.0f}/{baseline['sm_clock_max_mhz']:.0f} MHz")

    summaries: dict[int, dict] = {}
    for tier, samples in sorted(chosen.items()):
        if not samples:
            print(f"  {tier_label(tier):>12} : không có mẫu nào rơi vào mức này")
            continue
        timings = []
        for index, sample in enumerate(samples, start=1):
            timings.append(time_sample(extractor, sample))
            print(f"    {tier_label(tier):>12} {index}/{len(samples)}", end="\r")
        summaries[tier] = summarise(timings)
        # Read straight after the tier finishes, while the card is still at the temperature
        # this tier's numbers were produced at.
        after = gpu_telemetry()
        if after is not None:
            readings.append(after)
            summaries[tier]["telemetry"] = after
        item = summaries[tier]
        print(
            f"  {tier_label(tier):>12} : {item['median_ms']:>7,.0f} ms trung vị"
            f" | {item['mean_ms']:>7,.0f} ms trung bình"
            f" | p90 {item['p90_ms']:>7,.0f} ms"
            f" | {item['mean_tokens']:>6,.0f} token"
            f" | VRAM đỉnh {item['peak_vram_mb']:>7,.0f} MB"
        )

    print()
    print(f"  {'Mức':>12} | {'chunk TB':>9} | {'bị cắt':>7} | {'lớp nan':>8} | "
          f"{'forward chiếm':>13}")
    for tier, item in sorted(summaries.items()):
        print(f"  {tier_label(tier):>12} | {item['mean_chunks']:>9,.1f} | "
              f"{item['n_truncated']:>3}/{item['n_samples']:<3} | "
              f"{item['n_nonfinite']:>4}/{item['n_samples']:<3} | "
              f"{item['forward_share'] * 100:>12.1f}%")

    if readings:
        print()
        print(f"  {'Mức':>12} | {'nhiệt độ':>9} | {'xung SM':>12} | {'% xung tối đa':>13}")
        for tier, item in sorted(summaries.items()):
            reading = item.get("telemetry")
            if reading is None:
                continue
            print(f"  {tier_label(tier):>12} | {reading['temperature_c']:>6.0f} °C | "
                  f"{reading['sm_clock_mhz']:>8.0f} MHz | "
                  f"{reading['clock_ratio'] * 100:>12.0f}%")
        throttled, reason = throttling_verdict(readings)
        print()
        if throttled:
            print(f"  CẢNH BÁO HẠ XUNG: {reason}.")
            print("  Mức đo sau chịu thiệt so với mức đo trước, và số của phiên này không so "
                  "thẳng được với phiên khác. Xem mục 5 của CLAUDE.md.")
        else:
            print(f"  Không thấy hạ xung: {reason}.")

    # Only tiers where nothing was truncated may enter the fit. ``mean_tokens`` is the length
    # of the sample as it arrived, but a truncated sample is fed at the token budget instead,
    # so pairing its original length with its measured cost fits the curve against an x value
    # the GPU never saw. Measured at T08: including them turned k = 1.00 into a bogus 0.85.
    clean = tiers_without_truncation(summaries)
    slope = log_log_slope(
        [item["mean_tokens"] for item in clean.values()],
        [item["median_ms"] for item in clean.values()],
    )
    dropped = sorted(set(summaries) - set(clean))
    print()
    if len(clean) < 2:
        print("  Không đủ mức không bị cắt để ước mũ k. Cần ít nhất hai mức mà mọi mẫu đều "
              "vừa ngân sách token.")
    else:
        print(f"  Chi phí tăng theo độ dài mũ k ≈ {slope:.2f}  "
              f"(k≈2 là ma trận chú ý chi phối, k≈1 là phần còn lại của mạng chi phối)")
        if dropped:
            print(f"  Ước trên {len(clean)} mức không bị cắt; bỏ qua "
                  f"{[tier_label(t) for t in dropped]} vì mẫu ở đó bị cắt nên độ dài thật "
                  f"khác độ dài dùng để xếp mức.")

    # -- projection -----------------------------------------------------------------------
    seconds_per_tier = {tier: item["median_ms"] / 1000 for tier, item in summaries.items()}
    unmeasured = [
        tier for tier in range(len(TIER_BOUNDS))
        if totals[tier] and tier not in seconds_per_tier
    ]
    if unmeasured:
        print(f"  CẢNH BÁO: mức {[tier_label(t) for t in unmeasured]} có mẫu thật nhưng chưa "
              f"đo được, phần dự báo dưới đây thiếu chúng.")

    print()
    print("-" * 80)
    print("DỰ BÁO THỜI GIAN TRÍCH ĐẶC TRƯNG TOÀN BỘ")
    print("-" * 80)
    print(f"  {'Bộ':<14} | {'số mẫu':>9} | {'ms/mẫu':>8} | {'thời gian GPU':>16} | "
          f"{'% quota tuần':>13}")
    print(f"  {'-' * 14}-+-{'-' * 9}-+-{'-' * 8}-+-{'-' * 16}-+-{'-' * 13}")

    projections: dict[str, float] = {}
    for name, histogram in histograms.items():
        seconds = project_seconds(histogram, seconds_per_tier)
        count = sum(histogram.values())
        projections[name] = seconds
        print(f"  {name:<14} | {count:>9,} | {seconds / count * 1000:>8,.0f} | "
              f"{format_duration(seconds):>16} | "
              f"{seconds / 3600 / WEEKLY_GPU_HOURS * 100:>12.1f}%")

    total_seconds = sum(projections.values())
    total_samples = sum(sum(h.values()) for h in histograms.values())
    print(f"  {'-' * 14}-+-{'-' * 9}-+-{'-' * 8}-+-{'-' * 16}-+-{'-' * 13}")
    print(f"  {'tổng':<14} | {total_samples:>9,} | "
          f"{total_seconds / total_samples * 1000:>8,.0f} | "
          f"{format_duration(total_seconds):>16} | "
          f"{total_seconds / 3600 / WEEKLY_GPU_HOURS * 100:>12.1f}%")

    core_histogram = dict.fromkeys(range(len(TIER_BOUNDS)), 0)
    for name in CORE_CORPORA:
        for tier, count in histograms.get(name, {}).items():
            core_histogram[tier] += count
    core_seconds = project_seconds(core_histogram, seconds_per_tier)
    print()
    print(f"  Hai bộ bắt buộc (ViHallu + ISE-DSC01): {format_duration(core_seconds)}, "
          f"{core_seconds / 3600 / WEEKLY_GPU_HOURS * 100:.1f} % quota tuần")

    # -- verdict --------------------------------------------------------------------------
    peak_vram = max(item["peak_vram_mb"] for item in summaries.values())
    budget_hours = WEEKLY_GPU_HOURS * COMFORTABLE_SHARE
    core_hours = core_seconds / 3600
    fits = core_hours <= budget_hours

    print()
    print("=" * 80)
    print("KẾT LUẬN")
    print("=" * 80)
    print(f"  Mô hình dùng được     : {args.model}")
    print(f"  Ngữ cảnh tối đa       : {args.max_context_tokens} token")
    print(f"  VRAM đỉnh đo được     : {peak_vram:,.0f} MB")
    print(f"  Thông lượng chung     : {total_seconds / total_samples * 1000:,.0f} ms/mẫu "
          f"trên toàn bộ phân bố độ dài")
    # Every sample in a tier is priced at that tier's median, and the timed samples are spread
    # evenly across the tier while the corpora bunch toward its short end. The projection is
    # therefore an upper bound, not a point estimate — which is the safe direction for a plan.
    print("  Cách tính             : mỗi mẫu tính theo trung vị của mức nó rơi vào; mẫu đo "
          "trải đều trong mức còn dữ liệu thật dồn về phía ngắn, nên đây là cận trên")
    verdict = "ĐẠT" if fits else "CẦN QUYẾT ĐỊNH"
    print(f"  Hai bộ bắt buộc trong {budget_hours:.0f} giờ (nửa quota tuần): {verdict} "
          f"— cần {core_hours:.1f} giờ")
    if not fits:
        # What a 2,048-token budget would cost: tiers at or below 2,048 are untouched, and
        # everything above is truncated down, so it ends up paying the 1025–2048 price. This
        # is an estimate from tiers already measured, not a substitute for re-running.
        capped = dict.fromkeys(range(len(TIER_BOUNDS)), 0)
        for tier, count in core_histogram.items():
            capped[min(tier, CAP_TIER)] += count
        capped_hours = project_seconds(capped, seconds_per_tier) / 3600

        print()
        print("  Không nằm gọn trong nửa quota. Ba hướng, theo thứ tự rẻ nhất trước:")
        print(f"    1. Hạ ngân sách token xuống 2.048 — đo ở T05 chỉ cắt thêm 1,09 % mẫu "
              f"ISE-DSC01. Ước từ chính các mức đã đo: còn khoảng {capped_hours:.1f} giờ. "
              f"Chạy lại với --max-context-tokens 2048 để có số thật.")
        print("    2. Lấy mẫu con ISE-DSC01 — nó chiếm phần lớn chi phí và chỉ dùng cho E06, "
              "E07, E16.")
        print("    3. Lùi Qwen2.5-3B theo nấc 4 của mục 5 CLAUDE.md — nhưng đây là đổi mô "
              "hình đọc chính, phải hỏi trước.")

    # -- log ------------------------------------------------------------------------------
    config = {
        "extractor": {
            "model_name": args.model,
            "quantization": "nf4",
            "max_context_tokens": args.max_context_tokens,
            "device": "cuda",
            "compute_dtype": args.compute_dtype,
            "exclude_layers": sorted(args.exclude_layers or []),
        },
        "measurement": {
            "tier_bounds": list(TIER_BOUNDS),
            "per_tier": args.per_tier,
            "sample_pool": ["vihallu", "isedsc01"],
        },
    }
    metrics = {
        "tiers": {
            tier_label(tier): summaries[tier] for tier in sorted(summaries)
        },
        "length_scaling_exponent": slope,
        "projected_hours": {
            name: seconds / 3600 for name, seconds in projections.items()
        },
        "projected_hours_core": core_hours,
        "projected_hours_all": total_seconds / 3600,
        "tier_histogram": {
            name: {tier_label(tier): count for tier, count in histogram.items()}
            for name, histogram in histograms.items()
        },
        "fits_half_weekly_quota": fits,
    }
    extra = {
        "ms_per_sample": total_seconds / total_samples * 1000,
        "peak_vram_mb": peak_vram,
        "n_samples_timed": sum(item["n_samples"] for item in summaries.values()),
        "n_layers_hooked": len(extractor.layer_indices),
        "weekly_gpu_hours": WEEKLY_GPU_HOURS,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    }
    if readings:
        throttled, reason = throttling_verdict(readings)
        extra["gpu_throttled"] = throttled
        extra["gpu_throttle_reason"] = reason
        extra["gpu_telemetry"] = readings
    record = log_result(run_name, config, metrics, extra, path=args.results_path)
    print()
    print(f"  Đã ghi vào {args.results_path} — run_name {record['run_name']}, "
          f"config_hash {record['config_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
