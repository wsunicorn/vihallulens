"""Splitting by context group, and measuring the leakage that grouping prevents.

Two samples that share a context are not independent: a model that has seen one during training
has seen most of what the other is made of. Splitting by row would scatter such samples across
train and test, and the test score would then measure memorisation as much as generalisation.
Section 5 of docs/DATA.md therefore fixes the unit of splitting as ``context_id``.

This module also measures the leakage, because two of the four corpora ship an original split
that has it and must be kept anyway for comparability. Something that cannot be fixed still has
to be reported, which is what section 6 of docs/DATA.md is for.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_RATIOS = (0.8, 0.1, 0.1)
SPLIT_NAMES = ("train", "dev", "test")
GROUP_COLUMN = "context_id"


def assert_no_leakage(
    splits: dict[str, pd.DataFrame], group_col: str = GROUP_COLUMN
) -> None:
    """Raise if any group appears in more than one split.

    Section 2.1 of docs/SPEC.md requires this check rather than trusting the split function.
    It is kept public so it can also be run on splits that came from somewhere else — an
    original split shipped with a corpus, or a file someone edited by hand.
    """
    names = list(splits)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            shared = set(splits[first][group_col]) & set(splits[second][group_col])
            if shared:
                sample = sorted(shared)[:3]
                raise ValueError(
                    f"rò rỉ giữa '{first}' và '{second}': {len(shared)} {group_col} xuất hiện ở "
                    f"cả hai tập, ví dụ {sample}"
                )


def group_split(
    df: pd.DataFrame,
    ratios: tuple[float, ...] = DEFAULT_RATIOS,
    seed: int = 42,
    group_col: str = GROUP_COLUMN,
) -> dict[str, pd.DataFrame]:
    """Split a frame into train/dev/test so that no context spans two splits.

    Whole groups are dealt out, never rows, so the ratios are approximate: a group has to land
    somewhere entire. Groups are shuffled with the seed and then each is given to whichever
    split has so far received the smallest share of its own quota, which keeps the result close
    to the requested ratios without letting one large group skew a small split.

    Measured at T14: with the largest ViHallu group at 5 rows and the largest ISE-DSC01 group at
    33, both under 0,1 % of their corpus, the realised ratios land within a fraction of a point
    of 80/10/10.
    """
    if len(ratios) != len(SPLIT_NAMES):
        raise ValueError(f"cần đúng {len(SPLIT_NAMES)} tỷ lệ cho {SPLIT_NAMES}, nhận {ratios}")
    if not np.isclose(sum(ratios), 1.0):
        raise ValueError(f"tổng tỷ lệ phải bằng 1, nhận {sum(ratios)}")
    if any(ratio <= 0 for ratio in ratios):
        raise ValueError(f"mọi tỷ lệ phải dương, nhận {ratios}")
    if group_col not in df.columns:
        raise ValueError(f"không có cột {group_col}")

    sizes = df.groupby(group_col, sort=True).size()
    if len(sizes) < len(SPLIT_NAMES):
        raise ValueError(
            f"chỉ có {len(sizes)} nhóm {group_col}, không đủ chia thành {len(SPLIT_NAMES)} tập"
        )

    # Sorting before shuffling is what makes the seed enough: the group order must not depend
    # on the order rows happened to arrive in.
    order = np.asarray(sizes.index)
    rng = np.random.default_rng(seed)
    rng.shuffle(order)

    targets = {name: ratio * len(df) for name, ratio in zip(SPLIT_NAMES, ratios, strict=True)}
    filled = dict.fromkeys(SPLIT_NAMES, 0)
    assignment: dict[str, str] = {}
    for group in order:
        # "Furthest behind its own quota" rather than "smallest", so dev and test are not
        # starved by train simply because train is bigger.
        name = min(SPLIT_NAMES, key=lambda item: filled[item] / targets[item])
        assignment[group] = name
        filled[name] += int(sizes[group])

    labels = df[group_col].map(assignment)
    splits = {
        name: df[labels == name].copy().reset_index(drop=True) for name in SPLIT_NAMES
    }
    for name, part in splits.items():
        if part.empty:
            raise ValueError(f"tập '{name}' rỗng sau khi chia; dữ liệu quá ít nhóm")
        # The split column has to follow the split, or a frame would claim to be training data
        # while sitting in the test file.
        if "split" in part.columns:
            part["split"] = name

    assert_no_leakage(splits, group_col)
    return splits


def leakage_between(
    first: pd.DataFrame, second: pd.DataFrame, group_col: str = GROUP_COLUMN
) -> dict:
    """How much of ``second`` was already seen in ``first``.

    Counted two ways because they answer different questions. The share of *groups* says how
    much of the material is recycled; the share of *rows* says how much of the score being
    reported rests on it, and it is the larger and more alarming of the two when a repeated
    context carries many samples.
    """
    seen = set(first[group_col])
    groups = set(second[group_col])
    shared_groups = groups & seen
    shared_rows = int(second[group_col].isin(seen).sum())
    return {
        "n_groups": len(groups),
        "shared_groups": len(shared_groups),
        "group_rate": len(shared_groups) / len(groups) if groups else 0.0,
        "n_rows": len(second),
        "shared_rows": shared_rows,
        "row_rate": shared_rows / len(second) if len(second) else 0.0,
    }
