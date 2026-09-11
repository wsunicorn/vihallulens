"""Turning stored feature blocks into the matrix a classifier sees. Signature per SPEC 2.3.

Two things are decided here, and both are decided *after* the reading model has run, which is
why they live apart from extraction:

* **Which groups** enter the matrix. ``basic`` is the aggregate lookback ratio reproducing
  Lookback Lens; ``chunk_aware`` and ``stability`` are this thesis's contribution. Keeping them
  separable is what makes the ablation of E12 a slice rather than a re-run.
* **How attention heads are aggregated.** With 27 layers and 28 heads, six feature families come
  to 4.536 columns against 5.600 training rows. Section 2.3 of docs/SPEC.md offers three answers
  and section 4 of docs/EXPERIMENTS.md requires the choice be made on the **dev** split.
"""

from __future__ import annotations

import numpy as np

from vihallulens.features.chunk_aware import CHUNK_FEATURE_NAMES

# Which stored blocks each configured group draws on. Names match the keys the extraction
# script writes, so a group that asks for a block absent from a shard fails loudly rather than
# silently producing a narrower matrix.
GROUP_BLOCKS: dict[str, tuple[str, ...]] = {
    "basic": ("lookback_total",),
    "chunk_aware": tuple(name for name in CHUNK_FEATURE_NAMES if name != "chunk_drift"),
    "stability": ("chunk_drift",),
}

HEAD_AGGREGATIONS = ("all", "mean_over_heads", "topk_heads")


def blocks_for(groups) -> list[str]:
    """Stored block names for a list of configured groups, in a fixed order.

    Order follows ``GROUP_BLOCKS`` rather than the order the config happens to list its groups,
    so two configs naming the same groups produce the same column layout and their fitted
    weights stay comparable.
    """
    unknown = [group for group in groups if group not in GROUP_BLOCKS]
    if unknown:
        raise ValueError(
            f"nhóm đặc trưng chưa hiện thực: {unknown}; có {sorted(GROUP_BLOCKS)}. "
            f"Nhóm 'surface' và 'localization' thuộc thí nghiệm khác."
        )
    wanted = set(groups)
    return [block for group, names in GROUP_BLOCKS.items() if group in wanted for block in names]


def stack_blocks(records, blocks, n_layers: int, n_heads: int) -> np.ndarray:
    """Rows of ``(blocks × layers × heads)``, one row per record."""
    columns = []
    for block in blocks:
        missing = [record["sample_id"] for record in records if block not in record][:3]
        if missing:
            raise ValueError(
                f"khối '{block}' không có trong đặc trưng đã trích, ví dụ mẫu {missing}. "
                f"Lượt trích cũ chưa lưu khối này — chạy lại scripts/extract_features.py."
            )
        values = np.asarray([record[block] for record in records], dtype=np.float32)
        if values.shape[1] != n_layers * n_heads:
            raise ValueError(
                f"khối '{block}' có {values.shape[1]} cột, cần {n_layers * n_heads} "
                f"= {n_layers} lớp × {n_heads} đầu"
            )
        columns.append(values)
    return np.hstack(columns)


def aggregate_heads(matrix: np.ndarray, n_blocks: int, n_layers: int, n_heads: int,
                    mode: str, keep: np.ndarray | None = None) -> np.ndarray:
    """Reduce the head axis according to ``mode``.

    ``all`` keeps every column. ``mean_over_heads`` averages within each layer, which cuts the
    width by 28 at the cost of the paper's own finding that a few specific heads carry the
    signal. ``topk_heads`` keeps the columns of the ``(layer, head)`` pairs listed in ``keep``,
    which is the compromise: it drops most of the width while leaving individual heads intact.

    ``keep`` holds flat ``layer * n_heads + head`` indices, applied identically to every block —
    a head either survives for all six statistics or for none. Selecting different heads per
    statistic would make the surviving columns hard to interpret and would multiply the number
    of choices made against the dev split.
    """
    if mode not in HEAD_AGGREGATIONS:
        raise ValueError(f"cách gộp đầu chưa biết: {mode!r}; có {list(HEAD_AGGREGATIONS)}")
    grid = matrix.reshape(len(matrix), n_blocks, n_layers, n_heads)
    if mode == "all":
        return matrix
    if mode == "mean_over_heads":
        return grid.mean(axis=3).reshape(len(matrix), -1)
    if keep is None or len(keep) == 0:
        raise ValueError("topk_heads cần danh sách đầu giữ lại")
    flat = grid.reshape(len(matrix), n_blocks, n_layers * n_heads)
    return flat[:, :, np.asarray(keep, dtype=int)].reshape(len(matrix), -1)


