"""Every model the experiments load is pinned to one Hugging Face commit."""

import re
from pathlib import Path

import yaml

from vihallulens.detect.encoder import MODELS
from vihallulens.revisions import MODEL_REVISIONS, revision_for
from vihallulens.serve.rag import GENERATOR_MODEL

CONFIGS = Path(__file__).resolve().parents[1] / "configs"


def test_every_reading_model_in_configs_is_pinned():
    names = set()
    for path in CONFIGS.glob("*.yaml"):
        extractor = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("extractor")
        if extractor:
            names.add(extractor["model_name"])
    assert names, "no extractor section found in configs/"
    assert names <= MODEL_REVISIONS.keys(), names - MODEL_REVISIONS.keys()


def test_encoder_baselines_and_demo_generator_are_pinned():
    for spec in MODELS.values():
        assert revision_for(spec["name"]) is not None, spec["name"]
    assert revision_for(GENERATOR_MODEL) is not None


def test_pins_are_full_commit_hashes():
    for name, commit in MODEL_REVISIONS.items():
        assert re.fullmatch(r"[0-9a-f]{40}", commit), name


def test_unknown_model_falls_back_to_latest():
    assert revision_for("someone/new-model") is None
