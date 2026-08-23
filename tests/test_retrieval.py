"""The ViWikiFC evidence pool and BM25 search over it.

The pool is what makes experiment E08 possible: ViWikiFC's own contexts are too short to cut
into chunks — task T15 measured 15,3 % of them collapsing to a single chunk — so E08 builds a
longer context by retrieving from this pool instead.
"""

import pandas as pd
import pytest

from vihallulens.data.retrieval import (
    COLUMNS,
    EXPECTED_ARTICLES,
    EXPECTED_SENTENCES,
    EvidenceIndex,
    build_evidence_corpus,
    check_expected,
    evidence_id,
    tokenize,
)


def corpus(texts=None) -> pd.DataFrame:
    texts = texts or [
        "Hà Nội là thủ đô của Việt Nam và nằm bên bờ sông Hồng.",
        "Thành phố Hồ Chí Minh là thành phố đông dân nhất cả nước.",
        "Thời nhà Thương, đồ đồng đã được dùng phổ biến và đạt trình độ chế tác cao.",
        "Sông Cửu Long đổ ra biển qua chín cửa sông lớn ở miền Tây.",
    ]
    return pd.DataFrame(
        {
            "evidence_id": [evidence_id(text) for text in texts],
            "text": texts,
            "title": ["Việt Nam"] * len(texts),
            "link": ["https://vi.wikipedia.org/Việt Nam"] * len(texts),
            "n_claims": [1] * len(texts),
        }
    )


def write_raw(directory, rows):
    for split in ("train", "dev", "test"):
        pd.DataFrame.from_records(rows if split == "train" else rows[:1]).to_csv(
            directory / f"viwikifc_{split}.csv", index=False
        )
    return directory


def raw_row(**overrides):
    base = {
        "pairID": "uit_1",
        "evidence": "Hà Nội là thủ đô của Việt Nam.",
        "gold_label": "Supports",
        "link": "https://vi.wikipedia.org/Việt Nam",
        "context": "Hà Nội là thủ đô của Việt Nam.",
        "sentenceID": "uit_1_1",
        "claim": "Thủ đô là Hà Nội.",
        "annotator_labels": "['Support']",
        "title": "Việt Nam",
    }
    return {**base, **overrides}


# -- tokenising ---------------------------------------------------------------------------


def test_diacritics_survive_tokenising():
    """A punctuation filter written as an ASCII range would strip Vietnamese letters and leave
    the index searching a mangled corpus."""
    assert tokenize("Hà Nội, thủ đô!") == ["hà", "nội", "thủ", "đô"]


def test_case_is_folded():
    assert tokenize("HÀ NỘI") == tokenize("hà nội")


def test_a_vietnamese_word_becomes_its_syllables():
    """No word segmenter, so "Hà Nội" is two tokens rather than one. A real limitation, written
    down rather than assumed away."""
    assert len(tokenize("Hà Nội")) == 2


def test_text_with_nothing_but_punctuation_gives_no_tokens():
    assert tokenize("!!! ??? ...") == []


# -- identifiers --------------------------------------------------------------------------


def test_the_same_sentence_always_gets_the_same_id():
    assert evidence_id("Hà Nội là thủ đô.") == evidence_id("Hà Nội là thủ đô.")


def test_surrounding_whitespace_does_not_change_the_id():
    assert evidence_id("  Hà Nội.  ") == evidence_id("Hà Nội.")


def test_different_sentences_get_different_ids():
    assert evidence_id("Hà Nội.") != evidence_id("Huế.")


# -- building the pool --------------------------------------------------------------------


def test_each_distinct_sentence_appears_once(tmp_path):
    rows = [raw_row(), raw_row(claim="Cách nói khác."), raw_row(evidence="Câu thứ hai ở đây.")]
    built = build_evidence_corpus(write_raw(tmp_path, rows))
    assert len(built) == 2
    assert tuple(built.columns) == COLUMNS


def test_the_number_of_claims_per_sentence_is_recorded(tmp_path):
    """A sentence serving 42 claims is a different kind of object from one serving a single
    claim, and E08 may want to tell them apart."""
    rows = [raw_row(), raw_row(claim="Cách nói khác."), raw_row(claim="Cách nói thứ ba.")]
    built = build_evidence_corpus(write_raw(tmp_path, rows))
    # train has all three rows, dev and test repeat the first one.
    assert int(built["n_claims"].iloc[0]) == 5


