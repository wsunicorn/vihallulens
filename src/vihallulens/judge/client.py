"""Talking to Gemini over plain HTTP, at a pace the free tier tolerates.

No SDK. The call is one POST to one endpoint, and the standard library does it in forty lines,
so adding a dependency would buy a retry loop this module needs to own anyway — the free tier's
two limits behave differently and the difference decides whether a run should wait or stop.

**Per-minute limit**: wait and try again. It clears by itself.
**Per-day limit**: stop. Waiting cannot help, and a script that keeps retrying turns a clean
"resume tomorrow" into an hour of silence. That is what :class:`QuotaExhaustedError` is for; the
cache is what makes stopping cheap.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Pinned, not an alias. ``gemini-flash-latest`` would quietly become a different model between
# the run that produced Bảng 1 and the run that checks it, which section 2 of CLAUDE.md rules
# out. Measured at T19: ``gemini-2.5-flash`` had already been withdrawn — the API answers 404
# with "no longer available to new users" and names this as the replacement — so a model name
# is something to verify before a run, not to assume. ``scripts/list_judge_models.py`` asks the
# API what this key can actually call.
#
# Chosen at T19 by measurement, not by reputation. ``gemini-3.6-flash`` is the stronger model
# and would be the better judge, but its free allowance is
# ``GenerateRequestsPerDayPerProjectPerModel-FreeTier = 20`` — twenty requests a *day*, which
# turns a 300-sample baseline into a fifteen-day errand. ``gemini-3.5-flash-lite`` answers
# Vietnamese with the diacritics stripped. This one keeps them, matched flash-lite's accuracy
# on a six-sample check, and costs about five seconds a call.
#
# The free tier's real ceiling is part of what E11's cost table is meant to show, so running
# the judge that the free tier actually permits is the honest measurement, not a compromise.
DEFAULT_MODEL = "gemini-3.1-flash-lite"

# Whatever Google currently allows on the free tier, listed at
# https://ai.google.dev/gemini-api/docs/rate-limits — it changes, so it is a parameter and not
# a constant buried in the code. Ten per minute is below every published free-tier figure.
DEFAULT_RPM = 10

# 599 is not an HTTP status. It is what the transport reports when the request never got an
# answer at all — a dropped connection, a DNS failure, a read timeout — so that a network
# hiccup takes the same retry path as a server error instead of killing a run mid-way. Found at
# T19, when one timed-out read ended the whole script with a traceback.
NETWORK_FAILURE = 599
RETRY_STATUSES = (429, 500, 502, 503, 504, NETWORK_FAILURE)
DEFAULT_ATTEMPTS = 4
BACKOFF_SECONDS = 5.0
MAX_BACKOFF_SECONDS = 60.0

# Thinking tokens count against this budget on the current models, and a judge cut off mid-JSON
# costs the sample entirely. Measured at T19: a short context used 741 tokens in total, so this
# leaves several times the headroom for the long contexts of ViHallu.
#
# Thinking is deliberately left at the model default rather than switched off. It is slower, but
# a baseline exists to be hard to beat, and weakening it on purpose would flatter the thesis.
# ``thinkingConfig`` is also not portable — ``gemini-3.5-flash-lite`` rejects it outright with
# HTTP 400.
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.0


class GeminiError(RuntimeError):
    """The API refused a request in a way retrying will not fix."""


class QuotaExhaustedError(GeminiError):
    """The daily allowance is gone. Stop, keep the cache, resume tomorrow."""


# Measured at T19 on a real ViHallu sample: 705 prompt tokens in, 4,3 seconds out. Sixty is
# fifteen times that, which is generous for a slow answer and cheap for a hung connection —
# the first attempt at this used 180 and a flaky link turned a twelve-sample run into eight
# minutes of waiting for sockets that were never going to answer.
TIMEOUT_SECONDS = 60


def http_transport(url: str, payload: bytes, headers: dict) -> tuple[int, bytes]:
    """The real network call, kept behind a seam so every test runs offline.

    Every failure comes back as a status rather than as an exception, so the retry ladder above
    is the single place that decides what to do about any of them.
    """
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return NETWORK_FAILURE, f"không gọi được: {error}".encode()


class GeminiJudge:
    """One judging call per :meth:`ask`, paced and retried.

    ``transport``, ``sleep`` and ``clock`` are injectable so the pacing and the retry ladder can
    be tested without a network and without the tests actually sleeping.
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        rpm: int = DEFAULT_RPM,
        attempts: int = DEFAULT_ATTEMPTS,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        transport=http_transport,
        sleep=time.sleep,
        clock=time.monotonic,
    ):
        if not api_key:
            raise ValueError(
                "thiếu khóa API. Đặt GEMINI_API_KEY trong .env — xem .env.example. "
                "Mục 2 CLAUDE.md cấm ghi khóa vào code, YAML hay notebook."
            )
        if rpm < 1:
            raise ValueError(f"rpm phải ít nhất 1, nhận {rpm}")
        if attempts < 1:
            raise ValueError(f"attempts phải ít nhất 1, nhận {attempts}")
        self.api_key = api_key
        self.model = model
        self.min_interval = 60.0 / rpm
        self.attempts = attempts
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._transport = transport
        self._sleep = sleep
        self._clock = clock
        self._last_call = None
        self.calls = 0
        self.waited_seconds = 0.0

    # -- pacing ---------------------------------------------------------------------------

    def _pace(self) -> None:
        if self._last_call is None:
            return
        idle = self.min_interval - (self._clock() - self._last_call)
        if idle > 0:
            self._sleep(idle)
            self.waited_seconds += idle

    # -- one request ----------------------------------------------------------------------

    def _payload(self, system: str, prompt: str, schema: dict) -> bytes:
        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                # Zero temperature so a re-run of an uncached sample gives the same verdict.
                # A judge that answers differently each time cannot be a reproducible baseline.
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }
        return json.dumps(body, ensure_ascii=False).encode("utf-8")

    def ask(self, system: str, prompt: str, schema: dict) -> dict:
        """Send one prompt and return the parsed JSON object the schema asked for."""
        url = ENDPOINT.format(model=self.model)
        headers = {"Content-Type": "application/json", "x-goog-api-key": self.api_key}
        payload = self._payload(system, prompt, schema)

        last = ""
        for attempt in range(self.attempts):
            self._pace()
            status, raw = self._transport(url, payload, headers)
            self._last_call = self._clock()
            self.calls += 1

            if status == 200:
                return _extract(raw)

            body = raw.decode("utf-8", "replace")
            # Classify on the whole body, show only the head of it. The first version truncated
            # first and then looked for the marker, which put the quotaId naming the limit past
            # the cut on exactly the responses that needed reading.
            last = f"{describe_quota(body)} | {body[:300]}"
            if status == 429 and is_daily(body):
                raise QuotaExhaustedError(
                    f"hết hạn mức theo ngày của {self.model} — {describe_quota(body)}. "
                    f"Cache đã lưu những mẫu đã chấm, chạy lại lệnh này ngày mai là đi tiếp "
                    f"từ chỗ dừng."
                )
            if status not in RETRY_STATUSES or attempt == self.attempts - 1:
                break
            delay = min(BACKOFF_SECONDS * 2**attempt, MAX_BACKOFF_SECONDS)
            self._sleep(delay)
            self.waited_seconds += delay

        raise GeminiError(f"API trả về {status} sau {self.attempts} lần thử: {last}")


