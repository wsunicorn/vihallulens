"""The feature vector of experiment E02, and the shard format it is stored in.

Task T20 asks for a faithful reproduction rather than something close, and section 1 of
docs/REFERENCES.md lists the four ways a reproduction goes subtly wrong. Each of those is a test
here, because every one of them produces a full matrix of plausible-looking numbers.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from vihallulens.features.lookback import (
    DENOMINATORS,
    E02_DENOMINATOR,
    feature_names,
    flatten_heads,
    pool_over_tokens,
    sample_vector,
)


class Features:
    """The parts of an AttentionFeatures that this module touches."""

    def __init__(self, total, context=None):
        self.lookback_total = np.asarray(total, dtype=np.float32)
        self.lookback_context = np.asarray(
            total if context is None else context, dtype=np.float32
        )


# -- pooling over the span -----------------------------------------------------------------


def test_the_span_is_averaged_not_summed():
    """Point 2 of section 1 of docs/REFERENCES.md: average the per-step vectors over the span.

    Summing would make the feature a proxy for response length, and the classifier would learn
    that instead of anything about attention."""
    lookback = np.full((2, 3, 10), 0.4, dtype=np.float32)
    assert pool_over_tokens(lookback) == pytest.approx(0.4)


def test_pooling_keeps_the_layer_and_head_axes():
    pooled = pool_over_tokens(np.zeros((27, 28, 15), dtype=np.float32))
    assert pooled.shape == (27, 28)


def test_each_head_is_averaged_on_its_own():
    lookback = np.zeros((1, 2, 4), dtype=np.float32)
    lookback[0, 0] = [0.1, 0.2, 0.3, 0.4]
    lookback[0, 1] = [0.9, 0.9, 0.9, 0.9]
    pooled = pool_over_tokens(lookback)
    assert pooled[0, 0] == pytest.approx(0.25)
    assert pooled[0, 1] == pytest.approx(0.9)


def test_a_layer_that_overflowed_does_not_poison_the_others():
    """A layer that went non-finite in float16 fills its slice with nan. A plain mean would
    spread that through standardisation into every other feature; the excluded layers are
    configured, so a nan here is a surprise the surviving layers should survive."""
    lookback = np.full((2, 1, 4), 0.5, dtype=np.float32)
    lookback[1, 0, 2] = np.nan
    pooled = pool_over_tokens(lookback)
    assert pooled[0, 0] == pytest.approx(0.5)
    assert pooled[1, 0] == pytest.approx(0.5)


def test_a_wrong_shape_is_rejected():
    with pytest.raises(ValueError, match="lớp, đầu, token"):
        pool_over_tokens(np.zeros((27, 28)))


def test_a_sample_with_nothing_scored_is_rejected():
    """A one-token response has no scored token: the first is always dropped."""
    with pytest.raises(ValueError, match="không có token"):
        pool_over_tokens(np.zeros((2, 2, 0)))


# -- flattening ----------------------------------------------------------------------------


def test_every_layer_head_pair_survives_into_the_vector():
    """Point 2 again, from the other side: concatenate all L × H, do not average over heads.

    The paper's own finding is that a few specific heads carry most of the signal, so averaging
    the heads together destroys exactly what makes the method work."""
    assert flatten_heads(np.zeros((27, 28))).shape == (756,)


def test_the_vector_is_laid_out_layer_by_layer():
    pooled = np.arange(6, dtype=np.float32).reshape(2, 3)
    assert list(flatten_heads(pooled)) == [0, 1, 2, 3, 4, 5]


def test_names_line_up_with_the_values():
    pooled = np.arange(6, dtype=np.float32).reshape(2, 3)
    names = feature_names([0, 1], 3)
    assert len(names) == flatten_heads(pooled).size
    assert names[0] == "lookback_total_l0_h0"
    assert names[5] == "lookback_total_l1_h2"


def test_names_use_the_model_s_own_layer_numbers():
    """With layer 27 excluded the array has 27 slices but they are layers 0 to 26. A name that
    said l26 for a slice holding layer 24 would make every head-location claim wrong."""
    names = feature_names([0, 5, 26], 2)
    assert names[-1] == "lookback_total_l26_h1"


# -- which denominator ---------------------------------------------------------------------


def test_e02_uses_the_whole_prompt_as_the_denominator():
    """Section 3 of CLAUDE.md keeps both, and the paper's X is the whole input sequence, so the
    faithful reproduction is the total one. The context-only variant is the chunk-aware basis."""
    assert E02_DENOMINATOR == "total"
    assert set(DENOMINATORS) == {"total", "context"}


def test_the_vector_comes_from_the_denominator_asked_for():
    features = Features(
        total=np.full((1, 2, 3), 0.8, dtype=np.float32),
        context=np.full((1, 2, 3), 0.2, dtype=np.float32),
    )
    assert sample_vector(features, "total") == pytest.approx(0.8)
    assert sample_vector(features, "context") == pytest.approx(0.2)


def test_an_unknown_denominator_is_rejected():
    with pytest.raises(ValueError, match="mẫu số lạ"):
        sample_vector(Features(np.zeros((1, 1, 2))), "prompt")


# -- the shard the extraction writes -------------------------------------------------------


def shard(tmp_path, rows):
    path = tmp_path / "vihallu_test_abc.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    return path


def row(sample_id, label="no", values=(0.1, 0.2)):
    return {
        "sample_id": sample_id, "label": label,
        "lookback_total": list(values), "lookback_context": list(values),
        "layer_indices": [0], "truncated": False, "nonfinite_layers": [],
    }


def test_a_shard_reads_back_as_a_matrix(tmp_path):
    from extract_features import load_matrix

    path = shard(tmp_path, [row("s1", "no"), row("s2", "intrinsic")])
    matrix, labels, ids, _ = load_matrix(path)
    assert matrix.shape == (2, 2)
    assert list(labels) == ["no", "intrinsic"]
    assert ids == ["s1", "s2"]


def test_the_matrix_does_not_depend_on_the_order_rows_were_written(tmp_path):
    """A run interrupted and resumed writes its rows in a different order from one that ran
    straight through. The matrix has to be the same either way, or resuming would quietly
    change the result."""
    from extract_features import load_matrix

    def ids_from(folder, rows):
        folder.mkdir()
        return load_matrix(shard(folder, rows))[2]

    forward = ids_from(tmp_path / "a", [row("s1"), row("s2"), row("s3")])
    backward = ids_from(tmp_path / "b", [row("s3"), row("s1"), row("s2")])
    assert forward == backward == ["s1", "s2", "s3"]


def test_a_truncated_last_line_costs_one_sample_not_the_shard(tmp_path):
    """Fifty minutes of GPU killed mid-write leaves half a line. Refusing to read the file
    would throw away every sample already paid for."""
    from extract_features import load_matrix

    path = shard(tmp_path, [row("s1"), row("s2")])
    with path.open("a", encoding="utf-8") as handle:
        handle.write('{"sample_id": "s3", "lookb')
    matrix, _, ids, _ = load_matrix(path)
    assert ids == ["s1", "s2"] and matrix.shape == (2, 2)


def test_a_shard_written_twice_for_one_sample_keeps_the_later_row(tmp_path):
    """Re-running skips finished samples, but a retry after a crash can still append a second
    row for one that was half written."""
    from extract_features import load_matrix

    path = shard(tmp_path, [row("s1", values=(0.1, 0.1)), row("s1", values=(0.9, 0.9))])
    matrix, _, ids, _ = load_matrix(path)
    assert ids == ["s1"] and matrix[0] == pytest.approx(0.9)


def test_features_of_different_widths_are_refused(tmp_path):
    """Two shards concatenated by hand, or a config changed mid-run, would otherwise produce a
    ragged matrix and a confusing numpy error much later."""
    from extract_features import load_matrix

    path = shard(tmp_path, [row("s1", values=(0.1, 0.2)), row("s2", values=(0.1, 0.2, 0.3))])
    with pytest.raises(ValueError, match="không đồng nhất"):
        load_matrix(path)


def test_an_empty_shard_is_refused(tmp_path):
    from extract_features import load_matrix

    with pytest.raises(ValueError, match="không có mẫu nào"):
        load_matrix(shard(tmp_path, []))


# -- the shard name carries the config -----------------------------------------------------


def test_two_configs_do_not_share_a_shard(tmp_path):
    """Features from a different reading model or token budget are different features. Sharing
    a filename would let a re-run with new settings silently reuse the old numbers."""
    from extract_features import shard_path

    a = shard_path(tmp_path, "aaaa", "vihallu", "test")
    b = shard_path(tmp_path, "bbbb", "vihallu", "test")
    assert a != b


def test_splits_do_not_share_a_shard(tmp_path):
    from extract_features import shard_path

    assert (shard_path(tmp_path, "a", "vihallu", "train")
            != shard_path(tmp_path, "a", "vihallu", "test"))
