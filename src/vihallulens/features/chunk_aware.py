"""The five chunk-aware features — the contribution of this thesis.

Lookback Lens asks one question of the attention map: how much of it went to the context at
all. This module asks a second one: **how that attention was spread across the pieces of the
context**. The claim being tested is that the shape of that spread separates the two kinds of
hallucination, which the aggregate ratio cannot:

* **Intrinsic** — the model *did* read the context and then contradicted it. Attention lands
  somewhere specific, so the distribution is peaked.
* **Extrinsic** — the model did not read it and invented something. There is nothing in
  particular to look at, so attention is diffuse.

Both produce text that fails to match the context, which is why every text-based method in
Bảng 1 confuses them. Measured at T20, the aggregate ratio already scores 0,731 on the
intrinsic class against PhoBERT's 0,693; these features exist to test whether the *shape* adds
more on top of the *amount*.

Two normalisation decisions decide whether these numbers mean anything, and both are the same
class of mistake as "sum instead of mean" in the original formula: getting them wrong still
produces a full matrix of plausible values, and the classifier then learns context length
instead of attention shape. Both are spelled out at :func:`chunk_shares` and
:func:`chunk_entropy`.
"""

from __future__ import annotations

import numpy as np

CHUNK_FEATURE_NAMES = (
    "chunk_entropy",
    "chunk_max_share",
    "chunk_gini",
    "top1_top2_gap",
    "chunk_drift",
)

# Below this, a slice carries no attention worth describing and every shape statistic would be
# reading rounding noise. It happens for heads that attend almost entirely to the scaffolding.
EPSILON = 1e-12


def chunk_shares(per_chunk: np.ndarray) -> np.ndarray:
    """Turn per-chunk attention densities into a distribution over chunks.

    ``per_chunk`` arrives from the extractor shaped ``(layers, heads, tokens, chunks)`` and is
    already an attention **density**: divided by the number of tokens in the chunk, so a long
    chunk does not win by being long. What it is not is a distribution — the values do not sum
    to one, because the denominator is the whole context.

    Every statistic below describes the *shape* of a distribution, so the normalisation has to
    happen here, once, rather than being assumed by four functions independently.

    A slice with no attention at all normalises to uniform rather than to nan. Uniform is the
    honest answer: nothing was looked at, so nothing was preferred, and every shape statistic
    then reports "maximally spread" instead of poisoning the sample with nan.
    """
    if per_chunk.ndim != 4:
        raise ValueError(f"cần mảng (lớp, đầu, token, đoạn), nhận {per_chunk.shape}")
    if per_chunk.shape[3] == 0:
        raise ValueError("không có đoạn nào")

    values = np.clip(per_chunk.astype(np.float64), 0.0, None)
    total = values.sum(axis=3, keepdims=True)
    n_chunks = per_chunk.shape[3]
    return np.where(total > EPSILON, values / np.maximum(total, EPSILON), 1.0 / n_chunks)


def chunk_entropy(shares: np.ndarray) -> np.ndarray:
    """Entropy of the chunk distribution, **divided by its own maximum**.

    Raw entropy tops out at ``ln(n_chunks)``, so a context cut into 23 pieces scores higher than
    one cut into 5 no matter how the attention is spread. Samples differ enormously here —
    measured at T15, ViHallu averages 5,3 chunks and ISE-DSC01 averages 22,8 — so an unnormalised
    entropy would largely encode **how long the context is**, and the classifier would learn
    that instead of anything about attention.

    That is exactly the trap the original lookback formula avoids by averaging per token rather
    than summing, and it has to be avoided again here. Dividing by ``ln(n_chunks)`` puts every
    sample on the same [0, 1] scale: 0 is all attention on one chunk, 1 is perfectly even.

    A context with a single chunk scores 0 — there is only one place to look, so the spread is
    as concentrated as it can be. That case is not rare: 15,3 % of ViWikiFC contexts, measured
    at T15.
    """
    n_chunks = shares.shape[-1]
    if n_chunks == 1:
        return np.zeros(shares.shape[:-1], dtype=np.float32)
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(shares > EPSILON, shares * np.log(np.maximum(shares, EPSILON)), 0.0)
    return (-terms.sum(axis=-1) / np.log(n_chunks)).astype(np.float32)


def chunk_max_share(shares: np.ndarray) -> np.ndarray:
    """Share of the single most-attended chunk. High means the model fixed on one place."""
    return shares.max(axis=-1).astype(np.float32)