def is_daily(body: str) -> bool:
    """Tell the per-day limit from the per-minute one, which share status 429.

    Google names the quota in the error body. The per-day ones say so in their identifier; the
    per-minute ones mention minutes. Anything unrecognised is treated as per-minute, because
    waiting on a daily limit merely wastes time, while stopping on a per-minute one throws away
    a run that would have finished on its own.
    """
    lowered = body.lower()
    return "perday" in lowered or "per day" in lowered


def describe_quota(body: str) -> str:
    """Pull the quota name and its limit out of a 429, for a message worth reading.

    Measured at T19: ``gemini-3.6-flash`` allows twenty free requests a *day*, which the error
    states and nothing else does. A run that reports only "429" leaves the reader guessing
    whether to wait a minute or to pick a different model — two very different answers.
    """
    try:
        details = json.loads(body).get("error", {}).get("details", [])
    except (json.JSONDecodeError, AttributeError, TypeError):
        return "không đọc được hạn mức"
    for detail in details:
        for violation in detail.get("violations", []):
            quota = violation.get("quotaId") or violation.get("quotaMetric", "")
            value = violation.get("quotaValue")
            if quota:
                return f"{quota}={value}" if value else str(quota)
    match = re.search(r"limit:\s*(\d+)", body)
    return f"hạn mức {match.group(1)}" if match else "không rõ hạn mức"


def _extract(raw: bytes) -> dict:
    """Pull the JSON object out of a generateContent response.

    Structured output still arrives as text inside the usual envelope, so there are two layers
    to unwrap and two ways for it to be empty — a blocked prompt, or a reply cut off before the
    closing brace.
    """
    envelope = json.loads(raw.decode("utf-8"))
    candidates = envelope.get("candidates") or []
    if not candidates:
        feedback = envelope.get("promptFeedback", {})
        raise GeminiError(f"không có câu trả lời nào, promptFeedback={feedback}")

    candidate = candidates[0]
    parts = (candidate.get("content") or {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise GeminiError(
            f"câu trả lời rỗng, finishReason={candidate.get('finishReason')!r}"
        )
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise GeminiError(f"câu trả lời không phải JSON hợp lệ: {text[:200]}") from error
