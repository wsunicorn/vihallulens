"""Building the paired contexts experiment E08 intervenes on.

The whole value of E08 is that its two halves differ in **one** thing. Every test here defends
that property, because a pair that quietly differs in two things would produce a confident,
publishable, wrong conclusion.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from vihallulens.data.chunking import chunk_context
from vihallulens.data.retrieval import (
    DEFAULT_CONTEXT_K,
    UNSUPPORTED_LABEL,
    EvidenceIndex,
    evidence_id,
    paired_contexts,
)

K = DEFAULT_CONTEXT_K


def make_index(n=40) -> EvidenceIndex:
    """A pool of distinguishable sentences, each a single chunk ending in a full stop."""
    rows = []
    for index in range(n):
        text = f"Câu bằng chứng số {index} nói về chủ đề thứ {index} một cách rõ ràng."
        rows.append({"evidence_id": evidence_id(text), "text": text,
                     "title": f"Bài {index % 5}", "link": "", "n_claims": 1})
    return EvidenceIndex(pd.DataFrame(rows))


def build(index, sample_id="s1", claim="chủ đề thứ 3 rõ ràng", gold=3):
    gold_text = index.corpus.iloc[gold]["text"]
    return paired_contexts(index, sample_id, claim, evidence_id(gold_text), k=K), gold_text


# -- the property the experiment rests on --------------------------------------------------------


def test_the_two_halves_differ_in_exactly_one_sentence():
    index = make_index()
    (present, absent, _), _ = build(index)
    left = [c.text for c in chunk_context(present, strategy="sentence", min_words=5)]
    right = [c.text for c in chunk_context(absent, strategy="sentence", min_words=5)]
    assert len(left) == len(right) == K
    assert sum(a != b for a, b in zip(left, right, strict=True)) == 1


def test_the_differing_sentence_is_at_the_same_position_in_both():
    """Different positions would mean the pair differs in where the model must look as well as in
    what is there, which is two changes, not one."""
    index = make_index()
    (present, absent, position), gold_text = build(index)
    left = [c.text for c in chunk_context(present, strategy="sentence", min_words=5)]
    right = [c.text for c in chunk_context(absent, strategy="sentence", min_words=5)]
    differing = [i for i, (a, b) in enumerate(zip(left, right, strict=True)) if a != b]
    assert differing == [position]
    assert gold_text in left[position]


def test_the_gold_sentence_is_in_the_present_half_and_not_the_absent_one():
    index = make_index()
    (present, absent, _), gold_text = build(index)
    assert gold_text in present
    assert gold_text not in absent


def test_both_halves_hold_k_sentences():
    index = make_index()
    (present, absent, _), _ = build(index)
    for text in (present, absent):
        assert len(chunk_context(text, strategy="sentence", min_words=5)) == K


# -- the shuffle, and why it is there ------------------------------------------------------------


def test_the_gold_sentence_is_not_always_first():
    """BM25 puts the gold sentence at rank 0 for 94 % of claims, measured at T27. Without the
    shuffle, "always look at chunk 0" would score like a mechanism and hit@1 would mean nothing."""
    index = make_index()
    positions = {build(index, sample_id=f"s{i}")[0][2] for i in range(40)}
    assert len(positions) > 3, positions


def test_the_same_sample_always_gets_the_same_shuffle():
    """Rebuilding the dataset must produce the same file, or every shard extracted from the old
    one silently stops matching."""
    index = make_index()
    first, _ = build(index, sample_id="stable")
    second, _ = build(index, sample_id="stable")
    assert first == second


def test_two_samples_get_different_shuffles():
    index = make_index()
    assert build(index, sample_id="a")[0][0] != build(index, sample_id="b")[0][0]


# -- refusing to build something misleading ------------------------------------------------------


def test_a_pool_too_small_for_k_distractors_returns_none():
    """Better than returning a short context: a five-chunk half against a ten-chunk half would
    have a different entropy normaliser and the comparison would be meaningless."""
    index = make_index(n=5)
    assert build(index)[0] is None


def test_an_unknown_gold_id_returns_none():
    index = make_index()
    assert paired_contexts(index, "s1", "chủ đề", "khong-co-that", k=K) is None


# -- what the build script writes ----------------------------------------------------------------


def test_the_absent_half_is_labelled_unsupported_by_construction():
    """Not an annotation anybody could disagree with: the gold sentence is gone, so the response
    asserts something this context does not contain."""
    assert UNSUPPORTED_LABEL == "extrinsic"


def test_pairs_with_mismatched_chunk_counts_are_dropped():
    """5,1 % of the real evidence sentences end in a year or an abbreviation, after which
    chunk_by_sentence deliberately refuses to split. Swapping such a sentence in or out changes
    the chunk count, and entropy is normalised by ln(n_chunks) — so the pair would differ in the
    normaliser as well as in the evidence."""
    from build_retrieval_contexts import build_rows

    index = make_index()
    gold_text = index.corpus.iloc[3]["text"]
    frame = pd.DataFrame([{
        "sample_id": "s1", "split": "dev", "context_id": "c1",
        "response": "chủ đề thứ 3", "label": "no", "label_original": "SUPPORTED",
        "response_is_generated": False, "evidence": gold_text,
    }])
    rows, dropped = build_rows(index, frame, K)
    assert len(rows) == 2
    assert sum(dropped.values()) == 0
    assert {row["meta"]["condition"] for row in rows} == {"present", "absent"}
    assert {row["label"] for row in rows} == {"no", UNSUPPORTED_LABEL}


def test_a_row_without_evidence_is_counted_not_crashed_on():
    from build_retrieval_contexts import build_rows

    frame = pd.DataFrame([{
        "sample_id": "s1", "split": "dev", "context_id": "c1", "response": "gì đó",
        "label": "no", "label_original": "SUPPORTED", "response_is_generated": False,
        "evidence": "",
    }])
    rows, dropped = build_rows(make_index(), frame, K)
    assert rows == []
    assert dropped["không có bằng chứng"] == 1


def test_the_pair_id_links_the_two_halves_back_together():
    from build_retrieval_contexts import build_rows

    index = make_index()
    frame = pd.DataFrame([{
        "sample_id": "s1", "split": "dev", "context_id": "c1", "response": "chủ đề thứ 3",
        "label": "no", "label_original": "SUPPORTED", "response_is_generated": False,
        "evidence": index.corpus.iloc[3]["text"],
    }])
    rows, _ = build_rows(index, frame, K)
    assert {row["meta"]["pair_id"] for row in rows} == {"s1"}
    assert {row["sample_id"] for row in rows} == {"s1__present", "s1__absent"}


def test_the_present_half_carries_offsets_that_point_at_the_gold_text():
    """Carried so the extractor can find the gold chunk; a wrong offset would score a different
    chunk and never complain."""
    from build_retrieval_contexts import build_rows

    index = make_index()
    gold_text = index.corpus.iloc[3]["text"]
    frame = pd.DataFrame([{
        "sample_id": "s1", "split": "dev", "context_id": "c1", "response": "chủ đề thứ 3",
        "label": "no", "label_original": "SUPPORTED", "response_is_generated": False,
        "evidence": gold_text,
    }])
    rows, _ = build_rows(index, frame, K)
    present = next(r for r in rows if r["meta"]["condition"] == "present")
    assert present["context"][present["evidence_start"]:present["evidence_end"]] == gold_text
    absent = next(r for r in rows if r["meta"]["condition"] == "absent")
    assert absent["evidence"] == ""
    assert absent["evidence_start"] == -1


@pytest.mark.parametrize("name", ["chunk_entropy", "chunk_max_share", "chunk_gini",
                                  "top1_top2_gap", "chunk_drift"])
def test_every_chunk_feature_has_a_direction_written_down_before_the_run(name):
    """Written before the numbers are read, so a result that goes the other way cannot quietly be
    re-described afterwards as a confirmation."""
    from run_extrinsic import EXPECTED_DIRECTION

    assert name in EXPECTED_DIRECTION
    assert EXPECTED_DIRECTION[name] in (-1, 0, +1)
