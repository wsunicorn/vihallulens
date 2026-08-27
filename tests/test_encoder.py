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


# -- the whole training loop, on a CPU, with no download ----------------------------------


def tiny_build(spec):
    """A two-layer randomly initialised Roberta sharing nothing with the real checkpoints.

    Enough to run the real loop end to end in a couple of seconds. The point is not to learn
    anything but to prove the loop *runs*: the first Kaggle attempt at T18 crashed on
    ``torch.tensor`` receiving label strings, after the model had already been downloaded and
    the session had already been paid for.
    """
    from transformers import RobertaConfig, RobertaForSequenceClassification

    config = RobertaConfig(
        vocab_size=1000,
        hidden_size=32,
        num_hidden_layers=2,
        num_attention_heads=2,
        intermediate_size=64,
        max_position_embeddings=64,
        num_labels=len(LABELS),
    )
    return StubTokenizer(), RobertaForSequenceClassification(config)


class StubTokenizer:
    """Turns text pairs into fixed-width id tensors without any vocabulary file."""

    def __call__(self, left, right=None, truncation=True, max_length=16,
                 padding="max_length", return_tensors=None, add_special_tokens=True):
        import torch

        rows = []
        for index in range(len(left)):
            text = f"{left[index]} {right[index] if right else ''}"
            ids = [abs(hash(word)) % 999 + 1 for word in text.split()][:max_length]
            ids += [0] * (max_length - len(ids))
            rows.append(ids)
        ids_tensor = torch.tensor(rows, dtype=torch.long)
        out = {"input_ids": ids_tensor, "attention_mask": (ids_tensor != 0).long()}
        return out if return_tensors else {"input_ids": [row for row in rows]}


def test_the_training_loop_runs_end_to_end_on_a_cpu():
    """Would have caught the crash that cost a Kaggle session: labels reached the loader as
    strings because the test split kept them in the form compute_metrics wants."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from train_encoder_baseline import train_once

    labels = ["no", "intrinsic", "extrinsic"] * 4
    data = {
        "train": ([f"ngữ cảnh {i}" for i in range(12)],
                  [f"phản hồi {i}" for i in range(12)], labels),
        "test": ([f"ngữ cảnh {i}" for i in range(6)],
                 [f"phản hồi {i}" for i in range(6)], labels[:6]),
    }
    spec = {"name": "tiny", "max_length": 16, "segment": False, "batch_size": 4}
    result = train_once(spec, data, seed=42, epochs=1, lr=1e-3, device="cpu", build=tiny_build)

    assert set(result) >= {"metrics", "y_pred", "n_params", "ms_per_sample"}
    assert len(result["y_pred"]) == 6
    assert set(result["y_pred"]) <= set(LABELS)
    assert 0.0 <= result["metrics"]["macro_f1"] <= 1.0


def test_the_loop_scores_against_the_string_labels_not_the_encoded_ones():
    """The two forms have to stay separate: ids go to the loader, strings go to the scorer."""
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from train_encoder_baseline import train_once

    labels = ["no", "intrinsic", "extrinsic"] * 4
    data = {
        "train": ([f"a {i}" for i in range(12)], [f"b {i}" for i in range(12)], labels),
        "test": (["a 0", "a 1"], ["b 0", "b 1"], ["no", "extrinsic"]),
    }
    spec = {"name": "tiny", "max_length": 16, "segment": False, "batch_size": 4}
    result = train_once(spec, data, seed=42, epochs=1, lr=1e-3, device="cpu", build=tiny_build)
    assert all(isinstance(label, str) for label in result["y_pred"])


# -- collapse detection --------------------------------------------------------------------


def test_a_run_predicting_one_class_for_everything_is_flagged():
    """The signature of a fine-tune that never left its starting point. At T18 six runs out of
    nine came back like this — every sample labelled `intrinsic`, macro-F1 exactly 0,167 — and
    averaging them in beside the runs that worked put PhoBERT's mean outside its own confidence
    interval."""
    from vihallulens.detect.encoder import has_collapsed

    assert has_collapsed(["intrinsic"] * 700)


def test_a_run_using_more_than_one_class_is_not_flagged():
    from vihallulens.detect.encoder import has_collapsed

    assert not has_collapsed(["no", "intrinsic", "no", "extrinsic"])


def test_collapse_is_detected_by_the_predictions_not_by_the_score():
    """A score threshold would depend on the class balance; counting distinct predictions
    does not."""
    from vihallulens.detect.encoder import has_collapsed

    assert has_collapsed(["no"] * 10)
    assert not has_collapsed(["no"] * 9 + ["intrinsic"])


def test_every_model_carries_its_own_learning_rate():
    """Shared at 2e-5, the two 512-token models collapsed on three seeds out of three."""
    for name, spec in MODELS.items():
        assert "lr" in spec, name
        assert 0 < spec["lr"] <= 5e-5


def test_a_run_whose_loss_never_moved_is_not_counted_as_learned():
    """The second net, and the one that caught what the first missed.

    At T18 a PhoBERT seed answered `intrinsic` 699 times out of 700 and something else once.
    Two distinct classes, so the collapse check saw nothing wrong, while its loss had sat on
    ln(3) for a whole epoch and it had plainly learned nothing. It was averaged in anyway, and
    dragged the reported mean to 0,5490 — outside its own confidence interval of
    [0,6887 – 0,7546], which is the shape of a bug rather than of a noisy measurement.
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from train_encoder_baseline import train_once

    labels = ["no", "intrinsic", "extrinsic"] * 28
    data = {
        "train": ([f"ngữ cảnh {i}" for i in range(84)],
                  [f"phản hồi {i}" for i in range(84)], labels),
        "test": ([f"ngữ cảnh {i}" for i in range(6)],
                 [f"phản hồi {i}" for i in range(6)], labels[:6]),
    }
    spec = {"name": "tiny", "max_length": 16, "segment": False, "batch_size": 4}
    # A learning rate of zero cannot learn, so the loss stays where it started.
    result = train_once(spec, data, seed=42, epochs=3, lr=0.0, device="cpu", build=tiny_build)

    assert result["stopped_early"] is True
    assert result["learned"] is False


