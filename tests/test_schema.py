"""Invariants of the common schema.

These run on tiny hand-built frames, not on the real corpora, so they say what the schema
promises rather than what one download happens to contain.
"""

import json
import unicodedata

import pandas as pd
import pytest

from vihallulens.data import schema


def row(**overrides):
    base = {
        "sample_id": "vihallu_train_0",
        "dataset": "vihallu",
        "split": "train",
        "context": "Hà Nội là thủ đô của Việt Nam.",
        "context_id": schema.context_id("Hà Nội là thủ đô của Việt Nam."),
        "question": "Thủ đô ở đâu?",
        "response": "Hà Nội.",
        "label": "no",
        "label_original": "no",
        "evidence": "",
        "evidence_start": schema.NO_OFFSET,
        "evidence_end": schema.NO_OFFSET,
        "response_is_generated": True,
        "meta": "{}",
    }
    return {**base, **overrides}


def frame(*rows):
    return pd.DataFrame.from_records(list(rows) or [row()])


# -- context_id --------------------------------------------------------------------------


def test_the_same_text_always_gives_the_same_id():
    assert schema.context_id("Xin chào") == schema.context_id("Xin chào")


def test_different_texts_give_different_ids():
    assert schema.context_id("Hà Nội") != schema.context_id("Huế")


def test_composed_and_decomposed_vietnamese_share_one_id():
    """``ế`` can be stored as one code point or as ``e`` plus two combining marks, and the two
    look identical. If they hashed apart, the same context would land in two different splits
    and leak from train to test — the exact failure grouping exists to prevent."""
    composed = unicodedata.normalize("NFC", "Thế giới")
    decomposed = unicodedata.normalize("NFD", "Thế giới")
    assert composed != decomposed
    assert schema.context_id(composed) == schema.context_id(decomposed)


def test_surrounding_whitespace_does_not_change_the_id():
    assert schema.context_id("  Hà Nội  ") == schema.context_id("Hà Nội")


# -- evidence offsets --------------------------------------------------------------------


def test_evidence_span_points_at_the_evidence():
    context = "Câu một. Câu hai. Câu ba."
    start, end = schema.find_evidence(context, "Câu hai.")
    assert context[start:end] == "Câu hai."


def test_evidence_that_is_not_present_verbatim_is_a_miss():
    """No fuzzy matching: a plausible-looking number in a column later treated as ground
    truth is worse than admitting the evidence was not found."""
    assert schema.find_evidence("Câu một.", "Cau mot.") == (schema.NO_OFFSET, schema.NO_OFFSET)


def test_empty_evidence_is_a_miss_rather_than_a_match_at_zero():
    assert schema.find_evidence("Câu một.", "") == (schema.NO_OFFSET, schema.NO_OFFSET)


# -- meta --------------------------------------------------------------------------------


def test_meta_round_trips_through_json():
    payload = {"prompt_type": "noisy", "domain": "Pháp luật"}
    assert json.loads(schema.encode_meta(payload)) == payload


def test_meta_keeps_vietnamese_readable():
    assert "Pháp luật" in schema.encode_meta({"domain": "Pháp luật"})


def test_meta_is_byte_identical_for_the_same_content():
    assert schema.encode_meta({"b": 1, "a": 2}) == schema.encode_meta({"a": 2, "b": 1})


# -- validation --------------------------------------------------------------------------


def test_a_correct_frame_passes():
    schema.validate(schema.finalise(frame()))


def test_finalise_puts_the_columns_in_the_documented_order():
    shuffled = frame()[list(reversed(schema.COLUMNS))]
    assert tuple(schema.finalise(shuffled).columns) == schema.COLUMNS


@pytest.mark.parametrize("column", ["label", "dataset", "split"])
def test_an_unknown_categorical_value_is_rejected(column):
    with pytest.raises(ValueError, match="giá trị lạ"):
        schema.finalise(frame(row(**{column: "khong_ton_tai"})))


def test_a_missing_column_is_rejected():
    with pytest.raises(ValueError, match="thiếu cột"):
        schema.validate(frame().drop(columns=["label"]))


def test_an_extra_column_is_rejected():
    """A stray column usually means a reader kept a source field it meant to fold into meta."""
    stray = frame().assign(domain="Pháp luật")
    with pytest.raises(ValueError, match="cột lạ"):
        schema.validate(stray)


def test_duplicate_sample_ids_are_rejected():
    with pytest.raises(ValueError, match="sample_id trùng"):
        schema.finalise(frame(row(), row()))


def test_an_empty_required_field_is_rejected():
    with pytest.raises(ValueError, match="chuỗi rỗng"):
        schema.finalise(frame(row(response="")))


def test_an_empty_question_is_allowed():
    """Three of the four corpora are fact-checking sets with no question at all."""
    schema.finalise(frame(row(question="")))


def test_a_half_filled_evidence_span_is_rejected():
    with pytest.raises(ValueError, match="không khớp nhau"):
        schema.finalise(frame(row(evidence="Hà Nội", evidence_start=0, evidence_end=-1)))


def test_an_evidence_span_past_the_end_of_the_context_is_rejected():
    with pytest.raises(ValueError, match="vượt quá độ dài"):
        schema.finalise(frame(row(evidence="Hà Nội", evidence_start=0, evidence_end=9999)))


def test_an_empty_frame_is_rejected():
    with pytest.raises(ValueError, match="rỗng"):
        schema.validate(frame().iloc[0:0])
