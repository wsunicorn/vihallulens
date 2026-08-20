"""The ISE-DSC01 reader.

The interesting part is not the column mapping but what happens to evidence: NEI rows carry
JSON ``null``, two rows carry only a blank line, and one row names a sentence that is not in
its own context. All three have to end up as "no offset" rather than as a plausible number.
"""

import json

import pytest

from vihallulens.data import isedsc01


def write_json(directory, records):
    path = directory / isedsc01.SOURCE_FILE
    payload = {str(7125 + index): record for index, record in enumerate(records)}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return directory


def record(**overrides):
    base = {
        "context": "Câu một. Câu hai nói rõ điều này. Câu ba.",
        "claim": "Điều này đúng.",
        "verdict": "SUPPORTED",
        "evidence": "Câu hai nói rõ điều này.",
        "domain": "khoa-hoc",
    }
    return {**base, **overrides}


def read_one(tmp_path, **overrides):
    """Run the real reader on a single record and return the row it produced."""
    write_json(tmp_path, [record(**overrides)])
    return isedsc01.read_isedsc01(tmp_path).iloc[0]


# -- label mapping -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("verdict", "label"),
    [("SUPPORTED", "no"), ("REFUTED", "intrinsic"), ("NEI", "extrinsic")],
)
def test_verdicts_map_as_section_3_of_data_md_says(verdict, label):
    assert isedsc01.VERDICT_TO_LABEL[verdict] == label


def test_the_expected_counts_match_the_documented_total():
    assert sum(isedsc01.EXPECTED_LABELS.values()) == isedsc01.EXPECTED_ROWS


def test_an_unknown_verdict_stops_the_run_naming_the_record(tmp_path):
    write_json(tmp_path, [record(verdict="MAYBE")])
    with pytest.raises(ValueError, match="verdict lạ"):
        isedsc01.read_isedsc01(tmp_path)


# -- file shape --------------------------------------------------------------------------


def test_a_missing_source_file_is_reported_by_name(tmp_path):
    with pytest.raises(FileNotFoundError, match=isedsc01.SOURCE_FILE):
        isedsc01.read_isedsc01(tmp_path)


def test_a_json_list_instead_of_a_dict_is_rejected(tmp_path):
    (tmp_path / isedsc01.SOURCE_FILE).write_text(
        json.dumps([record()], ensure_ascii=False), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="phải là một dict"):
        isedsc01.read_isedsc01(tmp_path)


def test_a_changed_row_count_stops_the_run(tmp_path):
    write_json(tmp_path, [record()])
    with pytest.raises(ValueError, match="mục 4 docs/DATA.md"):
        isedsc01.normalize_isedsc01(tmp_path)


# -- evidence ----------------------------------------------------------------------------


def test_evidence_present_verbatim_gets_a_real_span(tmp_path):
    row = read_one(tmp_path)
    assert row["context"][row["evidence_start"] : row["evidence_end"]] == row["evidence"]


def test_a_null_evidence_becomes_no_offset(tmp_path):
    """Every NEI row carries JSON null here, not an empty string."""
    row = read_one(tmp_path, verdict="NEI", evidence=None)
    assert row["evidence"] == ""
    assert row["evidence_start"] == -1


def test_a_blank_line_as_evidence_becomes_no_offset(tmp_path):
    """Two real rows hold "\\n\\n". Left alone it matches a blank line in the context and the
    row ends up with an offset pointing at nothing."""
    row = read_one(tmp_path, context="Câu một.\n\nCâu hai.", evidence="\n\n")
    assert row["evidence_start"] == -1


def test_evidence_absent_from_its_own_context_becomes_no_offset(tmp_path):
    """One real row names a sentence with a doubled full stop that its context does not have.
    A corpus defect, and the right answer is to admit the miss rather than approximate it."""
    row = read_one(tmp_path, evidence="Câu hai nói rõ điều này..")
    assert row["evidence_start"] == -1


def test_evidence_text_is_dropped_when_the_offsets_say_it_was_not_found(tmp_path):
    """Keeping the text beside a -1 offset would let one experiment read the field while
    another trusts the offset, and the two would disagree."""
    row = read_one(tmp_path, evidence="câu không tồn tại")
    assert row["evidence"] == ""
    assert row["evidence_start"] == -1
