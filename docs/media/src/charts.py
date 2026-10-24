"""Result charts for the thesis report.

Every number here is transcribed from the tables in ``docs/EXPERIMENTS.md``,
which in turn are produced by the run logs in ``results/``.  Nothing is
estimated or smoothed.

Run:  python docs/media/src/charts.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator

OUT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- style ---
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 11,
    "axes.titlesize": 12.5,
    "axes.labelsize": 11.5,
    "axes.edgecolor": "#3f3f46",
    "axes.linewidth": 0.9,
    "axes.grid": True,
    "grid.color": "#dcdce2",
    "grid.linewidth": 0.7,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "mathtext.fontset": "stix",
    "axes.unicode_minus": True,
})

NAVY = "#1f3a5f"
BLUE = "#3b6ea5"
TEAL = "#2a8c82"
ORANGE = "#d98032"
RED = "#b5452f"
GRAY = "#8a8f98"
LIGHT = "#c3c8d0"

vn = FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ","))


def vn_axis(axis) -> None:
    """Two-decimal Vietnamese tick labels on steps of 1, 2 or 5 — never 2,5, which the
    default locator picks on narrow charts and which two decimals print wrong."""
    axis.set_major_locator(MaxNLocator(steps=[1, 2, 5, 10]))
    axis.set_major_formatter(vn)


# Every chart is printed 14 cm wide (build_docx.py, NARROW_IMAGES) whatever its canvas, so
# the canvas decides how big the text comes out: an 8-inch chart printed its 10 pt labels
# at 6–7 pt. Before saving, the canvas is resized until its saved width prints every point
# of text at PRINT_SCALE — at 1,0 a 10 pt label is 10 pt on paper, the template's floor.
PRINT_W_IN = 14.0 / 2.54
PRINT_SCALE = 1.0
PAD_IN = 0.1                    # savefig's pad_inches, added on each side of the tight box


def fit_to_print(fig, relayout=None) -> None:
    """Resize the canvas, keeping its aspect ratio, so the saved image is exactly as wide
    as PRINT_W_IN / PRINT_SCALE. The axes grow and shrink with the canvas, the text does
    not, hence the few rounds."""
    target = PRINT_W_IN / PRINT_SCALE - 2 * PAD_IN
    for _ in range(8):
        if relayout:
            relayout()
        fig.canvas.draw()
        w = fig.get_tightbbox(fig.canvas.get_renderer()).width
        if abs(w - target) < 0.005:
            break
        fw, fh = fig.get_size_inches()
        k = (fw + target - w) / fw
        fig.set_size_inches(fw * k, fh * k)


def save(fig, name: str, relayout=None) -> None:
    fit_to_print(fig, relayout)
    path = OUT / f"{name}.png"
    fig.savefig(path, pad_inches=PAD_IN)
    plt.close(fig)
    print(f"wrote {path.name}")


def vnum(x: float, nd: int = 4) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


# =========================================================================
# 1. Main comparison on ViHallu, macro-F1 with the 95 % test interval
# =========================================================================
def chart_main() -> None:
    rows = [
        ("Đặc trưng bề mặt (E01)",       0.6562, 0.6200, 0.6891, GRAY),
        ("Gemini giám khảo (E10) †",     0.6637, 0.6070, 0.7191, LIGHT),
        ("PhoBERT-large (E09)",          0.7487, 0.7137, 0.7776, BLUE),
        ("XLM-R-large (E09)",            0.7762, 0.7570, 0.8184, NAVY),
        ("Lookback gộp (E02)",           0.7451, 0.7111, 0.7762, ORANGE),
        ("Chunk-aware theo câu (E03)",   0.7567, 0.7242, 0.7885, RED),
    ]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    ys = np.arange(len(rows))[::-1]
    for y, (_name, m, lo, hi, color) in zip(ys, rows, strict=False):
        ax.barh(y, m, height=0.58, color=color, edgecolor="#2b2b31", linewidth=0.7)
        ax.errorbar(m, y, xerr=[[m - lo], [hi - m]], fmt="none",
                    ecolor="#2b2b31", elinewidth=1.1, capsize=4)
        # three decimals, as Bảng 6.1 next to it prints them
        ax.text(hi + 0.006, y, vnum(m, 3), va="center", ha="left", fontsize=10.5,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.5))  # masks the 0,818 line
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.set_xlim(0.55, 0.885)
    ax.set_xlabel("macro-F1 (ba lớp) với khoảng tin cậy 95 % của tập test")
    # the dagger on the Gemini row is explained inside the figure, where the reader meets it
    ax.text(1.0, -0.285, "† chấm trên 300/700 mẫu test", transform=ax.transAxes,
            ha="right", va="top", fontsize=9.5, color="#3f3f46")
    vn_axis(ax.xaxis)
    ax.axvline(0.8184, color=NAVY, linestyle="--", linewidth=1.0, alpha=0.8)
    ax.text(0.866, 2.6, "mốc “hơn hẳn”: 0,818",
            color=NAVY, fontsize=9.5, va="center", ha="left", rotation=90)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_ketqua_chinh")


# =========================================================================
# 2. Per-class F1: what the aggregate number hides
# =========================================================================
def chart_per_class() -> None:
    labels = ["no\n(trung thực)", "intrinsic\n(ảo giác nội tại)", "extrinsic\n(ảo giác ngoại lai)"]
    e02 = [0.7925, 0.7308, 0.7121]
    e03 = [0.8228, 0.6858, 0.7615]
    x = np.arange(len(labels))
    w = 0.36

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    b1 = ax.bar(x - w / 2, e02, w, label="Lookback gộp (E02)",
                color=ORANGE, edgecolor="#2b2b31", linewidth=0.7)
    b2 = ax.bar(x + w / 2, e03, w, label="Chunk-aware theo câu (E03)",
                color=RED, edgecolor="#2b2b31", linewidth=0.7)
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.008,
                    vnum(b.get_height()), ha="center", fontsize=10)
    for xi, (a, b) in enumerate(zip(e02, e03, strict=False)):
        d = b - a
        ax.annotate(("+" if d > 0 else "−") + vnum(abs(d)),
                    xy=(xi, max(a, b) + 0.075), ha="center", fontsize=10.5,
                    color=(TEAL if d > 0 else RED), weight="bold")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.2)
    ax.set_ylabel("F1 từng lớp")
    vn_axis(ax.yaxis)
    ax.legend(frameon=False, loc="upper center", ncols=2, fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_f1_tung_lop")


# =========================================================================
# 3. Attention localisation against the gold evidence chunk (E06)
# =========================================================================
def chart_localization() -> None:
    metrics = ["hit@1", "hit@3", "MRR"]
    best = [0.8779, 0.9562, 0.9200]
    mean = [0.3320, 0.5177, 0.4709]
    floor = [0.0614, 0.1843, 0.1987]
    x = np.arange(3)
    w = 0.26

    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.bar(x - w, floor, w, label="Mức ngẫu nhiên", color=LIGHT,
           edgecolor="#2b2b31", linewidth=0.7)
    ax.bar(x, mean, w, label="Trung bình 756 đầu chú ý", color=BLUE,
           edgecolor="#2b2b31", linewidth=0.7)
    ax.bar(x + w, best, w, label="Đầu chú ý mạnh nhất", color=RED,
           edgecolor="#2b2b31", linewidth=0.7)
    for xi, (f, m, b) in enumerate(zip(floor, mean, best, strict=False)):
        for dx, v in ((-w, f), (0, m), (w, b)):
            ax.text(xi + dx, v + 0.012, vnum(v), ha="center", fontsize=9.8)
    ax.annotate("gấp 14,29 lần mức ngẫu nhiên", xy=(w + 0.04, 0.925), xytext=(-0.38, 1.12),
                fontsize=10.5, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, linewidth=1.1))
    ax.set_xticks(x, metrics)
    ax.set_ylim(0, 1.62)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_ylabel("Giá trị chỉ số")
    vn_axis(ax.yaxis)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_dinh_vi_chu_y")


# =========================================================================
# 4. Accuracy against inference cost (E11)
# =========================================================================
def chart_tradeoff() -> None:
    # every row of Bảng 6.14. The six reading-model points sit within half a decade of each
    # other, so their labels are centred on the marker's height and split by side: the 7B
    # and 1.5B pairs read to the right, the 3B pair to the left.
    pts = [
        ("Đặc trưng bề mặt",       0.001,   0.6562, GRAY,      (10, 8),    "left",  "baseline"),
        ("Gemini giám khảo",       8194.0,  0.6637, LIGHT,     (-46, -20), "left",  "baseline"),
        ("PhoBERT-large",          12.3,    0.7487, BLUE,      (-40, 16),  "left",  "baseline"),
        ("XLM-R-large",            25.2,    0.7762, NAVY,      (6, 8),     "left",  "baseline"),
        ("Chunk-aware 7B",         437.6,   0.7567, RED,       (15, 3),    "left",  "center"),
        ("Lookback gộp 7B",        437.6,   0.7451, ORANGE,    (15, 1),    "left",  "center"),
        ("Chunk-aware 1.5B",       608.1,   0.7345, "#8a4a70", (10, -2),   "left",  "center"),
        ("Lookback gộp 1.5B",      608.1,   0.7232, "#b98aa8", (10, -4),   "left",  "center"),
        ("Lookback gộp 3B",        222.7,   0.7345, "#9c6b2f", (-10, 1),   "right", "center"),
        ("Chunk-aware 3B",         222.7,   0.7217, "#c9a36b", (-10, -2),  "right", "center"),
    ]
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    for name, ms, f1, color, off, ha, va in pts:
        ax.scatter(ms, f1, s=96, color=color, edgecolor="#2b2b31",
                   linewidth=0.8, zorder=3)
        ax.annotate(name, (ms, f1), textcoords="offset points", xytext=off,
                    fontsize=10, ha=ha, va=va)
    ax.set_xscale("log")
    ax.set_xlabel("Chi phí suy luận mỗi mẫu (ms, thang log) — càng trái càng rẻ")
    ax.set_ylabel("macro-F1")
    vn_axis(ax.yaxis)
    ax.set_ylim(0.63, 0.80)
    ax.set_xlim(5e-4, 3e5)       # room on the right for the labels of the 7B and 1.5B points
    ax.axhspan(0.7570, 0.8184, color=NAVY, alpha=0.07, zorder=0)
    ax.text(7e-4, 0.7875, "khoảng tin cậy của XLM-R — mốc phải vượt",
            fontsize=9.5, color=NAVY)
    ax.grid(which="both", alpha=0.55)
    ax.set_axisbelow(True)
    save(fig, "bieudo_danh_doi_chi_phi")


# =========================================================================
# 5. Cumulative feature-group ablation (E12)
# =========================================================================
def chart_ablation() -> None:
    labels = ["Chỉ đặc trưng\nbề mặt", "+ lookback\ngộp", "+ chunk-\naware", "+ đặc trưng\nổn định"]
    sep = [0.6562, 0.7653, 0.7388, 0.7746]
    joint = [0.6562, 0.7759, 0.7688, 0.7746]
    x = np.arange(4)
    w = 0.36

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.bar(x - w / 2, sep, w, label="Dev chọn cách gộp đầu riêng từng mức",
           color=BLUE, edgecolor="#2b2b31", linewidth=0.7)
    ax.bar(x + w / 2, joint, w, label="Gộp chung topk k = 32",
           color=TEAL, edgecolor="#2b2b31", linewidth=0.7)
    for xi in x:
        ax.text(xi - w / 2, sep[xi] + 0.008, vnum(sep[xi]), ha="center", fontsize=9.8)
        ax.text(xi + w / 2, joint[xi] + 0.008, vnum(joint[xi]), ha="center", fontsize=9.8)
    for xi in (1, 2, 3):
        d = sep[xi] - sep[xi - 1]
        # above both value labels of the group, still over the bar it describes
        ax.annotate(("+" if d > 0 else "−") + vnum(abs(d)),
                    xy=(xi - w / 2, max(sep[xi], joint[xi]) + 0.03), ha="center",
                    fontsize=10.5, weight="bold", color=(TEAL if d > 0 else RED))
    ax.axhline(0.6562, color=GRAY, linestyle=":", linewidth=1.1)
    ax.set_xticks(x, labels)
    ax.set_ylim(0.6, 0.88)
    ax.set_ylabel("macro-F1 (cộng dồn nhóm đặc trưng)")
    vn_axis(ax.yaxis)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_ablation")


# =========================================================================
# 6. Reading-model ladder (E13 + E14)
# =========================================================================
def chart_ladder() -> None:
    models = ["Qwen2.5-1.5B", "Qwen2.5-3B", "Qwen2.5-7B", "Sailor2-8B"]
    look = [0.7232, 0.7345, 0.7451, 0.7377]
    chunk = [0.7345, 0.7217, 0.7567, 0.7120]
    x = np.arange(4)
    w = 0.36

    fig, ax = plt.subplots(figsize=(7.8, 4.2))
    ax.bar(x - w / 2, look, w, label="Lookback gộp", color=ORANGE,
           edgecolor="#2b2b31", linewidth=0.7)
    ax.bar(x + w / 2, chunk, w, label="Chunk-aware", color=RED,
           edgecolor="#2b2b31", linewidth=0.7)
    for xi in x:
        d = chunk[xi] - look[xi]
        ax.text(xi - w / 2, look[xi] + 0.004, vnum(look[xi]), ha="center", fontsize=9.6)
        ax.text(xi + w / 2, chunk[xi] + 0.004, vnum(chunk[xi]), ha="center", fontsize=9.6)
        ax.annotate(("+" if d > 0 else "−") + vnum(abs(d)),
                    xy=(xi, max(look[xi], chunk[xi]) + 0.020), ha="center",
                    fontsize=10.5, weight="bold", color=(TEAL if d > 0 else RED))
    ax.set_xticks(x, models)
    ax.set_ylim(0.66, 0.80)
    ax.set_ylabel("macro-F1 trên ViHallu")
    vn_axis(ax.yaxis)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_bac_thang_mo_hinh")


# =========================================================================
# 7. Cross-dataset generalisation (E16)
# =========================================================================
def chart_cross() -> None:
    labels = ["ViHallu →\nISE-DSC01\nlookback gộp", "ViHallu →\nISE-DSC01\nchunk-aware",
              "ISE-DSC01 →\nViHallu\nlookback gộp", "ISE-DSC01 →\nViHallu\nchunk-aware"]
    cross = [0.4301, 0.3584, 0.5540, 0.5521]
    own = [0.7851, 0.7919, 0.7451, 0.7567]
    x = np.arange(4)

    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.bar(x, own, 0.56, color=LIGHT, edgecolor="#2b2b31", linewidth=0.7,
           label="Đích tự chấm (huấn luyện trên chính bộ đích)")
    ax.bar(x, cross, 0.56, color=RED, edgecolor="#2b2b31", linewidth=0.7,
           label="Chéo bộ (huấn luyện trên bộ nguồn)")
    for xi in x:
        ax.text(xi, cross[xi] - 0.045, vnum(cross[xi]), ha="center",
                fontsize=10, color="white", weight="bold")
        ax.text(xi, own[xi] + 0.008, vnum(own[xi]), ha="center", fontsize=10)
        ax.annotate(f"sụt {vnum(own[xi] - cross[xi])}", xy=(xi, (own[xi] + cross[xi]) / 2),
                    ha="center", fontsize=10, color="#2b2b31")
    # the chance line is named in the legend: a label on the line itself would sit on a bar
    ax.axhline(0.3333, color=GRAY, linestyle="--", linewidth=1.1,
               label="Mức ngẫu nhiên 0,33")
    ax.set_xticks(x, labels, fontsize=9.6)
    ax.set_ylim(0, 1.2)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    ax.set_ylabel("macro-F1")
    vn_axis(ax.yaxis)
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_khai_quat_cheo_bo")


# =========================================================================
# 8. Memory budget: the reason the hook design is not optional
# =========================================================================
def chart_memory() -> None:
    seq = ["2.048 token", "4.096 token", "8.192 token"]
    naive = [6.6, 26.0, 105.0]
    hooked = [0.23, 0.94, 3.76]
    x = np.arange(3)
    w = 0.36

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    ax.bar(x - w / 2, naive, w, label="output_attentions — giữ cả 28 lớp",
           color=RED, edgecolor="#2b2b31", linewidth=0.7)
    ax.bar(x + w / 2, hooked, w, label="Forward hook — giữ một lớp",
           color=TEAL, edgecolor="#2b2b31", linewidth=0.7)
    for xi in x:
        ax.text(xi - w / 2, naive[xi] * 1.08, f"{naive[xi]:g}".replace(".", ",") + " GB",
                ha="center", fontsize=10)
        ax.text(xi + w / 2, hooked[xi] * 1.08, f"{hooked[xi]:g}".replace(".", ",") + " GB",
                ha="center", fontsize=10)
    ax.axhline(16, color=NAVY, linestyle="--", linewidth=1.2)
    ax.text(-0.45, 18, "giới hạn Tesla T4 — 16 GB", color=NAVY, fontsize=10)
    ax.set_yscale("log")
    ax.set_xticks(x, seq)
    ax.set_ylim(0.1, 400)
    ax.set_ylabel("Bộ nhớ ma trận chú ý (GB, thang log)")
    ax.set_xlabel("Độ dài chuỗi đầu vào")
    ax.legend(frameon=False, loc="upper left", fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_ngan_sach_bo_nho")


# =========================================================================
# 9. The four corpora at a glance
# =========================================================================
def chart_datasets() -> None:
    names = ["ViHallu", "ISE-DSC01", "ViWikiFC", "ViFactCheck"]
    n = [7000, 36369, 20919, 7232]
    words = [179.7, 637, 153, 693]
    sents = [5, 19, 4, 17]

    # Horizontal bars that share one column of corpus names: three column charts side by
    # side, once shrunk to print their text at 90 %, ran their titles and names together.
    # Every bar carries its value, so the value axes are left off.
    fig, axes = plt.subplots(1, 3, figsize=(6.1, 2.4), sharey=True)
    colors = [RED, BLUE, TEAL, ORANGE]
    ys = np.arange(len(names))[::-1]
    panels = [
        (n, "Số mẫu có nhãn", lambda v: f"{v:,}".replace(",", ".")),
        (words, "Độ dài ngữ cảnh\ntrung bình (từ)", lambda v: f"{v:g}".replace(".", ",")),
        (sents, "Số câu mỗi ngữ\ncảnh (trung vị)", str),
    ]
    for ax, (vals, title, fmt) in zip(axes, panels, strict=False):
        ax.barh(ys, vals, height=0.62, color=colors, edgecolor="#2b2b31", linewidth=0.7)
        for y, v in zip(ys, vals, strict=False):
            ax.text(v + max(vals) * 0.04, y, fmt(v), va="center", fontsize=9.8)
        ax.set_title(title, fontsize=11)
        ax.set_xlim(0, max(vals) * 1.45)
        ax.set_xticks([])
        ax.grid(False)
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
    axes[0].set_yticks(ys, names)
    save(fig, "bieudo_bon_bo_du_lieu", relayout=fig.tight_layout)


# =========================================================================
# 10. Calibration against accuracy — one axis, one point per method
# =========================================================================
def chart_ece() -> None:
    pts = [
        ("Đặc trưng bề mặt (E01)", 0.6562, 0.061, GRAY, (8, -4)),
        ("PhoBERT-large (E09)", 0.7487, 0.081, BLUE, (-128, 4)),
        ("XLM-R-large (E09)", 0.7762, 0.097, NAVY, (-40, 12)),
        ("Lookback gộp (E02)", 0.7451, 0.109, ORANGE, (-122, 6)),
        ("Chunk-aware (E03)", 0.7567, 0.044, RED, (-104, -4)),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 4.3))
    for name, f1, ece, color, off in pts:
        ax.scatter(f1, ece, s=110, color=color, edgecolor="#2b2b31", linewidth=0.8, zorder=3)
        ax.annotate(name, (f1, ece), textcoords="offset points", xytext=off, fontsize=10.2)
    ax.set_xlabel("macro-F1 ba lớp (càng phải càng tốt)")
    ax.set_ylabel("ECE (càng thấp càng tốt)")
    ax.set_xlim(0.63, 0.80)
    ax.set_ylim(0.0, 0.13)
    vn_axis(ax.xaxis)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.3f}".replace(".", ",")))
    ax.set_axisbelow(True)
    save(fig, "bieudo_hieu_chinh_ece")


# =========================================================================
# 11. Label distribution of the four corpora, per split
# =========================================================================
def chart_label_distribution() -> None:
    rows = [
        ("ViHallu · train", 1780, 1984, 1836),
        ("ViHallu · dev", 225, 230, 245),
        ("ViHallu · test", 240, 234, 226),
        ("ISE-DSC01 · train", 10193, 8856, 10028),
        ("ISE-DSC01 · dev", 1291, 1086, 1269),
        ("ISE-DSC01 · test", 1302, 1058, 1286),
        ("ViWikiFC · train", 5594, 5573, 5571),
        ("ViWikiFC · dev", 666, 694, 730),
        ("ViWikiFC · test", 708, 706, 677),
        ("ViFactCheck · train", 1751, 1658, 1653),
        ("ViFactCheck · dev", 256, 244, 223),
        ("ViFactCheck · test", 508, 468, 471),
    ]
    classes = [("no (trung thực)", TEAL), ("intrinsic (nội tại)", ORANGE),
               ("extrinsic (ngoại lai)", RED)]
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ys = np.arange(len(rows))[::-1]
    for y, (_name, *counts) in zip(ys, rows, strict=False):
        total = sum(counts)
        left = 0.0
        for (label, color), c in zip(classes, counts, strict=False):
            w = c / total
            ax.barh(y, w - 0.004, left=left, height=0.66, color=color, edgecolor="white",
                    linewidth=0.8, label=label if y == ys[0] else None)
            ax.text(left + w / 2, y, f"{w * 100:.0f} %", ha="center", va="center",
                    fontsize=9.5, color="white", weight="bold")
            left += w
        ax.text(1.012, y, f"n = {total:,}".replace(",", "."), va="center", fontsize=9.5,
                color="#3f3f46")
    for sep in (2.5, 5.5, 8.5):
        ax.axhline(sep, color="#9ca3af", linewidth=0.8)
    ax.set_yticks(ys, [r[0] for r in rows], fontsize=9.8)
    ax.set_xlim(0, 1.13)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0 %", "25 %", "50 %", "75 %", "100 %"])
    ax.set_xlabel("Tỷ lệ nhãn trong từng tập")
    ax.grid(False)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.1), ncols=3, fontsize=10,
              handlelength=1.2, columnspacing=1.0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    save(fig, "bieudo_phan_bo_nhan")


# =========================================================================
# 12. Plan of the thesis — 18 weeks
# =========================================================================
def chart_plan() -> None:
    phases = [
        ("Khảo sát và đề xuất", NAVY, [
            ("Khảo sát tài liệu, xác định khoảng trống nghiên cứu", 1, 2),
            ("Thu thập và kiểm tra bốn bộ dữ liệu", 1, 2),
            ("Viết và trình đề xuất đề tài", 2, 1)]),
        ("Nền tảng và dữ liệu", BLUE, [
            ("Dựng khung mã nguồn, cấu hình, ghi kết quả", 3, 1),
            ("Kiểm tra khả thi trích chú ý trên T4", 3, 1),
            ("Chuẩn hóa bốn bộ về lược đồ chung", 3, 2),
            ("Kiểm chứng thủ công ánh xạ nhãn NEI", 4, 1),
            ("Chia tập theo ngữ cảnh, báo cáo rò rỉ", 4, 1),
            ("Chia đoạn và kho truy xuất ViWikiFC", 4, 1)]),
        ("Mốc so sánh và tái lập", TEAL, [
            ("Mốc đặc trưng bề mặt", 5, 1),
            ("Mốc bộ mã hóa tinh chỉnh", 5, 1),
            ("Mốc LLM giám khảo", 5, 1),
            ("Tái lập Lookback Lens", 5, 1)]),
        ("Đóng góp và kiểm chứng cơ chế", RED, [
            ("Hiện thực đặc trưng chunk-aware", 6, 1),
            ("So sánh cách chia đoạn, chốt cấu hình", 6, 2),
            ("Định vị chú ý trên ISE-DSC01", 7, 1),
            ("Ngữ cảnh dài và thí nghiệm can thiệp", 7, 2)]),
        ("Thực nghiệm mở rộng", ORANGE, [
            ("Ablation, mô hình đọc, bậc thang kích thước", 10, 2),
            ("Đánh đổi chi phí, đối chứng ngoài", 10, 2),
            ("Khái quát hóa chéo bộ, phân tích sai sót", 11, 1)]),
        ("Hệ thống", "#7a6a9c", [
            ("Thư viện, dịch vụ REST, Docker", 12, 2),
            ("Giao diện quan sát, hệ RAG minh họa", 13, 1)]),
        ("Báo cáo và bảo vệ", GRAY, [
            ("Báo cáo giữa kỳ", 8, 2),
            ("Viết quyển khóa luận", 14, 2),
            ("Báo cáo cuối kỳ và phản biện", 16, 2),
            ("Bảo vệ trước hội đồng", 18, 1)]),
    ]
    rows = [(task, s, d, color, ph) for ph, color, tasks in phases for task, s, d in tasks]
    # The task names sit beside their bars and the phases go into a legend: a column of
    # names on the left and another of phases on the right made the chart 11 inches wide,
    # and printed 14 cm wide its text came out at 4,7 pt.
    fig, ax = plt.subplots(figsize=(6.1, 5.4))
    ys = np.arange(len(rows))[::-1]
    label_box = dict(facecolor="white", edgecolor="none", pad=0.4)
    for y, (task, s, d, color, _) in zip(ys, rows, strict=False):
        left, width = s - 0.94, d - 0.12
        ax.barh(y, width, left=left, height=0.62, color=color, edgecolor="none", zorder=2)
        # after the bar in the first half of the plan, before it in the second, so no
        # name runs off either edge
        if s <= 9:
            ax.text(left + width + 0.15, y, task, va="center", ha="left", fontsize=9.5,
                    bbox=label_box, zorder=3)
        else:
            ax.text(left - 0.15, y, task, va="center", ha="right", fontsize=9.5,
                    bbox=label_box, zorder=3)
    ax.set_yticks([])
    # phase separators
    idx = 0
    for _ph, _color, tasks in phases:
        idx += len(tasks)
        if idx < len(rows):
            ax.axhline(ys[idx - 1] - 0.5, color="#d1d5db", linewidth=0.7, zorder=1)
    starts = ["03/08", "10/08", "17/08", "24/08", "31/08", "07/09", "14/09", "21/09", "28/09",
              "05/10", "12/10", "19/10", "26/10", "02/11", "09/11", "16/11", "23/11", "30/11"]
    # the week number under every tick, its start date under every other one: eighteen
    # dates side by side ran into each other at 9 pt
    ax.set_xticks(np.arange(18) + 0.5, [f"{w + 1}\n{starts[w] if w % 2 == 0 else ''}"
                                        for w in range(18)], fontsize=9.5)
    ax.set_xlim(0, 18)
    ax.set_ylim(-0.8, len(rows) + 1.4)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#eceef2", zorder=0)
    ax.set_axisbelow(True)
    # the three last milestones are a week apart, narrower than their names: the middle
    # one drops two rows, into the empty top right of the chart
    for week, label, drop in ((2.5, "Kiểm tra\nkhả thi", 0), (15.5, "Báo cáo\ncuối kỳ", 0),
                              (16.5, "Phản\nbiện", 2.6), (17.5, "Bảo\nvệ", 0)):
        ax.axvline(week, color="#2b2b31", linestyle=(0, (3, 3)), linewidth=0.9, zorder=1)
        ax.text(week, len(rows) - 0.3 - drop, label, ha="center", va="bottom", fontsize=9.5,
                color="#2b2b31", bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
    ax.set_xlabel("Tuần thực hiện (ngày bắt đầu tuần, năm 2026)")
    handles = [Patch(color=color, label=ph) for ph, color, _ in phases]
    ax.legend(handles=handles, frameon=False, loc="upper center", ncols=3, fontsize=9.5,
              bbox_to_anchor=(0.5, -0.15), handlelength=1.2, columnspacing=1.2)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    save(fig, "bieudo_ke_hoach")


# =========================================================================
# 13. Intervention: share of pairs that moved in the predicted direction
# =========================================================================
def chart_intervention() -> None:
    rows = [
        ("ENT — dự đoán tăng", 75.4, 0.716, BLUE),
        ("GINI — dự đoán giảm", 74.5, -0.686, BLUE),
        ("MAX — dự đoán giảm", 72.4, -0.657, BLUE),
        ("GAP — dự đoán giảm", 71.2, -0.624, BLUE),
        ("DRIFT — không dự đoán", 63.3, 0.401, LIGHT),
    ]
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    ys = np.arange(len(rows))[::-1]
    for y, (_name, pct, r, color) in zip(ys, rows, strict=False):
        ax.barh(y, pct, height=0.58, color=color, edgecolor="#2b2b31", linewidth=0.6)
        ax.text(pct + 0.8, y,
                f"{pct:.1f} %".replace(".", ",")
                + f"   ($r_{{rb}}$ = {r:+.2f})".replace(".", ",").replace("-", "−"),
                va="center", fontsize=10)
    ax.axvline(50, color=RED, linestyle="--", linewidth=1.1)
    ax.text(50.6, ys[0] + 0.52, "mức ngẫu nhiên 50 %", color=RED, fontsize=9.6, va="bottom")
    ax.set_yticks(ys, [r[0] for r in rows])
    # room on the right for the value and r_rb printed after each bar
    ax.set_xlim(0, 118)
    ax.set_xticks(range(0, 101, 20))
    ax.set_xlabel("Tỷ lệ cặp có đặc trưng thay đổi đúng hướng dự đoán (%)")
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_can_thiep")


# =========================================================================
# 14. Localisation replicated on a second corpus
# =========================================================================
def chart_localization_replication() -> None:
    groups = ["Đầu chú ý mạnh nhất", "Trung bình 756 đầu", "Mức ngẫu nhiên"]
    ise = [0.8779, 0.3320, 0.0614]
    wiki = [0.8529, 0.3289, 0.1027]
    x = np.arange(3)
    w = 0.34
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    ax.bar(x - w / 2, ise, w, color=BLUE, edgecolor="#2b2b31", linewidth=0.7,
           label="ISE-DSC01 · 22,6 đoạn")
    ax.bar(x + w / 2, wiki, w, color="#c9d6e8", edgecolor="#2b2b31", linewidth=0.7, hatch="///",
           label="ViWikiFC · 9,8 đoạn")
    for xi in x:
        ax.text(xi - w / 2, ise[xi] + 0.015, vnum(ise[xi]), ha="center", fontsize=9.8)
        ax.text(xi + w / 2, wiki[xi] + 0.015, vnum(wiki[xi]), ha="center", fontsize=9.8)
    ax.annotate("chênh lệch 0,003", xy=(1, 0.36), xytext=(1.32, 0.56), fontsize=10,
                arrowprops=dict(arrowstyle="->", color="#2b2b31", linewidth=0.9))
    ax.set_xticks(x, groups)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("hit@1 — tỷ lệ xếp đúng\nđoạn bằng chứng lên đầu")
    vn_axis(ax.yaxis)
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.grid(axis="x", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_lap_lai_dinh_vi")


# =========================================================================
# 15. Confusion matrix of the chunk-aware detector (E03) on the ViHallu test set
# =========================================================================
def chart_confusion() -> None:
    # rows: true no / intrinsic / extrinsic; columns: predicted — rebuilt from the confusion
    # pairs in results/error_analysis.json and the test label counts in
    # results/leakage_report.md; it reproduces the per-class F1 0,8228 / 0,6858 / 0,7615.
    m = np.array([[202, 27, 11], [33, 155, 46], [16, 36, 174]])
    labels = ["Trung thực\n(no)", "Nội tại\n(intrinsic)", "Ngoại lai\n(extrinsic)"]
    row_share = m / m.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    im = ax.imshow(row_share, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            v = row_share[i, j]
            ax.text(j, i, f"{m[i, j]}\n({v * 100:.1f} %)".replace(".", ","), ha="center",
                    va="center", fontsize=10.5, color="white" if v > 0.5 else "#1f2937")
    ax.set_xticks(range(3), labels)
    ax.set_yticks(range(3), labels)
    ax.set_xlabel("Nhãn dự đoán")
    ax.set_ylabel("Nhãn thật")
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Tỷ lệ theo hàng")
    cb.ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v * 100:.0f} %"))
    save(fig, "bieudo_ma_tran_nham_lan")


# =========================================================================
# 16. ECE and the size of the classifier, seven paired settings (dumbbell)
# =========================================================================
def chart_ece_params() -> None:
    rows = [
        ("ViHallu · Qwen2.5-7B", (2271, 0.109), (579, 0.044)),
        ("ViHallu · Qwen2.5-3B", (195, 0.061), (1851, 0.089)),
        ("ViHallu · Qwen2.5-1.5B", (1011, 0.050), (1131, 0.061)),
        ("ViHallu · Sailor2-8B", (195, 0.048), (1155, 0.071)),
        ("ISE-DSC01 · 5.600 mẫu huấn luyện", (2271, 0.146), (2511, 0.152)),
        ("ISE-DSC01 · 29.077 mẫu huấn luyện", (2271, 0.026), (2751, 0.033)),
        ("ViWikiFC · Qwen2.5-7B", (2271, 0.050), (2751, 0.062)),
    ]
    def fmt(n):
        return f"{n:,}".replace(",", ".")
    fig, ax = plt.subplots(figsize=(8.2, 6.0))
    ys = np.arange(len(rows))[::-1]
    for y, (_name, (lp, le), (cp, ce)) in zip(ys, rows, strict=False):
        ax.plot([le, ce], [y, y], color="#9ca3af", linewidth=2.0, zorder=1)
        ax.scatter(le, y, s=90, marker="o", color=ORANGE, edgecolor="#2b2b31", linewidth=0.7,
                   zorder=3)
        ax.scatter(ce, y, s=90, marker="s", color=RED, edgecolor="#2b2b31", linewidth=0.7, zorder=3)
        (x1, n1), (x2, n2) = sorted(((le, lp), (ce, cp)))
        ax.annotate(fmt(n1), (x1, y), textcoords="offset points", xytext=(-3, 8.5),
                    ha="right", fontsize=9.5, color="#2b2b31")
        ax.annotate(fmt(n2), (x2, y), textcoords="offset points", xytext=(3, 8.5),
                    ha="left", fontsize=9.5, color="#2b2b31")
    ax.scatter([], [], s=90, marker="o", color=ORANGE, edgecolor="#2b2b31", label="Lookback gộp")
    ax.scatter([], [], s=90, marker="s", color=RED, edgecolor="#2b2b31", label="Chunk-aware")
    ax.set_yticks(ys, [r[0] for r in rows], fontsize=10)
    ax.set_ylim(-0.7, len(rows) - 0.1)
    ax.set_xlim(0.0, 0.17)
    # fixed ticks: left to itself the locator picks 0,025 steps, printed as "0,03", "0,08"
    ax.set_xticks(np.arange(0, 0.17, 0.02))
    ax.set_xlabel("ECE (càng thấp càng tốt)\nsố trên mỗi điểm là số tham số phải huấn luyện")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ",")))
    ax.legend(frameon=False, loc="lower right", fontsize=10)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    save(fig, "bieudo_ece_tham_so")


if __name__ == "__main__":
    chart_main()
    chart_per_class()
    chart_localization()
    chart_tradeoff()
    chart_ablation()
    chart_ladder()
    chart_cross()
    chart_memory()
    chart_datasets()
    chart_ece()
    chart_label_distribution()
    chart_plan()
    chart_intervention()
    chart_localization_replication()
    chart_confusion()
    chart_ece_params()
