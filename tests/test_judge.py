"""The LLM-judge baseline of E10.

Everything here runs offline. The transport is a seam precisely so the pacing, the retry ladder
and the two different meanings of HTTP 429 can be tested without spending free-tier quota — and
so a mistake in them is caught here rather than halfway through a 300-sample run.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from vihallulens.evaluation.metrics import LABELS
from vihallulens.judge.cache import JudgeCache, cache_key
from vihallulens.judge.client import (
    GeminiError,
    GeminiJudge,
    QuotaExhaustedError,
)
from vihallulens.judge.prompt import (
    RESPONSE_SCHEMA,
    VERDICT_TO_LABEL,
    build_prompt,
    clamp_confidence,
    to_label,
)


def reply(**fields) -> bytes:
    body = {"candidates": [{"content": {"parts": [{"text": json.dumps(fields)}]}}]}
    return json.dumps(body).encode("utf-8")


VERDICT = reply(ly_do="vì ngữ cảnh nói khác", nhan_dinh="noi_tai", do_tin_cay=0.9)


class Transport:
    """Replays a fixed list of (status, body) pairs and records what it was sent."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.sent = []

    def __call__(self, url, payload, headers):
        self.sent.append({"url": url, "payload": json.loads(payload), "headers": headers})
        return self.responses.pop(0) if self.responses else (200, VERDICT)


def judge(*responses, **kwargs):
    slept = []
    transport = Transport(*responses)
    client = GeminiJudge(
        "khoa-gia", transport=transport, sleep=slept.append, clock=lambda: 0.0, **kwargs
    )
    client.transport, client.slept = transport, slept
    return client


# -- the prompt ---------------------------------------------------------------------------


def test_the_prompt_carries_the_context_and_the_response():
    prompt = build_prompt("Hà Nội là thủ đô.", "Hà Nội có 8 triệu dân.")
    assert "Hà Nội là thủ đô." in prompt
    assert "Hà Nội có 8 triệu dân." in prompt


def test_a_corpus_without_questions_gets_no_question_block():
    """Rule 1 of section 8 of CLAUDE.md: an empty ``Câu hỏi:`` line is noise, and three of the
    four corpora have no question at all. Counted rather than searched for, because the rubric
    itself says "Câu hỏi duy nhất" while explaining the task — so one mention is the floor."""
    assert build_prompt("Ngữ cảnh.", "Phản hồi.").count("Câu hỏi") == 1
    assert build_prompt("Ngữ cảnh.", "Phản hồi.", "   ").count("Câu hỏi") == 1
    assert build_prompt("Ngữ cảnh.", "Phản hồi.", "Ở đâu?").count("Câu hỏi") == 2


def test_a_question_appears_when_there_is_one():
    assert "Câu hỏi: Thủ đô ở đâu?" in build_prompt("Ngữ cảnh.", "Phản hồi.", "Thủ đô ở đâu?")


def test_the_rubric_names_all_three_verdicts():
    """The judge is given the same three codes the two students used at T13. Handing it a
    different definition of the classes would make Bảng 1 compare instructions, not methods."""
    prompt = build_prompt("a", "b")
    for verdict in VERDICT_TO_LABEL:
        assert verdict in prompt


def test_the_schema_offers_exactly_the_three_verdicts():
    """No ``khong_chac``. The humans could decline to answer; a baseline cannot, or its macro-F1
    is computed on a different set of samples from every other row."""
    assert RESPONSE_SCHEMA["properties"]["nhan_dinh"]["enum"] == list(VERDICT_TO_LABEL)


def test_the_schema_asks_for_the_reason_before_the_verdict():
    """Gemini emits fields in this order, so it works through the evidence before committing
    rather than justifying a label it has already produced."""
    ordering = RESPONSE_SCHEMA["propertyOrdering"]
    assert ordering.index("ly_do") < ordering.index("nhan_dinh")


