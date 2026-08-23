"""The ViWikiFC evidence pool, and BM25 search over it.

ViWikiFC ships a very short ``context`` per claim — usually three or four sentences — and task
T15 measured the consequence: 15,3 % of its contexts collapse to a single chunk, where the
chunk-aware contribution degenerates into the aggregate lookback it is supposed to improve on.

Section 8 of docs/DATA.md is the answer. The whole corpus rests on only 3.814 distinct evidence
sentences drawn from 73 Wikipedia articles, few enough to hold in memory as a retrieval pool.
Experiment E08 then builds a real multi-passage context by retrieving the top-k sentences for a
claim, instead of using the short one that came with it.

The index itself is not persisted, only the pool: BM25 over a few thousand short documents is
rebuilt in well under a second, and a pickled index would be a version-fragile file holding
nothing that cannot be recomputed.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

CORPUS_FILENAME = "viwikifc_evidence_corpus.parquet"
COLUMNS = ("evidence_id", "text", "title", "link", "n_claims")

# Section 8 of docs/DATA.md, re-measured at T16.
EXPECTED_SENTENCES = 3814
EXPECTED_ARTICLES = 73

EVIDENCE_ID_LENGTH = 16

# Everything that is not a letter, a digit or whitespace. Vietnamese diacritics survive because
# the class is defined by what it keeps, not by an ASCII range.
_PUNCTUATION = re.compile(r"[^\w\s]", flags=re.UNICODE)


def evidence_id(text: str) -> str:
    """Stable identifier of an evidence sentence.

    Hashed from the text rather than numbered by position, so that the ids stay the same if the
    pool is ever rebuilt from a corpus whose rows arrive in a different order. Same construction
    as ``context_id`` in schema.py, for the same reason.
    """
    canonical = unicodedata.normalize("NFC", text).strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:EVIDENCE_ID_LENGTH]


def tokenize(text: str) -> list[str]:
    """Split text into the units BM25 counts.

    Vietnamese words are written as separate syllables — "Hà Nội" is two whitespace-separated
    pieces of one word — so splitting on whitespace yields syllables, not words. A proper word
    segmenter would group them, but that means a new dependency, and for retrieval the cost is
    small: BM25 scores a claim mentioning both syllables of a word higher anyway, because both
    appear in the same document. Recorded here because it is a real limitation, measured at T16
    rather than assumed away — see the recall figures in TASKS.md.
    """
    folded = unicodedata.normalize("NFC", text).lower()
    return _PUNCTUATION.sub(" ", folded).split()


@dataclass(frozen=True)
class Hit:
    """One retrieved evidence sentence."""

    evidence_id: str
    text: str
    title: str
    link: str
    score: float
    rank: int


def build_evidence_corpus(raw_dir: Path) -> pd.DataFrame:
    """Every distinct evidence sentence of ViWikiFC, from the raw CSVs.

    Read from ``data/raw`` rather than from the normalised Parquet on purpose. Task T11 clears
    the ``evidence`` column of any row whose evidence could not be located in its own context,
    and exactly one row is in that state — its evidence reads "NhậtaimBản" where the article
    reads "Nhật Bản". Building the pool from the normalised data would drop that sentence, and
    then the one claim it belongs to could never retrieve its own gold evidence, which would
    quietly cost experiment E08 a sample for a reason that has nothing to do with retrieval.

    A retrieval pool is a set of sentences to search, and whether an offset could be found for
    one of them is a different question entirely.
    """
    frames = []
    for split in ("train", "dev", "test"):
        path = Path(raw_dir) / f"viwikifc_{split}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"không thấy {path}")
        frames.append(pd.read_csv(path, dtype=str, keep_default_na=False))
    raw = pd.concat(frames, ignore_index=True)

    raw["evidence"] = raw["evidence"].str.strip()
    raw = raw[raw["evidence"] != ""]

    records = []
    for text, group in raw.groupby("evidence", sort=True):
        # 35 sentences appear under more than one article title. The most frequent one wins, with
        # the alphabetically first as a deterministic tie-break, so a rebuild cannot reshuffle
        # them. The schema of section 8 of docs/DATA.md carries one title per sentence.
        titles = group["title"].value_counts()
        title = sorted(titles[titles == titles.max()].index)[0]
        link = sorted(group.loc[group["title"] == title, "link"].unique())[0]
        records.append(
            {
                "evidence_id": evidence_id(text),
                "text": text,
                "title": title,
                "link": link,
                # How many claims this sentence is the evidence for. Kept because a sentence
                # serving 42 claims is a different kind of object from one serving a single
                # claim, and E08 may want to know.
                "n_claims": len(group),
            }
        )

    corpus = pd.DataFrame.from_records(records)[list(COLUMNS)]
    if corpus["evidence_id"].duplicated().any():
        raise ValueError("evidence_id trùng: hai câu khác nhau băm ra cùng một mã")
    return corpus.sort_values("evidence_id").reset_index(drop=True)


def check_expected(corpus: pd.DataFrame) -> None:
    """Compare against section 8 of docs/DATA.md and raise on any difference."""
    if len(corpus) != EXPECTED_SENTENCES:
        raise ValueError(
            f"kho có {len(corpus)} câu, mục 8 docs/DATA.md ghi {EXPECTED_SENTENCES}"
        )
    articles = corpus["title"].nunique()
    if articles != EXPECTED_ARTICLES:
        raise ValueError(
            f"kho lấy từ {articles} bài Wikipedia, mục 8 docs/DATA.md ghi {EXPECTED_ARTICLES}"
        )


class EvidenceIndex:
    """BM25 over the evidence pool.

    BM25 ranks a document by how many of the query's rarer terms it contains, discounting terms
    that appear everywhere and normalising for document length. It needs no training and no GPU,
    which is why section 8 of docs/DATA.md chose it: the point of E08 is what attention does with
    a multi-passage context, not how good the retriever is.
    """

    def __init__(self, corpus: pd.DataFrame) -> None:
        from rank_bm25 import BM25Okapi

        missing = [column for column in COLUMNS if column not in corpus.columns]
        if missing:
            raise ValueError(f"kho thiếu cột: {', '.join(missing)}")
        if corpus.empty:
            raise ValueError("kho rỗng")

        self.corpus = corpus.reset_index(drop=True)
        self._tokens = [tokenize(text) for text in self.corpus["text"]]
        self._bm25 = BM25Okapi(self._tokens)

    @classmethod
    def from_parquet(cls, path: Path | str) -> EvidenceIndex:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(
                f"không thấy {path}. Chạy trước: python scripts/build_evidence_corpus.py"
            )
        return cls(pd.read_parquet(path))

    def __len__(self) -> int:
        return len(self.corpus)

    def search(self, query: str, k: int = 5, exclude: set[str] | None = None) -> list[Hit]:
        """The ``k`` highest-scoring evidence sentences for a claim.

        ``exclude`` drops sentences by id before ranking is reported, which is how E08 will be
        able to build a context that deliberately does *not* contain the gold evidence — the
        setting where an extrinsic hallucination is the only honest answer.
        """
        if k < 1:
            raise ValueError(f"k phải >= 1, nhận {k}")
        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self._bm25.get_scores(tokens)
        order = scores.argsort()[::-1]

        hits: list[Hit] = []
        for position in order:
            row = self.corpus.iloc[position]
            if exclude and row["evidence_id"] in exclude:
                continue
            hits.append(
                Hit(
                    evidence_id=row["evidence_id"],
                    text=row["text"],
                    title=row["title"],
                    link=row["link"],
                    score=float(scores[position]),
                    rank=len(hits) + 1,
                )
            )
            if len(hits) == k:
                break
        return hits

    def rank_of(self, query: str, wanted_id: str, limit: int = 100) -> int | None:
        """Where a known sentence lands for a query, or ``None`` beyond ``limit``.

        Used to measure recall@k: how often the gold evidence is actually retrievable at all is
        the number that says whether E08 can be run on this pool.
        """
        for hit in self.search(query, k=limit):
            if hit.evidence_id == wanted_id:
                return hit.rank
        return None
