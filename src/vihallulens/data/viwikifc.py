"""Normalise ViWikiFC into the common schema.

ViWikiFC is the only one of the four corpora that names an evidence sentence for the
"not enough information" label as well as for the other two. Everywhere else NEI simply has no
evidence, which makes the extrinsic class impossible to study directly; here it can be. That is
what experiment E08 rests on, and why this corpus is the outside control.

Section 7 of docs/DATA.md specifies the mapping. The original train/dev/test split is kept, so
results stay comparable with the numbers published for this corpus.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from vihallulens.data.schema import (
    context_id,
    encode_meta,
    finalise,
    find_evidence,
    sample_id,
)

DATASET = "viwikifc"
SPLITS = ("train", "dev", "test")

# Section 3 of docs/DATA.md.
LABEL_MAP = {
    "Supports": "no",
    "Refutes": "intrinsic",
    "Not_Enough_Information": "extrinsic",
}

# Row counts from section 4 of docs/DATA.md; label counts measured at T11. The train row of
# this table is the one docs/DATA.md already published; dev and test are recorded here so a
# changed release fails on all three splits rather than only on the largest.
EXPECTED = {
    "train": {"rows": 16738, "no": 5594, "intrinsic": 5573, "extrinsic": 5571},
    "dev": {"rows": 2090, "no": 666, "intrinsic": 694, "extrinsic": 730},
    "test": {"rows": 2091, "no": 708, "intrinsic": 706, "extrinsic": 677},
}

# Measured at T11: 20.918 of 20.919 evidence sentences are present verbatim. The single miss is
# a train row whose evidence reads "NhậtaimBản" where its own context reads "Nhật Bản" — three
# stray letters spliced over a space, a defect in the published corpus rather than an encoding
# problem on our side, since every other row matches exactly.
#
# The guard fires on *more* misses than this, not on a different number: an encoding fault would
# push the count into the thousands, while fewer misses could only mean the corpus was repaired,
# and refusing to run on a repaired corpus would be perverse.
EXPECTED_EVIDENCE_MISSES = 1


def source_file(split: str) -> str:
    return f"{DATASET}_{split}.csv"


def normalize_viwikifc(raw_dir: Path) -> pd.DataFrame:
    """Read all three splits, check them against the documented counts, and return them."""
    frame = read_viwikifc(raw_dir)
    check_expected(frame)
    return frame


def read_viwikifc(raw_dir: Path) -> pd.DataFrame:
    """Read the three ViWikiFC CSVs and return them in the common schema, split column kept."""
    records = []
    for split in SPLITS:
        source = Path(raw_dir) / source_file(split)
        if not source.is_file():
            raise FileNotFoundError(f"không thấy {source}")

        raw = pd.read_csv(source, dtype=str, keep_default_na=False)
        expected_columns = {"pairID", "evidence", "gold_label", "link", "context",
                            "sentenceID", "claim", "title"}
        missing = expected_columns - set(raw.columns)
        if missing:
            raise ValueError(f"{source.name} thiếu cột: {', '.join(sorted(missing))}")

        for index, row in enumerate(raw.itertuples(index=False)):
            gold = str(row.gold_label)
            if gold not in LABEL_MAP:
                raise ValueError(f"{source.name} dòng {index} có gold_label lạ: {gold!r}")

            context = str(row.context)
            evidence = str(row.evidence)
            start, end = find_evidence(context, evidence)
            records.append(
                {
                    "sample_id": sample_id(DATASET, split, index),
                    "dataset": DATASET,
                    "split": split,
                    "context": context,
                    "context_id": context_id(context),
                    # A fact-checking corpus: a claim to judge, no question.
                    "question": "",
                    "response": str(row.claim),
                    "label": LABEL_MAP[gold],
                    "label_original": gold,
                    "evidence": evidence if start >= 0 else "",
                    "evidence_start": start,
                    "evidence_end": end,
                    "response_is_generated": False,
                    "meta": encode_meta(
                        {
                            # pairID identifies an (evidence, label) pair, NOT a sample: 835
                            # train rows share one with a different claim. Anything treating it
                            # as a key would silently collapse those rows together.
                            "source_id": str(row.pairID),
                            "title": str(row.title),
                            "link": str(row.link),
                            "sentence_id": str(row.sentenceID),
                            "evidence_given": bool(evidence.strip()),
                        }
                    ),
                }
            )

    return finalise(pd.DataFrame.from_records(records))


def check_expected(frame: pd.DataFrame) -> None:
    """Both guards: the documented counts, then the evidence match rate."""
    check_counts(frame)
    check_evidence(frame)


def check_counts(frame: pd.DataFrame) -> None:
    """Compare each split against its documented row and label counts."""
    for split, expected in EXPECTED.items():
        part = frame[frame["split"] == split]
        if len(part) != expected["rows"]:
            raise ValueError(
                f"ViWikiFC {split} có {len(part)} dòng, mục 4 docs/DATA.md ghi {expected['rows']}"
            )
        counts = part["label"].value_counts().to_dict()
        wanted = {key: value for key, value in expected.items() if key != "rows"}
        if counts != wanted:
            raise ValueError(f"ViWikiFC {split}: phân bố nhãn {counts} khác {wanted}")


def check_evidence(frame: pd.DataFrame) -> None:
    """Check that essentially every evidence sentence was located.

    This is the guard that matters for this corpus. Section 7 of docs/DATA.md warns that a
    shortfall here means an encoding fault, and an encoding fault would not damage a handful
    of rows — it would damage thousands, silently, while every count above still looked right.
    """
    misses = int((frame["evidence_start"] < 0).sum())
    if misses > EXPECTED_EVIDENCE_MISSES:
        raise ValueError(
            f"ViWikiFC có {misses} mẫu không định vị được bằng chứng, T11 đo được "
            f"{EXPECTED_EVIDENCE_MISSES}. Mục 7 docs/DATA.md bảo dừng lại kiểm tra encoding "
            f"chứ không chạy tiếp."
        )
