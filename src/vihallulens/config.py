"""Experiment configuration: pydantic schema, YAML loading and reproducible hashing.

The schema mirrors section 3 of ``docs/SPEC.md``. Every experiment is declared in a YAML
file under ``configs/``; nothing that influences a result may live outside that file.

All models set ``extra="forbid"`` so a typo in a YAML key raises instead of being silently
ignored, which would otherwise produce two runs that look identical but are not.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Fixed by section 3 of CLAUDE.md. Changing it invalidates every comparison made so far,
# so it may only be changed by editing CLAUDE.md first.
REQUIRED_SPLIT_SEED = 42

DatasetName = Literal["vihallu", "isedsc01", "viwikifc", "vifactcheck"]
ChunkStrategy = Literal["sentence", "token_window"]
Quantization = Literal["nf4", "none"]
FeatureGroup = Literal["surface", "basic", "chunk_aware", "stability", "localization"]
HeadAggregation = Literal["all", "mean_over_heads", "topk_heads"]
DetectorType = Literal["logistic_regression", "linear_svc", "lightgbm"]
ClassWeight = Literal["balanced", "none"]


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DatasetConfig(_Base):
    """Which corpus to run on and how it is split."""

    name: DatasetName
    split_seed: int = REQUIRED_SPLIT_SEED

    @field_validator("split_seed")
    @classmethod
    def _seed_is_locked(cls, value: int) -> int:
        if value != REQUIRED_SPLIT_SEED:
            raise ValueError(
                f"split_seed must stay {REQUIRED_SPLIT_SEED}: section 3 of CLAUDE.md fixes it and "
                f"section 7 forbids changing it. Update CLAUDE.md first if this is deliberate."
            )
        return value


class ChunkingConfig(_Base):
    """How the context is cut into chunks before attention is attributed to them."""

    strategy: ChunkStrategy
    # Used by the "sentence" strategy: sentences shorter than this merge into the previous one.
    min_words: int = Field(default=5, ge=1)
    # Used by the "token_window" strategy.
    window_size: int | None = Field(default=None, ge=1)
    stride: int | None = Field(default=None, ge=1)

    @model_validator(mode="before")
    @classmethod
    def _default_stride_to_half_window(cls, data: Any) -> Any:
        """Fill in the default stride before validation, since the model is frozen afterwards."""
        if isinstance(data, dict) and data.get("strategy") == "token_window":
            window = data.get("window_size")
            if data.get("stride") is None and isinstance(window, int):
                # Half the window, as fixed by experiment E05 in docs/EXPERIMENTS.md.
                data = {**data, "stride": window // 2}
        return data

    @model_validator(mode="after")
    def _check_strategy_fields(self) -> ChunkingConfig:
        if self.strategy == "token_window":
            if self.window_size is None:
                raise ValueError("chunking.window_size is required when strategy is token_window")
            if self.stride is not None and self.stride > self.window_size:
                raise ValueError("chunking.stride must not exceed chunking.window_size")
        return self


class ExtractorConfig(_Base):
    """The reading model that is run under teacher forcing to obtain attention weights."""

    model_name: str
    quantization: Quantization = "nf4"
    max_context_tokens: int = Field(default=4096, ge=128)
    device: str = "cuda"


class FeatureConfig(_Base):
    """Which feature groups enter the classifier and how attention heads are aggregated."""

    groups: list[FeatureGroup] = Field(min_length=1)
    head_aggregation: HeadAggregation = "all"
    topk: int | None = Field(default=None, ge=1)

    @field_validator("groups")
    @classmethod
    def _groups_are_unique(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("features.groups must not contain duplicates")
        return value

    @model_validator(mode="after")
    def _topk_required_for_topk_heads(self) -> FeatureConfig:
        if self.head_aggregation == "topk_heads" and self.topk is None:
            raise ValueError("features.topk is required when head_aggregation is topk_heads")
        return self


class DetectorConfig(_Base):
    """The classifier trained on the feature matrix."""

    type: DetectorType = "logistic_regression"
    class_weight: ClassWeight = "balanced"


class ExperimentConfig(_Base):
    """One complete, reproducible experiment declaration."""

    run_name: str = Field(min_length=1)
    dataset: DatasetConfig
    chunking: ChunkingConfig
    extractor: ExtractorConfig
    features: FeatureConfig
    detector: DetectorConfig

    def to_dict(self) -> dict[str, Any]:
        """Plain dictionary of the whole config, suitable for logging to results/runs.jsonl."""
        return self.model_dump(mode="json")


def load_config(path: str | Path) -> ExperimentConfig:
    """Read a YAML experiment declaration and validate it.

    Raises FileNotFoundError if the path does not exist, TypeError if the file does not hold
    a YAML mapping, and pydantic.ValidationError if a field is missing, unknown or invalid.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"config file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise TypeError(f"config file must contain a YAML mapping at the top level: {path}")
    return ExperimentConfig(**raw)


def config_hash(cfg: ExperimentConfig, length: int = 12) -> str:
    """Short, stable hash of everything in the config that can change a result.

    ``run_name`` is excluded on purpose: it is a label, not a parameter. Two runs that differ
    only by name describe the same experiment and must share a hash, so that re-running under
    a new name is recognisable as a repeat rather than a new configuration.
    """
    payload = cfg.to_dict()
    payload.pop("run_name", None)
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:length]
