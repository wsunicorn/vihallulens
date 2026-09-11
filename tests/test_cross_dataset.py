"""Tests for the cross-corpus transfer script (task T34, E16).

The scoring itself is the same code path as ``run_chunk_aware.py`` and is covered there. What
is new here — and what can go wrong silently — is the *pairing* of two configs. Two shards
extracted with different reading models or different chunkers produce feature vectors of the
same length whose columns mean different things, and the classifier runs on them without
complaint. So the guard that refuses such pairs is the thing worth testing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_cross_dataset import assert_compatible, same_corpus_reference  # noqa: E402


class Cfg:
    """Just enough of ExperimentConfig for ``assert_compatible``: a ``to_dict``."""

    def __init__(self, **overrides):
        base = {
            "dataset": {"name": "vihallu", "split_seed": 42},
            "chunking": {"strategy": "sentence", "min_words": 5},
            "extractor": {"model_name": "Qwen/Qwen2.5-7B-Instruct", "exclude_layers": [27],
                          "compute_dtype": "float16"},
            "features": {"groups": ["basic", "chunk_aware", "stability"],
                         "head_aggregation": "all"},
            "detector": {"type": "logistic_regression"},
        }
        for key, value in overrides.items():
            base[key] = {**base[key], **value}
        self._d = base

    def to_dict(self):
        return self._d


def test_accepts_configs_that_differ_only_in_dataset():
    assert_compatible(Cfg(), Cfg(dataset={"name": "isedsc01"}))


def test_refuses_same_dataset():
    """Source equal to target is run_chunk_aware.py, not a transfer experiment."""
    with pytest.raises(SystemExit, match="cùng một bộ"):
        assert_compatible(Cfg(), Cfg())


@pytest.mark.parametrize("key, change", [
    ("extractor", {"model_name": "sail/Sailor2-8B-SFT"}),
    ("extractor", {"exclude_layers": []}),
    ("extractor", {"compute_dtype": "bfloat16"}),
    ("chunking", {"strategy": "token_window"}),
    ("chunking", {"min_words": 8}),
    ("features", {"groups": ["basic"]}),
])
def test_refuses_any_difference_that_changes_column_meaning(key, change):
    """Each of these keeps the vector length and changes what the columns mean.

    A different reading model puts different heads at the same indices (E13, E14). A different
    exclude list shifts every layer index after the gap. A different chunker changes what the
    five shape statistics describe. A different group list changes the column layout outright.
    All of them would run and return a number.
    """
    with pytest.raises(SystemExit, match=key):
        assert_compatible(Cfg(), Cfg(dataset={"name": "isedsc01"}, **{key: change}))


def test_reference_lookup_returns_last_row_for_the_name(tmp_path):
    """Re-scoring an experiment appends; the reproduction check must read the newest row."""
    path = tmp_path / "runs.jsonl"
    rows = [
        {"run_name": "e03_chunk_aware", "metrics": {"macro_f1": 0.70}},
        {"run_name": "e02_lookback_lens", "metrics": {"macro_f1": 0.7451}},
        {"run_name": "e03_chunk_aware", "metrics": {"macro_f1": 0.7567}},
    ]
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    assert same_corpus_reference(path, "e03_chunk_aware") == 0.7567
    assert same_corpus_reference(path, "e02_lookback_lens") == 0.7451


def test_reference_lookup_is_none_when_absent(tmp_path):
    """No record means no check — reported as such, not as a silent pass."""
    path = tmp_path / "runs.jsonl"
    path.write_text(json.dumps({"run_name": "other", "metrics": {"macro_f1": 0.5}}),
                    encoding="utf-8")

    assert same_corpus_reference(path, "e03_chunk_aware") is None
    assert same_corpus_reference(tmp_path / "missing.jsonl", "e03_chunk_aware") is None
