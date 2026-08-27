"""Group splitting and leakage measurement.

The one property that matters is that no context ever lands in two splits. Everything else —
the ratios, the ordering, the seed — exists to make that property hold while still producing a
usable split, so the tests lead with it.
"""

import numpy as np
import pandas as pd
import pytest

from vihallulens.data.splits import (
    DEFAULT_RATIOS,
    SPLIT_NAMES,
    assert_no_leakage,
    group_split,
    leakage_between,
)


def corpus(n_groups: int = 300, rows_per_group: int = 3) -> pd.DataFrame:
    records = []
    for group in range(n_groups):
        for index in range(rows_per_group):
            records.append(
                {
                    "sample_id": f"s_{group}_{index}",
                    "context_id": f"ctx_{group:04d}",
                    "split": "train",
                    "label": ("no", "intrinsic", "extrinsic")[index % 3],
                }
            )
    return pd.DataFrame.from_records(records)


# -- the property the whole task exists for ----------------------------------------------


def test_no_context_lands_in_two_splits():
    splits = group_split(corpus())
    for first in SPLIT_NAMES:
        for second in SPLIT_NAMES:
            if first < second:
                shared = set(splits[first]["context_id"]) & set(splits[second]["context_id"])
                assert not shared


def test_every_row_ends_up_in_exactly_one_split():
    frame = corpus()
    splits = group_split(frame)
    placed = pd.concat(splits.values(), ignore_index=True)
    assert len(placed) == len(frame)
    assert set(placed["sample_id"]) == set(frame["sample_id"])


def test_leaking_splits_are_rejected():
    """Section 2.1 of docs/SPEC.md asks for the check rather than trust in the split function,
    so it has to raise on splits that came from anywhere else too."""
    shared = pd.DataFrame({"context_id": ["ctx_0001"]})
    with pytest.raises(ValueError, match="rò rỉ"):
        assert_no_leakage({"train": shared, "test": shared.copy()})


def test_the_error_names_both_splits_and_a_sample_context():
    a = pd.DataFrame({"context_id": ["ctx_a", "ctx_b"]})
    b = pd.DataFrame({"context_id": ["ctx_b"]})
    with pytest.raises(ValueError) as caught:
        assert_no_leakage({"train": a, "dev": b})
    message = str(caught.value)
    assert "train" in message and "dev" in message and "ctx_b" in message


def test_disjoint_splits_pass():
    assert_no_leakage(
        {
            "train": pd.DataFrame({"context_id": ["ctx_a"]}),
            "test": pd.DataFrame({"context_id": ["ctx_b"]}),
        }
    )


# -- ratios ------------------------------------------------------------------------------


def test_the_realised_ratios_are_close_to_the_requested_ones():
    """Whole groups are dealt out, never rows, so the ratios can only be approximate."""
    frame = corpus()
    splits = group_split(frame)
    for name, wanted in zip(SPLIT_NAMES, DEFAULT_RATIOS, strict=True):
        assert abs(len(splits[name]) / len(frame) - wanted) < 0.02


def test_uneven_group_sizes_do_not_starve_the_small_splits():
    """One oversized group must not swallow dev or test. Assignment goes to whichever split is
    furthest behind its own quota, not to whichever is smallest."""
    frame = pd.concat(
        [corpus(n_groups=100, rows_per_group=1),
         pd.DataFrame({"sample_id": [f"big_{i}" for i in range(50)],
                       "context_id": "ctx_big", "split": "train", "label": "no"})],
        ignore_index=True,
    )
    splits = group_split(frame)
    assert all(len(splits[name]) > 0 for name in SPLIT_NAMES)


# -- reproducibility ---------------------------------------------------------------------


def test_the_split_is_the_same_every_time():
    first = group_split(corpus())
    second = group_split(corpus())
    for name in SPLIT_NAMES:
        assert first[name]["sample_id"].tolist() == second[name]["sample_id"].tolist()


def test_the_split_does_not_depend_on_the_order_of_the_rows():
    """Rows arrive in whatever order the Parquet file was written in. If that changed the
    split, regenerating data/interim would silently move samples between train and test."""
    frame = corpus()
    shuffled = frame.sample(frac=1.0, random_state=7).reset_index(drop=True)
    first = group_split(frame)
    second = group_split(shuffled)
    for name in SPLIT_NAMES:
        assert sorted(first[name]["sample_id"]) == sorted(second[name]["sample_id"])


