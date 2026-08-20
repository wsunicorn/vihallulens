"""The ViWikiFC reader.

Two things matter here beyond the column mapping. Evidence must be found for essentially every
row, including the NEI rows — that property is what makes experiment E08 possible and no other
corpus has it. And ``pairID`` looks like a key but is not one, so nothing may treat it as one.
"""

import json

import pandas as pd
import pytest

from vihallulens.data import viwikifc


def write_splits(directory, rows_by_split):
    for split, rows in rows_by_split.items():
        pd.DataFrame.from_records(rows).to_csv(
            directory / viwikifc.source_file(split), index=False
        )
    return directory


def row(**overrides):
    base = {
        "pairID": "uit_424_27_39_3_11",
        "evidence": "Câu hai nói rõ điều này.",
        "gold_label": "Supports",
        "link": "https://vi.wikipedia.org/Trung Quốc",
        "context": "Câu một. Câu hai nói rõ điều này. Câu ba.",
        "sentenceID": "uit_424_27_39_3",
        "claim": "Điều này đúng.",
        "annotator_labels": "['Support']",
        "title": "Trung Quốc",
    }
    return {**base, **overrides}


def read_all(tmp_path, train=None, dev=None, test=None):
    """Run the real reader over three tiny splits."""
    write_splits(tmp_path, {
        "train": train or [row()],
        "dev": dev or [row(claim="Câu khác.")],
        "test": test or [row(claim="Câu khác nữa.")],
    })
    return viwikifc.read_viwikifc(tmp_path)


# -- label mapping -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("gold", "label"),
    [("Supports", "no"), ("Refutes", "intrinsic"), ("Not_Enough_Information", "extrinsic")],
)
def test_labels_map_as_section_3_of_data_md_says(gold, label):
    assert viwikifc.LABEL_MAP[gold] == label


def test_documented_label_counts_add_up_to_the_documented_row_counts():
    for split, expected in viwikifc.EXPECTED.items():
        labels = sum(value for key, value in expected.items() if key != "rows")
        assert labels == expected["rows"], split


def test_an_unknown_label_stops_the_run(tmp_path):
    with pytest.raises(ValueError, match="gold_label lạ"):
        read_all(tmp_path, train=[row(gold_label="Maybe")])


# -- file shape --------------------------------------------------------------------------


def test_a_missing_split_file_is_reported_by_name(tmp_path):
    write_splits(tmp_path, {"train": [row()]})
    with pytest.raises(FileNotFoundError, match=viwikifc.source_file("dev")):
        viwikifc.read_viwikifc(tmp_path)


def test_a_file_missing_a_column_is_rejected(tmp_path):
    thin = {key: value for key, value in row().items() if key != "title"}
    with pytest.raises(ValueError, match="thiếu cột"):
        read_all(tmp_path, train=[thin])


def test_the_original_split_is_kept(tmp_path):
    """Section 5 of docs/DATA.md: this corpus is not re-split, so its numbers stay comparable
    with the ones published for it."""
    frame = read_all(tmp_path)
    assert sorted(frame["split"].unique()) == ["dev", "test", "train"]


# -- evidence ----------------------------------------------------------------------------


def test_evidence_gets_a_real_span(tmp_path):
    item = read_all(tmp_path).iloc[0]
    assert item["context"][item["evidence_start"] : item["evidence_end"]] == item["evidence"]


def test_nei_rows_carry_evidence_too(tmp_path):
    """The property no other corpus has, and the whole reason this one is the outside control
    for the extrinsic class."""
    item = read_all(tmp_path, train=[row(gold_label="Not_Enough_Information")]).iloc[0]
    assert item["label"] == "extrinsic"
    assert item["evidence_start"] >= 0


def test_evidence_corrupted_at_the_source_becomes_a_miss(tmp_path):
    """One real train row reads "NhậtaimBản" where its own context reads "Nhật Bản" — three
    stray letters spliced over a space. Not an encoding fault, since every other row matches;
    a defect in the published corpus, and the answer is to admit the miss."""
    item = read_all(tmp_path, train=[row(evidence="Câu hai nóiaimrõ điều này.")]).iloc[0]
    assert item["evidence_start"] == -1
    assert item["evidence"] == ""


def test_a_wholesale_evidence_failure_stops_the_run(tmp_path):
    """The check exists for encoding faults, which would damage thousands of rows silently
    while every other count still looked right."""
    frame = read_all(
        tmp_path,
        train=[row(evidence="không có trong ngữ cảnh"), row(evidence="cũng không có")],
        dev=[row(evidence="không có nốt")],
    )
    with pytest.raises(ValueError, match="encoding"):
        viwikifc.check_evidence(frame)


def test_the_one_known_miss_does_not_trip_the_guard(tmp_path):
    """One miss is the measured state of the corpus, so it must pass — otherwise the guard
    would fire on every correct run."""
    viwikifc.check_evidence(read_all(tmp_path, train=[row(evidence="không có trong ngữ cảnh")]))


def test_a_repaired_corpus_with_no_misses_still_passes(tmp_path):
    """Fewer misses can only mean the published corpus was fixed. Refusing to run on a
    repaired corpus would be perverse, so the guard fires on more, not on different."""
    viwikifc.check_evidence(read_all(tmp_path))


# -- pairID ------------------------------------------------------------------------------


def test_rows_sharing_a_pairid_stay_separate_samples(tmp_path):
    """835 train rows share a pairID with a different claim: it identifies an (evidence, label)
    pair, not a sample. Anything using it as a key would collapse those rows together."""
    frame = read_all(tmp_path, train=[row(claim="Cách nói thứ nhất."),
                                      row(claim="Cách nói thứ hai.")])
    train = frame[frame["split"] == "train"]
    assert len(train) == 2
    assert train["sample_id"].nunique() == 2
    assert {json.loads(value)["source_id"] for value in train["meta"]} == {row()["pairID"]}
