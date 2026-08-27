"""The two surface features of the trivial baseline, experiment E01.

Section 4 of docs/EXPERIMENTS.md calls E01 the experiment that must be run earliest, because it
defines the real floor. A hallucinated response tends to be longer and to reuse fewer of the
context's words, and those two facts alone carry a surprising amount of the signal. Anything
more elaborate — including this thesis's own contribution — has to beat *this*, not the numbers
other papers happen to publish.

Two features, nothing else. Adding a third would make it a better classifier and a worse floor.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from vihallulens.data.text import tokenize, word_count

FEATURE_NAMES = ("response_len", "lexical_overlap")


def response_len(response: str) -> float:
    """Length of the response in words.

    Plain whitespace count, punctuation included. Measured at T17 on ViHallu, this reproduces
    the per-label averages published in section 4 of docs/EXPERIMENTS.md exactly: 32,9 words for
    ``no``, 39,5 for ``intrinsic``, 45,9 for ``extrinsic``.
    """
    return float(word_count(response))


def lexical_overlap(response: str, context: str) -> float:
    """Share of the response's words that also occur in the context.

    Counted over word *occurrences*, not distinct words: a response repeating one context word
    ten times should score higher than one using it once, because the question being asked is
    how much of this text was lifted from the source.

    An empty response scores 0. It cannot have copied anything, and 0 is also what a maximally
    unfaithful response scores, which is the right neighbourhood for a response with no content.
    """
    words = tokenize(response)
    if not words:
        return 0.0
    seen = set(tokenize(context))
    return sum(1 for word in words if word in seen) / len(words)


def surface_features(frame: pd.DataFrame) -> np.ndarray:
    """Feature matrix of shape ``(n_samples, 2)`` for a normalised corpus frame."""
    for column in ("response", "context"):
        if column not in frame.columns:
            raise ValueError(f"thiếu cột {column}")
    return np.array(
        [
            [response_len(str(row.response)), lexical_overlap(str(row.response), str(row.context))]
            for row in frame.itertuples(index=False)
        ],
        dtype=np.float64,
    ).reshape(len(frame), len(FEATURE_NAMES))
