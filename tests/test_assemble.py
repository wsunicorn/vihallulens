"""Assembling stored feature blocks into a classifier's input matrix.

Two decisions live here and both are made after the GPU has finished: which feature groups enter
the matrix, and how the head axis is reduced. Getting either wrong changes the result without
changing anything the reading model did, so they are worth pinning down.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from vihallulens.config import config_hash, extraction_hash, load_config
from vihallulens.features.assemble import (
    GROUP_BLOCKS,
    aggregate_heads,
    blocks_for,
    build_feature_matrix,
    column_names,
    rank_heads,
    stack_blocks,
)

LAYERS, HEADS = 3, 4
ALL_BLOCKS = [block for names in GROUP_BLOCKS.values() for block in names]


def record(sample_id="s0", fill=None):
    rng = np.random.default_rng(abs(hash(sample_id)) % 1000)
    return {
        "sample_id": sample_id,
        "label": "no",
        **{
            block: ([fill] * (LAYERS * HEADS) if fill is not None
                    else list(rng.random(LAYERS * HEADS)))
            for block in ALL_BLOCKS
        },
    }


def records(n=5):
    return [record(f"s{index}") for index in range(n)]


# -- which groups enter --------------------------------------------------------------------------


def test_the_three_groups_cover_all_six_stored_blocks():
    assert sorted(blocks_for(["basic", "chunk_aware", "stability"])) == sorted(ALL_BLOCKS)


def test_basic_is_exactly_the_reproduction_of_the_paper():
    """``basic`` has to stay the aggregate lookback ratio and nothing else, or E02 and E03 stop
    being comparable and the thesis loses its own control."""
    assert blocks_for(["basic"]) == ["lookback_total"]


def test_drift_is_filed_under_stability_not_chunk_aware():
    """Section 2.3 of docs/SPEC.md separates them, and E12's ablation depends on the split:
    drift is about movement over time, the other four about spread at one moment."""
    assert "chunk_drift" in blocks_for(["stability"])
    assert "chunk_drift" not in blocks_for(["chunk_aware"])


def test_the_column_order_does_not_follow_the_order_groups_were_listed():
    """Two configs naming the same groups have to produce the same layout, or their fitted
    weights are not comparable and a saved model cannot be read by the other."""
    assert blocks_for(["stability", "basic"]) == blocks_for(["basic", "stability"])


def test_a_group_from_another_experiment_is_refused_by_name():
    with pytest.raises(ValueError, match="surface"):
        blocks_for(["basic", "surface"])


# -- reading stored records ----------------------------------------------------------------------


def test_a_block_missing_from_an_old_extraction_says_so():
    """The shards written before T22 hold only the lookback blocks. Failing with the sample ids
    and the fix beats failing with a KeyError three frames deep."""
    rows = [{"sample_id": "s1", "lookback_total": [0.0] * (LAYERS * HEADS)}]
    with pytest.raises(ValueError, match="chunk_entropy"):
        stack_blocks(rows, ["chunk_entropy"], LAYERS, HEADS)


def test_a_block_of_the_wrong_width_is_refused():
    """A shard from a model with a different number of layers would otherwise reshape into
    nonsense that still has the right number of rows."""
    rows = [{"sample_id": "s1", "lookback_total": [0.0] * 7}]
    with pytest.raises(ValueError, match="cần 12"):
        stack_blocks(rows, ["lookback_total"], LAYERS, HEADS)


def test_blocks_are_laid_out_one_after_another():
    rows = [{"sample_id": "s1", "lookback_total": [1.0] * 12, "chunk_drift": [2.0] * 12}]
    stacked = stack_blocks(rows, ["lookback_total", "chunk_drift"], LAYERS, HEADS)
    assert stacked.shape == (1, 24)
    assert list(stacked[0, :12]) == [1.0] * 12
    assert list(stacked[0, 12:]) == [2.0] * 12


# -- reducing the head axis ----------------------------------------------------------------------


def test_keeping_everything_changes_nothing():
    matrix = np.arange(2 * 2 * LAYERS * HEADS, dtype=np.float32).reshape(2, -1)
    assert np.array_equal(aggregate_heads(matrix, 2, LAYERS, HEADS, "all"), matrix)


def test_averaging_heads_leaves_one_column_per_layer():
    matrix = np.ones((5, 2 * LAYERS * HEADS), dtype=np.float32)
    reduced = aggregate_heads(matrix, 2, LAYERS, HEADS, "mean_over_heads")
    assert reduced.shape == (5, 2 * LAYERS)
    assert reduced == pytest.approx(1.0)


def test_averaging_heads_averages_within_a_layer_not_across_layers():
    grid = np.zeros((1, 1, LAYERS, HEADS), dtype=np.float32)
    grid[0, 0, 0] = [1.0, 3.0, 5.0, 7.0]
    grid[0, 0, 1] = 2.0
    reduced = aggregate_heads(grid.reshape(1, -1), 1, LAYERS, HEADS, "mean_over_heads")
    assert reduced[0, 0] == pytest.approx(4.0)
    assert reduced[0, 1] == pytest.approx(2.0)


def test_keeping_k_heads_keeps_them_in_every_block():
    """A head survives for all six statistics or for none. Selecting different heads per
    statistic would make the surviving columns hard to read and would multiply the number of
    choices being made against the dev split."""
    matrix = np.arange(2 * LAYERS * HEADS, dtype=np.float32).reshape(1, -1)
    kept = aggregate_heads(matrix, 2, LAYERS, HEADS, "topk_heads", keep=[0, 5])
    assert kept.shape == (1, 2 * 2)
    assert list(kept[0]) == [0.0, 5.0, 12.0, 17.0]


def test_an_unknown_aggregation_is_refused():
    with pytest.raises(ValueError, match="chưa biết"):
        aggregate_heads(np.zeros((1, 12)), 1, LAYERS, HEADS, "median_over_heads")


def test_topk_without_a_list_of_heads_is_refused():
    with pytest.raises(ValueError, match="cần danh sách"):
        aggregate_heads(np.zeros((1, 12)), 1, LAYERS, HEADS, "topk_heads")


# -- ranking heads -------------------------------------------------------------------------------


def test_a_head_that_matters_for_one_block_survives_the_ranking():
    """Scored by the largest weight across the blocks a pair appears in, not the average, so a
    head carrying one statistic is not voted down by the five that ignore it."""
    weights = np.zeros(3 * LAYERS * HEADS)
    weights[2 * LAYERS * HEADS + 7] = 9.0  # third block, pair 7
    assert rank_heads(weights, 3, LAYERS, HEADS)[0] == 7


def test_the_ranking_covers_every_pair_exactly_once():
    order = rank_heads(np.random.default_rng(0).random(2 * LAYERS * HEADS), 2, LAYERS, HEADS)
    assert sorted(order) == list(range(LAYERS * HEADS))


# -- names line up with columns ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "keep"), [("all", None), ("mean_over_heads", None), ("topk_heads", [0, 5, 11])]
)
def test_every_column_has_exactly_one_name(mode, keep):
    matrix = build_feature_matrix(records(), ["basic", "stability"], LAYERS, HEADS, mode, keep)
    names = column_names(["lookback_total", "chunk_drift"], [0, 1, 2], HEADS, mode, keep)
    assert matrix.shape[1] == len(names)


def test_names_use_the_model_s_own_layer_numbers():
    names = column_names(["lookback_total"], [0, 5, 26], HEADS, "all")
    assert names[-1] == "lookback_total_l26_h3"


def test_a_kept_head_is_named_by_its_real_layer_and_head():
    """Index 5 of a 4-head grid is layer 1, head 1 — and with layer 27 excluded the layer list
    is 0..26, so the name has to come from the list rather than from the position."""
    assert column_names(["lookback_total"], [0, 10, 20], HEADS, "topk_heads", keep=[5]) == [
        "lookback_total_l10_h1"
    ]


def test_the_averaged_names_say_so():
    names = column_names(["chunk_drift"], [0, 1], HEADS, "mean_over_heads")
    assert names == ["chunk_drift_l0_hmean", "chunk_drift_l1_hmean"]


# -- the reason the extraction hash exists -------------------------------------------------------


def test_e02_and_e03_share_one_extraction():
    """The decision this function was added for. Both configs run the same reading model over the
    same data with the same chunking; only the feature groups differ, and those are decided after
    the GPU is finished. Hashing the whole config would spend fifty minutes again for E03."""
    e02 = load_config("configs/e02_lookback_vihallu.yaml")
    e03 = load_config("configs/e03_chunk_sentence_vihallu.yaml")
    assert extraction_hash(e02) == extraction_hash(e03)


def test_they_are_still_two_different_experiments():
    e02 = load_config("configs/e02_lookback_vihallu.yaml")
    e03 = load_config("configs/e03_chunk_sentence_vihallu.yaml")
    assert config_hash(e02) != config_hash(e03)


def test_changing_the_chunking_changes_the_extraction():
    """Per-chunk features depend on where the boundaries fall, so the sentence and token-window
    variants genuinely are different extractions and must not share a shard."""
    e03 = load_config("configs/e03_chunk_sentence_vihallu.yaml")
    windowed = e03.model_copy(
        update={"chunking": e03.chunking.model_copy(
            update={"strategy": "token_window", "window_size": 128, "stride": 64})}
    )
    assert extraction_hash(e03) != extraction_hash(windowed)


def test_the_extraction_hash_ignores_the_run_name():
    e03 = load_config("configs/e03_chunk_sentence_vihallu.yaml")
    renamed = e03.model_copy(update={"run_name": "một cái tên khác"})
    assert extraction_hash(e03) == extraction_hash(renamed)


# -- choosing the aggregation ---------------------------------------------------------------


def test_a_tie_on_dev_goes_to_the_narrower_matrix():
    """Several widths scoring the same on 700 dev samples is common and says the extra columns
    bought nothing. Taking the widest would carry overfitting risk into the test score for no
    measured gain — so the tie-break is deliberate rather than an accident of listing order."""
    from run_chunk_aware import select_aggregation

    rows = {split: [record(f"{split}{i}") for i in range(60)] for split in ("train", "dev")}
    y_train = np.asarray([("no", "intrinsic", "extrinsic")[i % 3] for i in range(60)])
    y_dev = y_train.copy()
    x_train = build_feature_matrix(rows["train"], ["basic"], LAYERS, HEADS)

    best, trials = select_aggregation(
        x_train, y_train, rows, ["basic"], LAYERS, HEADS, y_dev, 42
    )
    top = max(trial["dev_macro_f1"] for trial in trials)
    tied = [trial for trial in trials if trial["dev_macro_f1"] == top]
    assert best["n_features"] == min(trial["n_features"] for trial in tied)


def test_both_scripts_look_for_the_same_shard():
    """The bug this test exists for. T22 split the extraction hash out of the config hash so E02
    and E03 could share one GPU pass, but ``run_lookback_baseline.py`` kept calling the old one
    and could no longer find its own features — which only showed up as a failure at the end of
    a fifty-minute Kaggle run."""
    from extract_features import shard_path as extract_shard
    from run_chunk_aware import load_split  # noqa: F401  (imports the same helper)
    from run_lookback_baseline import main  # noqa: F401  (import proves the module loads)

    cfg = load_config("configs/e02_lookback_vihallu.yaml")
    wanted = extract_shard(Path("data/processed"), extraction_hash(cfg), "vihallu", "train")
    assert wanted.name == f"vihallu_train_{extraction_hash(cfg)}.jsonl"
    assert extraction_hash(cfg) != config_hash(cfg)
