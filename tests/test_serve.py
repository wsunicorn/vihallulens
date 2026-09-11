"""Tests for the REST service (task T37), run against a fake detector — no GPU, no model.

What is checked is the contract of ``docs/SPEC.md`` §2.6 and the two places the service can go
wrong quietly: answering before the model is loaded, and accepting a ``chunk_strategy`` the
detector was not fitted for.
"""

from __future__ import annotations

import sys
import time
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


def test_scoring_is_503_when_nothing_will_load():
    """No detector and no loader: the server says so, it does not raise or return garbage."""
    app = create_app(detector=None, load_on_startup=False)
    with TestClient(app) as client:
        health = client.get("/health").json()
        assert health["model_loaded"] is False and health["status"] == "not_loaded"
        r = client.post("/score", json={"context": "c", "response": "r"})
        assert r.status_code == 503
        assert "chưa nạp" in r.json()["detail"]


def test_health_answers_while_the_model_is_still_loading():
    """The bug T38 found: a synchronous load kept the port closed for the whole load.

    The loader blocks on an event; the server must already be answering /health with
    ``loading`` before the event is set, and switch to ``ok`` after.
    """
    import threading

    gate = threading.Event()
    fake = FakeDetector()

    def slow_loader():
        gate.wait(timeout=10)
        return fake

    app = create_app(detector=None, load_on_startup=True, loader=slow_loader)
    with TestClient(app) as client:
        health = client.get("/health").json()
        assert health["status"] == "loading" and health["model_loaded"] is False
        r = client.post("/score", json={"context": "c", "response": "r"})
        assert r.status_code == 503 and "đang nạp" in r.json()["detail"]

        gate.set()
        for _ in range(100):
            if client.get("/health").json()["status"] == "ok":
                break
            time.sleep(0.02)
        health = client.get("/health").json()
        assert health["status"] == "ok" and health["model_loaded"] is True
        assert client.post("/score", json={"context": "c", "response": "r"}).status_code == 200


def test_health_reports_a_failed_load_with_the_reason():
    def broken_loader():
        raise RuntimeError("không có CUDA")

    app = create_app(detector=None, load_on_startup=True, loader=broken_loader)
    with TestClient(app) as client:
        for _ in range(100):
            if client.get("/health").json()["status"] == "error":
                break
            time.sleep(0.02)
        health = client.get("/health").json()
        assert health["status"] == "error"
        assert "không có CUDA" in health["error"]
        r = client.post("/score", json={"context": "c", "response": "r"})
        assert r.status_code == 503 and "không có CUDA" in r.json()["detail"]


# ---------------------------------------------------------------- T39: the observation page

def test_index_serves_the_observation_page(client):
    client, _ = client
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    page = r.text
    # It must use the API's own field names, or a schema change would break it silently.
    for marker in ("/score", "/health", "chunk_attention", "risk_score", "char_start", "char_end"):
        assert marker in page, marker
    assert "<script src=" not in page   # HTML + JS thuần, không framework, đúng SPEC §2.6


def test_index_is_not_in_the_openapi_schema(client):
    client, _ = client
    paths = client.get("/openapi.json").json()["paths"]
    assert "/" not in paths
    assert set(paths) >= {"/score", "/score/batch", "/health"}


# ---------------------------------------------------------------- T40: the demo RAG

class FakeGenerator:
    def __init__(self):
        self.calls = []

    def generate(self, context, question):
        self.calls.append((context, question))
        return "Câu trả lời sinh từ ngữ cảnh."

    def describe(self):
        return "fake generator"


fake_generator = FakeGenerator()


@pytest.fixture
def rag_client():
    detector = FakeDetector()
    app = create_app(detector=detector, load_on_startup=False, generator=fake_generator)
    with TestClient(app) as client:
        yield client, detector


def test_demo_corpus_is_readable_without_a_model():
    app = create_app(detector=None, load_on_startup=False)
    with TestClient(app) as client:
        docs = client.get("/demo/corpus").json()
    assert len(docs) >= 20
    assert {"id", "title", "text"} <= set(docs[0])
    assert any(d["title"] == "Sa Pa" for d in docs)


def test_demo_ask_retrieves_answers_and_scores(rag_client):
    client, detector = rag_client
    r = client.post("/demo/ask", json={"question": "Đỉnh núi cao nhất Đông Dương là gì?"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["retrieved"][0]["title"] == "Sa Pa"            # BM25 found the right document
    assert out["answer"] == "Câu trả lời sinh từ ngữ cảnh."
    assert "Fansipan" in out["context"]
    assert fake_generator.calls[-1] == (out["context"], out["question"])   # same context it scored
    assert client.get("/health").json()["generator"] == "fake generator"
    assert out["score"]["label"] in ("no", "intrinsic", "extrinsic")
    assert set(out["elapsed_ms"]) == {"retrieve", "generate", "score"}
    # The scored triple is exactly the retrieved context, the question, and the generated answer.
    assert detector.calls[-1] == (out["context"], out["question"], out["answer"])


def test_demo_ask_respects_top_k(rag_client):
    client, _ = rag_client
    body = {"question": "Huế là kinh đô của triều nào?", "top_k": 1}
    out = client.post("/demo/ask", json=body).json()
    assert len(out["retrieved"]) == 1 and out["retrieved"][0]["title"] == "Huế"


def test_demo_ask_is_503_before_the_model_loads():
    app = create_app(detector=None, load_on_startup=False)
    with TestClient(app) as client:
        assert client.post("/demo/ask", json={"question": "x"}).status_code == 503


def test_index_has_the_rag_panel(rag_client):
    client, _ = rag_client
    page = client.get("/").text
    assert "/demo/ask" in page and 'id="ask"' in page