def test_empty_evidence_is_left_out(tmp_path):
    rows = [raw_row(), raw_row(evidence="   ", claim="Không có bằng chứng.")]
    assert len(build_evidence_corpus(write_raw(tmp_path, rows))) == 1


def test_a_sentence_under_two_titles_gets_the_more_frequent_one(tmp_path):
    """35 real sentences appear under more than one article. The pick has to be deterministic
    or a rebuild would reshuffle them."""
    rows = [
        raw_row(title="Việt Nam"),
        raw_row(title="Việt Nam", claim="Cách nói khác."),
        raw_row(title="Hà Nội", claim="Cách nói thứ ba."),
    ]
    built = build_evidence_corpus(write_raw(tmp_path, rows))
    assert built["title"].iloc[0] == "Việt Nam"


def test_a_missing_split_file_is_reported(tmp_path):
    pd.DataFrame.from_records([raw_row()]).to_csv(tmp_path / "viwikifc_train.csv", index=False)
    with pytest.raises(FileNotFoundError, match="viwikifc_dev.csv"):
        build_evidence_corpus(tmp_path)


def test_a_changed_sentence_count_stops_the_run():
    with pytest.raises(ValueError, match="mục 8 docs/DATA.md"):
        check_expected(corpus())


def test_the_documented_numbers_are_the_ones_the_module_checks():
    assert EXPECTED_SENTENCES == 3814
    assert EXPECTED_ARTICLES == 73


# -- searching ----------------------------------------------------------------------------


def test_the_matching_sentence_ranks_first():
    index = EvidenceIndex(corpus())
    hits = index.search("Đồ đồng thời nhà Thương đạt trình độ chế tác cao", k=3)
    assert "nhà Thương" in hits[0].text


def test_search_returns_at_most_k_hits():
    assert len(EvidenceIndex(corpus()).search("Hà Nội", k=2)) == 2


def test_ranks_are_numbered_from_one_without_gaps():
    hits = EvidenceIndex(corpus()).search("sông", k=3)
    assert [hit.rank for hit in hits] == [1, 2, 3]


def test_scores_never_increase_down_the_ranking():
    hits = EvidenceIndex(corpus()).search("thành phố sông Việt Nam", k=4)
    assert all(a.score >= b.score for a, b in zip(hits, hits[1:], strict=False))


def test_excluded_sentences_do_not_come_back():
    """E08 needs to build a context that deliberately lacks the gold evidence — the setting
    where an extrinsic hallucination is the only honest answer."""
    pool = corpus()
    index = EvidenceIndex(pool)
    gold = index.search("Đồ đồng thời nhà Thương", k=1)[0].evidence_id
    hits = index.search("Đồ đồng thời nhà Thương", k=3, exclude={gold})
    assert gold not in {hit.evidence_id for hit in hits}
    assert len(hits) == 3


def test_a_query_of_only_punctuation_returns_nothing():
    assert EvidenceIndex(corpus()).search("!!! ???") == []


def test_asking_for_no_hits_is_rejected():
    with pytest.raises(ValueError, match="k phải >= 1"):
        EvidenceIndex(corpus()).search("Hà Nội", k=0)


def test_rank_of_finds_a_known_sentence():
    pool = corpus()
    index = EvidenceIndex(pool)
    wanted = pool["evidence_id"].iloc[2]
    assert index.rank_of("Đồ đồng thời nhà Thương chế tác cao", wanted) == 1


def test_rank_of_returns_nothing_beyond_the_limit():
    index = EvidenceIndex(corpus())
    assert index.rank_of("Đồ đồng nhà Thương", corpus()["evidence_id"].iloc[0], limit=1) is None


# -- index construction -------------------------------------------------------------------


def test_an_empty_pool_is_rejected():
    with pytest.raises(ValueError, match="rỗng"):
        EvidenceIndex(corpus().iloc[0:0])


def test_a_pool_missing_a_column_is_rejected():
    with pytest.raises(ValueError, match="thiếu cột"):
        EvidenceIndex(corpus().drop(columns=["title"]))


def test_a_missing_corpus_file_says_which_command_to_run(tmp_path):
    with pytest.raises(FileNotFoundError, match="build_evidence_corpus.py"):
        EvidenceIndex.from_parquet(tmp_path / "khong_ton_tai.parquet")
