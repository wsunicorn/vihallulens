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


# -- the T24 control: same density, no overlap, arbitrary boundaries -----------------------------


def control_config():
    return load_config("configs/e05_control_window48_vihallu.yaml")


def test_the_control_does_not_overlap():
    """The whole point of it. With stride equal to the window the chunks tile the context the way
    sentences do, so the only thing left separating it from sentence chunking is whether the
    boundaries mean anything."""
    chunking = control_config().chunking
    assert chunking.stride == chunking.window_size == 48


def test_the_control_is_its_own_extraction():
    """Different boundaries, different per-chunk array — it cannot reuse any earlier shard."""
    others = {
        extraction_hash(load_config(f"configs/{name}.yaml"))
        for name in ("e03_chunk_sentence_vihallu", "e04_chunk_window64_vihallu",
                     "e04_chunk_window128_vihallu", "e04_chunk_window256_vihallu")
    }
    assert extraction_hash(control_config()) not in others


def test_the_control_differs_from_e03_only_in_the_cutting():
    """A control that also changed the reading model or the feature groups would answer a
    different question than the one T23 left open."""
    e03 = load_config("configs/e03_chunk_sentence_vihallu.yaml")
    control = control_config()
    assert control.extractor.model_dump() == e03.extractor.model_dump()
    assert control.features.groups == e03.features.groups
    assert control.detector.model_dump() == e03.detector.model_dump()
    assert control.dataset.model_dump() == e03.dataset.model_dump()


def test_the_control_window_matches_sentence_density():
    """Measured on CPU at T24: window 48 tiling gives 5,56 chunks against 5,29 for sentences, so
    the comparison holds chunk count roughly fixed. The first idea — window 128 with stride 128 —
    gives only 2,43 and would have confounded density back in, which is why the size was measured
    rather than guessed. This test pins the size that measurement produced."""
    assert control_config().chunking.window_size == 48


# -- the matched-size comparison E07 needs -------------------------------------------------------


def test_a_subsample_keeps_the_label_balance():
    """The detector is fitted with class_weight='balanced', so a wobble in the class shares
    changes the weights and adds a second difference to a comparison meant to have one."""
    from run_chunk_aware import stratified_sample

    labels = np.array(["no"] * 500 + ["intrinsic"] * 300 + ["extrinsic"] * 200)
    rows = [{"sample_id": f"s{i:04d}"} for i in range(len(labels))]
    _, taken = stratified_sample(rows, labels, 100, 42)
    assert len(taken) == 100
    for label, share in (("no", 0.5), ("intrinsic", 0.3), ("extrinsic", 0.2)):
        assert (taken == label).mean() == pytest.approx(share, abs=0.02), label


def test_asking_for_more_than_there_is_returns_everything():
    from run_chunk_aware import stratified_sample

    labels = np.array(["no"] * 30 + ["intrinsic"] * 30)
    rows = [{"sample_id": f"s{i}"} for i in range(60)]
    rows_out, labels_out = stratified_sample(rows, labels, 500, 42)
    assert len(rows_out) == 60
    assert len(labels_out) == 60


def test_the_subsample_is_the_same_every_time():
    """A different subset each run would make the matched-size number irreproducible, and it is
    reported next to a number that is."""
    from run_chunk_aware import stratified_sample

    labels = np.array(["no", "intrinsic", "extrinsic"] * 200)
    rows = [{"sample_id": f"s{i:04d}"} for i in range(600)]
    first, _ = stratified_sample(rows, labels, 90, 42)
    second, _ = stratified_sample(rows, labels, 90, 42)
    assert [r["sample_id"] for r in first] == [r["sample_id"] for r in second]


def test_rows_and_labels_stay_aligned():
    """The bug worth guarding: sampling rows and labels separately would silently train on
    mislabelled data and still produce a plausible-looking score."""
    from run_chunk_aware import stratified_sample

    labels = np.array([f"L{i % 3}" for i in range(300)])
    rows = [{"sample_id": f"s{i:04d}", "label": labels[i]} for i in range(300)]
    rows_out, labels_out = stratified_sample(rows, labels, 60, 42)
    assert [r["label"] for r in rows_out] == list(labels_out)


# -- the baseline must come from the same dataset ------------------------------------------------


def write_runs(tmp_path, rows):
    import json

    path = tmp_path / "runs.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def run_row(dataset, groups, macro_f1, name, dev_only=False):
    return {
        "run_name": name,
        "config": {"dataset": {"name": dataset}, "features": {"groups": groups}},
        "metrics": {"macro_f1": macro_f1},
        "extra": {"dev_only": dev_only} if dev_only else {},
    }


def test_the_baseline_ignores_other_datasets():
    """The bug this replaced. E02's 0,7465 is a ViHallu number, and the hardcoded version applied
    it to ISE-DSC01 — a different label balance, context length and difficulty. It printed a
    verdict that meant nothing and returned a failure code for it."""
    import tempfile
    from pathlib import Path

    from run_chunk_aware import lookback_baseline

    with tempfile.TemporaryDirectory() as tmp:
        path = write_runs(Path(tmp), [
            run_row("vihallu", ["basic"], 0.7465, "e02_lookback_lens"),
            run_row("isedsc01", ["basic"], 0.6900, "e07_baseline"),
        ])
        assert lookback_baseline("isedsc01", path) == (0.69, "e07_baseline")


def test_no_baseline_on_the_dataset_returns_none():
    """Better than silently borrowing another corpus's number: the caller says there is no
    baseline and refuses to render a verdict."""
    import tempfile
    from pathlib import Path

    from run_chunk_aware import lookback_baseline

    with tempfile.TemporaryDirectory() as tmp:
        path = write_runs(Path(tmp), [run_row("vihallu", ["basic"], 0.7465, "e02")])
        assert lookback_baseline("isedsc01", path) is None


def test_only_lookback_only_runs_count_as_a_baseline():
    """A chunk-aware run on the same dataset is the thing being measured, not the thing to
    measure against."""
    import tempfile
    from pathlib import Path

    from run_chunk_aware import lookback_baseline

    with tempfile.TemporaryDirectory() as tmp:
        path = write_runs(Path(tmp), [
            run_row("isedsc01", ["basic", "chunk_aware", "stability"], 0.99, "e07"),
            run_row("isedsc01", ["basic"], 0.70, "e07_baseline"),
        ])
        assert lookback_baseline("isedsc01", path) == (0.70, "e07_baseline")


def test_a_dev_only_row_is_not_read_as_a_test_score():
    """dev_only rows carry dev_macro_f1, never macro_f1 — but a future row that carried both
    would otherwise slip into the baseline as though the test set had been scored."""
    import tempfile
    from pathlib import Path

    from run_chunk_aware import lookback_baseline

    with tempfile.TemporaryDirectory() as tmp:
        path = write_runs(Path(tmp), [
            run_row("isedsc01", ["basic"], 0.95, "chi_dev", dev_only=True),
            run_row("isedsc01", ["basic"], 0.70, "e07_baseline"),
        ])
        assert lookback_baseline("isedsc01", path) == (0.70, "e07_baseline")
