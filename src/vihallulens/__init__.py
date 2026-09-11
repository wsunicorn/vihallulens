"""Hallucination detection for Vietnamese RAG systems using internal attention signals.

The one-call entry point::

    from vihallulens import HallucinationDetector

    detector = HallucinationDetector.from_pretrained("models/e03_chunk_aware.pkl")
    result = detector.score(context, question, response)
    result.label, result.risk_score, result.chunk_attention

Below that, the four layers of ``docs/SPEC.md`` are importable on their own:

* ``vihallulens.extract`` — the reading model and its forward hooks (needs a GPU)
* ``vihallulens.features`` — lookback ratios, chunk-shape statistics, shard records
* ``vihallulens.detect`` — the classifier and the bundle that makes it deployable
* ``vihallulens.evaluation`` — metrics, confidence intervals, the results ledger
"""

from vihallulens.detect.bundle import DetectorBundle
from vihallulens.detect.detector import LookbackDetector
from vihallulens.pipeline import ChunkAttention, HallucinationDetector, ScoreResult

__version__ = "0.1.0"

__all__ = [
    "ChunkAttention",
    "DetectorBundle",
    "HallucinationDetector",
    "LookbackDetector",
    "ScoreResult",
    "__version__",
]
