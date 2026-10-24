"""System overview: the four tiers a sample travels through, top to bottom.

Drawn on the same 900 px canvas as the other report figures so the labels survive being
printed across the 15,5 cm text column (see the note in method_figs.py). This is the
densest figure — 21 labelled steps — so its step labels sit at the floor size T_SMALL
and each tier's output store shares the line of its note, to keep the page height.

Run:  python docs/media/src/fig_tong_quat_he_thong.py
"""

from __future__ import annotations

from method_figs import (
    GRAY,
    GREEN,
    INK,
    NAVY,
    OUT,
    PAGE_W,
    PURPLE,
    RED,
    SOFT,
    T_SMALL,
    TINT_BLUE,
    TINT_GRAY,
    TINT_GREEN,
    TINT_PURPLE,
    header_band,
    render,
    text_left,
)
from svgkit import Canvas, text_block, wrap

M = 30
W = PAGE_W - 2 * M
LH = 22                           # line pitch of T_SMALL text
MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def tier(c: Canvas, y: float, title: str, subtitle: str, color: str, tint: str,
         rows: list[list[str]], note: str, store: str | None) -> float:
    """One tier: a titled panel holding rows of steps, then its note and output store."""
    hdr, gap, pad = 40, 18, 14
    # measure first: the panel is drawn under its content
    layout = []
    for row in rows:
        bw = (W - 2 * pad - (len(row) - 1) * gap) / len(row)
        n = max(len(wrap(label, bw - 10, T_SMALL)) for label in row)
        layout.append((row, bw, n * LH + 14))
    tag_w = 290 if store else 0
    note_w = W - 2 * pad - (tag_w + 16 if store else 0)
    n_note = len(wrap(note, note_w, T_SMALL))
    note_h = max(n_note * LH, 36 if store else 0)
    h = hdr + 10 + sum(rh + 8 for _, _, rh in layout) + note_h + 12

    c.add(f'<rect x="{M}" y="{y}" width="{W}" height="{h}" rx="12" fill="#ffffff" '
          f'stroke="{color}" stroke-width="1.7"/>')
    header_band(c, M, y, W, title, color, tint, hdr=hdr, radius=12)
    c.raw_text(M + W - 16, y + hdr / 2 + 1, subtitle, T_SMALL, anchor="end", fill=SOFT)
    yy = y + hdr + 10
    for row, bw, rh in layout:
        for k, label in enumerate(row):
            bx = M + pad + k * (bw + gap)
            c.band(bx, yy, bw, rh, TINT_GRAY, radius=7, stroke="#c8c8d0")
            c.add(text_block(bx + bw / 2, yy + rh / 2, label, bw - 10, font_size=T_SMALL,
                             fill=INK))
            if k:
                c.arrow((bx - gap + 3, yy + rh / 2), (bx - 3, yy + rh / 2), stroke=SOFT,
                        stroke_width=1.3)
        yy += rh + 8
    text_left(c, M + pad, yy + (note_h - n_note * LH) / 2 + LH / 2, note, note_w, T_SMALL,
              fill=SOFT, style="italic", line_h=LH, balance=True)
    if store:
        tx = M + W - pad - tag_w
        c.band(tx, yy + (note_h - 36) / 2, tag_w, 36, tint, radius=7, stroke=color)
        c.raw_text(tx + tag_w / 2, yy + note_h / 2 + 1, store, T_SMALL, anchor="middle",
                   fill=color, weight="bold", family=MONO)
    return y + h


