"""Start the REST service (task T37).

    python scripts/serve.py --bundle models/e03_chunk_aware.pkl --port 8000

Loads the bundle and its reading model once at startup — about a minute for Qwen2.5-7B in NF4
on a T4 — then serves the three endpoints of ``docs/SPEC.md`` §2.6. ``GET /health`` reports
``loading`` until the model is in, ``ok`` after, and ``error`` with the reason if loading failed,
so a caller polling it never mistakes a half-started server for a ready one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.pipeline import DEFAULT_BUNDLE  # noqa: E402


def main() -> int:
    # Before argparse: --help prints Vietnamese, and a cp1252 console would crash on it.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Dịch vụ REST phát hiện ảo giác.")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--host", default="127.0.0.1",
                        help="127.0.0.1 chỉ nhận kết nối từ máy này; 0.0.0.0 để mở ra ngoài")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--generator", default=None,
                        help="mô hình sinh câu trả lời cho hệ RAG demo, nạp lười ở câu hỏi đầu "
                             "tiên; mặc định Qwen2.5-3B bfloat16 — cỡ lớn nhất còn vừa cạnh bộ "
                             "đọc 7B trên card 16 GB")
    args = parser.parse_args()

    import uvicorn

    from vihallulens.serve.app import create_app

    app = create_app(bundle_path=args.bundle, device=args.device,
                     generator_model=args.generator)
    print(f"  bundle   : {args.bundle}")
    print(f"  thiết bị : {args.device}")
    print(f"  địa chỉ  : http://{args.host}:{args.port}  (tài liệu ở /docs)")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
