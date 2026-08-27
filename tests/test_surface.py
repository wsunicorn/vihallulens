"""The two surface features of experiment E01.

They define the floor the whole thesis has to clear, so what exactly they measure needs pinning
down: a floor that moves is not a floor.
"""

import numpy as np
import pandas as pd
import pytest

from vihallulens.data.text import tokenize, word_count
from vihallulens.features.surface import (
    FEATURE_NAMES,
    lexical_overlap,
    response_len,
    surface_features,
)


def frame(rows):
    return pd.DataFrame.from_records(rows)


# -- tokenising ---------------------------------------------------------------------------


def test_diacritics_survive_tokenising():
    assert tokenize("Hà Nội, thủ đô!") == ["hà", "nội", "thủ", "đô"]


def test_word_count_is_not_the_tokenised_count():
    """Deliberately different. word_count is the plain reading of "how long is this response",
    and it is what reproduces the per-label averages published in docs/EXPERIMENTS.md."""
    text = "Hà Nội - thủ đô"
    assert word_count(text) == 5  # dấu gạch ngang đứng riêng, vẫn tính là một "từ"
    assert len(tokenize(text)) == 4  # tokenize bỏ dấu câu nên chỉ còn bốn âm tiết


# -- response length ----------------------------------------------------------------------


def test_length_counts_whitespace_separated_pieces():
    assert response_len("một hai ba bốn") == 4


def test_length_of_an_empty_response_is_zero():
    assert response_len("") == 0
    assert response_len("   ") == 0


def test_repeated_whitespace_does_not_inflate_the_length():
    assert response_len("một    hai\n\nba") == 3


# -- lexical overlap ----------------------------------------------------------------------


def test_a_response_copied_from_the_context_scores_one():
    assert lexical_overlap("Hà Nội là thủ đô", "Hà Nội là thủ đô của Việt Nam") == 1.0


def test_a_response_sharing_nothing_scores_zero():
    assert lexical_overlap("hoàn toàn khác biệt", "Hà Nội thủ đô") == 0.0


def test_half_the_words_shared_scores_a_half():
    assert lexical_overlap("Hà Nội xyz abc", "Hà Nội là thủ đô") == pytest.approx(0.5)


def test_overlap_counts_occurrences_not_distinct_words():
    """A response repeating one context word ten times should score higher than one using it
    once: the question is how much of this text was lifted from the source."""
    assert lexical_overlap("Hà Hà Hà xyz", "Hà Nội") == pytest.approx(0.75)


def test_case_and_punctuation_do_not_break_the_match():
    assert lexical_overlap("HÀ NỘI!", "hà nội") == 1.0


def test_an_empty_response_scores_zero_rather_than_dividing_by_zero():
    """Zero is also what a maximally unfaithful response scores, which is the right
    neighbourhood for a response with no content at all."""
    assert lexical_overlap("", "Hà Nội") == 0.0


def test_an_empty_context_makes_everything_unmatched():
    assert lexical_overlap("Hà Nội", "") == 0.0


# -- the matrix ---------------------------------------------------------------------------


def test_the_matrix_has_one_row_per_sample_and_one_column_per_feature():
    data = frame([
        {"response": "một hai", "context": "một hai ba"},
        {"response": "bốn", "context": "một hai ba"},
    ])
    matrix = surface_features(data)
    assert matrix.shape == (2, len(FEATURE_NAMES))


def test_the_columns_are_in_the_documented_order():
    data = frame([{"response": "một hai ba", "context": "một"}])
    matrix = surface_features(data)
    assert FEATURE_NAMES == ("response_len", "lexical_overlap")
    assert matrix[0, 0] == 3.0
    assert matrix[0, 1] == pytest.approx(1 / 3)


def test_a_single_row_frame_still_gives_a_two_dimensional_matrix():
    """A one-row matrix collapsing to one dimension would break the classifier with an error
    several lines away from the cause."""
    matrix = surface_features(frame([{"response": "một", "context": "một"}]))
    assert matrix.ndim == 2


def test_an_empty_frame_gives_an_empty_matrix_of_the_right_width():
    matrix = surface_features(frame([]).reindex(columns=["response", "context"]))
    assert matrix.shape == (0, len(FEATURE_NAMES))


def test_a_frame_missing_a_column_is_rejected():
    with pytest.raises(ValueError, match="thiếu cột"):
        surface_features(frame([{"response": "một"}]))


def test_the_matrix_is_float_so_the_classifier_can_scale_it():
    matrix = surface_features(frame([{"response": "một hai", "context": "một"}]))
    assert matrix.dtype == np.float64
