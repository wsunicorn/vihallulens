"""The sampling and agreement arithmetic behind task T13.

The annotating itself is done by two people and cannot be tested. What can be tested is that
they are given the same 100 samples on any machine, that the sheet carries no answer key, and
that the agreement figures mean what the report says they mean.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from audit_nei_mapping import (  # noqa: E402
    CHOICES,
    CONTROL_ANSWER,
    N_CONTROLS_PER_LABEL,
    N_SAMPLES,
    SHEET_COLUMNS,
    agreement,
    build_sheet,
    describe_kappa,
    draw_sample,
    normalise_answer,
)


def corpus(n_per_label: int = 150) -> pd.DataFrame:
    """A stand-in ViWikiFC with enough rows of each original label to draw from."""
    records = []
    for original in ("Not_Enough_Information", "Supports", "Refutes"):
        for index in range(n_per_label):
            records.append(
                {
                    "sample_id": f"viwikifc_train_{original[:3]}_{index}",
                    "label_original": original,
                    "context": f"Ngữ cảnh số {index} của nhãn {original}.",
                    "response": f"Phát biểu số {index}.",
                }
            )
    return pd.DataFrame.from_records(records)


# -- sampling ----------------------------------------------------------------------------


def test_the_draw_holds_a_hundred_nei_samples():
    drawn = draw_sample(corpus())
    assert int((drawn["vai_tro"] == "nei").sum()) == N_SAMPLES
    assert set(drawn.loc[drawn["vai_tro"] == "nei", "label_original"]) == {
        "Not_Enough_Information"
    }


def test_controls_come_from_the_other_two_labels():
    drawn = draw_sample(corpus())
    controls = drawn[drawn["vai_tro"] == "doi_chung"]
    assert len(controls) == 2 * N_CONTROLS_PER_LABEL
    assert set(controls["label_original"]) == set(CONTROL_ANSWER)


def test_the_draw_is_the_same_on_every_machine():
    """A fixed seed is the whole reason the audit can be repeated or checked by someone else."""
    first = draw_sample(corpus())["sample_id"].tolist()
    second = draw_sample(corpus())["sample_id"].tolist()
    assert first == second


def test_the_draw_does_not_depend_on_the_order_of_the_source():
    """Rows arrive in whatever order the Parquet files were written in; the sample must not."""
    shuffled = corpus().sample(frac=1.0, random_state=7).reset_index(drop=True)
    assert (
        draw_sample(corpus())["sample_id"].tolist()
        == draw_sample(shuffled)["sample_id"].tolist()
    )


def test_controls_are_scattered_rather_than_grouped_at_one_end():
    """Controls bunched at the end would be spotted and read more carefully than the rest,
    which would defeat the point of having them."""
    drawn = draw_sample(corpus())
    positions = [index for index, role in enumerate(drawn["vai_tro"]) if role == "doi_chung"]
    assert min(positions) < len(drawn) // 3
    assert max(positions) > 2 * len(drawn) // 3


def test_too_few_samples_to_draw_from_is_reported():
    with pytest.raises(ValueError, match="cần ít nhất"):
        draw_sample(corpus(n_per_label=5))


# -- the sheet ---------------------------------------------------------------------------


def test_the_sheet_has_the_documented_columns():
    assert tuple(build_sheet(draw_sample(corpus())).columns) == SHEET_COLUMNS


def test_the_sheet_carries_no_answer_key():
    """The true label is recovered at report time by looking sample_id back up, so there is no
    answer sitting in the file beside the question."""
    sheet = build_sheet(draw_sample(corpus()))
    assert "label_original" not in sheet.columns
    assert "vai_tro" not in sheet.columns


def test_the_sheet_starts_empty():
    sheet = build_sheet(draw_sample(corpus()))
    assert (sheet["nhan_dinh"] == "").all()


# -- reading what people typed -----------------------------------------------------------


@pytest.mark.parametrize("typed", ["ngoai_lai", " ngoai_lai ", "NGOAI_LAI", "ngoai lai",
                                   "ngoai-lai"])
def test_reasonable_variations_of_a_valid_answer_are_accepted(typed):
    assert normalise_answer(typed) == "ngoai_lai"


@pytest.mark.parametrize("typed", ["", "  ", "nan", "None"])
def test_an_unfilled_cell_stays_blank_so_it_can_be_counted(typed):
    assert normalise_answer(typed) == ""


def test_a_wrong_answer_is_passed_through_rather_than_silently_dropped():
    """Turning a typo into a blank would let it be reported as "not finished yet" instead of
    as the mistake it is."""
    assert normalise_answer("ngoai_lai_") == "ngoai_lai_"
    assert normalise_answer("ngoai_lai_") not in CHOICES


# -- agreement ---------------------------------------------------------------------------


def test_perfect_agreement_on_a_mix_of_answers_gives_kappa_one():
    answers = pd.Series(["ngoai_lai", "noi_tai", "khong", "ngoai_lai"])
    stats = agreement(answers, answers.copy())
    assert stats["raw"] == 1.0
    assert stats["kappa"] == pytest.approx(1.0)


def test_two_people_who_both_answer_the_same_thing_every_time_get_no_kappa():
    """The failure this whole design guards against. Raw agreement says 100 %, which looks
    excellent, while kappa refuses to give a number because there is nothing to compare
    against — neither person made a single distinction."""
    answers = pd.Series(["ngoai_lai"] * 20)
    stats = agreement(answers, answers.copy())
    assert stats["raw"] == 1.0
    assert stats["kappa"] != stats["kappa"]  # nan
    assert "không tính được" in describe_kappa(stats["kappa"])


def test_high_raw_agreement_can_still_mean_a_near_zero_kappa():
    """Why the report prints both. With one dominant answer, two people agreeing 80 % of the
    time may have agreed no more than their answer frequencies alone would predict."""
    first = pd.Series(["ngoai_lai"] * 9 + ["khong"])
    second = pd.Series(["ngoai_lai"] * 8 + ["khong", "ngoai_lai"])
    stats = agreement(first, second)
    assert stats["raw"] >= 0.8
    assert abs(stats["kappa"]) < 0.5


@pytest.mark.parametrize(
    ("kappa", "wording"),
    [(-0.1, "tệ hơn ngẫu nhiên"), (0.1, "rất thấp"), (0.3, "thấp"), (0.5, "trung bình"),
     (0.7, "cao"), (0.9, "rất cao")],
)
def test_kappa_is_reported_with_its_band(kappa, wording):
    assert describe_kappa(kappa) == wording


# -- controls ----------------------------------------------------------------------------


def test_every_control_label_has_an_expected_answer():
    assert set(CONTROL_ANSWER.values()) <= set(CHOICES)


def test_the_control_answers_are_the_two_non_extrinsic_classes():
    """A control that should be answered "ngoai_lai" would teach nothing: that is already the
    answer someone rubber-stamping would give."""
    assert "ngoai_lai" not in CONTROL_ANSWER.values()
