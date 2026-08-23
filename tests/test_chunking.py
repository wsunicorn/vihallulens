"""Cutting a context into chunks.

The two cases task T15 names explicitly — a Vietnamese sentence carrying a decimal number, and
evidence straddling a chunk boundary — are the ones that break a naive implementation, so they
each get a section. Everything else guards the invariant that makes per-chunk attention mean
anything at all: ``context[char_start:char_end] == text``.
"""

import re

import pytest

from vihallulens.data.chunking import (
    Chunk,
    chunk_by_sentence,
    chunk_by_token_window,
    chunk_context,
    locate_evidence_chunk,
    merge_short_spans,
    reconstruct_context,
    sentence_spans,
)


class WordTokenizer:
    """Whitespace tokenizer with offset mapping — enough to test windowing, no download."""

    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        offsets = [(match.start(), match.end()) for match in re.finditer(r"\S+", text)]
        return {"input_ids": list(range(len(offsets))), "offset_mapping": offsets}


def assert_offsets_are_honest(context: str, chunks: list[Chunk]) -> None:
    """The invariant task T07 lost a day to: a chunk's offsets must point at its own text."""
    for chunk in chunks:
        assert context[chunk.char_start : chunk.char_end] == chunk.text


# -- the decimal case, named in the task ---------------------------------------------------


def test_a_decimal_number_does_not_end_a_sentence():
    """Vietnamese writes thousands with a full stop and no space: 331.212. A splitter keying on
    the full stop alone cuts the number in half."""
    context = "Việt Nam có diện tích 331.212 km2. Thủ đô là Hà Nội."
    chunks = chunk_by_sentence(context, min_words=1)
    assert len(chunks) == 2
    assert "331.212" in chunks[0].text
    assert_offsets_are_honest(context, chunks)


def test_a_sentence_ending_in_a_number_still_splits():
    context = "Diện tích cả nước là 331.212. Thủ đô là Hà Nội."
    assert len(chunk_by_sentence(context, min_words=1)) == 2


@pytest.mark.parametrize(
    "context",
    [
        "Ông ThS. Trương Vĩnh Linh hướng dẫn đề tài này cho nhóm sinh viên.",
        "Nhóm khảo sát tại TP. Hồ Chí Minh trong ba tháng liên tiếp vừa qua.",
        "Tác giả Nguyễn V. A. đã công bố kết quả nghiên cứu này từ năm ngoái.",
        "Xem thêm ở Nxb. Giáo dục để biết chi tiết đầy đủ về phương pháp này.",
    ],
)
def test_an_abbreviation_does_not_end_a_sentence(context):
    """Every abbreviation missing from the list becomes a split in the middle of a name."""
    assert len(chunk_by_sentence(context, min_words=1)) == 1


def test_a_date_written_with_full_stops_is_not_cut_up():
    context = "Hội đồng họp ngày 31. 12. 2024 tại trụ sở chính của trường đại học."
    assert len(chunk_by_sentence(context, min_words=1)) == 1


def test_question_and_exclamation_marks_still_split():
    context = "Thủ đô ở đâu? Hà Nội. Thật tuyệt vời!"
    assert len(chunk_by_sentence(context, min_words=1)) == 3


# -- evidence straddling a boundary, named in the task -------------------------------------


def test_evidence_inside_one_chunk_finds_that_chunk():
    context = "Câu một ở đây. Câu hai nói rõ điều này. Câu ba ở cuối."
    chunks = chunk_by_sentence(context, min_words=1)
    assert locate_evidence_chunk(chunks, "Câu hai nói rõ điều này.") == 1


def test_evidence_straddling_two_chunks_goes_to_the_one_holding_most_of_it():
    """Experiment E06 scores hit@1 against a single gold chunk, so there has to be exactly one,
    and "most of the evidence" is the only defensible way to pick it."""
    context = "Câu một ở đây. Câu hai. Đoạn bằng chứng rất dài nằm trải ra ở phần cuối."
    chunks = chunk_by_sentence(context, min_words=1)
    evidence = "Câu hai. Đoạn bằng chứng rất dài nằm trải ra ở phần cuối."
    index = locate_evidence_chunk(chunks, evidence)
    assert chunks[index].n_words > chunks[1].n_words


def test_evidence_split_evenly_still_returns_one_chunk():
    context = "Phần đầu bằng chứng. Phần sau bằng chứng."
    chunks = chunk_by_sentence(context, min_words=1)
    assert locate_evidence_chunk(chunks, context) in {0, 1}


def test_evidence_that_is_not_present_returns_nothing():
    """Only exact matching, as everywhere in this project: a nearest guess in a column later
    treated as ground truth is worse than admitting it was not found."""
    chunks = chunk_by_sentence("Câu một ở đây. Câu hai ở kia.", min_words=1)
    assert locate_evidence_chunk(chunks, "Câu ba không tồn tại.") is None


def test_empty_evidence_returns_nothing():
    chunks = chunk_by_sentence("Câu một ở đây.", min_words=1)
    assert locate_evidence_chunk(chunks, "   ") is None


def test_evidence_can_be_located_in_overlapping_token_windows():
    context = " ".join(f"từ{index}" for index in range(40))
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=10, stride=5)
    evidence = "từ12 từ13 từ14"
    index = locate_evidence_chunk(chunks, evidence)
    assert index is not None
    assert evidence in chunks[index].text


# -- tiling ---------------------------------------------------------------------------------


