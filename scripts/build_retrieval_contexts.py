"""Task T27: build the paired retrieved contexts experiment E08 runs on.

    python scripts/build_retrieval_contexts.py --split dev

Every other experiment in this thesis is correlational: a signal is measured, a label somebody
else assigned is compared against it, and agreement is reported. This one intervenes. For each
ViWikiFC claim it builds **two** contexts from the same evidence pool, differing in exactly one
sentence — one holding the gold evidence, one with a distractor in its place — and asks whether
the attention signal moves the way the mechanism says it should when the answer is taken away.

Why ViWikiFC and not the other corpora: it is the only one whose NEI class **has** evidence
(measured at T11, 100 % verbatim), and the only one small enough — 3.814 unique sentences from 73
Wikipedia articles — to serve as its own retrieval pool. Section 8 of docs/DATA.md plans this.

The absent half is labelled ``extrinsic`` for every row, and that is not an annotation, it is a
fact about how the row was made: the response asserts something the context does not contain.
Any label a person could disagree with has been removed from the experiment.

Writes ``data/interim/viwikifc_e08_{split}.parquet``. CPU only, about two minutes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vihallulens.data.chunking import chunk_context  # noqa: E402
from vihallulens.data.loading import DEFAULT_INTERIM_DIR, load_dataset  # noqa: E402
from vihallulens.data.retrieval import (  # noqa: E402
    CORPUS_FILENAME,
    DEFAULT_CONTEXT_K,
    UNSUPPORTED_LABEL,
    EvidenceIndex,
    evidence_id,
    paired_contexts,
)
from vihallulens.data.schema import NO_OFFSET  # noqa: E402

PRESENT, ABSENT = "present", "absent"


def cut(text: str) -> list[str]:
    return [chunk.text for chunk in chunk_context(text, strategy="sentence", min_words=5)]


def differing_chunks(present: str, absent: str) -> int | None:
    """How many chunks the two halves disagree on, or ``None`` if they have different counts.

    Checked directly rather than inferred from the chunk counts. Equal counts are **not** enough:
    the gold sentence can merge with its neighbour on one side while the distractor merges the
    other way, shifting two boundaries and leaving the total unchanged. Measured at T27, that
    happens to 5 of 1.841 otherwise-valid pairs — 0,3 %, small enough to miss and large enough to
    weaken the one property the whole experiment rests on.
    """
    left, right = cut(present), cut(absent)
    if len(left) != len(right):
        return None
    return sum(a != b for a, b in zip(left, right, strict=True))


def build_rows(index: EvidenceIndex, frame: pd.DataFrame, k: int) -> tuple[list[dict], dict]:
    """One pair of rows per usable claim, plus a count of why the others were dropped.

    A pair is kept only when its two halves cut into the same number of chunks **and disagree on
    exactly one of them**. That is the single property the experiment rests on, so it is built in
    rather than hoped for.

    Both halves of the check earn their place. 5,1 % of the evidence sentences end in a year or an
    abbreviation, after which :func:`chunk_by_sentence` deliberately refuses to split — in ordinary
    prose that full stop is not a sentence end. Swapping such a sentence in or out changes the
    chunk count, and entropy is normalised by ``ln(n_chunks)``, so the normaliser itself would move.
    And equal counts alone are not enough: the gold can merge one way while the distractor merges
    the other, shifting two boundaries and leaving the total unchanged.

    Measured at T27: 87,2 % survive the count check, and 5 of those 1.841 still disagree on two
    chunks. Those five are dropped too.
    """
    corpus_ids = set(index.corpus["evidence_id"])
    rows: list[dict] = []
    dropped = {"không có bằng chứng": 0, "bằng chứng ngoài kho": 0,
               "kho không đủ câu nhiễu": 0, "hai vế lệch số đoạn": 0,
               "khác nhau hơn một đoạn": 0}

    for record in frame.to_dict("records"):
        gold_text = (record.get("evidence") or "").strip()
        if not gold_text:
            dropped["không có bằng chứng"] += 1
            continue
        gold_id = evidence_id(gold_text)
        if gold_id not in corpus_ids:
            dropped["bằng chứng ngoài kho"] += 1
            continue

        built = paired_contexts(index, record["sample_id"], record["response"], gold_id, k=k)
        if built is None:
            dropped["kho không đủ câu nhiễu"] += 1
            continue
        present, absent, position = built
        differing = differing_chunks(present, absent)
        if differing is None:
            dropped["hai vế lệch số đoạn"] += 1
            continue
        if differing != 1:
            dropped["khác nhau hơn một đoạn"] += 1
            continue

        shared = {
            "dataset": "viwikifc_e08",
            "split": record["split"],
            "question": "",
            "response": record["response"],
            "label_original": record["label_original"],
            "response_is_generated": record["response_is_generated"],
        }
        # Real offsets into the built context, not the sentinel: the gold sentence is genuinely
        # in the present half, and schema validation rejects a start without an end anyway.
        start = present.find(gold_text)
        end = start + len(gold_text) if start >= 0 else NO_OFFSET
        rows.append({
            **shared,
            "sample_id": f"{record['sample_id']}__{PRESENT}",
            "context": present,
            "context_id": f"{record['context_id']}__{PRESENT}",
            "label": record["label"],
            # Carried so the extractor can locate the gold chunk and record its rank, which is
            # what lets E08 double as an external check on E06's localisation result.
            "evidence": gold_text,
            "evidence_start": start if start >= 0 else NO_OFFSET,
            "evidence_end": end if start >= 0 else NO_OFFSET,
            "meta": {"condition": PRESENT, "gold_position": position,
                     "pair_id": record["sample_id"]},
        })
        rows.append({
            **shared,
            "sample_id": f"{record['sample_id']}__{ABSENT}",
            "context": absent,
            "context_id": f"{record['context_id']}__{ABSENT}",
            # Not an annotation — a fact about construction. The gold sentence is gone, so the
            # response is unsupported by this context whatever it was before.
            "label": UNSUPPORTED_LABEL,
            "evidence": "",
            # No evidence in this half by construction, so the sentinel is the honest value.
            "evidence_start": NO_OFFSET,
            "evidence_end": NO_OFFSET,
            "meta": {"condition": ABSENT, "gold_position": position,
                     "pair_id": record["sample_id"]},
        })
    return rows, dropped


def main() -> int:
    parser = argparse.ArgumentParser(description="T27: dựng ngữ cảnh truy xuất theo cặp cho E08.")
    parser.add_argument("--split", default="dev", choices=("train", "dev", "test"))
    parser.add_argument("--k", type=int, default=DEFAULT_CONTEXT_K)
    parser.add_argument("--interim-dir", type=Path, default=DEFAULT_INTERIM_DIR)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    index = EvidenceIndex.from_parquet(Path(args.interim_dir) / CORPUS_FILENAME)
    frame = load_dataset("viwikifc", args.split, args.interim_dir)

    print()
    print("=" * 80)
    print("T27 — DỰNG NGỮ CẢNH TRUY XUẤT THEO CẶP CHO E08")
    print("=" * 80)
    print(f"  kho truy xuất         : {len(index):,} câu bằng chứng")
    print(f"  nguồn                 : viwikifc/{args.split}, {len(frame):,} mẫu")
    print(f"  câu mỗi ngữ cảnh      : {args.k}")

    rows, dropped = build_rows(index, frame, args.k)
    kept = len(rows) // 2
    print(f"  dựng được             : {kept:,} cặp = {len(rows):,} dòng "
          f"({kept / len(frame):.1%} số mẫu nguồn)")
    for reason, count in dropped.items():
        if count:
            print(f"    bỏ, {reason:<22}: {count:,}")

    if not rows:
        print("\nKhông dựng được cặp nào. Kiểm lại kho truy xuất.")
        return 1

    out = pd.DataFrame(rows)
    counts = [len(cut(text)) for text in out["context"]]
    print(f"  số đoạn mỗi ngữ cảnh  : trung bình {sum(counts) / len(counts):.1f}, "
          f"nhỏ nhất {min(counts)}, lớn nhất {max(counts)}")
    print(f"  nhãn nửa 'present'    : "
          f"{dict(out[out['meta'].str['condition'] == PRESENT]['label'].value_counts())}")
    print(f"  nhãn nửa 'absent'     : tất cả {UNSUPPORTED_LABEL} theo cách dựng")

    path = Path(args.interim_dir) / f"viwikifc_e08_{args.split}.parquet"
    out.to_parquet(path, index=False)
    print(f"  đã ghi                : {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
