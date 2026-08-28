"""Task T19, experiment E10: an LLM judge as a baseline, on Gemini's free tier.

This is the third kind of baseline in Bảng 1 and the one the cost argument of CH2 is really
aimed at. E01 reads nothing, E09 reads the text but has to be fine-tuned first, and this one
reads the text with no training at all — for the price of an API call per sample and a network
round trip. If the attention method cannot beat a judge that costs nothing to build, the thesis
has a problem; if it matches one while running locally, that is the argument.

Usage:
    python scripts/run_judge_baseline.py                 # 300 mẫu, gemini-3.1-flash-lite
    python scripts/run_judge_baseline.py --limit 50      # thử nhỏ trước
    python scripts/run_judge_baseline.py --dry-run       # không gọi API, chỉ dùng cache

The key comes from ``.env`` via python-dotenv, per section 2 of CLAUDE.md. Answers are cached,
so re-running costs nothing and a run stopped by the daily quota resumes where it left off.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import REQUIRED_SPLIT_SEED  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.data.splits import shuffle_order  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.evaluation.logging import log_result  # noqa: E402
from vihallulens.evaluation.metrics import (  # noqa: E402
    LABELS,
    bootstrap_ci,
    compute_metrics,
    expected_calibration_error,
)
from vihallulens.features.surface import surface_features  # noqa: E402
from vihallulens.judge.cache import JudgeCache, cache_key  # noqa: E402
from vihallulens.judge.client import (  # noqa: E402
    DEFAULT_MODEL,
    DEFAULT_RPM,
    GeminiError,
    GeminiJudge,
    QuotaExhaustedError,
)
from vihallulens.judge.prompt import (  # noqa: E402
    RESPONSE_SCHEMA,
    SYSTEM,
    build_prompt,
    clamp_confidence,
    to_label,
)

RUN_NAME = "e10_gemini_judge"

# Section T19 of TASKS.md caps the sample at 300. The free tier is the reason: a daily
# allowance in the low hundreds makes the whole 700-sample test set a multi-day run for a
# number that is only a baseline.
DEFAULT_LIMIT = 300

# What a judge does when it cannot be read: an unparseable answer still has to become a label,
# or the sample silently vanishes and macro-F1 is computed on a set nobody chose. The majority
# class is the least flattering choice available, and it is counted and reported.
FALLBACK_LABEL = "intrinsic"

PROGRESS_EVERY = 25


def choose_samples(frame, limit: int, seed: int = REQUIRED_SPLIT_SEED):
    """Take a fixed pseudo-random subset of the test split.

    The same SHA-256 ordering the splits use, for the same reason: the subset has to be
    identical on every machine and in every re-run, or the cache misses and the number moves.
    Taking the first N rows instead would follow whatever order the Parquet file was written in.
    """
    if limit >= len(frame):
        return frame.reset_index(drop=True)
    wanted = set(shuffle_order(frame["sample_id"], seed)[:limit])
    picked = frame[frame["sample_id"].isin(wanted)]
    return picked.sort_values("sample_id").reset_index(drop=True)


def judge_one(judge, cache, row, model: str) -> tuple[dict, bool]:
    """One verdict, from the cache when possible. Returns the record and whether it was fresh.

    ``model`` is passed in rather than read off ``judge``, because a dry run has no judge and
    still has to look in the same drawer. The first version derived the name from the object and
    fell back to the string ``"dry-run"``, so ``--dry-run`` computed a key that could never
    match anything and reported all 300 samples as missing from a cache that held all 300.
    """
    prompt = build_prompt(row["context"], row["response"], row.get("question", ""))
    cached = cache.get(cache_key(model, prompt))
    if cached is not None:
        return cached, False
    if judge is None:
        return {"sample_id": row["sample_id"], "error": "chưa có trong cache"}, False

    answer = judge.ask(SYSTEM, prompt, RESPONSE_SCHEMA)
    record = {
        "sample_id": row["sample_id"],
        "model": model,
        "verdict": answer.get("nhan_dinh"),
        "confidence": clamp_confidence(answer.get("do_tin_cay")),
        "reason": str(answer.get("ly_do", ""))[:500],
    }
    return cache.put(cache_key(model, prompt), record), True


def surface_anchor(interim_dir: Path, dataset: str, chosen) -> dict | None:
    """E01 scored on exactly the samples the judge saw.

    Without it the judge's score floats free: every other row of Bảng 1 is measured on all 700
    test samples, and a number from a different 300 cannot be compared with them by eye. E01 is
    two features and a logistic regression, so recomputing it on the subset costs a second and
    turns the judge's row into something a reader can place.

    The whole metric set is returned, not just macro-F1, so the binary view of both methods is
    compared on the same 300 samples too. Comparing a binary score from 300 against one from
    700 would repeat the very mistake this anchor exists to prevent.
    """
    try:
        train = load_dataset(dataset, "train", interim_dir)
    except FileNotFoundError:
        return None
    detector = LookbackDetector(seed=REQUIRED_SPLIT_SEED).fit(
        surface_features(train), train["label"].to_numpy()
    )
    predicted = detector.predict(surface_features(chosen))
    return compute_metrics(chosen["label"].to_numpy(), predicted)


def as_probabilities(y_pred, confidence) -> tuple[np.ndarray, int]:
    """Spread a self-reported confidence over the three classes.

    The judge names one label and says how sure it is; the remaining mass is split evenly over
    the other two, which is the only assumption available and is stated rather than hidden.

    Confidence is floored just above ``1/3`` so the named label stays the argmax. Below that the
    answer contradicts itself — less sure of the label it chose than of each label it rejected —
    and leaving it alone would make the calibration figure score a *different* prediction than
    the one being reported. The count of floored answers is returned and printed.
    """
    floor = 1.0 / len(LABELS) + 1e-6
    proba = np.zeros((len(y_pred), len(LABELS)))
    floored = 0
    for index, (label, score) in enumerate(zip(y_pred, confidence, strict=True)):
        if score < floor:
            score, floored = floor, floored + 1
        proba[index] = (1.0 - score) / (len(LABELS) - 1)
        proba[index][LABELS.index(label)] = score
    return proba, floored


def main() -> int:
    parser = argparse.ArgumentParser(description="E10: baseline LLM giám khảo trên Gemini.")
    parser.add_argument("--dataset", default="vihallu")
    parser.add_argument("--split", default="test")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--rpm", type=int, default=DEFAULT_RPM,
                        help="số lượt gọi mỗi phút; để dưới hạn mức free tier")
    parser.add_argument("--dry-run", action="store_true",
                        help="không gọi API, chỉ chấm những mẫu đã có trong cache")
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--cache-path", type=Path, default=Path("results/judge_cache.jsonl"))
    parser.add_argument("--results-path", type=Path, default=Path("results/runs.jsonl"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from dotenv import load_dotenv

    load_dotenv()

    frame = load_dataset(args.dataset, args.split, args.interim_dir)
    chosen = choose_samples(frame, args.limit)
    cache = JudgeCache(args.cache_path)

    print()
    print("=" * 80)
    print("T19 / E10 — BASELINE LLM GIÁM KHẢO")
    print("=" * 80)
    print(f"  mô hình               : {args.model}")
    print(f"  bộ dữ liệu            : {args.dataset}/{args.split}")
    print(f"  cỡ mẫu                : {len(chosen):,} / {len(frame):,} mẫu test")
    print(f"  nhịp gọi              : {args.rpm} lượt/phút")
    print(f"  cache                 : {args.cache_path} ({len(cache):,} câu trả lời sẵn có)")

    judge = None
    if args.dry_run:
        print("  chế độ                : DRY RUN, không gọi API")
    else:
        try:
            judge = GeminiJudge(os.getenv("GEMINI_API_KEY", ""), args.model, args.rpm)
        except ValueError as error:
            print(f"\n  {error}")
            return 1

    started = time.perf_counter()
    records, fresh, failed = [], 0, 0
    stopped_early = None
    for position, row in enumerate(chosen.to_dict("records"), start=1):
        try:
            record, is_fresh = judge_one(judge, cache, row, args.model)
        except QuotaExhaustedError as error:
            stopped_early = str(error)
            break
        except GeminiError as error:
            record, is_fresh = {"sample_id": row["sample_id"], "error": str(error)[:200]}, False
            failed += 1
            # The first one, in full. A run that fails on every sample has one cause, and
            # printing only a count leaves nothing to diagnose it with — which is exactly how
            # a withdrawn model name cost twelve identical failures at T19.
            if failed == 1:
                print()
                print(f"  LỖI ĐẦU TIÊN ({row['sample_id']}): {error}")
        records.append(record)
        fresh += int(is_fresh)
        if position % PROGRESS_EVERY == 0 or position == len(chosen):
            print(f"      {position:>4}/{len(chosen)}  gọi mới {fresh:,}  lỗi {failed:,}",
                  end="\r")
    elapsed = time.perf_counter() - started
    print()

    if stopped_early:
        print()
        print("  DỪNG VÌ HẾT HẠN MỨC THEO NGÀY")
        print(f"  {stopped_early.splitlines()[0]}")
        print(f"  Đã chấm {len(records):,}/{len(chosen):,} mẫu và lưu hết vào cache.")
        print("  Chạy lại đúng lệnh này ngày mai, nó đi tiếp từ chỗ dừng.")
        return 2

    scored = [record for record in records if record.get("verdict")]
    if len(scored) < len(chosen):
        print(f"  THIẾU {len(chosen) - len(scored):,} mẫu chưa có câu trả lời.")
        if args.dry_run:
            print("  Đang ở chế độ dry run — bỏ cờ --dry-run để gọi API cho những mẫu còn lại.")
        return 1

    # -- scoring --------------------------------------------------------------------------

    y_true = chosen["label"].to_numpy()
    unreadable = 0
    y_pred, confidence = [], []
    for record in scored:
        try:
            y_pred.append(to_label(record["verdict"]))
        except ValueError:
            y_pred.append(FALLBACK_LABEL)
            unreadable += 1
        confidence.append(float(record.get("confidence", 0.0)))
    y_pred = np.asarray(y_pred)

    point = compute_metrics(y_true, y_pred)
    spread = bootstrap_ci(y_true, y_pred, seed=REQUIRED_SPLIT_SEED)
    # Self-reported confidence, not a softmax. Kept out of the ECE column of Bảng 1 on purpose:
    # filing two different quantities under one name is the mistake T18 had to undo twice.
    proba, floored = as_probabilities(y_pred, confidence)
    ece_self = expected_calibration_error(y_true, proba)

    print()
    print("-" * 80)
    print(f"KẾT QUẢ — trên {len(y_pred):,} mẫu")
    print("-" * 80)
    print(f"  {'Chỉ số':<14} {'Giá trị':>9}   {'khoảng tin cậy 95 %':>21}")
    for key in ("macro_f1", "accuracy", *[f"f1_{label}" for label in LABELS]):
        print(f"  {key:<14} {point[key]:>9.4f}   [{spread[f'{key}_lo']:.4f}, "
              f"{spread[f'{key}_hi']:.4f}]")

    print()
    print(f"  Gọi API mới               : {fresh:,}  (còn lại lấy từ cache)")
    print(f"  Thời gian                 : {elapsed / 60:.1f} phút, "
          f"{elapsed * 1000 / max(len(y_pred), 1):,.0f} ms/mẫu kể cả chờ nhịp")
    print(f"  Câu trả lời không đọc được: {unreadable:,} (gán về '{FALLBACK_LABEL}')")
    print(f"  Độ tin cậy tự khai        : trung bình {np.mean(confidence):.3f}, "
          f"ECE {ece_self:.4f}"
          + (f", {floored:,} câu khai dưới 1/3 đã nâng lên sàn" if floored else ""))
    print("  ECE trên KHÔNG so thẳng được với ECE của E01 và E09: đó là xác suất softmax,")
    print("  còn đây là con số mô hình tự khai. Hai đại lượng khác nhau, để riêng.")

    print()
    print("-" * 80)
    print("CHỈ CÒN HỎI CÓ ẢO GIÁC HAY KHÔNG — gộp nội tại và ngoại lai làm một")
    print("-" * 80)
    print(f"  macro-F1 nhị phân : {point['binary_macro_f1']:.4f}  "
          f"(so với {point['macro_f1']:.4f} khi phải gọi đúng tên loại)")
    print(f"  bắt được          : {point['binary_recall']:.4f} số mẫu có ảo giác")
    print(f"  báo đúng          : {point['binary_precision']:.4f} số lần báo động là thật")

    anchor = surface_anchor(args.interim_dir, args.dataset, chosen)
    if anchor is not None:
        print()
        print(f"  Neo so sánh trên ĐÚNG {len(chosen):,} mẫu này:")
        print(f"  {'':<14}{'ba lớp':>9}{'nhị phân':>11}{'bắt được':>11}")
        for label, scores in (("E01 bề mặt", anchor), ("Gemini", point)):
            print(f"  {label:<14}{scores['macro_f1']:>9.4f}{scores['binary_macro_f1']:>11.4f}"
                  f"{scores['binary_recall']:>11.4f}")
        print("  Các dòng khác của Bảng 1 đo trên cả 700 mẫu test nên không so thẳng được;")
        print("  neo này để biết con số trên hơn hay kém baseline tầm thường trên cùng mẫu.")

    config = {
        "experiment": "E10",
        "dataset": {"name": args.dataset, "split_seed": REQUIRED_SPLIT_SEED},
        "judge": {"model": args.model, "temperature": 0.0, "limit": args.limit},
    }
    extra = {
        "n_test": len(y_pred),
        "n_test_full_split": len(frame),
        "subset_note": f"{len(y_pred)}/{len(frame)} mẫu test, chọn tất định theo SHA-256",
        "n_api_calls": fresh,
        "n_unreadable": unreadable,
        "ms_per_sample": elapsed * 1000 / max(len(y_pred), 1),
        "peak_vram_mb": 0.0,
        "n_params_trainable": 0,
        "confidence_mean": float(np.mean(confidence)),
        "ece_self_reported": ece_self,
        "n_confidence_floored": floored,
        "e01_same_subset": anchor,
        # Raw predictions, so any metric thought of later can be computed without paying for
        # the run again. T19 needed exactly this and E09 did not have it.
        "y_pred": list(y_pred),
        "sample_ids": list(chosen["sample_id"]),
        "std_method": "_lo/_hi/_se từ bootstrap tập con; không có seed nào để lấy _std",
    }
    if not fresh:
        # A run served entirely from cache measured cache lookups, not the API. Writing it would
        # overwrite the cost columns of Bảng 1 with a number three orders of magnitude too small
        # — which is exactly what happened once: a verification dry run replaced 8.194 ms/mẫu
        # with 0,03. Verification prints the table; it does not get to rewrite the record.
        print()
        print("  Không ghi vào runs.jsonl: lượt này lấy hết từ cache nên không đo được chi phí")
        print("  thật. Bản ghi của lượt gọi API vẫn giữ nguyên, và bảng trên khớp với nó là")
        print("  đúng thứ cần kiểm.")
        return 0

    record = log_result(RUN_NAME, config, {**point, **spread}, extra, path=args.results_path)
    print()
    print(f"  Đã ghi {args.results_path} — config_hash {record['config_hash']}")
    print(f"  Cache: {len(cache):,} câu trả lời, {cache.writes:,} mới ghi lần này")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