def test_a_different_seed_gives_a_different_split():
    """Otherwise the seed would not be doing anything and reproducibility would be an accident."""
    first = group_split(corpus(), seed=42)
    second = group_split(corpus(), seed=7)
    assert sorted(first["test"]["sample_id"]) != sorted(second["test"]["sample_id"])


# -- the split column --------------------------------------------------------------------


def test_the_split_column_follows_the_split():
    """Otherwise a frame would claim to be training data while sitting in the test file."""
    splits = group_split(corpus())
    for name, part in splits.items():
        assert set(part["split"]) == {name}


# -- bad input ---------------------------------------------------------------------------


@pytest.mark.parametrize("ratios", [(0.8, 0.2), (0.5, 0.3, 0.3), (0.8, 0.2, 0.0)])
def test_impossible_ratios_are_rejected(ratios):
    with pytest.raises(ValueError):
        group_split(corpus(), ratios=ratios)


def test_a_missing_group_column_is_reported():
    with pytest.raises(ValueError, match="context_id"):
        group_split(corpus().drop(columns=["context_id"]))


def test_too_few_groups_to_split_is_reported():
    with pytest.raises(ValueError, match="không đủ chia"):
        group_split(corpus(n_groups=2))


# -- measuring leakage -------------------------------------------------------------------


def test_leakage_is_counted_by_group_and_by_row():
    """Both, because they answer different questions: how much material is recycled, and how
    much of the reported score rests on it."""
    train = pd.DataFrame({"context_id": ["a", "a", "b"]})
    test = pd.DataFrame({"context_id": ["a", "a", "a", "c"]})
    stats = leakage_between(train, test)
    assert stats["shared_groups"] == 1 and stats["n_groups"] == 2
    assert stats["shared_rows"] == 3 and stats["n_rows"] == 4
    assert stats["group_rate"] == pytest.approx(0.5)
    assert stats["row_rate"] == pytest.approx(0.75)


def test_no_overlap_measures_zero():
    stats = leakage_between(
        pd.DataFrame({"context_id": ["a"]}), pd.DataFrame({"context_id": ["b"]})
    )
    assert stats["shared_groups"] == 0
    assert stats["row_rate"] == 0.0


def test_a_group_split_leaks_nothing_by_construction():
    splits = group_split(corpus())
    for later in ("dev", "test"):
        assert leakage_between(splits["train"], splits[later])["shared_rows"] == 0


# -- portability, the reason the ordering is hashed rather than shuffled -------------------


def test_the_order_is_the_same_every_time():
    from vihallulens.data.splits import shuffle_order

    ids = [f"{index:016x}" for index in range(50)]
    assert shuffle_order(ids, 42) == shuffle_order(ids, 42)


def test_the_order_does_not_depend_on_the_order_it_was_given():
    from vihallulens.data.splits import shuffle_order

    ids = [f"{index:016x}" for index in range(50)]
    assert shuffle_order(ids, 42) == shuffle_order(list(reversed(ids)), 42)


def test_a_different_seed_gives_a_different_order():
    from vihallulens.data.splits import shuffle_order

    ids = [f"{index:016x}" for index in range(50)]
    assert shuffle_order(ids, 42) != shuffle_order(ids, 7)


def test_the_order_is_pinned_to_exact_values():
    """The golden test. At T18 the same seed and the same data split 5.598/702/700 on the
    development machine and 5.632/706/662 on Kaggle, because the old ordering leaned on NumPy's
    shuffle and the two machines run different NumPy versions. A split that moves with the
    library version is not reproducible, and every experiment from here rests on this one.

    These values come from SHA-256, which is fixed by the standard rather than by a library, so
    a change here means someone changed the algorithm — not that a dependency was upgraded."""
    from vihallulens.data.splits import shuffle_order

    ids = [f"{index:016x}" for index in range(10)]
    assert shuffle_order(ids, 42)[:4] == [
        "0000000000000005",
        "0000000000000004",
        "0000000000000008",
        "0000000000000006",
    ]


def test_the_split_uses_no_random_generator_at_all():
    """Guards against the fix being undone by someone reaching for numpy again: with the
    global NumPy seed set to something hostile, the split must not budge."""
    frame = corpus()
    before = {name: sorted(part["sample_id"]) for name, part in group_split(frame).items()}
    np.random.seed(1234)
    after = {name: sorted(part["sample_id"]) for name, part in group_split(frame).items()}
    assert before == after
