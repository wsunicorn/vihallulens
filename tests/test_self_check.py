"""The bookkeeping of the self-check cost measurement; the timing itself needs a GPU."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import measure_self_check as m  # noqa: E402


def frame(n=30):
    return pd.DataFrame({
        "sample_id": [f"s{i:02d}" for i in range(n)],
        "context_id": [f"c{i // 2}" for i in range(n)],
        "question": ["q" if i % 10 else " " for i in range(n)],
    })


def test_samples_do_not_depend_on_row_order():
    a = m.pick_samples(frame(), 8)
    b = m.pick_samples(frame().sample(frac=1, random_state=3), 8)
    assert a["sample_id"].tolist() == b["sample_id"].tolist()
    assert a["context_id"].is_unique
    assert (a["question"].str.strip() != "").all()


def test_every_arm_takes_every_position_and_rounds_mirror():
    assert {m.arm_order(i, 0)[0] for i in range(4)} == set(m.ARMS)
    assert m.arm_order(1, 1) == m.arm_order(1, 0)[::-1]


def sample(a, b, c, r, drift=0.001):
    arms = {k: [{"ms": v, "peak_mb": 10.0}, {"ms": v, "peak_mb": 12.0}]
            for k, v in zip("ABCR", (a, b, c, r), strict=True)}
    pack = {"mean": drift, "max": drift}
    return {"arms": arms, "response_tokens": 10, "prompt_tokens": 100,
            "agreed": {"A": 10, "B": 10, "C": 9},
            "drift": {"total": pack, "context": pack, "per_chunk": pack, "pooled_total": pack}}


def test_summary_contrasts_and_verdicts():
    out = m.summarise([sample(100, 110, 115, 40), sample(200, 220, 230, 60)])
    assert out["contrast"]["C-B"]["ms"] == 7.5
    assert out["contrast"]["B-A"]["ms"] == 15.0
    assert out["contrast"]["C-A"]["ms"] == 22.5
    assert np.isclose(out["contrast"]["C-B"]["share_of_A"], 0.05)
    assert out["agreement"]["C"] == 0.9
    assert out["peak_mb"]["A"] == 12.0
    assert all(out["verdict"].values())


def test_verdicts_can_fail():
    bad = sample(100, 90, 140, 20, drift=0.5)
    assert not any(m.summarise([bad, bad])["verdict"].values())