def test_sentence_chunks_tile_the_context_with_no_gaps():
    """A character falling between two chunks would be a token whose attention is counted in
    the denominator but attributed to no chunk."""
    context = "Câu một ở đây.   Câu hai ở kia.\n\nCâu ba ở cuối."
    chunks = chunk_by_sentence(context, min_words=1)
    assert chunks[0].char_start == 0
    assert chunks[-1].char_end == len(context)
    for earlier, later in zip(chunks, chunks[1:], strict=False):
        assert earlier.char_end == later.char_start


def test_joining_the_chunks_gives_back_the_context():
    context = "Câu một ở đây. Câu hai ở kia. Câu ba ở cuối."
    chunks = chunk_by_sentence(context, min_words=1)
    assert "".join(chunk.text for chunk in chunks) == context


def test_reconstruction_from_offsets_gives_back_the_context():
    context = "Câu một ở đây. Câu hai ở kia."
    assert reconstruct_context(chunk_by_sentence(context, min_words=1)) == context


# -- merging short sentences ----------------------------------------------------------------


def test_a_short_sentence_merges_into_the_previous_one():
    context = "Đây là một câu đủ dài để đứng riêng một mình. Ngắn thôi."
    chunks = chunk_by_sentence(context, min_words=5)
    assert len(chunks) == 1


def test_a_short_first_sentence_merges_forward_instead():
    """Section 2.1 of docs/SPEC.md says "into the previous one", which leaves the first span
    nowhere to go. A short opening line is common in these corpora — a headline, a dateline —
    and left alone it becomes a chunk no attention distribution can say anything about."""
    context = "Theo VnExpress. Đây là một câu đủ dài để đứng riêng một mình được."
    chunks = chunk_by_sentence(context, min_words=5)
    assert len(chunks) == 1
    assert chunks[0].char_start == 0


def test_merging_keeps_the_tiling_intact():
    context = "Ngắn. Đây là một câu đủ dài để đứng riêng. Cũng ngắn. Câu cuối cũng khá dài đấy."
    chunks = chunk_by_sentence(context, min_words=5)
    assert_offsets_are_honest(context, chunks)
    assert "".join(chunk.text for chunk in chunks) == context


def test_a_context_of_only_short_sentences_becomes_one_chunk():
    chunks = chunk_by_sentence("Ngắn. Rất ngắn. Ngắn nữa.", min_words=5)
    assert len(chunks) == 1


def test_indices_are_contiguous_after_merging():
    context = "Ngắn. Đây là một câu đủ dài để đứng riêng. Câu cuối cũng khá dài đấy nhé."
    chunks = chunk_by_sentence(context, min_words=5)
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))


# -- token windows ---------------------------------------------------------------------------


def test_windows_advance_by_the_stride():
    context = " ".join(f"từ{index}" for index in range(20))
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=8, stride=4)
    assert [chunk.token_start for chunk in chunks] == [0, 4, 8, 12]
    assert chunks[0].token_end == 8


def test_a_stride_equal_to_the_window_gives_no_overlap():
    context = " ".join(f"từ{index}" for index in range(20))
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=5, stride=5)
    for earlier, later in zip(chunks, chunks[1:], strict=False):
        assert earlier.char_end <= later.char_start


def test_a_stride_below_the_window_makes_chunks_overlap():
    """The documented default, and the reason the per-chunk shares no longer sum to one: a token
    in the overlap is counted by both chunks."""
    context = " ".join(f"từ{index}" for index in range(20))
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=8, stride=4)
    assert chunks[1].char_start < chunks[0].char_end


def test_token_window_offsets_are_honest():
    context = " ".join(f"từ{index}" for index in range(30))
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=7, stride=3)
    assert_offsets_are_honest(context, chunks)


def test_a_context_shorter_than_one_window_gives_one_chunk():
    context = "chỉ có bốn từ"
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=50, stride=25)
    assert len(chunks) == 1
    assert chunks[0].text == context


def test_the_last_window_does_not_repeat_the_one_before_it():
    context = " ".join(f"từ{index}" for index in range(12))
    chunks = chunk_by_token_window(context, WordTokenizer(), window_size=8, stride=4)
    assert chunks[-1].char_end == len(context)
    assert len({chunk.char_start for chunk in chunks}) == len(chunks)


def test_token_window_without_a_tokenizer_says_so():
    with pytest.raises(ValueError, match="cần tokenizer"):
        chunk_by_token_window("một hai ba", None, window_size=4)


@pytest.mark.parametrize(
    ("window_size", "stride"), [(0, 1), (4, 0), (4, 8)]
)
def test_impossible_window_settings_are_rejected(window_size, stride):
    with pytest.raises(ValueError):
        chunk_by_token_window("một hai ba", WordTokenizer(), window_size, stride)


# -- dispatch and edge cases -----------------------------------------------------------------


def test_chunk_context_dispatches_to_both_strategies():
    context = "Câu một ở đây. Câu hai ở kia."
    assert chunk_context(context, "sentence", min_words=1)
    assert chunk_context(context, "token_window", tokenizer=WordTokenizer(), window_size=3)


def test_an_unknown_strategy_is_rejected():
    with pytest.raises(ValueError, match="không biết chiến lược"):
        chunk_context("Câu một.", "magic")


def test_an_empty_context_gives_no_chunks():
    assert chunk_by_sentence("") == []
    assert chunk_by_token_window("", WordTokenizer(), window_size=4) == []


def test_a_context_with_no_final_punctuation_still_becomes_a_chunk():
    context = "Một câu không có dấu chấm ở cuối"
    chunks = chunk_by_sentence(context, min_words=1)
    assert len(chunks) == 1
    assert chunks[0].text == context


def test_merging_with_min_words_of_one_changes_nothing():
    context = "Ngắn. Câu hai."
    spans = sentence_spans(context)
    assert merge_short_spans(context, spans, min_words=1) == spans
