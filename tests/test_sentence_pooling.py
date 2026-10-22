"""E18: per-sentence pooling of the response, on CPU and without a model."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from run_sentence_pooling import (  # noqa: E402
    EXPECTED,
    check_prediction,
    hallucinated_as_no,
    load_compact,
    macro_f1,
    paired_bootstrap,
)
from vihallulens.config import extraction_hash, load_config  # noqa: E402
from vihallulens.data.chunking import Chunk, chunk_context  # noqa: E402
from vihallulens.extract.attention import AttentionFeatures, sentence_token_groups  # noqa: E402
from vihallulens.features.chunk_aware import chunk_features  # noqa: E402
from vihallulens.features.lookback import pool_over_tokens  # noqa: E402
from vihallulens.features.records import to_record  # noqa: E402
from vihallulens.features.sentence import (  # noqa: E402
    SENTENCE_BLOCKS,
    pool_sentences,
    pooled_view,
    sentence_record_fields,
)

E03 = "configs/e03_chunk_sentence_vihallu.yaml"
E18 = "configs/e18_sentence_pooling_vihallu.yaml"


def test_prediction_is_locked():
    # Changing these after the run would turn a failed prediction into a "confirmation".
    assert EXPECTED == {"max_raises_extrinsic_f1": True, "max_reduces_hallucinated_as_no": True}


def test_the_new_flag_leaves_every_existing_hash_alone():
    # 8c49fc0417f1 names the E02/E03 shards on disk; a new key with its default value in the
    # hashed payload would make every one of them unreachable.
    e03 = load_config(E03)
    assert "response_sentences" not in e03.to_dict()["extractor"]
    assert extraction_hash(e03) == "8c49fc0417f1"


def test_e18_writes_its_own_shard_and_differs_from_e03_in_one_key_only():
    e03, e18 = load_config(E03).to_dict(), load_config(E18).to_dict()
    assert extraction_hash(load_config(E18)) != extraction_hash(load_config(E03))
    assert e18["extractor"].pop("response_sentences") is True
    for section in ("dataset", "chunking", "extractor", "features", "detector"):
        assert e18[section] == e03[section]


def char_offsets(text: str):
    return [(i, i + 1) for i in range(len(text))]


def test_sentence_groups_partition_the_scored_axis():
    prompt = "<u>ngữ cảnh</u><a>Câu một đây. Câu hai nữa.</a>"
    start = prompt.index("Câu")
    response = prompt[start: prompt.index("</a>")]
    sentences = chunk_context(response, strategy="sentence", min_words=2)
    assert len(sentences) == 2
    queries = list(range(start + 1, start + len(response)))  # the first token is never scored
    groups = sentence_token_groups(char_offsets(prompt), queries, start, sentences)
    flat = [index for group in groups for index in group]
    assert len(flat) == len(set(flat))  # no token pooled twice
    assert groups[0][0] == 0  # scored index 0 is the second response token
    second = response.index("Câu hai")
    assert groups[1][0] == second - 1


def test_a_sentence_with_nothing_scored_is_dropped():
    response = "A. Câu thứ hai dài hơn."
    sentences = [Chunk(text="A.", char_start=0, char_end=1, index=0),
                 Chunk(text="Câu thứ hai dài hơn.", char_start=3, char_end=len(response), index=1)]
    # Only the first response token is in sentence one, and it is never scored.
    groups = sentence_token_groups(char_offsets(response), list(range(1, len(response))), 0,
                                   sentences)
    assert len(groups) == 1


def fake_features(n_tokens=9, n_chunks=4, sentence_tokens=None, seed=0):
    rng = np.random.default_rng(seed)
    shape = (2, 3, n_tokens)
    return AttentionFeatures(
        lookback_per_chunk=rng.random((*shape, n_chunks)).astype(np.float16),
        lookback_total=rng.random(shape).astype(np.float16),
        lookback_context=rng.random(shape).astype(np.float16),
        self_attention=rng.random(shape).astype(np.float16),
        n_chunks=n_chunks, truncated=False, peak_vram_mb=0.0, elapsed_ms=1.0,
        layer_indices=[0, 1], sentence_tokens=sentence_tokens or [],
    )


def test_one_sentence_gives_back_the_whole_response_vector():
    features = fake_features(sentence_tokens=[list(range(9))])
    fields = sentence_record_fields(features)
    whole = pool_over_tokens(features.lookback_total).reshape(-1)
    assert np.allclose(fields["sentence_lookback_total"][0], whole, atol=1e-6)
    for name, value in chunk_features(features.lookback_per_chunk).items():
        assert np.allclose(fields[f"sentence_{name}"][0], value.reshape(-1), atol=1e-6)


def test_records_without_sentences_are_unchanged():
    features = fake_features()
    assert sentence_record_fields(features) == {}
    assert not any(key.startswith("sentence_") for key in to_record("s", "no", features, 1.0))


def test_records_with_sentences_only_add_fields():
    plain = to_record("s", "no", fake_features(), 1.0)
    split = to_record("s", "no", fake_features(sentence_tokens=[[0, 1, 2], [3, 4, 5, 6, 7, 8]]),
                      1.0)
    assert {key: split[key] for key in plain} == plain
    assert split["sentence_n_tokens"] == [3, 6]
    assert all(len(split[f"sentence_{block}"]) == 2 for block in SENTENCE_BLOCKS)


def test_pool_sentences_and_the_view_keep_block_names():
    per_sentence = np.array([[0.1, 0.9], [0.5, 0.3]])
    assert np.allclose(pool_sentences(per_sentence, "max"), [0.5, 0.9])
    assert np.allclose(pool_sentences(per_sentence, "min"), [0.1, 0.3])
    assert np.allclose(pool_sentences(per_sentence, "mean"), [0.3, 0.6])
    with pytest.raises(ValueError):
        pool_sentences(per_sentence, "median")
    record = {"lookback_total": np.zeros(2), "sentence_lookback_total": per_sentence}
    view = pooled_view(record, "max", blocks=("lookback_total",))
    assert np.allclose(view["lookback_total"], [0.5, 0.9])
    assert np.allclose(record["lookback_total"], 0.0)  # the original is not touched


def test_hallucinated_as_no_counts_only_missed_hallucinations():
    y_true = ["no", "intrinsic", "extrinsic", "extrinsic", "no"]
    y_pred = ["no", "no", "no", "intrinsic", "extrinsic"]
    assert hallucinated_as_no(y_true, y_pred) == 2


def test_paired_bootstrap_of_identical_predictions_is_zero():
    y = np.array(["no", "intrinsic", "extrinsic"] * 20)
    out = paired_bootstrap(y, y, y, macro_f1, rounds=50)
    assert out == {"delta": 0.0, "lo": 0.0, "hi": 0.0}


def test_check_prediction_reads_both_directions():
    y = np.array(["extrinsic", "extrinsic", "no", "intrinsic"])
    worse = np.array(["no", "no", "no", "intrinsic"])
    better = np.array(["extrinsic", "extrinsic", "no", "intrinsic"])
    assert check_prediction(y, worse, better) == {"max_raises_extrinsic_f1": True,
                                                  "max_reduces_hallucinated_as_no": True}
    assert check_prediction(y, better, worse) == {"max_raises_extrinsic_f1": False,
                                                  "max_reduces_hallucinated_as_no": False}


def test_load_compact_drops_nan_rows_and_a_truncated_line(tmp_path):
    path = tmp_path / "shard.jsonl"
    good = {"sample_id": "b", "label": "no", "lookback_total": [0.1, 0.2],
            "sentence_lookback_total": [[0.1, 0.2]], "sentence_n_tokens": [3]}
    bad = {**good, "sample_id": "a", "lookback_total": [float("nan"), 0.2]}
    path.write_text(json.dumps(good) + "\n" + json.dumps(bad) + "\n" + '{"sample_id": "c', "utf-8")
    rows, dropped = load_compact(path, ["lookback_total"])
    assert [row["sample_id"] for row in rows] == ["b"] and dropped == ["a"]
    assert rows[0]["sentence_lookback_total"].shape == (1, 2)
