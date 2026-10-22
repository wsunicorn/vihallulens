"""Pooling each sentence of the response on its own. Experiment E18.

Every block in a record is a mean over the whole response. Chapter 7 offers that as one reason
attention locates the evidence yet does not classify better: one fabricated clause among three
faithful sentences is averaged away. E18 tests the explanation by pooling **per sentence** and
only then across sentences, with the mean (to separate the effect of the unit from that of the
operator), the max (registered before the run) and the min.

The min is there because the blocks do not all move the same way on a fabricated sentence. A
sentence the model did not ground has a *low* lookback ratio, so the max over sentences would
pick the most grounded one and dilute the signal again. Which extreme carries it is a question
for the classifier, not for this module, so both are kept.

What is stored is the per-sentence vectors themselves; the operators are applied when the matrix
is built. Storing three pooled copies instead would cost more disk than the vectors (ViHallu
responses average 1,3 sentences) and would fix the operators before the data was seen.
"""

from __future__ import annotations

import numpy as np

from vihallulens.features.chunk_aware import CHUNK_FEATURE_NAMES, chunk_features
from vihallulens.features.lookback import DENOMINATORS, pool_over_tokens

SENTENCE_PREFIX = "sentence_"
SENTENCE_BLOCKS = tuple(f"lookback_{name}" for name in DENOMINATORS) + CHUNK_FEATURE_NAMES
POOLINGS = ("mean", "max", "min")


def sentence_vectors(features) -> dict[str, list[np.ndarray]]:
    """Each block computed on each sentence's tokens alone, each shaped ``(layers, heads)``.

    The same functions as the whole-response record, applied to a slice of the token axis, so
    a one-sentence response gets back exactly its whole-response values.
    """
    out: dict[str, list[np.ndarray]] = {block: [] for block in SENTENCE_BLOCKS}
    for group in features.sentence_tokens:
        index = np.asarray(group, dtype=int)
        for name in DENOMINATORS:
            sliced = getattr(features, f"lookback_{name}")[:, :, index]
            out[f"lookback_{name}"].append(pool_over_tokens(sliced))
        for name, value in chunk_features(features.lookback_per_chunk[:, :, index, :]).items():
            out[name].append(value)
    return out


def sentence_record_fields(features) -> dict:
    """The fields E18 adds to a record; empty when the extractor was not given sentences.

    Read with ``getattr`` because anything shaped like ``AttentionFeatures`` reaches here — the
    serving pipeline's own test doubles included — and none of them predates the need to work.
    """
    if not getattr(features, "sentence_tokens", None):
        return {}
    fields: dict = {"sentence_n_tokens": [len(group) for group in features.sentence_tokens]}
    for block, values in sentence_vectors(features).items():
        fields[f"{SENTENCE_PREFIX}{block}"] = [
            [round(float(item), 6) for item in value.reshape(-1)] for value in values
        ]
    return fields


def pool_sentences(per_sentence, pooling: str) -> np.ndarray:
    """Collapse ``(sentences, width)`` to ``(width,)`` with one of :data:`POOLINGS`.

    ``mean`` weighs every sentence equally whatever its length, which is what separates it from
    the whole-response vector, where a long sentence outweighs a short one token by token.
    """
    values = np.asarray(per_sentence, dtype=np.float32)
    if values.ndim != 2 or values.shape[0] == 0:
        raise ValueError(f"cần mảng (câu, chiều) có ít nhất một câu, nhận {values.shape}")
    if pooling not in POOLINGS:
        raise ValueError(f"cách gộp câu lạ: {pooling!r}; có {POOLINGS}")
    return getattr(values, pooling)(axis=0)


def pooled_view(record: dict, pooling: str, blocks=SENTENCE_BLOCKS) -> dict:
    """A copy of ``record`` whose whole-response blocks are replaced by sentence-pooled ones.

    The copy keeps the block names, so the matrix builders, the head selection and the detector
    of E03 run on it unchanged: the one thing that differs between E03 and E18 is how the
    response was pooled.
    """
    view = dict(record)
    for block in blocks:
        view[block] = pool_sentences(record[f"{SENTENCE_PREFIX}{block}"], pooling)
    return view
