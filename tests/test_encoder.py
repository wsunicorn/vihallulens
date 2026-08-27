"""What the encoder baselines of E09 are shown, and how their labels are numbered.

The fine-tuning itself needs a GPU and stays out of the test suite, per section 5 of
docs/SPEC.md. Everything here decides whether the baseline is a fair one, which is the part
most easily broken by accident and the part that runs fine on a CPU.
"""

import pandas as pd
import pytest

from vihallulens.data.segmentation import segment, segment_all
from vihallulens.detect.encoder import (
    MODELS,
    build_pairs,
    decode_labels,
    encode_labels,
)
from vihallulens.evaluation.metrics import LABELS


def frame(rows):
    return pd.DataFrame.from_records(rows)


# -- word segmentation --------------------------------------------------------------------


def test_syllables_of_one_word_are_joined():
    """PhoBERT was pre-trained on text in this form. Raw text puts it in front of a vocabulary
    it never saw, and its score drops for a reason unrelated to the task."""
    assert segment("Hà Nội là thủ đô") == "Hà_Nội là thủ_đô"


def test_segmentation_leaves_blank_text_alone():
    assert segment("") == ""
    assert segment("   ") == "   "


def test_segmenting_a_sequence_gives_one_result_per_input():
    assert len(segment_all(["Hà Nội", "Thành phố Hồ Chí Minh", ""])) == 3


def test_repeated_text_is_segmented_once():
    """The corpora repeat contexts heavily — ViHallu has 7.000 samples over 3.865 distinct
    contexts — so caching turns most of the work into lookups."""
    from vihallulens.data.segmentation import cache_info

    segment("một câu để kiểm tra bộ đệm")
    before = cache_info().hits
    segment("một câu để kiểm tra bộ đệm")
    assert cache_info().hits == before + 1


# -- what the model is shown --------------------------------------------------------------


def test_the_pair_puts_the_given_text_left_and_the_judged_text_right():
    """Mirrors the prompt template locked at T07: everything the model was given on the left,
    the text being judged on the right. That is what makes the comparison with the attention
    method a comparison of methods rather than of who was shown more."""
    left, right = build_pairs(
        frame([{"context": "Ngữ cảnh.", "question": "Câu hỏi?", "response": "Phản hồi."}]),
        segment=False,
    )
    assert left == ["Ngữ cảnh. Câu hỏi?"]
    assert right == ["Phản hồi."]


def test_a_corpus_without_questions_leaves_the_left_side_as_the_context():
    """Three of the four corpora are fact-checking sets with no question at all."""
    left, _ = build_pairs(
        frame([{"context": "Ngữ cảnh.", "question": "", "response": "Phát biểu."}]),
        segment=False,
    )
    assert left == ["Ngữ cảnh."]


def test_a_frame_with_no_question_column_still_works():
    left, right = build_pairs(
        frame([{"context": "Ngữ cảnh.", "response": "Phát biểu."}]), segment=False
    )
    assert left == ["Ngữ cảnh."] and right == ["Phát biểu."]


def test_segmentation_reaches_both_sides_of_the_pair():
    left, right = build_pairs(
        frame([{"context": "Hà Nội", "question": "", "response": "thủ đô"}]), segment=True
    )
    assert left == ["Hà_Nội"] and right == ["thủ_đô"]


def test_a_frame_missing_a_column_is_rejected():
    with pytest.raises(ValueError, match="thiếu cột"):
        build_pairs(frame([{"context": "Ngữ cảnh."}]), segment=False)


# -- label numbering ----------------------------------------------------------------------


def test_labels_are_numbered_by_the_fixed_order_not_by_what_the_data_contains():
    """Class 0 has to mean the same thing in every run, or a model saved from one cannot be
    read by another. Same trap that made the first E01 run report a wrong calibration error,
    approached from the other side."""
    assert encode_labels(["extrinsic", "no"]) == [LABELS.index("extrinsic"), 0]


def test_encoding_and_decoding_come_back_to_the_same_labels():
    labels = ["no", "intrinsic", "extrinsic", "no"]
    assert decode_labels(encode_labels(labels)) == labels


def test_a_label_outside_the_three_classes_is_rejected():
    with pytest.raises(ValueError, match="nhãn lạ"):
        encode_labels(["no", "maybe"])


def test_a_class_id_outside_the_range_is_rejected():
    with pytest.raises(ValueError, match="ngoài phạm vi"):
        decode_labels([0, 7])


# -- the model registry ---------------------------------------------------------------------


def test_all_three_encoders_are_registered():
    assert sorted(MODELS) == ["infoxlm", "phobert", "xlmr"]


def test_only_phobert_asks_for_segmentation():
    """XLM-R and InfoXLM use SentencePiece over raw text; giving them underscores would have
    them tokenise the underscores as ordinary characters."""
    assert MODELS["phobert"]["segment"] is True
    assert MODELS["xlmr"]["segment"] is False
    assert MODELS["infoxlm"]["segment"] is False


def test_phobert_is_capped_lower_than_the_other_two():
    """Not a choice: PhoBERT cannot go past 256 positions. Reported beside the scores, because
    a baseline losing partly for being unable to read the whole context is a fact the report
    has to state."""
    assert MODELS["phobert"]["max_length"] == 256
    assert MODELS["xlmr"]["max_length"] == 512


def test_every_entry_carries_what_the_training_loop_needs():
    for name, spec in MODELS.items():
        assert set(spec) >= {"name", "max_length", "segment", "batch_size"}, name
        assert spec["batch_size"] >= 1
