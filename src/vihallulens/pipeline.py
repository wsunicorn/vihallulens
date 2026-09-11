"""The whole method as one call: text in, verdict and per-chunk attention out.

Everything below this module already existed by T35 — the reading model with its forward hooks
(``extract``), the pooled features (``features``), the fitted classifier (``detect``) — but only
the experiment scripts knew how to chain them, and each of them did it slightly differently.
``HallucinationDetector`` is that chain written once, in the order training used, so that a
request is scored the way a training row was scored.

The output follows ``docs/SPEC.md`` §2.6::

    {label, proba, chunk_attention, risk_score, elapsed_ms}

Two of those need a word.

``chunk_attention`` is the share of the response's attention that lands on each context chunk,
averaged over every layer and head the extractor hooked. E06 measured this average against
gold evidence — hit@1 of 87,8 % among 22,6 chunks — so it is the quantity the observation page
(T39) colours the context with. It is *not* what the classifier consumes; the classifier reads
the pooled feature vector, which is a different summary of the same matrices.

``risk_score`` is ``1 - P(no)``: the probability that the response is hallucinated in either
way. Bảng 1 and Bảng 7 both found the detector separates "faithful or not" far better than it
separates the two kinds of unfaithfulness, and E16 found only the binary judgement transfers
across corpora. So the single number a RAG system should act on is the binary one, and the
three-class ``proba`` is there for anyone who wants the finer split with its wider error bars.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from vihallulens.config import ChunkingConfig
from vihallulens.data.chunking import chunk_context, chunking_arguments
from vihallulens.detect.bundle import DetectorBundle
from vihallulens.features.localization import mean_shares
from vihallulens.features.records import to_record

DEFAULT_BUNDLE = Path("models/e03_chunk_aware.pkl")


@dataclass
class ChunkAttention:
    """One context chunk and how much of the response's attention it received."""

    index: int
    text: str
    char_start: int
    char_end: int
    share: float


@dataclass
class ScoreResult:
    """What :meth:`HallucinationDetector.score` returns. ``to_dict`` matches the API schema."""

    label: str
    proba: dict[str, float]
    risk_score: float
    chunk_attention: list[ChunkAttention]
    elapsed_ms: float
    n_chunks: int
    truncated: bool
    nonfinite_layers: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "proba": dict(self.proba),
            "risk_score": self.risk_score,
            "chunk_attention": [
                {"index": c.index, "text": c.text, "char_start": c.char_start,
                 "char_end": c.char_end, "share": c.share}
                for c in self.chunk_attention
            ],
            "elapsed_ms": self.elapsed_ms,
            "n_chunks": self.n_chunks,
            "truncated": self.truncated,
            "nonfinite_layers": list(self.nonfinite_layers),
        }


def attention_per_chunk(features) -> np.ndarray:
    """Share of response attention on each surviving chunk, averaged over layers and heads.

    Sums to one over chunks. Uses the same normalisation as E06's localisation metric, so the
    number the page shows is the number the thesis evaluated.
    """
    shares = mean_shares(features.lookback_per_chunk)  # (layers, heads, chunks)
    return shares.reshape(-1, shares.shape[-1]).mean(axis=0)


