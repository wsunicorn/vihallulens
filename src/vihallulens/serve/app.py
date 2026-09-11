"""The REST service of ``docs/SPEC.md`` §2.6: three endpoints over ``HallucinationDetector``.

    POST /score        one (context, question, response) → label, proba, chunk_attention, ...
    POST /score/batch  a list of those → a list of results, sequential on one GPU
    GET  /health       is the model loaded, which one, how much VRAM it holds

Built as a factory, ``create_app``, so the tests can hand it a fake detector and exercise every
route without a GPU, and so the real server loads the model once at startup rather than on the
first request — a 7B model in NF4 takes about a minute to load, and a health check that says
"ready" before that minute is up would be lying.

One field of the spec is handled more strictly than it reads. The request schema carries
``chunk_strategy``. The detector, however, was fitted on features produced by one specific
chunking — sentence boundaries with ``min_words=5``, chosen at E05 over three window sizes and
a control — and its five shape statistics describe distributions over *those* chunks. Chunking
a request differently would hand the classifier a vector whose columns no longer mean what it
learned, and it would return a label anyway. So ``chunk_strategy`` is accepted, checked against
the bundle, and refused with 400 when it differs. Silently ignoring it would be the worse bug.
"""

from __future__ import annotations

import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from vihallulens import __version__
from vihallulens.pipeline import DEFAULT_BUNDLE

MAX_BATCH = 64


# ---------------------------------------------------------------- schemas

class ScoreRequest(BaseModel):
    context: str = Field(min_length=1, description="ngữ cảnh đã truy xuất")
    response: str = Field(min_length=1, description="câu trả lời cần chấm")
    question: str = Field(default="", description="câu hỏi; để trống với bài kiểm chứng")
    chunk_strategy: str | None = Field(
        default=None,
        description="phải trùng cách chia đoạn mà bộ phát hiện được khớp cùng; để trống là dùng "
                    "đúng cách đó. Gửi cách khác sẽ bị từ chối chứ không bị lặng lẽ bỏ qua.",
    )


class ChunkAttentionOut(BaseModel):
    index: int
    text: str
    char_start: int
    char_end: int
    share: float


class ScoreResponse(BaseModel):
    label: str
    proba: dict[str, float]
    risk_score: float
    chunk_attention: list[ChunkAttentionOut]
    elapsed_ms: float
    n_chunks: int
    truncated: bool
    nonfinite_layers: list[int]


class BatchRequest(BaseModel):
    items: list[ScoreRequest] = Field(min_length=1, max_length=MAX_BATCH)


class BatchResponse(BaseModel):
    results: list[ScoreResponse]
    elapsed_ms: float


class HealthResponse(BaseModel):
    status: str                 # loading | ok | error | not_loaded
    error: str | None = None    # lý do khi status == "error"
    version: str
    model_loaded: bool
    bundle: str | None
    reading_model: str | None
    chunking: dict | None
    device: str | None
    vram_allocated_mb: float | None
    vram_reserved_mb: float | None
    requests_served: int
    uptime_s: float


# ---------------------------------------------------------------- app

def vram_mb() -> tuple[float | None, float | None]:
    """Allocated and reserved VRAM on the current device, or ``None`` without CUDA."""
    try:
        import torch

        if not torch.cuda.is_available():
            return None, None
        return (torch.cuda.memory_allocated() / 1e6, torch.cuda.memory_reserved() / 1e6)
    except Exception:  # torch absent, or a CUDA context that cannot be queried
        return None, None