# -- reading the answer --------------------------------------------------------------------


def test_every_verdict_maps_to_a_corpus_label():
    assert {to_label(verdict) for verdict in VERDICT_TO_LABEL} == set(LABELS)


def test_an_unknown_verdict_is_rejected_rather_than_guessed():
    with pytest.raises(ValueError, match="mã lạ"):
        to_label("có lẽ vậy")


def test_a_verdict_is_read_case_and_space_insensitively():
    assert to_label("  NOI_TAI ") == "intrinsic"


@pytest.mark.parametrize(
    ("given", "wanted"),
    [(0.9, 0.9), (85, 0.85), (1.0, 1.0), (-3, 0.0), (200, 1.0), ("khá chắc", 0.0), (None, 0.0)],
)
def test_confidence_is_pulled_into_the_unit_interval(given, wanted):
    """Models answer 0,85 and 85 with equal cheer, and occasionally with a sentence."""
    assert clamp_confidence(given) == pytest.approx(wanted)


# -- the request ----------------------------------------------------------------------------


def test_the_key_travels_in_a_header_not_in_the_url():
    """A key in the query string ends up in server logs, in shell history and in any traceback
    that prints the URL."""
    client = judge()
    client.ask("hệ thống", "câu hỏi", RESPONSE_SCHEMA)
    sent = client.transport.sent[0]
    assert sent["headers"]["x-goog-api-key"] == "khoa-gia"
    assert "khoa-gia" not in sent["url"]


def test_the_request_pins_the_temperature_to_zero():
    """A judge that answers differently on a re-run is not a reproducible baseline."""
    client = judge()
    client.ask("hệ thống", "câu hỏi", RESPONSE_SCHEMA)
    assert client.transport.sent[0]["payload"]["generationConfig"]["temperature"] == 0.0


def test_the_request_asks_for_structured_output():
    client = judge()
    client.ask("hệ thống", "câu hỏi", RESPONSE_SCHEMA)
    config = client.transport.sent[0]["payload"]["generationConfig"]
    assert config["responseMimeType"] == "application/json"
    assert config["responseSchema"] == RESPONSE_SCHEMA


def test_a_missing_key_is_refused_before_any_call_is_made():
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        GeminiJudge("")


# -- pacing ---------------------------------------------------------------------------------


def test_the_first_call_does_not_wait():
    client = judge()
    client.ask("s", "p", RESPONSE_SCHEMA)
    assert client.slept == []


def test_later_calls_wait_out_the_per_minute_limit():
    """The clock is frozen, so the gap the pacer computes is the whole interval."""
    client = judge((200, VERDICT), (200, VERDICT), rpm=12)
    client.ask("s", "p", RESPONSE_SCHEMA)
    client.ask("s", "p", RESPONSE_SCHEMA)
    assert client.slept == [pytest.approx(5.0)]


# -- the two meanings of 429 ------------------------------------------------------------------


def test_a_per_minute_limit_is_waited_out_and_retried():
    body = json.dumps({"error": {"details": [
        {"quotaId": "GenerateRequestsPerMinutePerProjectPerModel"}]}}).encode()
    client = judge((429, body), (200, VERDICT))
    answer = client.ask("s", "p", RESPONSE_SCHEMA)
    assert answer["nhan_dinh"] == "noi_tai"
    assert client.calls == 2


def test_a_per_day_limit_stops_immediately():
    """Waiting cannot help, and retrying turns a clean "resume tomorrow" into an hour of
    silence. The cache is what makes stopping cheap."""
    body = json.dumps({"error": {"details": [
        {"quotaId": "GenerateRequestsPerDayPerProjectPerModel"}]}}).encode()
    client = judge((429, body))
    with pytest.raises(QuotaExhaustedError, match="ngày mai"):
        client.ask("s", "p", RESPONSE_SCHEMA)
    assert client.calls == 1


