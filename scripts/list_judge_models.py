"""Which Gemini models does this key actually reach today?

Written at T19 after the model chosen from documentation turned out to be withdrawn: the API
answered 404 with "no longer available to new users" on every one of twelve samples, and the
run failed twelve times before anyone asked the API what it would accept.

Model names come and go, so this asks rather than assumes:

    python scripts/list_judge_models.py
    python scripts/list_judge_models.py --probe gemini-3.6-flash

``--probe`` sends one real judging request, which is the only way to tell a model that is listed
from a model that answers. Listing costs no quota; probing costs one call per name.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.judge.client import (  # noqa: E402
    ENDPOINT,
    GeminiError,
    GeminiJudge,
)
from vihallulens.judge.prompt import (  # noqa: E402
    RESPONSE_SCHEMA,
    SYSTEM,
    build_prompt,
)

LIST_URL = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200"

# A context short enough to cost almost nothing and unambiguous enough that the right answer is
# not in doubt: the response adds a population figure the context never mentions.
PROBE_CONTEXT = "Hà Nội là thủ đô của Việt Nam. Thành phố Hồ Chí Minh đông dân nhất cả nước."
PROBE_RESPONSE = "Hà Nội có 8 triệu dân."
PROBE_EXPECTED = "ngoai_lai"


def list_models(api_key: str) -> list[dict]:
    request = urllib.request.Request(LIST_URL, headers={"x-goog-api-key": api_key})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.loads(response.read())
    return [
        model for model in payload.get("models", [])
        if "generateContent" in model.get("supportedGenerationMethods", [])
    ]


def probe(api_key: str, model: str) -> tuple[bool, str]:
    """Send one real judging request and report what came back."""
    judge = GeminiJudge(api_key, model=model, attempts=1)
    prompt = build_prompt(PROBE_CONTEXT, PROBE_RESPONSE)
    started = time.perf_counter()
    try:
        answer = judge.ask(SYSTEM, prompt, RESPONSE_SCHEMA)
    except GeminiError as error:
        return False, str(error).splitlines()[0][:150]
    seconds = time.perf_counter() - started
    verdict = answer.get("nhan_dinh")
    reason = str(answer.get("ly_do", ""))

    notes = [f"{seconds:.1f}s", f"nhận định {verdict!r}"]
    if verdict != PROBE_EXPECTED:
        notes.append(f"SAI, đáng lẽ {PROBE_EXPECTED!r}")
    # A model that strips Vietnamese diacritics is a poor baseline whatever it scores.
    # Measured at T19: gemini-3.5-flash-lite does exactly this.
    if reason and not any(character in reason for character in "ăâđêôơưáàảãạ"):
        notes.append("CẢNH BÁO: lý do không có dấu tiếng Việt")
    return verdict == PROBE_EXPECTED, ", ".join(notes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Xem khóa hiện tại gọi được model nào.")
    parser.add_argument("--probe", nargs="*", default=None,
                        help="gửi thử một yêu cầu chấm thật tới từng tên; tốn 1 lượt gọi mỗi tên")
    parser.add_argument("--all", action="store_true",
                        help="liệt kê cả model ảnh, TTS, robotics")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("thiếu GEMINI_API_KEY trong .env — xem .env.example")
        return 1

    print()
    print("=" * 80)
    print("MODEL GỌI ĐƯỢC BẰNG KHÓA HIỆN TẠI")
    print("=" * 80)
    print(f"  endpoint: {ENDPOINT.format(model='<model>')}")

    models = list_models(api_key)
    skip = ("image", "tts", "robotics", "lyria", "transcribe", "computer-use", "nano-banana")
    shown = [
        model for model in models
        if args.all or not any(word in model["name"] for word in skip)
    ]
    print(f"  {len(shown)} model sinh văn bản (trên tổng {len(models)} model)")
    print()
    for model in shown:
        print(f"    {model['name'][len('models/'):]:<40} {model.get('displayName', '')}")

    if args.probe is None:
        print()
        print("  Danh sách này chỉ nói model TỒN TẠI, không nói khóa này gọi được.")
        print("  Thêm --probe <tên> để gửi thử một yêu cầu chấm thật.")
        return 0

    names = args.probe or [GeminiJudge.__init__.__defaults__[0]]
    print()
    print("-" * 80)
    print("THỬ GỌI THẬT")
    print("-" * 80)
    print(f"  ngữ cảnh   : {PROBE_CONTEXT}")
    print(f"  phản hồi   : {PROBE_RESPONSE}")
    print(f"  đáp án đúng: {PROBE_EXPECTED}")
    print()
    failures = 0
    for name in names:
        ok, note = probe(api_key, name)
        failures += int(not ok)
        print(f"    {'ĐƯỢC' if ok else 'HỎNG'}  {name:<32} {note}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
