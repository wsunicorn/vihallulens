"""From one extraction to one shard row.

A *record* is the unit every later stage reads: one sample's pooled attention features plus the
bookkeeping needed to audit them. ``scripts/extract_features.py`` writes records to JSONL shards,
``vihallulens.features.assemble`` stacks them into matrices, and the serving pipeline builds one
in memory for each request and scores it without ever touching disk.

Moved here from the extraction script at T36 for exactly that last reason: a request has to go
through the same code as a training row, or the classifier is applied to vectors laid out
differently from the ones it was fitted on.
"""

from __future__ import annotations

from vihallulens.data.chunking import locate_evidence_chunk
from vihallulens.features.chunk_aware import chunk_features
from vihallulens.features.localization import gold_rank, mean_shares
from vihallulens.features.lookback import DENOMINATORS, pool_over_tokens


def gold_chunk_rank(features, evidence: str) -> tuple[int | None, list[int] | None]:
    """Where the gold evidence sits, and how each head ranked that chunk. Experiment E06.

    Computed here rather than afterwards because it needs two things only this scope has:
    the per-chunk array before it is pooled away, and — the part that is easy to get wrong —
    the chunks that **survived truncation**. Truncation removes whole chunks and re-indexes
    the rest, so an index found in the original chunk list would silently name a different
    chunk, and the resulting hit@1 would be measuring nothing.

    Returns ``(None, None)`` when the sample has no evidence — every NEI row of ISE-DSC01 —
    or when the chunk holding it was one of the ones truncation dropped.
    """
    if not evidence or not evidence.strip() or not features.chunks:
        return None, None
    gold = locate_evidence_chunk(features.chunks, evidence)
    if gold is None:
        return None, None
    ranks = gold_rank(mean_shares(features.lookback_per_chunk), gold)
    return int(gold), [int(value) for value in ranks.reshape(-1)]


def to_record(sample_id: str, label: str | None, features, elapsed_ms: float,
              evidence: str = "") -> dict:
    """One sample's row: the pooled vectors plus everything needed to audit them later.

    Both families are written in one pass. The chunk-aware statistics are computed from the same
    attention matrix as the lookback ratio, so extracting them separately would pay for the
    reading model twice to learn nothing new.

    ``label`` is ``None`` for a request being scored rather than a training row.
    """
    row = {
        "sample_id": sample_id,
        "label": label,
        "n_chunks": int(features.n_chunks),
        "truncated": bool(features.truncated),
        "n_scored_tokens": int(features.lookback_total.shape[2]),
        "layer_indices": list(features.layer_indices),
        "nonfinite_layers": list(features.nonfinite_layers),
        "row_sum_mean": float(features.row_sum_mean),
        "peak_vram_mb": float(features.peak_vram_mb),
        "elapsed_ms": float(elapsed_ms),
    }
    for name in DENOMINATORS:
        pooled = pool_over_tokens(getattr(features, f"lookback_{name}"))
        row[f"lookback_{name}"] = [round(float(value), 6) for value in pooled.reshape(-1)]
    for name, value in chunk_features(features.lookback_per_chunk).items():
        row[name] = [round(float(item), 6) for item in value.reshape(-1)]

    # Only written when the sample actually has evidence, so ViHallu rows — which have none —
    # do not each carry 756 null integers for a column no experiment on them will ever read.
    gold, ranks = gold_chunk_rank(features, evidence)
    if gold is not None:
        row["gold_chunk"] = gold
        row["gold_rank"] = ranks
    return row
