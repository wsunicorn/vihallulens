"""Hypothesis tests, written out rather than imported.

Only one test is needed anywhere in this thesis — experiment E06 asks whether the attention
distribution is more diffuse on the samples that have no evidence to attend to — and it is a
Mann-Whitney U. Writing it here rather than reaching for ``scipy.stats`` keeps ``scipy`` out of
``pyproject.toml``, where it would be a declared dependency of the whole project for one
function; it currently arrives only indirectly, through scikit-learn.

**The p-value is not the interesting number.** The two groups of E06 hold roughly 1.200 and
2.400 samples, and at that size a difference far too small to mean anything still comes out at
p < 0.001. So :func:`mann_whitney` returns an effect size alongside, and the write-up is required
to lead with that.
"""

from __future__ import annotations

import math

import numpy as np

# Above this, the normal approximation to U is accurate enough that the exact test is not worth
# implementing. E06's groups are far larger; the guard exists so a small-sample caller is told
# rather than quietly given a bad p-value.
MIN_GROUP = 20


def _rank_with_ties(values: np.ndarray) -> np.ndarray:
    """Average ranks, 1-based, ties sharing their mean rank."""
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    sorted_values = values[order]
    index = 0
    while index < len(values):
        stop = index
        while stop + 1 < len(values) and sorted_values[stop + 1] == sorted_values[index]:
            stop += 1
        ranks[order[index:stop + 1]] = (index + stop) / 2.0 + 1.0
        index = stop + 1
    return ranks


def mann_whitney(a, b) -> dict:
    """Test whether ``a`` tends to be larger than ``b``, without assuming a distribution.

    Entropy over chunks is bounded in [0, 1] and piles up near its ceiling on short contexts, so
    it is nowhere near normal and a t-test would be answering a question about means that the
    data cannot support. The rank test asks only "does a value drawn from ``a`` tend to exceed one
    drawn from ``b``", which is exactly the claim E06 makes.

    Returns ``u``, the two-sided ``p_value`` from the tie-corrected normal approximation, and
    ``effect``: the rank-biserial correlation, which is ``2 * P(a > b) - 1`` — so 0 means the two
    groups are interchangeable, and 1 means every value in ``a`` exceeds every value in ``b``.
    ``probability_superior`` reports ``P(a > b)`` directly, since that is the sentence a reader
    can check against intuition.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if len(a) < MIN_GROUP or len(b) < MIN_GROUP:
        raise ValueError(
            f"mỗi nhóm cần ít nhất {MIN_GROUP} mẫu để xấp xỉ chuẩn dùng được; "
            f"nhận {len(a)} và {len(b)}"
        )

    combined = np.concatenate([a, b])
    ranks = _rank_with_ties(combined)
    rank_sum_a = float(ranks[: len(a)].sum())
    n_a, n_b = len(a), len(b)
    u_a = rank_sum_a - n_a * (n_a + 1) / 2.0

    mean_u = n_a * n_b / 2.0
    # Tie correction: without it the variance is overstated and the p-value comes out too large,
    # which for once errs the safe way — but entropy rounded to six decimals ties often enough
    # that the correction is worth having.
    _, counts = np.unique(combined, return_counts=True)
    total = n_a + n_b
    tie_term = float(((counts ** 3 - counts).sum()) / (total * (total - 1)))
    variance = n_a * n_b / 12.0 * ((total + 1) - tie_term)

    if variance <= 0:
        z, p_value = 0.0, 1.0
    else:
        z = (u_a - mean_u) / math.sqrt(variance)
        p_value = math.erfc(abs(z) / math.sqrt(2.0))

    probability_superior = u_a / (n_a * n_b)
    return {
        "u": u_a,
        "z": float(z),
        "p_value": float(p_value),
        "effect": float(2.0 * probability_superior - 1.0),
        "probability_superior": float(probability_superior),
        "n_a": n_a,
        "n_b": n_b,
        "median_a": float(np.median(a)),
        "median_b": float(np.median(b)),
    }


def describe_effect(effect: float) -> str:
    """Plain words for a rank-biserial correlation, so the write-up cannot lean on p alone.

    Thresholds follow the conventional reading of Cliff's delta, which shares this scale.
    """
    size = abs(effect)
    if size < 0.11:
        return "không đáng kể"
    if size < 0.28:
        return "nhỏ"
    if size < 0.43:
        return "vừa"
    return "lớn"