class HallucinationDetector:
    """Score a ``(context, question, response)`` triple with a fitted detector.

    Build one with :meth:`from_pretrained` — it loads the bundle, then the reading model the
    bundle was trained with, so the two cannot drift apart. Constructing it directly from a
    bundle and an extractor is for tests and for callers that already hold an extractor.

    Example::

        detector = HallucinationDetector.from_pretrained("models/e03_chunk_aware.pkl")
        result = detector.score(context, question, response)
        result.label          # 'no' | 'intrinsic' | 'extrinsic'
        result.risk_score     # 1 - P(no)
        result.chunk_attention[0].share
    """

    def __init__(self, bundle: DetectorBundle, extractor, chunking: ChunkingConfig | None = None):
        self.bundle = bundle
        self.extractor = extractor
        self.chunking = chunking or ChunkingConfig(**bundle.config.get("chunking", {}))
        tokenizer = getattr(extractor, "tokenizer", None)
        self._chunk_kwargs = chunking_arguments(self.chunking, tokenizer)
        self._requests = 0

    # -- construction ------------------------------------------------------------------------

    @classmethod
    def from_pretrained(cls, bundle_path: Path | str = DEFAULT_BUNDLE, device: str = "cuda",
                        **extractor_overrides) -> HallucinationDetector:
        """Load a bundle and the reading model it was fitted against.

        The extractor is built from the bundle's own ``config["extractor"]`` — model name,
        quantisation, excluded layers, dtype — so a bundle fitted on Qwen2.5-7B with layer 27
        dropped is served on exactly that. Overrides are for ``device`` and the like, not for
        swapping the model: E13 and E14 measured what happens when the model changes.
        """
        # Fail before downloading anything. Asked for CUDA on a host without it, the extractor
        # would first pull the 15 GB of Qwen2.5-7B weights and only then hit the bitsandbytes
        # error — measured at T38 in the Docker image, where /health sat at "loading" through
        # the whole download. NF4 has no CPU path, so there is nothing to fall back to.
        if str(device).startswith("cuda"):
            import torch

            if not torch.cuda.is_available():
                raise RuntimeError(
                    "yêu cầu device='cuda' nhưng máy này không có CUDA. Mô hình đọc lượng tử "
                    "hóa NF4 qua bitsandbytes không chạy được trên CPU — cần GPU, hoặc chạy "
                    "trên Kaggle/Colab."
                )

        from vihallulens.extract.attention import AttentionExtractor

        bundle = DetectorBundle.load(bundle_path)
        spec = dict(bundle.config.get("extractor", {}))
        spec.update(extractor_overrides)
        spec["device"] = device
        extractor = AttentionExtractor(**spec)
        got = list(extractor.layer_indices)
        if got != list(bundle.layer_indices):
            raise ValueError(
                f"mô hình đọc nạp lên cho lưới lớp {got}, bộ phát hiện khớp trên "
                f"{bundle.layer_indices} — cấu hình extractor trong bundle không khớp mô hình"
            )
        return cls(bundle, extractor)

    # -- scoring -----------------------------------------------------------------------------

    def score(self, context: str, question: str, response: str) -> ScoreResult:
        """One request, end to end. The response's first token is not scored (CLAUDE.md §8.5)."""
        started = time.perf_counter()
        chunks = chunk_context(context, **self._chunk_kwargs)
        features = self.extractor.extract(context, question or "", response, chunks)
        self._requests += 1
        record = to_record(f"request_{self._requests}", None, features, features.elapsed_ms)
        label, proba = self.bundle.predict_record(record)
        shares = attention_per_chunk(features)
        attention = [
            ChunkAttention(index=chunk.index, text=chunk.text, char_start=chunk.char_start,
                           char_end=chunk.char_end, share=float(share))
            for chunk, share in zip(features.chunks, shares, strict=True)
        ]
        return ScoreResult(
            label=label,
            proba=proba,
            risk_score=float(1.0 - proba.get("no", 0.0)),
            chunk_attention=attention,
            elapsed_ms=(time.perf_counter() - started) * 1000,
            n_chunks=int(features.n_chunks),
            truncated=bool(features.truncated),
            nonfinite_layers=list(features.nonfinite_layers),
        )

    def score_batch(self, items) -> list[ScoreResult]:
        """Sequential; the reading model processes one prompt at a time on a 16 GB card."""
        return [self.score(item["context"], item.get("question", ""), item["response"])
                for item in items]

    def describe(self) -> str:
        model = self.bundle.config.get("extractor", {}).get("model_name", "?")
        return f"{self.bundle.describe()} · mô hình đọc {model}"