def build() -> None:
    c = Canvas(width=PAGE_W, height=1400)
    y = 20
    tiers = [
        ("TẦNG DỮ LIỆU", "CPU", NAVY, TINT_BLUE,
         [["Bốn bộ dữ liệu thô\nViHallu · ISE-DSC01 · ViWikiFC · ViFactCheck",
           "Chuẩn hóa về lược đồ chung\nvà định vị câu bằng chứng"],
          ["Chia tập theo ngữ cảnh\n80/10/10, hạt giống 42",
           "Chia ngữ cảnh thành đoạn\ntheo câu, min_words = 5",
           "Kiểm tra rò rỉ ngữ cảnh\ngiữa các tập"]],
         "7.000 · 36.369 · 20.919 · 7.232 mẫu có nhãn sau chuẩn hóa",
         "data/interim/*.parquet"),
        ("TẦNG TRÍCH TÍN HIỆU CHÚ Ý", "GPU Tesla T4 16 GB", RED, "#fbe7e1",
         [["Mẫu prompt chat template\nngữ cảnh · câu hỏi · phản hồi",
           "Qwen2.5-7B-Instruct\nlượng tử hóa NF4 4-bit",
           "Một lượt truyền xuôi\nteacher forcing"],
          ["Forward hook từng lớp\n27 lớp × 28 đầu chú ý",
           "Cộng dồn đặc trưng trong hook\nrồi giải phóng ma trận chú ý",
           "Bỏ lớp 27\ntràn số ở float16"]],
         "Đỉnh VRAM 8.428 MB. Giữ cả 28 lớp cùng lúc ở 4.096 token cần 26 GB — tràn 16 GB.",
         "data/processed/ shard .npz"),
        ("TẦNG ĐẶC TRƯNG VÀ BỘ PHÁT HIỆN", "CPU", GREEN, TINT_GREEN,
         [["lookback_total 756 cột\nlookback_context",
           "Nhóm chunk-aware\nMAX · ENT · GINI\nGAP · DRIFT",
           "Ghép véc-tơ và chuẩn hóa\nz theo thống kê tập huấn luyện"],
          ["Hồi quy logistic đa lớp\n2.271 tham số",
           "Nhãn argmax\nvà điểm rủi ro 1 − P(no)",
           "Chấm trên tập dev\nmacro-F1 và ECE"]],
         "Bộ phát hiện đã khớp được đóng gói thành bundle .pkl kèm tệp mô tả .json — 11,5 KB.",
         "models/ bundle .pkl"),
        ("TẦNG PHỤC VỤ", "CPU", PURPLE, TINT_PURPLE,
         [["Thư viện Python\nnạp bundle, chấm theo lô",
           "Dịch vụ REST FastAPI\nPOST /score · /score/batch\nGET /health",
           "Đóng gói Docker\nchạy bằng một lệnh"],
          ["Giao diện quan sát\ntô màu đoạn theo tỷ trọng chú ý",
           "Hệ RAG minh họa\ntruy xuất BM25 → sinh → chấm",
           "Cảnh báo ảo giác\nkèm đoạn ngữ cảnh đáng ngờ"]],
         "Chi phí biên trong hệ RAG tự giám sát chưa được đo: trên T4, mô hình sinh và "
         "mô hình đọc là hai mô hình khác nhau.", None),
    ]
    for title, subtitle, color, tint, rows, note, store in tiers:
        y = tier(c, y, title, subtitle, color, tint, rows, note, store)
        if title != "TẦNG PHỤC VỤ":
            c.arrow((PAGE_W / 2, y + 3), (PAGE_W / 2, y + 23), stroke=INK)
            y += 26

    # the environment every tier is pinned to
    y += 22
    # explicit breaks: a chip is too narrow for a separator to end a line cleanly
    items = ["Python 3.11\nuv.lock", "configs/*.yaml", "hạt giống 42",
             "results/*.jsonl", "KTC bootstrap\n2.000 lần", "pytest\n688 ca"]
    bw = (W - 5 * 8) / 6
    c.raw_text(M, y, "MÔI TRƯỜNG VÀ BẰNG CHỨNG TÁI LẬP", T_SMALL, fill=GRAY, weight="bold")
    y += 16
    for k, it in enumerate(items):
        bx = M + k * (bw + 8)
        c.band(bx, y, bw, 56, "#ffffff", radius=7, stroke="#c8c8d0")
        c.add(text_block(bx + bw / 2, y + 28, it, bw - 10, font_size=T_SMALL, fill=SOFT))
    c.height = y + 56 + 20
    c.save(OUT / "hinh_tong_quat_he_thong.svg")
    render("hinh_tong_quat_he_thong", PAGE_W, int(c.height))


if __name__ == "__main__":
    build()