def test_a_run_that_trained_normally_is_counted_as_learned():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from train_encoder_baseline import train_once

    # The toy task has to be learnable or the stop is right to fire, so the text here carries
    # its own answer. On text with no signal in it, ln(3) *is* the correct final loss.
    labels = ["no", "intrinsic", "extrinsic"] * 40
    data = {
        "train": ([f"dấu hiệu {label}" for label in labels], list(labels), labels),
        "test": ([f"dấu hiệu {label}" for label in labels[:6]], list(labels[:6]), labels[:6]),
    }
    spec = {"name": "tiny", "max_length": 16, "segment": False, "batch_size": 4}
    result = train_once(spec, data, seed=42, epochs=1, lr=5e-3, device="cpu", build=tiny_build)

    assert result["stopped_early"] is False
    assert result["learned"] is True


# -- which run carries the confidence interval ---------------------------------------------


def interval_run(scores):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from train_encoder_baseline import pick_interval_run

    return pick_interval_run([{"metrics": {"macro_f1": score}} for score in scores])


def test_the_interval_comes_from_the_most_ordinary_run():
    """An interval around an outlier describes that run, not the method."""
    assert interval_run([0.60, 0.75, 0.90]) == 1


def test_two_survivors_do_not_hand_the_interval_to_the_better_one():
    """Discarding a dead seed leaves an even number, and the earlier sorted-list version always
    reached for the upper of the two. A model that lost a seed would then quietly report the
    interval of its better half — a bias that grows precisely when the run went badly."""
    # Two runs are equally far from their own mean, so the tie has to break on something
    # unrelated to the score. It breaks on seed order: whichever ran first, high or low.
    assert interval_run([0.7542, 0.7234]) == 0
    assert interval_run([0.7234, 0.7542]) == 0


def test_a_lone_survivor_carries_it():
    assert interval_run([0.71]) == 0
