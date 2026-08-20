"""The ViFactCheck reader.

The corpus is the reserve one, used only by the optional experiment E17, and it is the one
where evidence usually cannot be located: about 59 % is present verbatim. Task T12 established
why, and these tests pin down that a low rate is accepted while a collapsed rate is not.
"""

import json

import pandas as pd
import pytest

from vihallulens.data import vifactcheck


def write_splits(directory, rows_by_split):
    for split, rows in rows_by_split.items():
        pd.DataFrame.from_records(rows).to_parquet(
            directory / vifactcheck.source_file(split), index=False
        )
    return directory


def row(**overrides):
    base = {
        "Unnamed: 0": 0,
        "index": 3049,
        "Statement": "Điều này đúng.",
        "Context": "Câu một. Câu hai nói rõ điều này. Câu ba.",
        "annotation_id": 18933775,
        "Topic": "Chính trị",
        "Author": "Chính Phủ",
        "Url": "https://example.vn/bai-viet",
        "labels": 0,
        "Evidence": "Câu hai nói rõ điều này.",
    }
    return {**base, **overrides}


def read_all(tmp_path, train=None, dev=None, test=None):
    """Run the real reader over three tiny splits."""
    write_splits(tmp_path, {
        "train": train or [row()],
        "dev": dev or [row(Statement="Câu khác.")],
        "test": test or [row(Statement="Câu khác nữa.")],
    })
    return vifactcheck.read_vifactcheck(tmp_path)


# -- label mapping -----------------------------------------------------------------------


@pytest.mark.parametrize(("code", "label"), [(0, "no"), (1, "intrinsic"), (2, "extrinsic")])
def test_integer_labels_map_as_section_3_of_data_md_says(code, label):
    assert vifactcheck.LABEL_MAP[code] == label


def test_documented_label_counts_add_up_to_the_documented_row_counts():
    for split, expected in vifactcheck.EXPECTED.items():
        labels = sum(value for key, value in expected.items() if key != "rows")
        assert labels == expected["rows"], split


def test_an_unknown_label_code_stops_the_run(tmp_path):
    with pytest.raises(ValueError, match="labels lạ"):
        read_all(tmp_path, train=[row(labels=7)])


def test_the_original_code_is_kept_for_tracing(tmp_path):
    item = read_all(tmp_path, train=[row(labels=2)]).iloc[0]
    assert item["label"] == "extrinsic"
    assert item["label_original"] == "2"


# -- file shape --------------------------------------------------------------------------


def test_a_missing_split_file_is_reported_by_name(tmp_path):
    write_splits(tmp_path, {"train": [row()]})
    with pytest.raises(FileNotFoundError, match=vifactcheck.source_file("dev")):
        vifactcheck.read_vifactcheck(tmp_path)


def test_a_file_missing_a_column_is_rejected(tmp_path):
    thin = {key: value for key, value in row().items() if key != "Topic"}
    with pytest.raises(ValueError, match="thiếu cột"):
        read_all(tmp_path, train=[thin])


def test_the_saved_row_number_column_is_dropped(tmp_path):
    """"Unnamed: 0" is a saved index, 0..n-1, carrying nothing. The schema would reject it as
    a stray column, so the reader has to drop it rather than pass it through."""
    frame = read_all(tmp_path)
    assert "Unnamed: 0" not in frame.columns


def test_a_file_without_the_saved_row_number_still_reads(tmp_path):
    """Dropping a column that is not there must not fail: a future release may omit it."""
    lean = {key: value for key, value in row().items() if key != "Unnamed: 0"}
    assert len(read_all(tmp_path, train=[lean])) == 3


# -- evidence ----------------------------------------------------------------------------


def test_evidence_present_verbatim_gets_a_real_span(tmp_path):
    item = read_all(tmp_path).iloc[0]
    assert item["context"][item["evidence_start"] : item["evidence_end"]] == item["evidence"]


def test_evidence_stitched_from_non_adjacent_sentences_becomes_a_miss(tmp_path):
    """This is what 1.741 of the 2.064 train misses look like: two real sentences of the
    context joined into one string with the full stop between them dropped. Both halves exist,
    the whole does not, and a single (start, end) span cannot represent it."""
    item = read_all(
        tmp_path, train=[row(Evidence="Câu hai nói rõ điều này Câu ba.")]
    ).iloc[0]
    assert item["evidence_start"] == -1
    assert item["evidence"] == ""


def test_the_documented_low_rate_is_accepted(tmp_path):
    """Roughly 41 % of this corpus cannot be located, and that is the documented normal.
    Three of these five rows match, so the rate is 60 % — inside the band."""
    frame = read_all(
        tmp_path,
        train=[row(), row(Evidence="không có"), row(Evidence="cũng không có")],
        dev=[row()],
        test=[row()],
    )
    vifactcheck.check_evidence(frame)


def test_an_unexpectedly_high_rate_also_stops_the_run(tmp_path):
    """The band is two-sided on purpose. Evidence suddenly locatable everywhere would mean the
    corpus was re-annotated, and results from it would not compare with anything measured
    before — the same reason a changed row count stops the run."""
    frame = read_all(tmp_path)
    with pytest.raises(ValueError, match="khoảng 59 %"):
        vifactcheck.check_evidence(frame)


def test_a_collapsed_evidence_rate_stops_the_run(tmp_path):
    """What mismatched columns look like: reading the statement as the evidence, or the wrong
    corpus entirely, gives almost no matches while every count above still looks right."""
    frame = read_all(
        tmp_path,
        train=[row(Evidence="không có")],
        dev=[row(Evidence="cũng không có")],
        test=[row(Evidence="không có nốt")],
    )
    with pytest.raises(ValueError, match="nhầm cột"):
        vifactcheck.check_evidence(frame)


# -- meta --------------------------------------------------------------------------------


def test_topic_is_kept_verbatim_rather_than_tidied(tmp_path):
    """The column mixes cases and spellings — "Thể thao" beside "THỂ THAO". Normalising here
    would lose the ability to trace a row back to its source; the folding belongs to whoever
    slices results by topic."""
    item = read_all(tmp_path, train=[row(Topic="THỂ THAO")]).iloc[0]
    assert json.loads(item["meta"])["topic"] == "THỂ THAO"


def test_rows_sharing_an_annotation_id_stay_separate_samples(tmp_path):
    """5.062 train rows carry only 1.250 annotation_id values — the same trap as pairID in
    ViWikiFC."""
    frame = read_all(tmp_path, train=[row(Statement="Cách nói một."),
                                      row(Statement="Cách nói hai.")])
    train = frame[frame["split"] == "train"]
    assert train["sample_id"].nunique() == 2
    assert {json.loads(value)["source_id"] for value in train["meta"]} == {"18933775"}
