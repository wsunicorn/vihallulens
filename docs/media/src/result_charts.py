"""Seven result charts of chapters 6 and 7, drawn straight from ``results/``.

Unlike ``charts.py``, no number is typed in here: each chart reads the run logs or the files that
``scripts/build_figure_data.py`` condenses from the feature shards.

Run:  python docs/media/src/result_charts.py
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from charts import (
    BLUE,
    GRAY,
    LIGHT,
    NAVY,
    ORANGE,
    RED,
    TEAL,
    save,
    vn_axis,
    vnum,
)
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import FuncFormatter, MultipleLocator

RESULTS = Path(__file__).resolve().parents[3] / "results"
INK = "#2b2b31"
MUTED = "#3f3f46"


def load(name: str):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def runs() -> dict[str, dict]:
    """Run name to its latest record — the same rule run_paired_tests.py reads the log by."""
    out = {}
    for line in (RESULTS / "runs.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        out[row["run_name"]] = row
    return out


def signed(x: float, nd: int = 3) -> str:
    return ("+" if x >= 0 else "−") + vnum(abs(x), nd)


def interval(lo: float, hi: float, nd: int = 3) -> str:
    return f"[{signed(lo, nd)}; {signed(hi, nd)}]"


# =========================================================================
# 1. hit@1 of every attention head, on two corpora (E06, E08)
# =========================================================================
def chart_head_map() -> None:
    data = load("figures/head_hit1.json")
    panels = [("ISE-DSC01 (E06), 22,6 đoạn", data["isedsc01"]),
              ("ViWikiFC (E08), 9,8 đoạn", data["viwikifc"])]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.5), sharey=True)
    for ax, (title, block) in zip(axes, panels, strict=True):
        grid = np.asarray(block["grid"])
        im = ax.imshow(grid, cmap="Blues", vmin=0, vmax=0.9, aspect="equal")
        layer, head = np.unravel_index(grid.argmax(), grid.shape)
        ax.add_patch(Rectangle((head - 0.5, layer - 0.5), 1, 1, fill=False, edgecolor=RED,
                               linewidth=1.6))
        ax.set_title(f"{title}\nô đỏ: lớp {layer}, đầu {head} ({vnum(grid.max(), 3)})",
                     fontsize=10.5)
        ax.set_xlabel("Chỉ số đầu chú ý")
        ax.set_xticks(range(0, 28, 5))
        ax.set_yticks(range(0, 27, 5))
        ax.grid(False)
    axes[0].set_ylabel("Chỉ số lớp")
    bar = fig.colorbar(im, ax=axes, orientation="horizontal", fraction=0.05, pad=0.2, aspect=38)
    bar.set_label("hit@1 (mức ngẫu nhiên: 0,061 trên ISE-DSC01; 0,103 trên ViWikiFC)")
    bar.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
    save(fig, "bieudo_ban_do_dau_chu_y")


# =========================================================================
# 2. How each pair changed when the evidence sentence was taken away (E08)
# =========================================================================
def chart_evidence_removed() -> None:
    data = load("figures/e08_changes.json")
    edges = np.asarray(data["edges"])
    mid, width = (edges[:-1] + edges[1:]) / 2, edges[1] - edges[0]
    names = [("chunk_entropy", "ENT"), ("chunk_gini", "GINI"), ("chunk_max_share", "MAX"),
             ("top1_top2_gap", "GAP")]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.8), sharex=True, sharey=True)
    for ax, (key, short) in zip(axes.ravel(), names, strict=True):
        block = data["features"][key]
        share = np.asarray(block["counts"]) / data["n_pairs"] * 100
        toward = mid * block["direction"] > 0
        ax.bar(mid, share, width, color=np.where(toward, BLUE, LIGHT), edgecolor="white",
               linewidth=0.4)
        ax.axvline(0, color=INK, linewidth=0.9)
        word = "tăng" if block["direction"] > 0 else "giảm"
        ax.set_title(f"{short} (dự đoán: {word})", fontsize=11)
        right = block["direction"] > 0
        ax.text(0.97 if right else 0.03, 0.93,
                f"{vnum(block['aligned'] * 100, 1)} %\nsố cặp", transform=ax.transAxes,
                ha="right" if right else "left", va="top", fontsize=10.5, color=INK)
        ax.set_xlim(-0.13, 0.13)
        ax.xaxis.set_major_locator(MultipleLocator(0.05))
        ax.xaxis.set_major_formatter(FuncFormatter(
            lambda v, _: f"{v:.2f}".replace(".", ",").replace("-", "−")))
        ax.yaxis.set_major_locator(MultipleLocator(2))
        ax.grid(axis="x", visible=False)
        ax.set_axisbelow(True)
    for ax in axes[:, 0]:
        ax.set_ylabel("Tỷ lệ cặp (%)")
    for ax in axes[1]:
        ax.set_xlabel("Giá trị khi mất bằng chứng\ntrừ giá trị khi có bằng chứng")
    fig.legend(handles=[Patch(color=BLUE, label="thay đổi đúng hướng dự đoán"),
                        Patch(color=LIGHT, label="thay đổi ngược hướng")],
               frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.99), ncols=2,
               fontsize=10)
    save(fig, "bieudo_thay_doi_khi_mat_bang_chung", relayout=fig.tight_layout)


# =========================================================================
# 3. Locating the evidence: attention against ablating the context (E19)
# =========================================================================
def chart_attribution() -> None:
    logged = runs()["e19_attribution_viwikifc"]["extra"]["rows"]

    def row(start: str) -> dict:
        return next(v for k, v in logged.items() if k.startswith(start))

    picked = [("Trung bình 756 đầu", "trung bình", ORANGE, "1 lượt đọc"),
              ("Cắt bỏ ngữ cảnh\n(ARC-JSD)", "cắt bỏ", TEAL, "10,9 lượt đọc"),
              ("Đầu chọn trên ISE-DSC01\n(lớp 14, đầu 6)", "đầu E06", BLUE, "1 lượt đọc"),
              ("Đầu định vị tốt nhất\n(lớp 19, đầu 20)", "đầu mạnh nhất", NAVY, "1 lượt đọc")]
    rows = [("Mức ngẫu nhiên", row("cắt bỏ")["floor@1"], None, None, GRAY, "")]
    rows += [(name, r["hit@1"], r["hit@1_low"], r["hit@1_high"], color, cost)
             for name, start, color, cost in picked for r in (row(start),)]
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    for y, (_, value, lo, hi, color, cost) in enumerate(rows):
        ax.barh(y, value, height=0.56, color=color, edgecolor=INK, linewidth=0.6)
        if lo is not None:
            ax.errorbar(value, y, xerr=[[value - lo], [hi - value]], fmt="none", ecolor=INK,
                        elinewidth=1.1, capsize=3.5)
        ax.text((hi or value) + 0.015, y, vnum(value, 3), va="center", fontsize=10.5)
        ax.text(1.34, y, cost, va="center", ha="right", fontsize=10, color=MUTED)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=10)
    ax.set_xlim(0, 1.36)
    ax.set_xticks(np.arange(0, 1.01, 0.2))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
    ax.set_xlabel("hit@1 với khoảng tin cậy 95 % (300 mẫu ViWikiFC)")
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_dinh_vi_va_cat_bo")


# =========================================================================
# 4. The paired differences H2 rests on, all eight settings (T22B)
# =========================================================================
def chart_paired() -> None:
    rows = load("paired_tests.json")["h2"]
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    ys = np.arange(len(rows))[::-1]
    for y, row in zip(ys, rows, strict=True):
        ax.plot([row["lo"], row["hi"]], [y, y], color=NAVY, linewidth=2.0, zorder=2,
                solid_capstyle="butt")
        ax.scatter(row["delta"], y, s=52, marker="s", color=RED, edgecolor="white", linewidth=1.0,
                   zorder=3)
        ax.text(0.066, y, f"{signed(row['delta'], 4)}", fontsize=10, va="center", ha="left")
        ax.text(0.126, y, vnum(row["p_holm"], 2), fontsize=10, va="center", ha="right")
    top = len(rows) - 0.35
    ax.text(0.066, top, "Hiệu", fontsize=10, va="bottom", ha="left", weight="bold")
    ax.text(0.126, top, "p (Holm)", fontsize=10, va="bottom", ha="right", weight="bold")
    ax.axvline(0, color=INK, linewidth=1.0)
    ax.set_yticks(ys, [r["name"] for r in rows], fontsize=10)
    ax.set_xlim(-0.062, 0.128)
    ax.set_ylim(-0.95, len(rows) + 0.25)
    ax.set_xticks([-0.05, 0, 0.05])
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda v, _: f"{v:+.2f}".replace(".", ",").replace("-", "−") if abs(v) > 1e-9 else "0"))
    ax.set_xlabel("Hiệu macro-F1 (KTC 95 % ghép cặp)")
    ax.xaxis.set_label_coords(0.33, -0.13)
    ax.text(-0.003, -0.62, "← lookback cao hơn", fontsize=9.5, ha="right", va="center",
            color=MUTED)
    ax.text(0.003, -0.62, "chunk-aware cao hơn →", fontsize=9.5, ha="left", va="center",
            color=MUTED)
    ax.grid(axis="y", visible=False)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_axisbelow(True)
    save(fig, "bieudo_hieu_ghep_cap")


# =========================================================================
# 5. Adding one feature group at a time (E12)
# =========================================================================
def chart_feature_groups() -> None:
    log = runs()
    steps = ["Bề\nmặt", "+ Look-\nback", "+ Chunk-\naware", "+\nDRIFT"]
    panels = [("ViHallu", "vihallu", (0.60, 0.83)), ("ISE-DSC01", "isedsc01", (0.43, 0.86))]
    lines = [("", "chọn cách gộp đầu riêng ở từng bước", NAVY, "o", "-"),
             ("_gopchung", "cố định 32 đầu", ORANGE, "s", "--")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.9))
    for ax, (title, key, ylim) in zip(axes, panels, strict=True):
        series = []
        for suffix, label, color, marker, style in lines:
            levels = log[f"e12_ablation_{key}{suffix}"]["extra"]["ablation"]
            series.append([lv["macro_f1"] for lv in levels])
            err = np.array([[lv["macro_f1"] - lv["ci_low"] for lv in levels],
                            [lv["ci_high"] - lv["macro_f1"] for lv in levels]])
            shift = -0.07 if not suffix else 0.07
            ax.errorbar(np.arange(4) + shift, series[-1], yerr=err, color=color, marker=marker,
                        markersize=7, linestyle=style, linewidth=1.8, elinewidth=0.9, capsize=2.5,
                        markeredgecolor="white", label=label)
        ax.set_title(title, fontsize=11.5)
        ax.set_xticks(range(4), steps, fontsize=9.5)
        ax.set_xlim(-0.35, 3.35)
        ax.set_ylim(*ylim)
        vn_axis(ax.yaxis)
        ax.grid(axis="x", visible=False)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("macro-F1 trên tập test (KTC 95 %)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.97),
               ncols=2, fontsize=9.8, columnspacing=1.2)
    save(fig, "bieudo_dong_gop_nhom_dac_trung", relayout=fig.tight_layout)


# =========================================================================
# 6. Trained on one corpus, tested on the other (E16)
# =========================================================================
def chart_cross_corpus() -> None:
    log = runs()
    rows = [("ViHallu → ISE-DSC01\nlookback gộp", "e16_vihallu_to_isedsc01_lookback",
             "e07_baseline_lookback_isedsc01"),
            ("ViHallu → ISE-DSC01\nchunk-aware", "e16_vihallu_to_isedsc01_chunk",
             "e07_chunk_aware_isedsc01"),
            ("ISE-DSC01 → ViHallu\nlookback gộp", "e16_isedsc01_to_vihallu_lookback",
             "e02_lookback_lens"),
            ("ISE-DSC01 → ViHallu\nchunk-aware", "e16_isedsc01_to_vihallu_chunk",
             "e03_chunk_aware")]
    panels = [("Ba lớp", "macro_f1", 1 / 3), ("Nhị phân",
                                             "binary_macro_f1", 0.5)]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.3), sharey=True)
    ys = np.arange(len(rows))[::-1]
    for ax, (title, key, chance) in zip(axes, panels, strict=True):
        for y, (_, cross_name, own_name) in zip(ys, rows, strict=True):
            cross, own = log[cross_name]["metrics"], log[own_name]["metrics"][key]
            ax.plot([cross[key], own], [y, y], color=LIGHT, linewidth=3, zorder=1)
            ax.plot([cross[f"{key}_lo"], cross[f"{key}_hi"]], [y, y], color=RED, linewidth=1.4,
                    zorder=2)
            ax.scatter(cross[key], y, s=58, color=RED, edgecolor="white", linewidth=1, zorder=3)
            ax.scatter(own, y, s=58, marker="D", color=NAVY, edgecolor="white", linewidth=1,
                       zorder=3)
            ax.text(cross[key] + 0.02, y + 0.2, vnum(cross[key], 3), fontsize=9.5, ha="right",
                    va="bottom", bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
            ax.text(own - 0.02, y + 0.2, vnum(own, 3), fontsize=9.5, ha="left", va="bottom")
        ax.axvline(chance, color=GRAY, linestyle="--", linewidth=1.2)
        ax.text(chance + 0.008, -0.62, "ngẫu nhiên", fontsize=9.5, ha="left", va="center",
                color=MUTED)
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0.22, 0.98)
        ax.xaxis.set_major_locator(MultipleLocator(0.2))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
        ax.set_xlabel("macro-F1")
        ax.grid(axis="y", visible=False)
        ax.set_axisbelow(True)
    axes[0].set_yticks(ys, [r[0] for r in rows], fontsize=9.8)
    axes[0].set_ylim(-0.85, len(rows) - 0.35)
    fig.legend(handles=[
        Line2D([], [], marker="o", color=RED, linewidth=1.4, markersize=8, markeredgecolor="white",
               label="huấn luyện trên bộ nguồn (KTC 95 %)"),
        Line2D([], [], marker="D", color=NAVY, linestyle="none", markersize=7.5,
               markeredgecolor="white", label="huấn luyện trên chính bộ đích")],
        frameon=False, loc="lower center", bbox_to_anchor=(0.5, 0.97), ncols=2, fontsize=9.8)
    save(fig, "bieudo_cheo_bo_du_lieu", relayout=fig.tight_layout)


# =========================================================================
# 7. Reliability diagram before and after temperature scaling (T22C)
# =========================================================================
def chart_reliability() -> None:
    data = load("figures/reliability.json")
    arms = [("lookback_full", "lookback gộp, 756 đầu", ORANGE, "o"),
            ("chunk_small", "chunk-aware, 32 đầu", RED, "s")]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.0), sharey=True)
    for ax, (when, title, field) in zip(
            axes, (("before", "Trước hiệu chỉnh", "ece"),
                   ("after", "Sau temperature scaling", "ece_scaled")), strict=True):
        ax.plot([0.3, 1], [0.3, 1], color=GRAY, linestyle="--", linewidth=1.2, zorder=1)
        for key, name, color, marker in arms:
            bins = [b for b in data[key][when] if b["n"] >= 10]
            ax.plot([b["confidence"] for b in bins], [b["accuracy"] for b in bins], color=color,
                    linewidth=1.8, marker=marker, markersize=6.5, markeredgecolor="white",
                    zorder=3, label=name)
        ax.set_title(title, fontsize=11.5)
        ax.set_xlabel("Độ tự tin trung bình của nhóm")
        ax.set_xlim(0.3, 1.02)
        ax.set_ylim(0.2, 1.02)
        for axis in (ax.xaxis, ax.yaxis):
            axis.set_major_locator(MultipleLocator(0.2))
            axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
        ax.set_aspect("equal")
        lines = [f"ECE {'lookback' if key == 'lookback_full' else 'chunk-aware'}: "
                 f"{vnum(data[key][field], 3)}" for key, *_ in arms]
        ax.text(0.97, 0.04, "\n".join(lines), transform=ax.transAxes, ha="right", va="bottom",
                fontsize=10, color=INK)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Tỷ lệ dự đoán đúng của nhóm")
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(Line2D([], [], color=GRAY, linestyle="--", linewidth=1.2))
    fig.legend(handles, [*labels, "lý tưởng"], frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 0.96), ncols=3, fontsize=9.8, columnspacing=1.0)
    save(fig, "bieudo_do_tin_cay", relayout=fig.tight_layout)


if __name__ == "__main__":
    chart_head_map()
    chart_evidence_removed()
    chart_attribution()
    chart_paired()
    chart_feature_groups()
    chart_cross_corpus()
    chart_reliability()