def test_a_server_error_is_retried():
    client = judge((503, b"unavailable"), (200, VERDICT))
    assert client.ask("s", "p", RESPONSE_SCHEMA)["nhan_dinh"] == "noi_tai"


def test_a_bad_request_is_not_retried():
    """400 means the request itself is wrong; sending it again wastes quota to be told so."""
    client = judge((400, b"bad request"))
    with pytest.raises(GeminiError):
        client.ask("s", "p", RESPONSE_SCHEMA)
    assert client.calls == 1


def test_retries_stop_after_the_configured_number_of_attempts():
    client = judge((503, b"x"), (503, b"x"), (503, b"x"), attempts=3)
    with pytest.raises(GeminiError, match="sau 3 lần thử"):
        client.ask("s", "p", RESPONSE_SCHEMA)
    assert client.calls == 3


# -- reading the envelope ---------------------------------------------------------------------


def test_a_blocked_prompt_is_reported_not_returned_as_empty():
    body = json.dumps({"promptFeedback": {"blockReason": "SAFETY"}}).encode()
    client = judge((200, body))
    with pytest.raises(GeminiError, match="promptFeedback"):
        client.ask("s", "p", RESPONSE_SCHEMA)


def test_an_answer_cut_off_mid_json_is_reported():
    cut = {"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": '{"ly_do": "vì'}]}}
    body = json.dumps({"candidates": [cut]}).encode()
    client = judge((200, body))
    with pytest.raises(GeminiError, match="không phải JSON"):
        client.ask("s", "p", RESPONSE_SCHEMA)


def test_an_empty_answer_names_the_finish_reason():
    body = json.dumps({"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": []}}]})
    client = judge((200, body.encode()))
    with pytest.raises(GeminiError, match="MAX_TOKENS"):
        client.ask("s", "p", RESPONSE_SCHEMA)


# -- the cache ---------------------------------------------------------------------------------


def test_the_key_changes_when_the_prompt_changes():
    """Reword the rubric and the old answers stop matching, which is correct: they answered a
    different question."""
    assert cache_key("m", "câu hỏi A") != cache_key("m", "câu hỏi B")


def test_the_key_changes_when_the_model_changes():
    assert cache_key("gemini-2.5-flash", "p") != cache_key("gemini-2.0-flash", "p")


def test_the_key_is_the_same_every_time():
    assert cache_key("m", "p") == cache_key("m", "p")


def test_an_answer_survives_a_restart(tmp_path):
    """The property the whole module exists for: a run killed by quota keeps what it paid for."""
    path = tmp_path / "cache.jsonl"
    JudgeCache(path).put("abc", {"verdict": "noi_tai"})
    assert JudgeCache(path).get("abc")["verdict"] == "noi_tai"


def test_an_answer_is_written_the_moment_it_arrives(tmp_path):
    """Not on exit. A process killed mid-run must not lose the calls it already spent."""
    path = tmp_path / "cache.jsonl"
    cache = JudgeCache(path)
    cache.put("abc", {"verdict": "khong"})
    assert path.read_text(encoding="utf-8").count("\n") == 1


def test_a_truncated_final_line_costs_one_entry_not_the_whole_cache(tmp_path):
    """A run killed mid-write leaves half a line. Refusing to start would throw away every
    answer already paid for."""
    path = tmp_path / "cache.jsonl"
    cache = JudgeCache(path)
    cache.put("a", {"verdict": "khong"})
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"key": "b", "verdi')
    reopened = JudgeCache(path)
    assert len(reopened) == 1 and "a" in reopened


def test_a_missing_cache_file_is_simply_empty(tmp_path):
    assert len(JudgeCache(tmp_path / "chua-co.jsonl")) == 0


def test_a_later_answer_replaces_an_earlier_one_for_the_same_key(tmp_path):
    path = tmp_path / "cache.jsonl"
    cache = JudgeCache(path)
    cache.put("a", {"verdict": "khong"})
    cache.put("a", {"verdict": "noi_tai"})
    assert JudgeCache(path).get("a")["verdict"] == "noi_tai"