def top1_top2_gap(shares: np.ndarray) -> np.ndarray:
    """How far the leading chunk is ahead of the runner-up.

    Separates two situations that ``chunk_max_share`` alone cannot: attention split between two
    plausible pieces of evidence, and attention committed to one. With a single chunk the gap is
    the whole distribution, so it is 1.
    """
    if shares.shape[-1] == 1:
        return shares[..., 0].astype(np.float32)
    top_two = np.partition(shares, -2, axis=-1)[..., -2:]
    return (top_two[..., 1] - top_two[..., 0]).astype(np.float32)


def chunk_gini(shares: np.ndarray) -> np.ndarray:
    """Gini coefficient of the chunk distribution, corrected for the number of chunks.

    Entropy and Gini both measure concentration but weigh it differently: entropy is dominated
    by how many chunks get *some* attention, Gini by how unequally the mass is split among them.
    A distribution with one large chunk and a long tail of small ones scores differently on the
    two, which is why both are kept.

    On ``n`` values the raw coefficient cannot exceed ``(n - 1) / n``, so it too would encode
    chunk count. Multiplying by ``n / (n - 1)`` — the standard small-sample correction — puts
    the maximum at 1 for every ``n``, for the same reason entropy is divided by its own maximum.
    """
    n_chunks = shares.shape[-1]
    if n_chunks == 1:
        return np.zeros(shares.shape[:-1], dtype=np.float32)
    ordered = np.sort(shares, axis=-1)
    ranks = np.arange(1, n_chunks + 1, dtype=np.float64)
    weighted = (ordered * ranks).sum(axis=-1)
    raw = 2.0 * weighted / n_chunks - (n_chunks + 1.0) / n_chunks
    return np.clip(raw * n_chunks / (n_chunks - 1.0), 0.0, 1.0).astype(np.float32)


def chunk_drift(shares: np.ndarray) -> np.ndarray:
    """How much the chunk distribution moves from one generated token to the next.

    Total variation distance between consecutive steps, averaged over the response: half the
    sum of absolute differences, which reads directly as "what fraction of the attention mass
    moved to a different chunk".

    This is the one feature that is *about* the token axis rather than pooled over it. A model
    working through one piece of evidence keeps looking at the same chunk and drifts little; one
    with nothing to ground itself on wanders. Section 2.3 of docs/SPEC.md files it under
    stability rather than chunk-aware for that reason.

    A response with a single scored token has no consecutive pair, so drift is 0 — no movement
    was observed, rather than movement of unknown size.
    """
    if shares.shape[2] < 2:
        return np.zeros(shares.shape[:2], dtype=np.float32)
    steps = 0.5 * np.abs(np.diff(shares, axis=2)).sum(axis=-1)
    return steps.mean(axis=2).astype(np.float32)


def chunk_features(per_chunk: np.ndarray) -> dict[str, np.ndarray]:
    """All five features for one sample, each shaped ``(layers, heads)``.

    The four shape statistics are computed per token and then averaged over the response, the
    same pooling the original method uses for its own span. Drift is already a summary across
    tokens, so it is returned as it comes.
    """
    shares = chunk_shares(per_chunk)
    pooled = {
        "chunk_entropy": chunk_entropy(shares),
        "chunk_max_share": chunk_max_share(shares),
        "chunk_gini": chunk_gini(shares),
        "top1_top2_gap": top1_top2_gap(shares),
    }
    out = {name: value.mean(axis=2).astype(np.float32) for name, value in pooled.items()}
    out["chunk_drift"] = chunk_drift(shares)
    return out


def feature_names(layer_indices, n_heads: int) -> list[str]:
    """Names in the order :func:`sample_vector` lays the values out.

    Feature first, then layer, then head — so the block belonging to one statistic is
    contiguous and an ablation over feature groups is a slice rather than a gather.
    """
    return [
        f"{name}_l{layer}_h{head}"
        for name in CHUNK_FEATURE_NAMES
        for layer in layer_indices
        for head in range(n_heads)
    ]


def sample_vector(per_chunk: np.ndarray) -> np.ndarray:
    """One flat feature vector for one sample: five statistics × layers × heads."""
    computed = chunk_features(per_chunk)
    return np.concatenate([computed[name].reshape(-1) for name in CHUNK_FEATURE_NAMES])
