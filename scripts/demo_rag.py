"""Ask the demo RAG one question from the command line (task T40).

    python scripts/demo_rag.py --question "Đỉnh núi cao nhất Đông Dương là gì?"

Loads the bundle and its reading model, retrieves from the 21 bundled documents, lets the model
answer, scores the answer, and prints all of it. Needs a GPU. ``--out`` writes the same result as
JSON — the Kaggle notebook uses that to bring the smoke test home as evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.pipeline import DEFAULT_BUNDLE  # noqa: E402

LABEL_VI = {"no": "trung thực", "intrinsic": "ảo giác nội tại", "extrinsic": "ảo giác ngoại lai"}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Hỏi hệ RAG minh họa và chấm câu trả lời.")
    parser.add_argument("--question", action="append", required=True,
                        help="lặp lại cờ này để hỏi nhiều câu với một lần nạp mô hình")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--out", type=Path, default=None, help="ghi JSON kết quả vào đây")
    args = parser.parse_args()

    from vihallulens.pipeline import HallucinationDetector
    from vihallulens.serve.rag import DemoRAG

    print(f"  nạp {args.bundle} và mô hình đọc trên {args.device} …")
    detector = HallucinationDetector.from_pretrained(args.bundle, args.device)
    print(f"  {detector.describe()}")
    rag = DemoRAG(detector, top_k=args.top_k)
    print(f"  kho demo: {len(rag.corpus)} tài liệu")

    results = []
    for question in args.question:
        out = rag.ask(question)
        results.append(out.to_dict())
        score = out.score
        print()
        print("=" * 78)
        print(f"  HỎI   : {question}")
        docs = " · ".join(f"{d['title']} ({d['score']:.1f})" for d in out.retrieved)
        print(f"  TÀI LIỆU: {docs}")
        print(f"  TRẢ LỜI: {out.answer}")
        print("-" * 78)
        print(f"  nhãn       : {score['label']}  ({LABEL_VI.get(score['label'], '?')})")
        print(f"  rủi ro     : {score['risk_score']:.3f}   "
              + "  ".join(f"{k} {v:.3f}" for k, v in score["proba"].items()))
        print(f"  đoạn       : {score['n_chunks']}, đoạn được nhìn nhiều nhất:")
        top = sorted(score["chunk_attention"], key=lambda c: -c["share"])[:3]
        for c in top:
            print(f"      {100 * c['share']:5.1f} %  {c['text'][:90]}")
        t = out.elapsed_ms
        print(f"  thời gian  : truy xuất {t['retrieve']:.0f} ms · sinh {t['generate']:.0f} ms · "
              f"chấm {t['score']:.0f} ms")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n  Đã ghi {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
