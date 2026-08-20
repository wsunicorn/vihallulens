"""The ViHallu reader, and above all its one inference: which prompts are ``noisy``.

The corpus ships no column saying which of the three prompt families a prompt belongs to, so
the rule of section 7 of docs/DATA.md is the only thing standing between task T35 and a column
full of guesses. These tests pin the rule down on cases with known answers; no file is read.
"""

import pandas as pd
import pytest

from vihallulens.data import vihallu

# -- diacritic detection -----------------------------------------------------------------


@pytest.mark.parametrize("char", ["á", "à", "ả", "ã", "ạ", "ă", "â", "ê", "ô", "ơ", "ư", "ệ",
                                  "ự", "ỹ", "Đ", "đ"])
def test_vietnamese_diacritic_letters_are_recognised(char):
    assert vihallu.is_diacritic_letter(char)


@pytest.mark.parametrize("char", ["a", "e", "z", "Z", "1", " ", ".", "?"])
def test_plain_ascii_is_not_a_diacritic(char):
    assert not vihallu.is_diacritic_letter(char)


def test_d_with_stroke_counts_even_though_it_does_not_decompose():
    """``đ`` carries a stroke rather than a combining mark, so Unicode does not decompose it —
    yet it disappears just the same when text is stripped of diacritics, so the rule has to
    name it explicitly."""
    import unicodedata

    assert len(unicodedata.normalize("NFD", "đ")) == 1
    assert vihallu.is_diacritic_letter("đ")


def test_decomposed_text_is_detected_as_having_diacritics():
    import unicodedata

    assert vihallu.has_diacritics(unicodedata.normalize("NFD", "Thế giới"))


def test_text_with_no_diacritics_is_reported_as_such():
    assert not vihallu.has_diacritics("The gioi khong dau")


# -- the noisy rule ----------------------------------------------------------------------


def test_a_stripped_prompt_beside_an_accented_context_is_noisy():
    assert vihallu.infer_prompt_type(
        "Thu do cua Viet Nam la gi?", "Hà Nội là thủ đô của Việt Nam."
    ) == vihallu.PROMPT_TYPE_NOISY


def test_a_normal_prompt_is_not_classified_further():
    """``factual`` and ``adversarial`` are not separable by any simple rule, so both come back
    as ``unknown`` rather than as a guess."""
    assert vihallu.infer_prompt_type(
        "Thủ đô của Việt Nam là gì?", "Hà Nội là thủ đô của Việt Nam."
    ) == vihallu.PROMPT_TYPE_UNKNOWN


def test_a_prompt_with_nothing_to_lose_is_not_called_noisy():
    """Judging the prompt on its own would flag a question made only of names and numbers,
    which never had a diacritic to strip. Comparing against the context is what prevents it."""
    assert vihallu.infer_prompt_type(
        "IBM 1970?", "IBM 1970 PC DOS."
    ) == vihallu.PROMPT_TYPE_UNKNOWN


# -- reading the file --------------------------------------------------------------------


def write_csv(directory, rows):
    path = directory / vihallu.SOURCE_FILE
    pd.DataFrame.from_records(rows).to_csv(path, index=False)
    return directory


def sample(**overrides):
    base = {
        "id": "abc-123",
        "context": "Hà Nội là thủ đô của Việt Nam.",
        "prompt": "Thủ đô của Việt Nam là gì?",
        "response": "Hà Nội.",
        "label": "no",
    }
    return {**base, **overrides}


def test_a_missing_source_file_is_reported_by_name(tmp_path):
    with pytest.raises(FileNotFoundError, match=vihallu.SOURCE_FILE):
        vihallu.normalize_vihallu(tmp_path)


def test_a_file_missing_a_column_is_rejected(tmp_path):
    write_csv(tmp_path, [{"id": "1", "context": "a", "prompt": "b", "response": "c"}])
    with pytest.raises(ValueError, match="thiếu cột"):
        vihallu.normalize_vihallu(tmp_path)


def test_a_changed_row_count_stops_the_run(tmp_path):
    """A different release of the corpus is not comparable with anything measured before, so
    section 4 of docs/DATA.md says to stop and report rather than carry on."""
    write_csv(tmp_path, [sample()])
    with pytest.raises(ValueError, match="mục 4 docs/DATA.md"):
        vihallu.normalize_vihallu(tmp_path)


def test_the_expected_counts_match_the_documented_total():
    assert sum(vihallu.EXPECTED_LABELS.values()) == vihallu.EXPECTED_ROWS
