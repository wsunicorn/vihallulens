"""Tests for the append-only result log and the table export."""

import json

import pytest

from vihallulens.config import ExperimentConfig, config_hash
from vihallulens.evaluation.logging import (
    export_table,
    log_result,
    read_results,
)

CONFIG_A = {
    "run_name": "run_a",
    "dataset": {"name": "vihallu", "split_seed": 42},
    "extractor": {"model_name": "Qwen/Qwen2.5-7B-Instruct", "max_context_tokens": 4096},
}
CONFIG_B = {
    "run_name": "run_b",
    "dataset": {"name": "isedsc01", "split_seed": 42},
    "extractor": {"model_name": "Qwen/Qwen2.5-3B-Instruct", "max_context_tokens": 2048},
}
EXTRA = {"ms_per_sample": 12.5, "peak_vram_mb": 8192.0}


def _log_two(path):
    log_result("run_a", CONFIG_A, {"macro_f1": 0.71, "accuracy": 0.73}, EXTRA, path=path)
    log_result(
        "run_b",
        CONFIG_B,
        {"macro_f1": 0.64, "accuracy": 0.66},
        {"ms_per_sample": 40.0, "peak_vram_mb": 5120.0},
        path=path,
    )


# --- the check required by task T04 ---------------------------------------------------


def test_two_calls_then_export_gives_two_rows(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    table = export_table(path=path)
    assert len(table) == 2
    assert list(table["run_name"]) == ["run_a", "run_b"]


# --- record shape ---------------------------------------------------------------------


def test_record_has_every_field_required_by_spec(tmp_path):
    path = tmp_path / "runs.jsonl"
    record = log_result("run_a", CONFIG_A, {"macro_f1": 0.71}, EXTRA, path=path)
    for field in ("timestamp", "git_commit", "config_hash", "config", "metrics", "extra"):
        assert field in record


def test_file_holds_one_json_object_per_line(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    lines = path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    assert all(isinstance(json.loads(line), dict) for line in lines)


def test_logging_is_append_only(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    _log_two(path)
    assert len(read_results(path)) == 4


def test_config_hash_matches_the_one_from_the_model(tmp_path):
    """A dict logged here and the model it came from must hash identically."""
    path = tmp_path / "runs.jsonl"
    cfg = ExperimentConfig(
        run_name="run_a",
        dataset={"name": "vihallu"},
        chunking={"strategy": "sentence"},
        extractor={"model_name": "Qwen/Qwen2.5-7B-Instruct"},
        features={"groups": ["basic"]},
        detector={},
    )
    record = log_result(cfg.run_name, cfg.to_dict(), {"macro_f1": 0.5}, EXTRA, path=path)
    assert record["config_hash"] == config_hash(cfg)


def test_unicode_survives_the_round_trip(tmp_path):
    path = tmp_path / "runs.jsonl"
    log_result("chạy_thử", CONFIG_A, {"ghi_chú": "ảo giác nội tại"}, EXTRA, path=path)
    assert read_results(path)["metrics.ghi_chú"].iloc[0] == "ảo giác nội tại"


# --- the two mandatory operational metrics --------------------------------------------


@pytest.mark.parametrize("missing", ["ms_per_sample", "peak_vram_mb"])
def test_missing_operational_metric_raises(tmp_path, missing):
    extra = {key: value for key, value in EXTRA.items() if key != missing}
    with pytest.raises(ValueError, match=missing):
        log_result("run_a", CONFIG_A, {"macro_f1": 0.7}, extra, path=tmp_path / "runs.jsonl")


def test_nothing_is_written_when_the_extra_check_fails(tmp_path):
    path = tmp_path / "runs.jsonl"
    with pytest.raises(ValueError):
        log_result("run_a", CONFIG_A, {"macro_f1": 0.7}, {}, path=path)
    assert not path.exists()


# --- export -----------------------------------------------------------------------------


def test_nested_objects_become_dotted_columns(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    table = export_table(path=path)
    assert "config.dataset.name" in table.columns
    assert "metrics.macro_f1" in table.columns
    assert "extra.ms_per_sample" in table.columns


def test_filter_selects_matching_runs(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    table = export_table({"config.dataset.name": "isedsc01"}, path=path)
    assert len(table) == 1
    assert table["run_name"].iloc[0] == "run_b"


def test_filter_on_an_unknown_column_returns_no_rows(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    assert len(export_table({"config.khong_ton_tai": 1}, path=path)) == 0


def test_columns_are_kept_in_the_order_given(tmp_path):
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    table = export_table(columns=["metrics.macro_f1", "run_name"], path=path)
    assert list(table.columns) == ["metrics.macro_f1", "run_name"]


def test_a_column_no_run_has_yet_exports_empty(tmp_path):
    """A half-filled result table must still export instead of raising."""
    path = tmp_path / "runs.jsonl"
    _log_two(path)
    table = export_table(columns=["run_name", "metrics.ece"], path=path)
    assert table["metrics.ece"].isna().all()


def test_missing_file_gives_an_empty_frame(tmp_path):
    assert read_results(tmp_path / "khong-co.jsonl").empty
    assert export_table(path=tmp_path / "khong-co.jsonl").empty
