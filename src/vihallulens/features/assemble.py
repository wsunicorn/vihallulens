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