# -- choosing the subset -------------------------------------------------------------------------


def frame(n):
    import pandas as pd

    return pd.DataFrame({
        "sample_id": [f"s{index:04d}" for index in range(n)],
        "context": ["ngữ cảnh"] * n,
        "response": ["phản hồi"] * n,
        "label": [LABELS[index % 3] for index in range(n)],
    })


def test_the_subset_is_the_same_every_time():
    """It has to be, or the cache misses on the second run and the bill is paid twice."""
    from run_judge_baseline import choose_samples

    first = choose_samples(frame(200), 50)["sample_id"].tolist()
    second = choose_samples(frame(200), 50)["sample_id"].tolist()
    assert first == second


def test_the_subset_does_not_depend_on_the_order_of_the_rows():
    from run_judge_baseline import choose_samples

    rows = frame(200)
    shuffled = rows.sample(frac=1.0, random_state=3).reset_index(drop=True)
    assert (sorted(choose_samples(rows, 50)["sample_id"])
            == sorted(choose_samples(shuffled, 50)["sample_id"]))


def test_the_subset_has_the_requested_size():
    from run_judge_baseline import choose_samples

    assert len(choose_samples(frame(200), 50)) == 50


def test_asking_for_more_than_there_is_returns_everything():
    from run_judge_baseline import choose_samples

    assert len(choose_samples(frame(40), 300)) == 40


# -- turning a self-reported number into probabilities --------------------------------------------


def test_the_named_label_stays_the_most_likely_one():
    """Otherwise the calibration figure would score a different prediction from the one being
    reported — the same two-quantities-one-name trap T18 had to undo twice."""
    import numpy as np

    from run_judge_baseline import as_probabilities

    proba, floored = as_probabilities(np.asarray(["no", "extrinsic"]), [0.05, 0.9])
    assert [LABELS[row] for row in proba.argmax(axis=1)] == ["no", "extrinsic"]
    assert floored == 1


def test_each_row_of_probabilities_sums_to_one():
    import numpy as np

    from run_judge_baseline import as_probabilities

    proba, _ = as_probabilities(np.asarray(["no", "intrinsic", "extrinsic"]), [0.9, 0.5, 0.34])
    assert proba.sum(axis=1) == pytest.approx(1.0)


def test_a_confident_answer_is_left_alone():
    import numpy as np

    from run_judge_baseline import as_probabilities

    proba, floored = as_probabilities(np.asarray(["no"]), [0.8])
    assert floored == 0
    assert proba[0][LABELS.index("no")] == pytest.approx(0.8)


# -- the network itself failing ----------------------------------------------------------------


def test_a_dropped_connection_is_retried_like_a_server_error():
    """Found at T19: one timed-out read ended the whole script with a traceback. A 300-sample
    run must not die on a single dropped packet."""
    from vihallulens.judge.client import NETWORK_FAILURE

    client = judge((NETWORK_FAILURE, b"khong goi duoc"), (200, VERDICT))
    assert client.ask("s", "p", RESPONSE_SCHEMA)["nhan_dinh"] == "noi_tai"
    assert client.calls == 2


def test_a_timeout_becomes_a_status_not_an_exception():
    """The retry ladder is the one place that decides what to do about a failure, so the
    transport has to hand it every failure in the same shape."""
    from vihallulens.judge.client import NETWORK_FAILURE, http_transport

    status, body = http_transport("https://khong-ton-tai.invalid/x", b"{}", {})
    assert status == NETWORK_FAILURE
    assert b"kh\xc3\xb4ng g\xe1\xbb\x8di \xc4\x91\xc6\xb0\xe1\xbb\xa3c" in body


# -- reading a 429 ------------------------------------------------------------------------------


