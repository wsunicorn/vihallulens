"""Task T16: build the ViWikiFC evidence pool and check that BM25 can actually find things in it.

Section 8 of docs/DATA.md asks for the pool. The recall measurement is the part that decides
whether experiment E08 is possible at all: if BM25 cannot retrieve a claim's own gold evidence
from 3.814 candidates, then a retrieved context would rarely contain the answer and E08 would be
measuring the retriever rather than the attention signal.

Usage:
    python scripts/build_evidence_corpus.py
    python scripts/build_evidence_corpus.py --sample 2000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_all_splits  # noqa: E402
from vihallulens.data.paths import find_raw_dir  # noqa: E402
from vihallulens.data.retrieval import (  # noqa: E402
    CORPUS_FILENAME,
    EvidenceIndex,
    build_evidence_corpus,
    check_expected,
    evidence_id,
)

RECALL_AT = (1, 5, 10, 20, 50)
DEMO_CLAIMS = 3


def measure_recall(index: EvidenceIndex, claims: pd.DataFrame) -> dict[int, float]:
    """How often a claim's own gold evidence appears in the top k of its retrieval.

    This is the honest version of "trả về top-5 hợp lý": eyeballing three results says nothing,
    while recall over a couple of thousand claims says whether the pool is usable.
    """
    ranks: list[int | None] = []
    started = time.perf_counter()
    for position, (_, row) in enumerate(claims.iterrows(), start=1):
        ranks.append(index.rank_of(row["response"], row["gold_id"], limit=max(RECALL_AT)))
        if position % 200 == 0:
            print(f"    {position}/{len(claims)}", end="\r")
    print(f"    xong {len(claims)} truy vấn trong {time.perf_counter() - started:.0f} s")
    return {
        k: sum(1 for rank in ranks if rank is not None and rank <= k) / len(ranks)
        for k in RECALL_AT
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="T16: dựng kho truy xuất ViWikiFC.")
    parser.add_argument("--raw-dir", type=Path, default=None)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    parser.add_argument("--sample", type=int, default=2000, help="số claim để đo recall")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    raw_dir = find_raw_dir(args.raw_dir)
    print()
    print("=" * 80)
    print("T16 — KHO TRUY XUẤT VIWIKIFC")
    print("=" * 80)
    print(f"  nguồn                 : {raw_dir}")

    corpus = build_evidence_corpus(raw_dir)
    check_expected(corpus)

    args.interim_dir.mkdir(parents=True, exist_ok=True)
    path = args.interim_dir / CORPUS_FILENAME
    corpus.to_parquet(path, index=False)

    words = corpus["text"].str.split().str.len()
    print(f"  câu bằng chứng        : {len(corpus):,}")
    print(f"  bài Wikipedia         : {corpus['title'].nunique()}")
    print(f"  độ dài câu (từ)       : trung vị {int(words.median())}, "
          f"trung bình {words.mean():.1f}, dài nhất {words.max()}")
    print(f"  claim mỗi câu         : trung bình {corpus['n_claims'].mean():.1f}, "
          f"tối đa {corpus['n_claims'].max()}")
    print(f"  đã ghi                : {path}")

    started = time.perf_counter()
    index = EvidenceIndex(corpus)
    print(f"  dựng chỉ mục BM25     : {time.perf_counter() - started:.2f} s")

    # -- the sanity query the task asks for ------------------------------------------------
    frame = pd.concat(load_all_splits("viwikifc", args.interim_dir).values(), ignore_index=True)
    frame["title"] = frame["meta"].map(lambda value: json.loads(value)["title"])
    with_evidence = frame[frame["evidence"].str.strip() != ""].copy()
    with_evidence["gold_id"] = with_evidence["evidence"].str.strip().map(evidence_id)

    print()
    print("-" * 80)
    print("TRUY VẤN THỬ")
    print("-" * 80)
    for _, row in with_evidence.sample(n=DEMO_CLAIMS, random_state=42).iterrows():
        print(f"\n  claim : {row['response'][:100]}")
        print(f"  nhãn  : {row['label']}  ·  bài: {row['title']}")
        gold = row["gold_id"]
        for hit in index.search(row["response"], k=5):
            mark = " ← BẰNG CHỨNG VÀNG" if hit.evidence_id == gold else ""
            print(f"    {hit.rank}. [{hit.score:5.1f}] {hit.text[:82]}{mark}")

    # -- recall, the number that decides whether E08 is possible ----------------------------
    sample = with_evidence.sample(
        n=min(args.sample, len(with_evidence)), random_state=42
    )
    print()
    print("-" * 80)
    print(f"RECALL BẰNG CHỨNG VÀNG — {len(sample):,} claim, seed 42")
    print("-" * 80)
    recall = measure_recall(index, sample)
    for k, value in recall.items():
        print(f"  recall@{k:<3}: {value * 100:5.1f} %")

    print()
    if recall[10] >= 0.7:
        print("  Kho dùng được cho E08: bằng chứng vàng nằm trong top-10 ở đa số truy vấn,")
        print("  nên ngữ cảnh ghép từ top-k sẽ thường chứa câu trả lời.")
    else:
        print("  CẢNH BÁO: recall@10 thấp. Ngữ cảnh ghép từ top-k sẽ thường KHÔNG chứa bằng")
        print("  chứng vàng, và E08 sẽ đo chất lượng bộ truy xuất chứ không đo tín hiệu chú ý.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
