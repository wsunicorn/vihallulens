"""Tests for the REST service (task T37), run against a fake detector — no GPU, no model.

What is checked is the contract of ``docs/SPEC.md`` §2.6 and the two places the service can go
wrong quietly: answering before the model is loaded, and accepting a ``chunk_strategy`` the
detector was not fitted for.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.pipeline import ChunkAttention, ScoreResult  # noqa: E402
from vihallulens.serve.app import MAX_BATCH, create_app  # noqa: E402


class FakeDetector:
    """Returns a fixed, well-formed result and remembers what it was asked."""

    def __init__(self, strategy="sentence"):
        self.calls = []
        self.chunking = SimpleNamespace(strategy=strategy, min_words=5)
        self.extractor = SimpleNamespace(device="cpu")
        self.bundle = SimpleNamespace(
            describe=lambda: "fake: basic · all · 2 × 2",
            config={"extractor": {"model_name": "fake/model"},
                    "chunking": {"strategy": strategy, "min_words": 5}},
        )

    def score(self, context, question, response):
        self.calls.append((context, question, response))
        return ScoreResult(
            label="intrinsic",
            proba={"no": 0.2, "intrinsic": 0.5, "extrinsic": 0.3},
            risk_score=0.8,
            chunk_attention=[ChunkAttention(0, "Một.", 0, 4, 0.7),
                             ChunkAttention(1, "Hai.", 5, 9, 0.3)],
            elapsed_ms=12.5,
            n_chunks=2,
            truncated=False,
        )


@pytest.fixture
def client():
    detector = FakeDetector()
    app = create_app(detector=detector, load_on_startup=False)
    with TestClient(app) as client:
        yield client, detector


def test_score_returns_the_spec_schema(client):
    client, detector = client
    body = {"context": "Một. Hai.", "question": "Hỏi?", "response": "Đáp."}
    r = client.post("/score", json=body)
    assert r.status_code == 200, r.text
    out = r.json()
    assert set(out) >= {"label", "proba", "chunk_attention", "risk_score", "elapsed_ms"}
    assert out["label"] == "intrinsic" and out["risk_score"] == 0.8
    assert [c["index"] for c in out["chunk_attention"]] == [0, 1]
    assert detector.calls == [("Một. Hai.", "Hỏi?", "Đáp.")]


def test_question_is_optional(client):
    client, detector = client
    r = client.post("/score", json={"context": "Ngữ cảnh.", "response": "Đáp."})
    assert r.status_code == 200
    assert detector.calls[-1][1] == ""


@pytest.mark.parametrize("missing", ["context", "response"])
def test_missing_required_field_is_422(client, missing):
    client, _ = client
    body = {"context": "Ngữ cảnh.", "response": "Đáp."}
    body.pop(missing)
    assert client.post("/score", json=body).status_code == 422


def test_matching_chunk_strategy_is_accepted(client):
    client, _ = client
    body = {"context": "c", "response": "r", "chunk_strategy": "sentence"}
    assert client.post("/score", json=body).status_code == 200


def test_foreign_chunk_strategy_is_refused_not_ignored(client):
    """The detector's shape features describe distributions over *its* chunks."""
    client, detector = client
    body = {"context": "c", "response": "r", "chunk_strategy": "token_window"}
    r = client.post("/score", json=body)
    assert r.status_code == 400
    assert "sentence" in r.json()["detail"]
    assert detector.calls == []   # refused before scoring, not after


def test_batch_returns_one_result_per_item_in_order(client):
    client, detector = client
    items = [{"context": f"c{i}", "response": f"r{i}"} for i in range(3)]
    r = client.post("/score/batch", json={"items": items})
    assert r.status_code == 200
    out = r.json()
    assert len(out["results"]) == 3
    assert [c[0] for c in detector.calls] == ["c0", "c1", "c2"]
    assert out["elapsed_ms"] >= 0


def test_batch_refuses_empty_and_oversized(client):
    client, _ = client
    assert client.post("/score/batch", json={"items": []}).status_code == 422
    too_many = [{"context": "c", "response": "r"}] * (MAX_BATCH + 1)
    assert client.post("/score/batch", json={"items": too_many}).status_code == 422


def test_batch_refuses_whole_batch_on_one_bad_strategy(client):
    """All or nothing: a caller must not get two results and one error mixed together."""
    client, detector = client
    items = [{"context": "c", "response": "r"},
             {"context": "c", "response": "r", "chunk_strategy": "token_window"}]
    assert client.post("/score/batch", json={"items": items}).status_code == 400
    assert detector.calls == []


def test_health_reports_loaded_model_and_counts_requests(client):
    client, _ = client
    before = client.get("/health").json()
    assert before["status"] == "ok" and before["model_loaded"] is True
    assert before["reading_model"] == "fake/model"
    assert before["chunking"]["strategy"] == "sentence"
    assert before["requests_served"] == 0

    client.post("/score", json={"context": "c", "response": "r"})
    after = client.get("/health").json()
    assert after["requests_served"] == 1
    assert after["uptime_s"] >= 0


def test_scoring_is_503_until_the_model_is_loaded():
    """A server that is still loading must say so, not raise or return garbage."""
    app = create_app(detector=None, load_on_startup=False)
    with TestClient(app) as client:
        health = client.get("/health").json()
        assert health["model_loaded"] is False and health["status"] == "loading"
        r = client.post("/score", json={"context": "c", "response": "r"})
        assert r.status_code == 503
        assert "chưa nạp" in r.json()["detail"]
