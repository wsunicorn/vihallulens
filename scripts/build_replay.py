"""Bundle the T40 Kaggle results into ``serve/static/replay.json`` for the landing page.

The page at ``/`` runs the real model when ``/health`` says ``ok``. On a machine without a GPU —
the authors' laptops, a GitHub Pages copy, a reviewer's browser — it switches to *replay mode*
and shows the results the same page produced on a T4 on 11/09/2026: the three library
examples of T36, the four RAG questions of T40 and the one asked through ``/demo/ask`` in T37.
Those results live in ``results/t40/*.json``; this script is the only path from there to the
page, so the page never carries a number typed by hand.

    python scripts/build_replay.py            # rewrite static/replay.json
    python scripts/build_replay.py --check    # exit 1 if the file is stale (used by a test)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "t40"
OUT = ROOT / "src" / "vihallulens" / "serve" / "static" / "replay.json"

# The T36 examples were scored against this context (notebooks/t40_demo_t4.ipynb, ô 5). The
# JSON keeps question and response but not the context, so it is restated here, once.
T36_CONTEXT = (
    "Hà Nội là thủ đô của Việt Nam, nằm bên bờ sông Hồng. Thành phố có lịch sử hơn một nghìn "
    "năm, từng mang tên Thăng Long dưới triều Lý. Dân số nội thành khoảng tám triệu người. Khí "
    "hậu Hà Nội có bốn mùa rõ rệt, mùa đông có thể xuống dưới mười độ."
)
T36_NAMES = {"trung thuc": "Trung thực", "noi tai": "Nội tại", "ngoai lai": "Ngoại lai"}
SCORE_KEYS = ("label", "proba", "risk_score", "chunk_attention", "elapsed_ms", "n_chunks",
              "truncated", "nonfinite_layers")


def build() -> dict:
    thu_vien = json.loads((RESULTS / "t36_thu_vien.json").read_text(encoding="utf-8"))
    rag = json.loads((RESULTS / "t40_rag.json").read_text(encoding="utf-8"))
    rest = json.loads((RESULTS / "t37_rest.json").read_text(encoding="utf-8"))

    examples = []
    for row in thu_vien:
        score = {k: row[k] for k in SCORE_KEYS}
        for c in score["chunk_attention"]:
            assert T36_CONTEXT[c["char_start"]:c["char_end"]] == c["text"], "context mismatch"
        examples.append({
            "name": T36_NAMES[row["vi_du"]], "context": T36_CONTEXT,
            "question": row["question"], "response": row["response"], "score": score,
        })

    questions = []
    for row in rag + [rest["demo_ask"]]:
        questions.append({
            "question": row["question"], "retrieved": row["retrieved"], "context": row["context"],
            "answer": row["answer"], "elapsed_ms": row["elapsed_ms"],
            "score": {k: row["score"][k] for k in SCORE_KEYS},
        })

    health = rest["health"]
    return {
        "source": "results/t40 — phiên Kaggle 11/09/2026, Tesla T4",
        "reading_model": health["reading_model"],
        "generator": "Qwen/Qwen2.5-3B-Instruct · nf4 · bfloat16",
        "vram_allocated_mb": health["vram_allocated_mb"],
        "examples": examples,
        "questions": questions,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Gom kết quả T40 thành replay.json cho trang chủ.")
    parser.add_argument("--check", action="store_true", help="chỉ kiểm file có cũ không")
    args = parser.parse_args()

    text = json.dumps(build(), ensure_ascii=False, indent=1) + "\n"
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"  {OUT.relative_to(ROOT)} cũ so với results/t40 — chạy lại build_replay.py")
            return 1
        print(f"  {OUT.relative_to(ROOT)} khớp results/t40")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"  ghi {OUT.relative_to(ROOT)}: {len(text) / 1e3:.1f} KB, "
          f"{len(build()['examples'])} ví dụ, {len(build()['questions'])} câu hỏi")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
