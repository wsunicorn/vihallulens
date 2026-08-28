"""Turning one sample's attention signal into the feature vector of experiment E02.

This is the faithful reproduction of Lookback Lens, whose formula is quoted in section 1 of
docs/REFERENCES.md. Three things there are easy to get almost right, and each is wrong in a way
that still produces plausible numbers:

1. The ratio is attention **averaged per source token**, not summed. Dividing is what makes a
   4.000-token context comparable with a 40-token response. Summing would make the ratio a
   proxy for context length, and the classifier would learn that instead.
2. A step's feature vector is **every layer-head pair concatenated**, and only then averaged
   over the steps of the span. Averaging over heads first would throw away the very structure
   the paper found signal in — that a few specific heads carry most of it.
3. The span here is the **whole response**, not the paper's sliding window of eight tokens,
   because ViHallu labels responses rather than spans.

Step 1 happens inside ``extract.attention``; this module does step 2, and step 3 by construction
since the extractor scores every response token.
"""

from __future__ import annotations

import numpy as np

# Both denominators are kept, as fixed in section 3 of CLAUDE.md. ``total`` counts every token
# before the response and reproduces the paper, where X is the whole input; ``context`` counts
# only the retrieved context and is the interpretable one the chunk-aware work builds on.
DENOMINATORS = ("total", "context")
E02_DENOMINATOR = "total"


def pool_over_tokens(lookback: np.ndarray) -> np.ndarray:
    """Average a ``(layers, heads, tokens)`` array over its token axis.

    The span is the whole response, so this is the paper's "average the per-step vectors over
    the span" with the span taken as everything scored.

    ``nanmean`` rather than ``mean``: a layer that overflowed in float16 fills its slice with
    nan, and a plain mean would spread that nan across every head of every other layer through
    the classifier's standardisation. Layers that overflow are excluded by configuration, so a
    nan here means something unexpected happened and the surviving layers should still be
    usable while the count is reported.
    """
    if lookback.ndim != 3:
        raise ValueError(f"cần mảng (lớp, đầu, token), nhận {lookback.shape}")
    if lookback.shape[2] == 0:
        raise ValueError("không có token nào được chấm")
    with np.errstate(invalid="ignore"):
        pooled = np.nanmean(lookback.astype(np.float64), axis=2)
    return pooled.astype(np.float32)


def flatten_heads(pooled: np.ndarray) -> np.ndarray:
    """Concatenate the layer-head grid into one vector, layer-major."""
    if pooled.ndim != 2:
        raise ValueError(f"cần mảng (lớp, đầu), nhận {pooled.shape}")
    return pooled.reshape(-1)


def feature_names(layer_indices, n_heads: int, denominator: str = E02_DENOMINATOR) -> list[str]:
    """Names matching the flattened order, so a classifier weight can be traced to a head.

    ``layer_indices`` are the model's own layer numbers, not positions in the array. With layer
    27 excluded the array has 27 slices but they are layers 0 to 26, and a name saying ``l26``
    for the last one is the difference between "head 14 of layer 26 matters" and a number
    nobody can point at.
    """
    return [
        f"lookback_{denominator}_l{layer}_h{head}"
        for layer in layer_indices
        for head in range(n_heads)
    ]


def sample_vector(features, denominator: str = E02_DENOMINATOR) -> np.ndarray:
    """The E02 feature vector for one sample, from an ``AttentionFeatures``."""
    if denominator not in DENOMINATORS:
        raise ValueError(f"mẫu số lạ: {denominator!r}; chỉ có {DENOMINATORS}")
    lookback = getattr(features, f"lookback_{denominator}")
    return flatten_heads(pool_over_tokens(lookback))