QUOTA_429 = json.dumps({"error": {
    "code": 429,
    "message": "You exceeded your current quota. " + "x" * 400,
    "details": [
        {"@type": "type.googleapis.com/google.rpc.Help", "links": [{"url": "https://x"}]},
        {"@type": "type.googleapis.com/google.rpc.QuotaFailure", "violations": [{
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
            "quotaValue": "20"}]},
    ],
}})


def test_the_quota_id_is_found_past_the_first_four_hundred_characters():
    """The bug this test exists for: the first version truncated the body to 400 characters and
    *then* looked for the marker, which put the quotaId past the cut on exactly the responses
    that needed reading. A daily limit was then treated as a per-minute one and retried."""
    from vihallulens.judge.client import is_daily

    assert QUOTA_429.index("quotaId") > 400
    assert is_daily(QUOTA_429)


def test_the_quota_is_named_with_its_limit():
    from vihallulens.judge.client import describe_quota

    assert describe_quota(QUOTA_429) == "GenerateRequestsPerDayPerProjectPerModel-FreeTier=20"


def test_a_per_day_limit_is_recognised_from_a_real_response():
    client = judge((429, QUOTA_429.encode()))
    with pytest.raises(QuotaExhaustedError, match="FreeTier=20"):
        client.ask("s", "p", RESPONSE_SCHEMA)
    assert client.calls == 1


def test_a_body_that_is_not_json_does_not_crash_the_reader():
    from vihallulens.judge.client import describe_quota, is_daily

    assert describe_quota("<html>502 Bad Gateway</html>") == "không đọc được hạn mức"
    assert not is_daily("<html>502 Bad Gateway</html>")


def test_a_limit_stated_only_in_prose_is_still_reported():
    from vihallulens.judge.client import describe_quota

    body = json.dumps({"error": {"message": "Quota exceeded for metric: x, limit: 20"}})
    assert describe_quota(body) == "hạn mức 20"


# -- the dry run has to look in the same drawer ---------------------------------------------


def test_a_dry_run_finds_what_a_real_run_stored(tmp_path):
    """The completion check of T19 in TASKS.md is exactly this: re-running must make no API
    call. The first version derived the model name from the judge object and fell back to the
    string "dry-run" when there was none, so --dry-run computed a key that could never match
    and reported all 300 samples missing from a cache that held all 300."""
    from run_judge_baseline import judge_one

    cache = JudgeCache(tmp_path / "cache.jsonl")
    row = {"sample_id": "s1", "context": "Ngữ cảnh.", "response": "Phản hồi.", "question": ""}
    client = judge()

    stored, fresh = judge_one(client, cache, row, client.model)
    assert fresh and stored["verdict"] == "noi_tai"

    # No judge at all: the dry-run path.
    replayed, fresh_again = judge_one(None, cache, row, client.model)
    assert not fresh_again
    assert replayed["verdict"] == "noi_tai"


def test_a_dry_run_without_a_cached_answer_says_so(tmp_path):
    from run_judge_baseline import judge_one

    cache = JudgeCache(tmp_path / "cache.jsonl")
    row = {"sample_id": "s1", "context": "Ngữ cảnh.", "response": "Phản hồi.", "question": ""}
    record, fresh = judge_one(None, cache, row, "gemini-3.1-flash-lite")
    assert not fresh and "chưa có trong cache" in record["error"]


def test_a_different_model_does_not_reuse_the_first_one_s_answers(tmp_path):
    """Two models answering the same prompt are two measurements, not one."""
    from run_judge_baseline import judge_one

    cache = JudgeCache(tmp_path / "cache.jsonl")
    row = {"sample_id": "s1", "context": "Ngữ cảnh.", "response": "Phản hồi.", "question": ""}
    client = judge()
    judge_one(client, cache, row, "model-a")
    record, _ = judge_one(None, cache, row, "model-b")
    assert "chưa có trong cache" in record["error"]
