"""Normalise ViFactCheck into the common schema.

The reserve corpus, used only for the optional domain-transfer experiment E17. Section 7 of
docs/DATA.md specifies the mapping, and warns that only about 59 % of its evidence is present
verbatim — normal for this corpus, not a fault. Task T12 found out why: see EVIDENCE_RATE_BAND.

The original train/dev/test split is kept, so results stay comparable with published numbers.
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

DATASET = "vifactcheck"
SPLITS = ("train", "dev", "test")

# Section 3 of docs/DATA.md. The source stores these as integers, not strings.
LABEL_MAP = {0: "no", 1: "intrinsic", 2: "extrinsic"}

# Row counts from section 4 of docs/DATA.md; label counts measured at T12.
EXPECTED = {
    "train": {"rows": 5062, "no": 1751, "intrinsic": 1658, "extrinsic": 1653},
    "dev": {"rows": 723, "no": 256, "intrinsic": 244, "extrinsic": 223},
    "test": {"rows": 1447, "no": 508, "intrinsic": 468, "extrinsic": 471},
}

# Measured at T12: 4.296 of 7.232 rows, or 59,4 %, matching the 59,2 % of section 4 of
# docs/DATA.md. Checked as a band rather than an exact count because the figure is a property
# of how the corpus was annotated, not a checksum; what a band still catches is the case where
# the rate collapses, which would mean the columns were mismatched.
EVIDENCE_RATE_BAND = (0.55, 0.65)


def source_file(split: str) -> str:
    return f"{DATASET}_{split}.parquet"


def normalize_vifactcheck(raw_dir: Path) -> pd.DataFrame:
    """Read all three splits, check them against the documented counts, and return them."""
    frame = read_vifactcheck(raw_dir)
    check_expected(frame)
    return frame


def read_vifactcheck(raw_dir: Path) -> pd.DataFrame:
    """Read the three ViFactCheck Parquet files and return them in the common schema."""
    records = []
    for split in SPLITS:
        source = Path(raw_dir) / source_file(split)
        if not source.is_file():
            raise FileNotFoundError(f"không thấy {source}")

        raw = pd.read_parquet(source)
        # "Unnamed: 0" is a saved row number, 0..n-1, carrying no information. Section 7 of
        # docs/DATA.md says to drop it; the schema would reject it as a stray column anyway.
        raw = raw.drop(columns=["Unnamed: 0"], errors="ignore")

        expected_columns = {"Statement", "Context", "Topic", "Author", "labels", "Evidence"}
        missing = expected_columns - set(raw.columns)
        if missing:
            raise ValueError(f"{source.name} thiếu cột: {', '.join(sorted(missing))}")

        for index, row in enumerate(raw.itertuples(index=False)):
            try:
                label = LABEL_MAP[int(row.labels)]
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"{source.name} dòng {index} có labels lạ: {row.labels!r}"
                ) from error

            context = str(row.Context)
            evidence = str(row.Evidence)
            start, end = find_evidence(context, evidence)
            records.append(
                {
                    "sample_id": sample_id(DATASET, split, index),
                    "dataset": DATASET,
                    "split": split,
                    "context": context,
                    "context_id": context_id(context),
                    # A fact-checking corpus: a statement to judge, no question.
                    "question": "",
                    "response": str(row.Statement),
                    "label": label,
                    "label_original": str(int(row.labels)),
                    "evidence": evidence if start >= 0 else "",
                    "evidence_start": start,
                    "evidence_end": end,
                    "response_is_generated": False,
                    "meta": encode_meta(
                        {
                            # Not unique: 5.062 train rows share 1.250 annotation_id values,
                            # the same trap as pairID in ViWikiFC. The key is sample_id.
                            "source_id": str(getattr(row, "annotation_id", "")),
                            # Kept verbatim. The column mixes cases and spellings — "Thể thao"
                            # beside "THỂ THAO", "Văn hoá" beside "Văn hóa" — so anything
                            # slicing by topic has to fold them first. Normalising here would
                            # lose the ability to trace a row back to its source.
                            "topic": str(row.Topic),
                            "author": str(row.Author),
                            "url": str(getattr(row, "Url", "")),
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
                f"ViFactCheck {split} có {len(part)} dòng, mục 4 docs/DATA.md ghi "
                f"{expected['rows']}"
            )
        counts = part["label"].value_counts().to_dict()
        wanted = {key: value for key, value in expected.items() if key != "rows"}
        if counts != wanted:
            raise ValueError(f"ViFactCheck {split}: phân bố nhãn {counts} khác {wanted}")


def check_evidence(frame: pd.DataFrame) -> None:
    """Check the verbatim-evidence rate is still around the documented 59 %.

    A low rate is expected here and is not an error. A rate near zero would be, because it is
    what mismatched columns look like: reading the statement as the evidence, or the wrong
    corpus entirely, both produce almost no matches while every count above still looks right.
    """
    rate = float((frame["evidence_start"] >= 0).mean())
    low, high = EVIDENCE_RATE_BAND
    if not low <= rate <= high:
        raise ValueError(
            f"ViFactCheck có {rate * 100:.1f} % bằng chứng nguyên văn, mục 4 docs/DATA.md ghi "
            f"khoảng 59 %. Ngoài dải {low * 100:.0f}–{high * 100:.0f} % nghĩa là đọc nhầm cột "
            f"hoặc nhầm bộ dữ liệu."
        )
