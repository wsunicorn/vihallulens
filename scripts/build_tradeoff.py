"""Build the accuracy-versus-cost table of E11 (task T32).

The table is the centre of chapter 7, and the only reason it needs a script rather than a typed
markdown block is that **its cost column comes from two files that measure different things**.

``results/runs.jsonl`` stores, for every scored run, the cost of the *classifier*: a logistic
regression over a few hundred numbers, which runs on CPU in microseconds and reports
``peak_vram_mb`` of 0. That figure is real but it is not what the method costs. What the method
costs is the pass of the reading model that produces the attention matrices, and that lives in
``results/feasibility.jsonl`` — measured per length tier and then weighted by the true length
histogram of each corpus.

Reading only the first file understates the attention rows by five orders of magnitude. Reading
only the second omits every baseline that has no reading model at all. So the join is the work,
and doing it by hand once into a markdown table is how a wrong number ends up in a thesis.

Three further decisions are baked in here rather than left to whoever formats the table:

1. **The three kinds of cost are not the same unit** and are never summed into one number. Local
   GPU for the reading model, local GPU for a fine-tuned encoder, and external API calls for the
   judge are different things to a person deciding what to deploy. The ``chi_phi`` column names
   which kind each row pays.
2. **Marginal cost is an argument, not a measurement.** The thesis claims that inside a real RAG
   system the reading pass happens anyway, so the marginal cost of these features is near zero.
   That claim is not tested by any experiment here, so it gets its own clearly labelled column
   instead of being quietly folded into the headline number.
3. **A missing measurement stays missing.** Sailor2-8B was never timed under the interleaved
   regime of T31, so its cost cells read "chưa đo" rather than borrowing the Qwen2.5-7B figure
   from a model of similar size.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

DEFAULT_RUNS = Path("results/runs.jsonl")
DEFAULT_FEASIBILITY = Path("results/feasibility.jsonl")
DEFAULT_OUT = Path("results/tradeoff.csv")

# Cost kinds. Kept as text rather than a boolean because "needs a GPU" and "needs an API key"
# are different obstacles to a person deploying this, and collapsing them loses that.
GPU_DOC = "GPU cục bộ, lượt đọc"
GPU_MAHOA = "GPU cục bộ, bộ mã hóa"
CPU = "chỉ CPU"
API = "API ngoài"

# Each row of the table: which scored run it comes from, and which reading model pays for it.
# ``doc`` is None when the method has no reading model, so its only cost is the row's own.
ROWS: tuple[dict, ...] = (
    {"ten": "Baseline bề mặt (E01)", "run": "e01_surface_baseline", "doc": None, "loai": CPU},
    {"ten": "Gemini giám khảo (E10)", "run": "e10_gemini_judge", "doc": None, "loai": API},
    {"ten": "PhoBERT-large tinh chỉnh (E09)", "run": "e09_phobert", "doc": None, "loai": GPU_MAHOA},
    {"ten": "XLM-R-large tinh chỉnh (E09)", "run": "e09_xlmr", "doc": None, "loai": GPU_MAHOA},
    {"ten": "Lookback gộp, Qwen2.5-7B (E02)", "run": "e02_lookback_lens", "doc": "7B",
     "loai": GPU_DOC},
    {"ten": "Chunk-aware, Qwen2.5-7B (E03)", "run": "e03_chunk_aware", "doc": "7B",
     "loai": GPU_DOC},
    {"ten": "Lookback gộp, Qwen2.5-3B (E14)", "run": "e14_baseline_lookback_qwen3b", "doc": "3B",
     "loai": GPU_DOC},
    {"ten": "Chunk-aware, Qwen2.5-3B (E14)", "run": "e14_qwen3b_vihallu", "doc": "3B",
     "loai": GPU_DOC},
    {"ten": "Lookback gộp, Qwen2.5-1.5B (E14)", "run": "e14_baseline_lookback_qwen15b",
     "doc": "1_5B", "loai": GPU_DOC},
    {"ten": "Chunk-aware, Qwen2.5-1.5B (E14)", "run": "e14_qwen15b_vihallu", "doc": "1_5B",
     "loai": GPU_DOC},
    {"ten": "Lookback gộp, Sailor2-8B (E13)", "run": "e13_baseline_lookback_sailor2",
     "doc": "sailor2", "loai": GPU_DOC},
    {"ten": "Chunk-aware, Sailor2-8B (E13)", "run": "e13_sailor2_vihallu", "doc": "sailor2",
     "loai": GPU_DOC},
)

# Reading models, and the interleaved T31 rounds that timed each one. Sailor2 has no entry: it
# was extracted at T30 but never timed under the interleaved regime, and a cost cell that
# silently borrows a similar model's number is worse than an empty one.
DOC_RUNS: dict[str, tuple[str, ...]] = {
    "7B": ("t31_chiphi_7B_lan1", "t31_chiphi_7B_lan2"),
    "3B": ("t31_chiphi_3B_lan1", "t31_chiphi_3B_lan2"),
    "1_5B": ("t31_chiphi_1_5B_lan1", "t31_chiphi_1_5B_lan2"),
}

SECONDS_PER_HOUR = 3600
MS_PER_SECOND = 1000


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def latest_by_name(rows: list[dict]) -> dict[str, dict]:
    """Last row wins, so re-running an experiment updates the table without editing it."""
    table: dict[str, dict] = {}
    for row in rows:
        name = row.get("run_name")
        if name:
            table[name] = row
    return table


def doc_cost(feasibility: dict[str, dict], key: str, dataset: str = "vihallu") -> dict | None:
    """Reading-model cost on one corpus, averaged over the interleaved passes.

    The per-sample figure is derived from ``projected_hours[dataset]`` rather than from the
    stored ``ms_per_sample``, because the latter is weighted over *every* corpus while the table
    reports one. ViHallu is short — 6.461 of 7.000 samples sit in the shortest tier — so the
    all-corpus figure would overstate this table by roughly 70 %.
    """
    names = [n for n in DOC_RUNS.get(key, ()) if n in feasibility]
    if not names:
        return None
    per_sample, vram, drift = [], [], []
    for name in names:
        row = feasibility[name]
        hours = row["metrics"]["projected_hours"][dataset]
        n_samples = sum(row["metrics"]["tier_histogram"][dataset].values())
        per_sample.append(hours * SECONDS_PER_HOUR * MS_PER_SECOND / n_samples)
        vram.append(row["extra"]["peak_vram_mb"])
        drift.append(row["extra"]["ms_per_sample"])
    spread = (max(drift) - min(drift)) / min(drift) * 100 if len(drift) > 1 else float("nan")
    return {
        "ms": sum(per_sample) / len(per_sample),
        "vram_mb": max(vram),
        "n_luot": len(names),
        "troi_pct": spread,
    }


def build(runs: dict[str, dict], feasibility: dict[str, dict]) -> list[dict]:
    out = []
    for spec in ROWS:
        run = runs.get(spec["run"])
        if run is None:
            continue
        extra = run.get("extra") or {}
        metrics = run["metrics"]
        cost = doc_cost(feasibility, spec["doc"]) if spec["doc"] else None

        if spec["doc"]:
            # Attention rows: the reading pass dominates and the classifier is noise beside it.
            ms = cost["ms"] if cost else None
            vram = cost["vram_mb"] if cost else None
        else:
            ms = extra.get("ms_per_sample")
            vram = extra.get("peak_vram_mb")

        out.append({
            "phuong_phap": spec["ten"],
            "run_name": spec["run"],
            "macro_f1": metrics["macro_f1"],
            "macro_f1_lo": metrics["macro_f1_lo"],
            "macro_f1_hi": metrics["macro_f1_hi"],
            "ms_moi_mau": ms,
            "vram_mb": vram,
            "tham_so_huan_luyen": extra.get("n_params_trainable"),
            "loai_chi_phi": spec["loai"],
            "ms_bien": 0.0 if spec["doc"] else ms,
            "ms_bo_phan_loai": extra.get("ms_per_sample") if spec["doc"] else None,
            "troi_giua_hai_luot_pct": cost["troi_pct"] if cost else None,
        })
    return out


def so(value, dang="{:.1f}") -> str:
    return "chưa đo" if value is None else dang.format(value)


def render(table: list[dict]) -> str:
    lines = [
        "| Phương pháp | macro-F1 [KTC 95 %] | ms/mẫu | VRAM đỉnh | Tham số huấn luyện "
        "| Loại chi phí |",
        "|---|---|---|---|---|---|",
    ]
    for row in table:
        vram = "—" if row["vram_mb"] == 0 else so(row["vram_mb"], "{:,.0f} MB")
        thamso = "—" if row["tham_so_huan_luyen"] is None else f"{row['tham_so_huan_luyen']:,}"
        lines.append(
            f"| {row['phuong_phap']} | {row['macro_f1']:.4f} "
            f"[{row['macro_f1_lo']:.4f}–{row['macro_f1_hi']:.4f}] | "
            f"{so(row['ms_moi_mau'], '{:,.1f}')} | {vram} | {thamso} | {row['loai_chi_phi']} |"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bảng đánh đổi độ chính xác và chi phí (E11).")
    parser.add_argument("--runs-path", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--feasibility-path", type=Path, default=DEFAULT_FEASIBILITY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dataset", default="vihallu")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    runs = latest_by_name(load_jsonl(args.runs_path))
    feasibility = latest_by_name(load_jsonl(args.feasibility_path))
    table = build(runs, feasibility)

    print()
    print("=" * 80)
    print(f"E11 — BẢNG ĐÁNH ĐỔI ĐỘ CHÍNH XÁC VÀ CHI PHÍ  ({args.dataset})")
    print("=" * 80)
    print(f"  nguồn độ chính xác : {args.runs_path}")
    print(f"  nguồn chi phí đọc  : {args.feasibility_path}")
    print(f"  số dòng            : {len(table)}/{len(ROWS)}")
    print()
    print(render(table))

    thieu = [row["phuong_phap"] for row in table if row["ms_moi_mau"] is None]
    if thieu:
        print()
        print("  Chưa đo chi phí, để trống thay vì mượn số của mô hình khác:")
        for ten in thieu:
            print(f"    - {ten}")

    print()
    print("-" * 80)
    print("HAI CỘT CHI PHÍ, VÀ CỘT THỨ HAI LÀ LẬP LUẬN CHỨ KHÔNG PHẢI PHÉP ĐO")
    print("-" * 80)
    print("  Cột ms/mẫu ở trên là chi phí TUYỆT ĐỐI: chạy lượt đọc từ đầu chỉ để chấm.")
    print("  Đề tài lập luận rằng trong một hệ RAG thật, lượt đọc ấy dù sao cũng phải chạy,")
    print("  nên chi phí BIÊN của các đặc trưng này gần bằng 0 — chỉ thêm phần cộng dồn")
    print("  trong hook và một hồi quy logistic vài trăm chiều.")
    print()
    print(f"  {'Phương pháp':<36}{'tuyệt đối':>12}{'biên':>10}   (ms mỗi mẫu)")
    for row in table:
        if row["ms_bo_phan_loai"] is None:
            continue
        print(f"  {row['phuong_phap']:<36}{so(row['ms_moi_mau'], '{:,.1f}'):>12}"
              f"{row['ms_bo_phan_loai']:>10.3f}")
    print()
    print("  KHÔNG thí nghiệm nào ở đây đo được cột biên — nó đòi một hệ RAG đầu cuối, và")
    print("  T40 mới dựng cái đó. Trình bày thì phải nói rõ, đừng gộp hai cột làm một.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    print()
    print(f"  Đã ghi {args.out} — {len(table)} dòng")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
