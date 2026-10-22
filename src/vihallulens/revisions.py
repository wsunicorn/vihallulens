"""Hugging Face commit of every model the experiments load.

``from_pretrained`` without ``revision`` fetches whatever the model repository holds at run
time, so a later push upstream would silently change the weights under an unchanged config.
Every model used in the thesis is pinned here to the commit that was current when its
experiments ran: checked on 22/10/2026, each repository was last modified before the run that
used it (latest: vinai/phobert-large on 03/08/2026, fine-tuned on 27/08), and the three models
still in the local cache carry the same commit.

The pin lives in code rather than in the YAML configs on purpose. Every feature shard carries
the hash of the full extraction config, so adding a field there would orphan every shard
already extracted.
"""

from __future__ import annotations

MODEL_REVISIONS: dict[str, str] = {
    # reading models (chapter 4, E13, E14) and the demo generator (section 5.6)
    "Qwen/Qwen2.5-7B-Instruct": "a09a35458c702b33eeacc393d103063234e8bc28",
    "Qwen/Qwen2.5-3B-Instruct": "aa8e72537993ba99e69dfaafa59ed015b17504d1",
    "Qwen/Qwen2.5-1.5B-Instruct": "989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    "sail/Sailor2-8B-SFT": "593ac5820c43aa361276b965322207197dcba387",
    # fine-tuned encoder baselines (E09)
    "vinai/phobert-large": "70e2cfcd3cce29c970aee4954ea34a32bb30afdc",
    "FacebookAI/xlm-roberta-large": "c23d21b0620b635a76227c604d44e43a9f0ee389",
    "microsoft/infoxlm-large": "d616d637f0720deda963cebbfc630657d2b7d3ae",
}


def revision_for(model_name: str) -> str | None:
    """Pinned commit for ``model_name``; ``None`` (latest) for a model outside the thesis."""
    return MODEL_REVISIONS.get(model_name)
