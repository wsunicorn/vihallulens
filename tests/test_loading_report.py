"""Reading a transformers load report.

The report is the only warning that a checkpoint arrived half-loaded, and T18 suppresses the
library's own log line to keep the tokenizer from burying it. So the reading of it belongs here,
where it is checked rather than trusted.
"""

import pytest

from vihallulens.detect.loading_report import body_gaps, describe


def report(**kwargs):
    base = {"missing_keys": [], "unexpected_keys": [], "mismatched_keys": [], "error_msgs": []}
    return {**base, **kwargs}


# -- the distinction the whole module exists for ------------------------------------------


def test_a_missing_classifier_is_normal():
    """Fine-tuning exists to create these. A checkpoint that already had them would be a
    checkpoint for some other task."""
    ok, message = describe(report(missing_keys=[
        "classifier.dense.weight", "classifier.out_proj.bias"]))
    assert ok
    assert "2" in message


def test_a_missing_body_weight_stops_the_run():
    """The failure this module was written for: a body weight absent from the checkpoint is
    replaced by a random draw, and the model then trains like a randomly initialised network
    while still answering to a famous name."""
    ok, message = describe(report(missing_keys=["encoder.layer.0.attention.self.query.weight"]))
    assert not ok
    assert "THÂN" in message


def test_the_message_names_the_weights_that_went_missing():
    _, message = describe(report(missing_keys=["embeddings.word_embeddings.weight"]))
    assert "embeddings.word_embeddings.weight" in message


# -- the other two ways a load goes wrong --------------------------------------------------


def test_a_size_mismatch_stops_the_run():
    ok, message = describe(report(mismatched_keys=[("embeddings.weight", (250002,), (32000,))]))
    assert not ok
    assert "lệch kích thước" in message


def test_a_reported_error_stops_the_run():
    ok, message = describe(report(error_msgs=["size mismatch for encoder"]))
    assert not ok
    assert "lỗi khi nạp" in message


def test_unexpected_weights_alone_are_fine():
    """Loading a masked-language checkpoint into a classifier always leaves the language head
    and the pooler behind. That is the normal case, not a warning."""
    ok, _ = describe(report(
        unexpected_keys=["lm_head.bias", "roberta.pooler.dense.weight"],
        missing_keys=["classifier.dense.weight"],
    ))
    assert ok


# -- shapes the library actually returns ---------------------------------------------------


def test_a_report_using_sets_is_read_the_same_as_one_using_lists():
    """transformers returns sets on some versions and lists on others; measured at T18 on
    5.15, which returns sets."""
    as_set = describe(report(missing_keys={"classifier.dense.weight"}))
    as_list = describe(report(missing_keys=["classifier.dense.weight"]))
    assert as_set == as_list


def test_a_report_missing_a_field_entirely_is_read_as_empty():
    ok, _ = describe({"missing_keys": ["classifier.dense.weight"]})
    assert ok


def test_a_clean_load_reports_clean():
    ok, message = describe(report())
    assert ok and "thân nạp đủ" in message


# -- the split itself ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "key", ["classifier.dense.weight", "score.weight", "lm_head.bias", "pooler.dense.weight"])
def test_head_weights_are_recognised_by_prefix(key):
    assert body_gaps(report(missing_keys=[key]))["body_missing"] == []


def test_the_two_groups_together_account_for_every_missing_key():
    keys = ["classifier.dense.weight", "encoder.layer.3.output.dense.bias", "pooler.dense.bias"]
    gaps = body_gaps(report(missing_keys=keys))
    assert sorted(gaps["body_missing"] + gaps["head_missing"]) == sorted(keys)
