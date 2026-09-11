"""Tests for ``DetectorBundle`` and the serving pipeline (task T36).

The failure these guard against is silent: a bundle that rebuilds its input columns in a
different order or from a different head set than training used would still produce a label
and a probability for every request. So the tests fit a tiny detector on synthetic records,
save it, load it, and check that the loaded bundle produces the *same* vectors and the *same*
predictions as the objects it was built from — and that it refuses records it cannot score.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.config import ChunkingConfig  # noqa: E402
from vihallulens.data.chunking import Chunk  # noqa: E402
from vihallulens.detect.bundle import DetectorBundle  # noqa: E402
from vihallulens.detect.detector import LookbackDetector  # noqa: E402
from vihallulens.features.assemble import MIXED, build_matrix  # noqa: E402
from vihallulens.pipeline import HallucinationDetector, attention_per_chunk  # noqa: E402

LAYERS = [0, 1, 3]   # a gap, like the real grid after dropping layer 27
HEADS = 4
GRID = len(LAYERS) * HEADS
LABELS = ["no", "intrinsic", "extrinsic"]


def record(rng, label, layers=LAYERS):
    """A shard row with every block the three groups read."""
    shift = {"no": 0.0, "intrinsic": 0.3, "extrinsic": -0.3}[label]
    grid = len(layers) * HEADS
    row = {"sample_id": f"s{rng.integers(1e9)}", "label": label, "n_chunks": 5,
           "layer_indices": list(layers)}
    for name in ("lookback_total", "lookback_context", "chunk_entropy", "chunk_max_share",
                 "chunk_gini", "top1_top2_gap", "chunk_drift"):
        row[name] = (rng.random(grid) * 0.5 + 0.25 + shift * rng.random()).round(6).tolist()
    return row


@pytest.fixture
def fitted(tmp_path):
    rng = np.random.default_rng(42)
    records = [record(rng, LABELS[i % 3]) for i in range(90)]
    labels = np.array([r["label"] for r in records])
    groups = ["basic", "chunk_aware", "stability"]
    keep = [5, 0, 11, 7]
    matrix = build_matrix(records, groups, len(LAYERS), HEADS, "topk_heads", np.asarray(keep))
    detector = LookbackDetector(seed=42).fit(matrix, labels)
    bundle = DetectorBundle(detector=detector, groups=groups, mode="topk_heads", keep=keep,
                            layer_indices=LAYERS, n_heads=HEADS, run_name="test",
                            config={"chunking": {"strategy": "sentence", "min_words": 5}})
    return bundle, records, matrix, tmp_path


def test_vector_rebuilds_the_training_matrix_row_by_row(fitted):
    bundle, records, matrix, _ = fitted
    for i, rec in enumerate(records[:10]):
        np.testing.assert_allclose(bundle.vector(rec)[0], matrix[i])


def test_roundtrip_preserves_predictions_and_recipe(fitted):
    bundle, records, _, tmp_path = fitted
    path = bundle.save(tmp_path / "b.pkl")
    loaded = DetectorBundle.load(path)

    assert loaded.groups == bundle.groups
    assert loaded.mode == bundle.mode and loaded.keep == bundle.keep
    assert loaded.layer_indices == LAYERS and loaded.n_heads == HEADS
    assert loaded.feature_names == bundle.feature_names
    for rec in records[:20]:
        assert loaded.predict_record(rec) == bundle.predict_record(rec)
    assert (tmp_path / "b.json").is_file()   # the sidecar for humans


def test_feature_count_matches_recipe(fitted):
    bundle, *_ = fitted
    # basic keeps 4 heads, chunk_aware has 4 blocks × 4 heads, stability 1 block × 4 heads
    assert bundle.n_features == 4 + 16 + 4
    assert bundle.vector(record(np.random.default_rng(1), "no")).shape == (1, 24)


def test_probabilities_come_back_in_reporting_order_and_sum_to_one(fitted):
    bundle, records, _, _ = fitted
    label, proba = bundle.predict_record(records[0])
    assert list(proba) == LABELS
    assert abs(sum(proba.values()) - 1.0) < 1e-9
    assert label in LABELS


def test_refuses_record_from_a_different_layer_grid(fitted):
    """Same vector length, different layers: E13/E14 showed the columns mean different things."""
    bundle, *_ = fitted
    other = record(np.random.default_rng(2), "no", layers=[0, 1, 2])
    with pytest.raises(ValueError, match="lưới lớp"):
        bundle.vector(other)


def test_refuses_record_with_wrong_head_count(fitted):
    bundle, records, _, _ = fitted
    rec = dict(records[0])
    rec["lookback_total"] = rec["lookback_total"][:-1]
    with pytest.raises(ValueError, match="đầu"):
        bundle.vector(rec)


def test_mixed_mode_bundle_rebuilds_mixed_matrix():
    """E15 chose the mixed aggregation; a bundle must be able to serve it."""
    rng = np.random.default_rng(7)
    records = [record(rng, LABELS[i % 3]) for i in range(60)]
    labels = np.array([r["label"] for r in records])
    groups = ["basic", "chunk_aware"]
    keep = [1, 9]
    matrix = build_matrix(records, groups, len(LAYERS), HEADS, MIXED, np.asarray(keep))
    detector = LookbackDetector(seed=42).fit(matrix, labels)
    bundle = DetectorBundle(detector, groups, MIXED, keep, LAYERS, HEADS, "mixed")
    assert bundle.n_features == GRID + 4 * len(keep)   # basic whole, wide blocks thinned
    np.testing.assert_allclose(bundle.vector(records[3])[0], matrix[3])


def test_load_rejects_foreign_pickle(tmp_path):
    import pickle

    path = tmp_path / "x.pkl"
    path.write_bytes(pickle.dumps({"not": "a bundle"}))
    with pytest.raises(TypeError):
        DetectorBundle.load(path)


# ---------------------------------------------------------------- the pipeline, without a GPU

class FakeFeatures:
    """Just enough of ``AttentionFeatures`` for ``to_record`` and ``attention_per_chunk``."""

    def __init__(self, rng, chunks, n_tokens=6):
        n = len(chunks)
        self.chunks = chunks
        self.n_chunks = n
        self.truncated = False
        self.layer_indices = list(LAYERS)
        self.nonfinite_layers = []
        self.row_sum_mean = 1.0
        self.peak_vram_mb = 0.0
        self.elapsed_ms = 1.0
        shape = (len(LAYERS), HEADS, n_tokens)
        self.lookback_total = rng.random(shape).astype(np.float32)
        self.lookback_context = rng.random(shape).astype(np.float32)
        self.self_attention = rng.random(shape).astype(np.float32)
        per_chunk = rng.random(shape + (n,)).astype(np.float32)
        per_chunk[..., 0] *= 3   # chunk 0 gets the most attention, by construction
        self.lookback_per_chunk = per_chunk


class FakeExtractor:
    tokenizer = None
    layer_indices = list(LAYERS)

    def __init__(self):
        self.rng = np.random.default_rng(0)
        self.calls = []

    def extract(self, context, question, response, chunks):
        self.calls.append((context, question, response, len(chunks)))
        return FakeFeatures(self.rng, chunks)


def test_pipeline_output_matches_the_spec_schema(fitted):
    bundle, *_ = fitted
    detector = HallucinationDetector(bundle, FakeExtractor(),
                                     ChunkingConfig(strategy="sentence", min_words=5))
    context = ("Hà Nội là thủ đô của Việt Nam. Thành phố nằm bên sông Hồng. "
               "Dân số khoảng tám triệu người. Khí hậu có bốn mùa rõ rệt.")
    result = detector.score(context, "Hà Nội ở đâu?", "Hà Nội nằm bên sông Hồng.")
    out = result.to_dict()

    assert set(out) >= {"label", "proba", "chunk_attention", "risk_score", "elapsed_ms"}
    assert out["label"] in LABELS
    assert abs(out["risk_score"] - (1 - out["proba"]["no"])) < 1e-9
    assert len(out["chunk_attention"]) == out["n_chunks"] == len(result.chunk_attention)
    assert abs(sum(c["share"] for c in out["chunk_attention"]) - 1.0) < 1e-6
    assert out["chunk_attention"][0]["share"] == max(c["share"] for c in out["chunk_attention"])
    assert all(context[c["char_start"]:c["char_end"]].strip() in context
               for c in out["chunk_attention"])
    assert out["elapsed_ms"] >= 0


def test_pipeline_passes_empty_question_through(fitted):
    """Fact-checking corpora have no question; the prompt template drops the block entirely."""
    bundle, *_ = fitted
    extractor = FakeExtractor()
    HallucinationDetector(bundle, extractor).score("Một câu ngữ cảnh đủ dài để chia.", "", "Đáp.")
    assert extractor.calls[0][1] == ""


def test_attention_per_chunk_sums_to_one():
    rng = np.random.default_rng(3)
    chunks = [Chunk(text=f"c{i}", char_start=i, char_end=i + 1, index=i) for i in range(4)]
    shares = attention_per_chunk(FakeFeatures(rng, chunks))
    assert shares.shape == (4,)
    assert abs(shares.sum() - 1.0) < 1e-6


def test_from_pretrained_fails_fast_without_cuda(monkeypatch, tmp_path, fitted):
    """Asked for CUDA on a CPU host, refuse before touching the network or the 15 GB weights."""
    import torch

    bundle, *_ = fitted
    path = bundle.save(tmp_path / "b.pkl")
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(RuntimeError, match="không có CUDA"):
        HallucinationDetector.from_pretrained(path, device="cuda")
