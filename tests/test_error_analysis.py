"""Tests for the structural error tags and the error sampler (task T35).

The tags decide what the 100-row CSV says about each mistake, and the sampler decides which
mistakes get into it. Both are deterministic rules that a reader will treat as facts about the
model, so they get tested as rules: given these measurements, this tag; given these counts,
this many rows per confusion pair.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from error_analysis import (  # noqa: E402
    BORDERLINE,
    CONFIDENT,
    OVERLAP_HIGH,
    OVERLAP_LOW,
    SHORT_RESPONSE,
    TAG_ORDER,
    stored_predictions,
    stratified_errors,
    tag_row,
)


def row(**over):
    base = {"label": "intrinsic", "prompt_type": "unknown", "n_chunks": 5,
            "lexical_overlap": 0.6, "response_words": 30, "confidence": 0.55, "margin": 0.3}
    base.update(over)
    return pd.Series(base)


def test_every_flag_is_a_column_and_khac_means_none():
    tag, flags = tag_row(row())
    assert set(flags) == {name for name, _ in TAG_ORDER}
    assert tag == "khac"
    assert flags["khac"] and not any(v for k, v in flags.items() if k != "khac")


@pytest.mark.parametrize("over, expected", [
    ({"prompt_type": "noisy"}, "prompt_noisy"),
    ({"n_chunks": 1}, "mot_doan"),
    ({"label": "extrinsic", "lexical_overlap": OVERLAP_HIGH}, "chep_lai_ma_sai"),
    ({"label": "no", "lexical_overlap": OVERLAP_LOW}, "dien_dat_lai"),
    ({"response_words": SHORT_RESPONSE - 1}, "phan_hoi_ngan"),
    ({"confidence": CONFIDENT}, "tu_tin_sai"),
    ({"margin": BORDERLINE - 0.01}, "phan_van"),
])
def test_each_tag_fires_on_its_own_condition(over, expected):
    tag, flags = tag_row(row(**over))
    assert tag == expected
    assert flags[expected]


def test_copy_tag_only_for_hallucinated_labels():
    """High overlap on a faithful answer is the normal case, not an error pattern."""
    _, flags = tag_row(row(label="no", lexical_overlap=0.95))
    assert not flags["chep_lai_ma_sai"]


def test_paraphrase_tag_only_for_faithful_labels():
    _, flags = tag_row(row(label="extrinsic", lexical_overlap=0.2))
    assert not flags["dien_dat_lai"]


def test_priority_puts_input_excuses_before_confidence_verdicts():
    """A noisy prompt that the model was also confident about is tagged by the input first."""
    tag, flags = tag_row(row(prompt_type="noisy", confidence=0.99))
    assert tag == "prompt_noisy"
    assert flags["tu_tin_sai"]   # still recorded, in its own column


def errors_frame(counts: dict[str, int]) -> pd.DataFrame:
    rows = []
    for pair, n in counts.items():
        for i in range(n):
            rows.append({"sample_id": f"{pair}_{i}", "cap_nham": pair})
    return pd.DataFrame(rows)


def test_sampler_keeps_everything_when_fewer_than_n():
    frame = errors_frame({"a→b": 30, "b→a": 20})
    assert len(stratified_errors(frame, 100, seed=42)) == 50


def test_sampler_is_proportional_and_sums_exactly_to_n():
    """60/30/10 of 200 errors should give 60/30/10 of the 100 rows, not 34/33/33."""
    frame = errors_frame({"a→b": 120, "b→a": 60, "c→a": 20})
    out = stratified_errors(frame, 100, seed=42)
    assert len(out) == 100
    assert out["cap_nham"].value_counts().to_dict() == {"a→b": 60, "b→a": 30, "c→a": 10}


def test_sampler_largest_remainder_rounding():
    """Shares that do not divide evenly still total n, with the extras going to the largest
    fractional parts rather than being dropped or duplicated."""
    frame = errors_frame({"a→b": 7, "b→a": 7, "c→a": 7})  # 21 errors, ask for 10
    out = stratified_errors(frame, 10, seed=42)
    counts = out["cap_nham"].value_counts()
    assert counts.sum() == 10
    assert sorted(counts.values) == [3, 3, 4]


def test_sampler_is_deterministic():
    frame = errors_frame({"a→b": 50, "b→a": 50})
    a = stratified_errors(frame, 20, seed=42)["sample_id"].tolist()
    b = stratified_errors(frame, 20, seed=42)["sample_id"].tolist()
    assert a == b


def test_stored_predictions_last_row_wins(tmp_path):
    path = tmp_path / "runs.jsonl"
    rows = [
        {"run_name": "e03", "extra": {"y_pred": ["no"]}},
        {"run_name": "e03", "extra": {"y_pred": ["intrinsic", "no"]}},
    ]
    path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    assert stored_predictions(path, "e03") == ["intrinsic", "no"]
    assert stored_predictions(path, "missing") is None
