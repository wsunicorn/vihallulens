"""Where the model looked, against where the evidence actually is. Experiment E06.

Every other experiment infers the mechanism from a classifier score: chunk-aware features help,
therefore attention must be landing somewhere meaningful. This one checks that directly. Given a
sample whose gold evidence is known, it asks whether the chunk the model attended to most **is**
the chunk holding the evidence.

That makes it the experiment CH1 stands or falls on. A detector can score well on ViHallu by
picking up any correlate of hallucination; only this can say the correlate is *reading the right
part of the context*.

Three things are measured, per section E06 of docs/EXPERIMENTS.md:

``hit@1``   the most-attended chunk is the gold chunk
``hit@3``   the gold chunk is in the top three
``MRR``     mean reciprocal rank of the gold chunk

each against the floor a random ranker would reach. The floor is **not** a constant: it depends
on how many chunks the context was cut into, which varies from 3 to 63 on ISE-DSC01. Comparing
against a single averaged floor would flatter or penalise long contexts, so the floor is computed
per sample and averaged the same way the score is.
"""

from __future__ import annotations

import numpy as np

from vihallulens.features.chunk_aware import chunk_shares

# Ranks are 0-based: rank 0 means the gold chunk received the most attention.
HIT_LEVELS = (1, 3)


def mean_shares(per_chunk: np.ndarray) -> np.ndarray:
    """Attention share per chunk, averaged over the response tokens.

    Shape ``(layers, heads, tokens, chunks)`` in, ``(layers, heads, chunks)`` out. Each token's
    distribution is normalised **before** averaging, not after, so that a token that happens to
    send more of its attention to the context does not count for more than the others. This is
    the same order of operations the per-token lookback ratio uses, and the same reason: the
    quantity being averaged has to be a share, or long responses drown out short ones.
    """
    if per_chunk.ndim != 4:
        raise ValueError(f"cần mảng 4 chiều (lớp, đầu, token, đoạn), nhận {per_chunk.shape}")
    return chunk_shares(per_chunk).mean(axis=2)


def gold_rank(shares: np.ndarray, gold: int) -> np.ndarray:
    """0-based rank of the gold chunk in each ``(layer, head)``'s ranking, best first.

    Ties are broken **pessimistically**: a chunk tied with the gold one is counted as ahead of
    it. With float16 arithmetic exact ties are not rare — a head that spreads its attention
    perfectly evenly ties every chunk — and an optimistic rule would report hit@1 for a head that
    expressed no preference at all. Reporting the mechanism as weaker than it might be is the
    error to prefer here.
    """
    if shares.ndim != 3:
        raise ValueError(f"cần mảng 3 chiều (lớp, đầu, đoạn), nhận {shares.shape}")
    n_chunks = shares.shape[2]
    if not 0 <= gold < n_chunks:
        raise ValueError(f"đoạn vàng {gold} nằm ngoài {n_chunks} đoạn")
    gold_share = shares[:, :, gold][:, :, None]
    # ``>=`` then subtract the gold chunk's own count: every chunk that ties with it is counted
    # as ahead. Using a strict ``>`` here would rank a perfectly flat head first and credit it
    # with hit@1 for expressing no preference at all.
    return ((shares >= gold_share).sum(axis=2) - 1).astype(np.int16)


def random_floor(n_chunks: int, k: int) -> float:
    """Probability a ranker that knows nothing puts the gold chunk in its top ``k``."""
    return min(k, n_chunks) / n_chunks


def hit_at(ranks: np.ndarray, k: int) -> np.ndarray:
    """Fraction of samples whose gold chunk landed in the top ``k``, per ``(layer, head)``.

    ``ranks`` is ``(samples, layers, heads)``.
    """
    return (np.asarray(ranks) < k).mean(axis=0)


def reciprocal_rank(ranks: np.ndarray) -> np.ndarray:
    """Mean reciprocal rank per ``(layer, head)``. Rank 0 scores 1, rank 1 scores 1/2."""
    return (1.0 / (np.asarray(ranks) + 1.0)).mean(axis=0)


def best_head(scores: np.ndarray) -> tuple[int, int, float]:
    """The ``(layer_position, head, score)`` of the strongest cell in a per-head score grid.

    Returns the layer's **position** in the grid, not its index in the model — the caller holds
    ``layer_indices`` and does that translation, because layer 27 is excluded and the two numbers
    stop agreeing after it.
    """
    flat = int(np.argmax(scores))
    layer, head = divmod(flat, scores.shape[1])
    return layer, head, float(scores[layer, head])


def summarise(ranks: np.ndarray, n_chunks: np.ndarray) -> dict:
    """Everything Bảng 2 needs, for the single best head and for the head-average.

    Two readings are reported because they answer different questions. The **best head** says
    whether the signal exists anywhere in the model, which is what CH1 asks. The **average over
    heads** says whether it is a broad property or one specialised circuit — Lookback Lens found
    the latter, and saying which one this is costs nothing extra here.

    The best head is chosen on the very data it is then reported on, so its number is optimistic
    by construction; it is reported as "the strongest head found", never as a held-out result.
    Selecting it honestly needs a split, which is what E12 does.
    """
    ranks = np.asarray(ranks)
    if ranks.ndim != 3:
        raise ValueError(f"cần mảng 3 chiều (mẫu, lớp, đầu), nhận {ranks.shape}")
    n_chunks = np.asarray(n_chunks, dtype=float)

    summary: dict = {"n_samples": int(ranks.shape[0]), "mean_chunks": float(n_chunks.mean())}
    for k in HIT_LEVELS:
        grid = hit_at(ranks, k)
        layer, head, score = best_head(grid)
        floor = float(np.mean([random_floor(int(n), k) for n in n_chunks]))
        summary[f"hit@{k}"] = score
        summary[f"hit@{k}_head"] = (layer, head)
        summary[f"hit@{k}_mean_over_heads"] = float(grid.mean())
        summary[f"hit@{k}_floor"] = floor
        summary[f"hit@{k}_lift"] = score / floor if floor else float("nan")

    grid = reciprocal_rank(ranks)
    layer, head, score = best_head(grid)
    # A random ranker's expected reciprocal rank over n chunks is the harmonic number over n.
    floor = float(np.mean([sum(1.0 / (r + 1) for r in range(int(n))) / n for n in n_chunks]))
    summary["mrr"] = score
    summary["mrr_head"] = (layer, head)
    summary["mrr_mean_over_heads"] = float(grid.mean())
    summary["mrr_floor"] = floor
    summary["mrr_lift"] = score / floor if floor else float("nan")
    return summary