def create_app(detector=None, bundle_path: Path | str = DEFAULT_BUNDLE,
               device: str = "cuda", load_on_startup: bool = True, loader=None) -> FastAPI:
    """Build the service.

    ``detector`` given: use it as is (tests, or a caller that already holds one).
    ``detector`` absent: load ``bundle_path`` on ``device`` **in a background thread** started
    at startup, unless ``load_on_startup`` is False. The port opens immediately either way;
    ``/health`` says ``loading`` until the thread finishes, then ``ok`` or ``error`` with the
    reason, and the scoring routes answer 503 in the meantime.

    Why a thread: uvicorn does not accept connections until the lifespan startup returns. A
    synchronous load there — a minute for the 7B model, far longer on a first run that has to
    download 15 GB — left the port closed for exactly the period ``/health`` exists to report on.
    Found at T38 by starting the image and watching ``/health`` time out for 150 seconds.

    ``loader`` is the callable that produces the detector; it defaults to
    ``HallucinationDetector.from_pretrained(bundle_path, device)`` and exists so a test can hand
    in one that blocks on an event.
    """
    state = {"detector": detector, "started": time.time(), "requests": 0, "error": None,
             "loading": False}

    def default_loader():
        from vihallulens.pipeline import HallucinationDetector

        return HallucinationDetector.from_pretrained(bundle_path, device)

    def load_in_background():
        state["loading"] = True
        try:
            state["detector"] = (loader or default_loader)()
        except Exception as error:  # keep serving /health so the failure is visible
            state["error"] = f"{type(error).__name__}: {error}"
        finally:
            state["loading"] = False

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if state["detector"] is None and load_on_startup:
            threading.Thread(target=load_in_background, name="nap-mo-hinh", daemon=True).start()
        yield

    app = FastAPI(
        title="vihallulens",
        version=__version__,
        description="Phát hiện ảo giác cho RAG tiếng Việt bằng tín hiệu chú ý nội tại.",
        lifespan=lifespan,
    )

    def current():
        det = state["detector"]
        if det is None:
            detail = "mô hình đang nạp" if state["loading"] else "mô hình chưa nạp"
            if state["error"]:
                detail += f" — {state['error']}"
            raise HTTPException(status_code=503, detail=detail)
        return det

    def check_strategy(det, wanted: str | None) -> None:
        have = getattr(det.chunking, "strategy", None)
        if wanted is not None and have is not None and wanted != have:
            raise HTTPException(
                status_code=400,
                detail=f"bộ phát hiện được khớp với cách chia đoạn '{have}', không chấm được "
                       f"với '{wanted}' — năm đặc trưng hình dạng mô tả phân bố trên đúng các "
                       f"đoạn ấy. Để trống chunk_strategy hoặc gửi '{have}'.",
            )

    def score_one(det, item: ScoreRequest) -> ScoreResponse:
        result = det.score(item.context, item.question, item.response)
        state["requests"] += 1
        return ScoreResponse(**result.to_dict())

    @app.post("/score", response_model=ScoreResponse)
    def score(item: ScoreRequest) -> ScoreResponse:
        det = current()
        check_strategy(det, item.chunk_strategy)
        return score_one(det, item)

    @app.post("/score/batch", response_model=BatchResponse)
    def score_batch(batch: BatchRequest) -> BatchResponse:
        det = current()
        for item in batch.items:
            check_strategy(det, item.chunk_strategy)
        started = time.perf_counter()
        results = [score_one(det, item) for item in batch.items]
        return BatchResponse(results=results, elapsed_ms=(time.perf_counter() - started) * 1000)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        det = state["detector"]
        allocated, reserved = vram_mb()
        loaded = det is not None
        bundle = det.bundle if loaded else None
        if loaded:
            status = "ok"
        elif state["error"]:
            status = "error"
        elif state["loading"] or load_on_startup:
            status = "loading"
        else:
            status = "not_loaded"
        return HealthResponse(
            status=status,
            error=state["error"],
            version=__version__,
            model_loaded=loaded,
            bundle=bundle.describe() if bundle else None,
            reading_model=(bundle.config.get("extractor", {}).get("model_name")
                           if bundle else None),
            chunking=(dict(bundle.config.get("chunking", {})) if bundle else None),
            device=getattr(getattr(det, "extractor", None), "device", None) if loaded else None,
            vram_allocated_mb=allocated,
            vram_reserved_mb=reserved,
            requests_served=state["requests"],
            uptime_s=time.time() - state["started"],
        )

    return app