def column_names(blocks, layer_indices, n_heads: int, mode: str,
                 keep: np.ndarray | None = None) -> list[str]:
    """Names matching the layout ``aggregate_heads`` produces, in the same order."""
    if mode == "mean_over_heads":
        return [f"{block}_l{layer}_hmean" for block in blocks for layer in layer_indices]
    if mode == "topk_heads":
        pairs = [(layer_indices[int(index) // n_heads], int(index) % n_heads) for index in keep]
        return [f"{block}_l{layer}_h{head}" for block in blocks for layer, head in pairs]
    return [
        f"{block}_l{layer}_h{head}"
        for block in blocks
        for layer in layer_indices
        for head in range(n_heads)
    ]


def rank_heads(weights: np.ndarray, n_blocks: int, n_layers: int, n_heads: int) -> np.ndarray:
    """Order ``(layer, head)`` pairs by how hard a fitted model leaned on them.

    A pair's score is the largest absolute weight across every block it appears in, so a head
    that matters for one statistic survives even if the other five ignore it. Returns flat
    indices, best first, ready to slice with ``keep``.
    """
    per_pair = np.abs(weights).reshape(n_blocks, n_layers * n_heads).max(axis=0)
    return np.argsort(per_pair)[::-1]


def build_feature_matrix(records, groups, n_layers: int, n_heads: int,
                         mode: str = "all", keep=None) -> np.ndarray:
    """The whole path from stored records to a classifier's input, in one call."""
    blocks = blocks_for(groups)
    stacked = stack_blocks(records, blocks, n_layers, n_heads)
    return aggregate_heads(stacked, len(blocks), n_layers, n_heads, mode, keep)


def drop_nonfinite(records, blocks=None):
    """Split records into the usable ones and the ones carrying ``nan`` or ``inf``.

    Measured at T30 with Sailor2-8B: 49 of 7.000 ViHallu samples (0,70 %) came out with every
    layer non-finite, not one particular layer. Qwen2.5-7B overflows at layer 27 on *every*
    sample, so excluding that layer fixes it for everyone. Sailor2 instead overflows on *every*
    layer for a few samples — a cascade from an early layer rather than one fragile layer — so
    there is no set of layers to exclude short of all of them.

    That makes dropping the samples the only path, which is fine as long as it stays small and
    stays *reported*. Silently returning a shorter matrix would move the test-set denominator
    without saying so.

    Returns ``(clean, dropped)``. Both are lists of records, so the caller can count, report and
    if needed inspect what it lost.
    """
    blocks = tuple(blocks) if blocks else ("lookback_total",)
    clean, dropped = [], []
    for record in records:
        values = np.concatenate([
            np.asarray(record[name], dtype=np.float64)
            for name in blocks if name in record
        ]) if any(name in record for name in blocks) else np.empty(0)
        (dropped if values.size and not np.isfinite(values).all() else clean).append(record)
    return clean, dropped


# ---------------------------------------------------------------- the mixed aggregation
#
# A seventh candidate for the head axis, added after the first E03 run exposed a gap in the
# search space. ``topk_heads`` thins *every* block, including the single narrow one, so the
# chosen k=32 gave the aggregate lookback ratio 32 columns where E02 had 756 — and E03 lost
# 0,045 on the intrinsic class those columns carried. This mode keeps the ``basic`` block whole
# and thins only the wide chunk-shape blocks, so the search space contains E02 as a special
# case. Lived in ``scripts/run_chunk_aware.py`` until T36; E15 chose it on ViWikiFC, so a saved
# detector has to be able to rebuild it.
MIXED = "mixed_all_basic_topk_rest"


def split_groups(groups) -> tuple[list[str], list[str]]:
    """Separate the aggregate lookback group from the chunk-shape ones."""
    wide = [group for group in groups if group != "basic"]
    return (["basic"] if "basic" in groups else []), wide


def build_mixed(records, groups, n_layers: int, n_heads: int, keep) -> np.ndarray:
    """All heads for ``basic``, only the chosen ones for the wide blocks."""
    narrow, wide = split_groups(groups)
    parts = []
    if narrow:
        parts.append(build_feature_matrix(records, narrow, n_layers, n_heads, "all"))
    if wide:
        parts.append(build_feature_matrix(records, wide, n_layers, n_heads, "topk_heads", keep))
    return np.hstack(parts)


def mixed_names(groups, layer_indices, n_heads: int, keep) -> list[str]:
    narrow, wide = split_groups(groups)
    names = []
    if narrow:
        names += column_names(blocks_for(narrow), layer_indices, n_heads, "all")
    if wide:
        names += column_names(blocks_for(wide), layer_indices, n_heads, "topk_heads", keep)
    return names


def build_matrix(records, groups, n_layers: int, n_heads: int, mode: str,
                 keep=None) -> np.ndarray:
    """One entry point for every aggregation mode a detector may have been fitted with.

    This is the function a saved detector must call on a new record: whichever of the seven
    candidates dev chose at training time, the same call rebuilds the same columns in the
    same order.
    """
    if mode == MIXED:
        return build_mixed(records, groups, n_layers, n_heads, keep)
    return build_feature_matrix(records, groups, n_layers, n_heads, mode, keep)


def matrix_names(groups, layer_indices, n_heads: int, mode: str, keep=None) -> list[str]:
    """Column names for :func:`build_matrix`, for whichever mode it was given."""
    if mode == MIXED:
        return mixed_names(groups, layer_indices, n_heads, keep)
    return column_names(blocks_for(groups), layer_indices, n_heads, mode, keep)
