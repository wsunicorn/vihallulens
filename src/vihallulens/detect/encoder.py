"""Preparing input for the encoder baselines of experiment E09.

Fine-tuning itself lives in the script, because it needs a GPU and section 5 of docs/SPEC.md
keeps GPU code out of the test suite. What lives here is everything that decides *what the
encoder sees*, which is testable on a CPU and is where a baseline is most easily made unfair
by accident.
"""

from __future__ import annotations

import pandas as pd

from vihallulens.data.segmentation import segment_all
from vihallulens.evaluation.metrics import LABELS

# The three encoders section 4 of docs/EXPERIMENTS.md names, with what each one needs.
#
# ``max_length`` is each model's own ceiling, not a common number. PhoBERT simply cannot go past
# 256 positions, and forcing XLM-R down to 256 to match would make the comparison fairer in one
# sense and weaker in another: the point of a baseline is to be the strongest thing the thesis
# has to beat, so each model gets its best setting and the truncation rates are reported beside
# the scores.
MODELS = {
    "phobert": {
        "name": "vinai/phobert-large",
        "max_length": 256,
        "segment": True,
        "batch_size": 16,
    },
    "xlmr": {
        "name": "FacebookAI/xlm-roberta-large",
        "max_length": 512,
        "segment": False,
        "batch_size": 8,
    },
    "infoxlm": {
        "name": "microsoft/infoxlm-large",
        "max_length": 512,
        "segment": False,
        "batch_size": 8,
    },
}


def build_pairs(frame: pd.DataFrame, segment: bool) -> tuple[list[str], list[str]]:
    """Split each sample into the two halves an encoder pair-classifies.

    The split mirrors the prompt template locked at T07 in section 8 of CLAUDE.md: everything
    the model was given goes on the left, the text being judged goes on the right. That is what
    makes the comparison with the attention method a comparison of *methods* rather than of who
    was shown more.

    ``segment`` joins the syllables of each word, which PhoBERT needs and the other two must not
    be given.
    """
    for column in ("context", "response"):
        if column not in frame.columns:
            raise ValueError(f"thiếu cột {column}")

    question = frame["question"] if "question" in frame.columns else pd.Series([""] * len(frame))
    left = [
        f"{context} {ask}".strip() if str(ask).strip() else str(context)
        for context, ask in zip(frame["context"], question.fillna(""), strict=True)
    ]
    right = [str(text) for text in frame["response"]]

    if segment:
        left, right = segment_all(left), segment_all(right)
    return left, right


def encode_labels(labels, order=LABELS) -> list[int]:
    """Turn label strings into the integer ids a classification head needs.

    The order is fixed by ``LABELS`` rather than by whatever the data happens to contain, so
    that class 0 means the same thing in every run and a model saved from one can be read by
    another. This is the same trap that made the first E01 run report a wrong calibration
    error, approached from the other side.
    """
    lookup = {label: index for index, label in enumerate(order)}
    unknown = sorted(set(labels) - set(lookup))
    if unknown:
        raise ValueError(f"nhãn lạ: {unknown}; chỉ chấp nhận {list(order)}")
    return [lookup[label] for label in labels]


def decode_labels(ids, order=LABELS) -> list[str]:
    """Inverse of :func:`encode_labels`."""
    out_of_range = sorted({index for index in ids if not 0 <= int(index) < len(order)})
    if out_of_range:
        raise ValueError(f"mã lớp ngoài phạm vi: {out_of_range}; chỉ có {len(order)} lớp")
    return [order[int(index)] for index in ids]


def truncation_rate(tokenizer, left, right, max_length: int) -> float:
    """Share of pairs that do not fit, so the cost of a short ceiling is reported not assumed.

    PhoBERT stops at 256 positions while the other two reach 512, and ViHallu contexts are long
    enough that this is not a rounding detail. A baseline losing to the thesis partly because it
    could not read the whole context is a fact the report has to state.
    """
    lengths = tokenizer(
        list(left), list(right), truncation=False, add_special_tokens=True
    )["input_ids"]
    return sum(1 for ids in lengths if len(ids) > max_length) / len(lengths)
