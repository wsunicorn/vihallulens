"""Task T23: the config's cutting parameters actually reaching the chunker.

Every test here runs on CPU and exists because the failure it catches would otherwise only show
up on a T4, after a fifty-minute model load, on the first sample of a run that had already been
queued behind two others.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from extract_features import chunking_arguments
from vihallulens.config import extraction_hash, load_config
from vihallulens.data.chunking import chunk_context
from vihallulens.features.chunk_aware import CHUNK_FEATURE_NAMES, chunk_features

WINDOWS = (64, 128, 256)


def window_config(size):
    return load_config(f"configs/e04_chunk_window{size}_vihallu.yaml")


class FakeTokenizer:
    """Enough of a tokenizer for the window strategy: offsets for whitespace-separated words."""

    def __call__(self, text, **kwargs):
        offsets, start = [], 0
        for word in text.split(" "):
            offsets.append((start, start + len(word)))
            start += len(word) + 1
        return {"input_ids": list(range(len(offsets))), "offset_mapping": offsets}


# -- the bug this file was written for -----------------------------------------------------------


def test_the_window_strategy_is_handed_a_tokenizer():
    """The T23 bug. ``chunk_context`` takes ``**kwargs`` and quietly ignores keys a strategy does
    not use, so the caller that passed only ``strategy`` and ``min_words`` was correct for the
    sentence strategy and silently wrong for the window one."""
    arguments = chunking_arguments(window_config(128).chunking, FakeTokenizer())
    assert arguments["tokenizer"] is not None


@pytest.mark.parametrize("size", WINDOWS)
def test_the_configured_window_and_stride_are_handed_over(size):
    """Passing a tokenizer but no window would fall back to ``chunk_context``'s default of 128,
    so all three configs would produce the same chunks and the sweep would compare nothing."""
    arguments = chunking_arguments(window_config(size).chunking, FakeTokenizer())
    assert arguments["window_size"] == size
    assert arguments["stride"] == size // 2


def test_the_sentence_strategy_does_not_grow_a_tokenizer_argument():
    """E02 and E03 must keep cutting exactly as they did before T23, or their stored shards stop
    matching the code that would rebuild them."""
    arguments = chunking_arguments(load_config("configs/e03_chunk_sentence_vihallu.yaml").chunking,
                                   FakeTokenizer())
    assert arguments == {"strategy": "sentence", "min_words": 5}


def test_the_arguments_actually_drive_the_chunker():
    """The end the mapping exists for: feed it straight to ``chunk_context`` and get windows."""
    text = " ".join(f"w{i}" for i in range(300))
    chunks = chunk_context(text, **chunking_arguments(window_config(64).chunking, FakeTokenizer()))
    assert len(chunks) > 1
    assert all(chunk.token_start is not None for chunk in chunks)


# -- the three configs are three experiments -----------------------------------------------------


def test_each_window_size_gets_its_own_extraction():
    """Chunk boundaries decide the per-chunk array, so the three windows cannot share a shard the
    way E02 and E03 do — each one is a separate GPU pass."""
    hashes = {size: extraction_hash(window_config(size)) for size in WINDOWS}
    assert len(set(hashes.values())) == len(WINDOWS)


def test_the_windows_do_not_share_the_sentence_extraction():
    sentence = extraction_hash(load_config("configs/e03_chunk_sentence_vihallu.yaml"))
    assert sentence not in {extraction_hash(window_config(size)) for size in WINDOWS}


@pytest.mark.parametrize("size", WINDOWS)
def test_the_windows_ask_for_the_same_feature_groups_as_e03(size):
    """E04 has to differ from E03 in the cutting and nothing else, or the sweep confounds the
    chunk size with the feature set."""
    e03 = load_config("configs/e03_chunk_sentence_vihallu.yaml")
    assert window_config(size).features.groups == e03.features.groups


# -- what a window wider than the context does ---------------------------------------------------


def test_a_single_chunk_makes_the_five_features_constant():
    """Measured on ViHallu at T23: a 256-token window leaves 67 % of contexts in one piece. The
    features stay finite — no NaN reaches the classifier — but they carry no information, which
    is the reason the probe runs before the GPU rather than after."""
    single = np.random.default_rng(0).random((2, 3, 5, 1)).astype(np.float16)
    values = chunk_features(single)
    assert set(values) == set(CHUNK_FEATURE_NAMES)
    assert all(np.isfinite(value).all() for value in values.values())
    constants = {"chunk_entropy": 0.0, "chunk_max_share": 1.0, "chunk_gini": 0.0,
                 "top1_top2_gap": 1.0, "chunk_drift": 0.0}
    for name, expected in constants.items():
        assert values[name] == pytest.approx(expected), name


def test_two_chunks_still_carry_signal():
    """The boundary case that says the constants above are about n=1 and not a broken formula."""
    values = chunk_features(np.random.default_rng(0).random((2, 3, 5, 2)).astype(np.float16))
    assert values["chunk_entropy"].std() > 0


# -- what --dev-only records ---------------------------------------------------------------------


def dev_only_record_block() -> str:
    """The source of the record ``--dev-only`` writes.

    Anchored on ``"dev_only": True`` rather than on ``if args.dev_only:`` — that condition appears
    twice, once for a banner line, and splitting on the first one silently returned the wrong
    block."""
    import inspect

    import run_chunk_aware

    source = inspect.getsource(run_chunk_aware.main)
    assert '"dev_only": True' in source
    return source.split("log_result(")[1].split("path=args.results_path")[0]


def test_dev_only_never_reports_a_cost_it_did_not_measure():
    """Bảng 3 is made of dev numbers, so ``--dev-only`` writes a record — but it must not write
    a *cost*. A 0.0 there would read as a free method in E11's accuracy-versus-cost table, which
    is how the T19 dry-run once overwrote E10's real 8.194 ms with 0.03."""
    block = dev_only_record_block()
    assert '"ms_per_sample": None' in block
    assert '"ms_per_sample": 0.0' not in block


def test_dev_only_metrics_cannot_be_mistaken_for_a_test_score():
    """Every key it writes carries a dev_ prefix, so a later reader of runs.jsonl cannot pick one
    up as a test result and put it in Bảng 1. Called rather than read out of the source, because
    a source-scraping version of this test passed while looking at the wrong block."""
    from run_chunk_aware import dev_metrics_record

    record = dev_metrics_record({
        "dev_macro_f1": 0.75,
        "dev_binary_macro_f1": 0.86,
        "dev_per_class": {"no": 0.8, "intrinsic": 0.7, "extrinsic": 0.75},
    })
    assert record
    assert all(key.startswith("dev_") for key in record), sorted(record)


def test_dev_only_reports_every_class_not_just_the_average():
    """T22 found chunk-aware wins `extrinsic` and loses `intrinsic`. A sweep that reports only the
    macro average cannot say whether the token-window variants share that shape."""
    from run_chunk_aware import dev_metrics_record

    record = dev_metrics_record({
        "dev_macro_f1": 0.75,
        "dev_binary_macro_f1": 0.86,
        "dev_per_class": {"no": 0.8, "intrinsic": 0.7, "extrinsic": 0.75},
    })
    assert record["dev_f1_intrinsic"] == 0.7
    assert {"dev_f1_no", "dev_f1_intrinsic", "dev_f1_extrinsic"} <= set(record)
