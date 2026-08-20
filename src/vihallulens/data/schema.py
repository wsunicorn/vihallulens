"""The common schema all four corpora are normalised into.

Section 1 of docs/DATA.md defines the columns. This module owns them in one place so the four
readers cannot drift apart: every one of them ends by handing its frame to :func:`finalise`,
which fixes the column order, the dtypes and the invariants.

Validation runs at write time on purpose. A corpus that quietly loses its labels, or that
carries a null where a model expects a string, is far cheaper to catch here than three weeks
later inside a training loop.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from typing import Any

import pandas as pd

DATASETS = ("vihallu", "isedsc01", "viwikifc", "vifactcheck")
SPLITS = ("train", "dev", "test")
LABELS = ("no", "intrinsic", "extrinsic")

# Column order of the normalised frame, exactly as section 1 of docs/DATA.md lists it.
COLUMNS = (
    "sample_id",
    "dataset",
    "split",
    "context",
    "context_id",
    "question",
    "response",
    "label",
    "label_original",
    "evidence",
    "evidence_start",
    "evidence_end",
    "response_is_generated",
    "meta",
)

# Columns that may never be empty. ``question`` and ``evidence`` are absent for whole corpora,
# so they are allowed to be the empty string, but never null.
REQUIRED_NON_EMPTY = ("sample_id", "dataset", "split", "context", "context_id", "response",
                      "label", "label_original", "meta")

# Sentinel for "this corpus has no evidence offsets", per section 1 of docs/DATA.md.
NO_OFFSET = -1

CONTEXT_ID_LENGTH = 16


def context_id(context: str) -> str:
    """Stable identifier of a context, used to group samples when splitting.

    The text is normalised to NFC before hashing. Vietnamese diacritics can be stored either
    precomposed (``ế`` as one code point) or decomposed (``e`` plus two combining marks), and
    the two render identically. Without normalising, the same context arriving in two forms
    would produce two ids, land in different splits, and leak the context from train to test —
    precisely the failure that grouping is meant to prevent.
    """
    canonical = unicodedata.normalize("NFC", context).strip()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:CONTEXT_ID_LENGTH]


def sample_id(dataset: str, split: str, index: int) -> str:
    """``{dataset}_{split}_{index}``, the format fixed by section 1 of docs/DATA.md."""
    return f"{dataset}_{split}_{index}"


def encode_meta(payload: dict[str, Any]) -> str:
    """Corpus-specific fields as a JSON string.

    Sorted keys and no ASCII escaping, so the same input always produces the same bytes and
    the column stays readable in Vietnamese when someone opens the Parquet by hand.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def find_evidence(context: str, evidence: str) -> tuple[int, int]:
    """Character span of the evidence inside the context, or ``(-1, -1)``.

    Only an exact match counts. An approximate match would put a plausible-looking number in
    a column that later experiments treat as ground truth, which is worse than admitting the
    evidence was not found: section 7 of docs/DATA.md asks for these misses to be counted.
    """
    if not evidence:
        return NO_OFFSET, NO_OFFSET
    start = context.find(evidence)
    if start < 0:
        return NO_OFFSET, NO_OFFSET
    return start, start + len(evidence)


def validate(frame: pd.DataFrame) -> None:
    """Raise if the frame breaks any invariant of the common schema."""
    missing = [column for column in COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"thiếu cột: {', '.join(missing)}")
    extra = [column for column in frame.columns if column not in COLUMNS]
    if extra:
        raise ValueError(f"cột lạ không có trong schema: {', '.join(extra)}")
    if frame.empty:
        raise ValueError("frame rỗng")

    for column in REQUIRED_NON_EMPTY:
        if frame[column].isna().any():
            raise ValueError(f"cột {column} có giá trị rỗng")
        if (frame[column].astype(str).str.len() == 0).any():
            raise ValueError(f"cột {column} có chuỗi rỗng")

    for column in ("question", "evidence"):
        if frame[column].isna().any():
            raise ValueError(f"cột {column} có null; dùng chuỗi rỗng thay vì null")

    for column, allowed in (("dataset", DATASETS), ("split", SPLITS), ("label", LABELS)):
        unexpected = sorted(set(frame[column]) - set(allowed))
        if unexpected:
            raise ValueError(f"cột {column} có giá trị lạ: {unexpected}")

    if frame["sample_id"].duplicated().any():
        count = int(frame["sample_id"].duplicated().sum())
        raise ValueError(f"sample_id trùng ở {count} dòng")

    # An offset must either point somewhere real or be the sentinel. A start without an end,
    # or a span running past the context, means the reader mismatched its columns.
    for column in ("evidence_start", "evidence_end"):
        if not pd.api.types.is_integer_dtype(frame[column]):
            raise ValueError(f"cột {column} phải là số nguyên, đang là {frame[column].dtype}")
    located = frame["evidence_start"] != NO_OFFSET
    if (located != (frame["evidence_end"] != NO_OFFSET)).any():
        raise ValueError("evidence_start và evidence_end không khớp nhau về việc có tìm thấy")
    if located.any():
        spans = frame.loc[located]
        if (spans["evidence_end"] > spans["context"].str.len()).any():
            raise ValueError("có evidence_end vượt quá độ dài context")
        if (spans["evidence_start"] >= spans["evidence_end"]).any():
            raise ValueError("có evidence_start không nhỏ hơn evidence_end")


def finalise(frame: pd.DataFrame) -> pd.DataFrame:
    """Put the columns in order, fix the dtypes, validate, and return the result.

    Every corpus reader ends here, so any of them that drifts from the schema fails loudly at
    the point of writing rather than silently downstream.
    """
    frame = frame.copy()
    for column in ("evidence_start", "evidence_end"):
        frame[column] = frame[column].astype("int64")
    frame["response_is_generated"] = frame["response_is_generated"].astype(bool)
    for column in ("sample_id", "dataset", "split", "context", "context_id", "question",
                   "response", "label", "label_original", "evidence", "meta"):
        frame[column] = frame[column].astype("string").fillna("")

    frame = frame[list(COLUMNS)].reset_index(drop=True)
    validate(frame)
    return frame
