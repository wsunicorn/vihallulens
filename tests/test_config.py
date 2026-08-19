"""Tests for the experiment configuration schema, loader and hash."""

import pytest
import yaml
from pydantic import ValidationError

from vihallulens.config import ExperimentConfig, config_hash, load_config

EXAMPLE = "configs/example.yaml"


def _valid_dict():
    return {
        "run_name": "test_run",
        "dataset": {"name": "vihallu", "split_seed": 42},
        "chunking": {"strategy": "sentence", "min_words": 5},
        "extractor": {"model_name": "Qwen/Qwen2.5-7B-Instruct", "max_context_tokens": 4096},
        "features": {"groups": ["basic", "chunk_aware"], "head_aggregation": "mean_over_heads"},
        "detector": {"type": "logistic_regression", "class_weight": "balanced"},
    }


def _write(tmp_path, payload, name="cfg.yaml"):
    path = tmp_path / name
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


# --- valid cases -------------------------------------------------------------------


def test_example_config_in_repo_loads():
    cfg = load_config(EXAMPLE)
    assert cfg.dataset.name == "vihallu"
    assert cfg.chunking.strategy == "sentence"
    assert cfg.features.topk == 32


def test_valid_dict_builds():
    cfg = ExperimentConfig(**_valid_dict())
    assert cfg.extractor.quantization == "nf4"  # default
    assert cfg.extractor.device == "cuda"


def test_token_window_stride_defaults_to_half_the_window():
    payload = _valid_dict()
    payload["chunking"] = {"strategy": "token_window", "window_size": 128}
    assert ExperimentConfig(**payload).chunking.stride == 64


# --- missing required fields must raise ----------------------------------------------


@pytest.mark.parametrize("missing", ["run_name", "dataset", "chunking", "extractor", "features"])
def test_missing_required_section_raises(missing):
    payload = _valid_dict()
    del payload[missing]
    with pytest.raises(ValidationError):
        ExperimentConfig(**payload)


def test_missing_model_name_raises():
    payload = _valid_dict()
    del payload["extractor"]["model_name"]
    with pytest.raises(ValidationError):
        ExperimentConfig(**payload)


# --- invalid values must raise -------------------------------------------------------


def test_unknown_key_raises():
    """A typo in a key must raise, otherwise two runs look identical without being so."""
    payload = _valid_dict()
    payload["extractor"]["max_context_token"] = 4096  # missing trailing "s"
    with pytest.raises(ValidationError):
        ExperimentConfig(**payload)


def test_unknown_dataset_raises():
    payload = _valid_dict()
    payload["dataset"]["name"] = "squad"
    with pytest.raises(ValidationError):
        ExperimentConfig(**payload)


def test_changed_split_seed_raises():
    payload = _valid_dict()
    payload["dataset"]["split_seed"] = 7
    with pytest.raises(ValidationError, match="split_seed"):
        ExperimentConfig(**payload)


def test_token_window_without_window_size_raises():
    payload = _valid_dict()
    payload["chunking"] = {"strategy": "token_window"}
    with pytest.raises(ValidationError, match="window_size"):
        ExperimentConfig(**payload)


def test_topk_heads_without_topk_raises():
    payload = _valid_dict()
    payload["features"]["head_aggregation"] = "topk_heads"
    with pytest.raises(ValidationError, match="topk"):
        ExperimentConfig(**payload)


def test_duplicate_feature_groups_raise():
    payload = _valid_dict()
    payload["features"]["groups"] = ["basic", "basic"]
    with pytest.raises(ValidationError):
        ExperimentConfig(**payload)


def test_empty_feature_groups_raise():
    payload = _valid_dict()
    payload["features"]["groups"] = []
    with pytest.raises(ValidationError):
        ExperimentConfig(**payload)


# --- loader --------------------------------------------------------------------------


def test_load_config_roundtrip(tmp_path):
    path = _write(tmp_path, _valid_dict())
    assert load_config(path).run_name == "test_run"


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "does-not-exist.yaml")


def test_non_mapping_file_raises(tmp_path):
    path = tmp_path / "list.yaml"
    path.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(TypeError, match="mapping"):
        load_config(path)


# --- hash ----------------------------------------------------------------------------


def test_hash_is_stable_across_calls():
    cfg = ExperimentConfig(**_valid_dict())
    assert config_hash(cfg) == config_hash(cfg)
    assert len(config_hash(cfg)) == 12


def test_hash_ignores_run_name():
    a = ExperimentConfig(**_valid_dict())
    payload = _valid_dict()
    payload["run_name"] = "a_completely_different_name"
    assert config_hash(a) == config_hash(ExperimentConfig(**payload))


def test_hash_changes_when_a_parameter_changes():
    a = ExperimentConfig(**_valid_dict())
    payload = _valid_dict()
    payload["extractor"]["max_context_tokens"] = 2048
    assert config_hash(a) != config_hash(ExperimentConfig(**payload))


def test_hash_is_order_independent():
    payload = _valid_dict()
    reordered = {k: payload[k] for k in reversed(list(payload))}
    assert config_hash(ExperimentConfig(**payload)) == config_hash(ExperimentConfig(**reordered))


def test_explicit_stride_is_kept():
    payload = _valid_dict()
    payload["chunking"] = {"strategy": "token_window", "window_size": 128, "stride": 32}
    assert ExperimentConfig(**payload).chunking.stride == 32


def test_stride_larger_than_window_raises():
    payload = _valid_dict()
    payload["chunking"] = {"strategy": "token_window", "window_size": 64, "stride": 128}
    with pytest.raises(ValidationError, match="stride"):
        ExperimentConfig(**payload)
