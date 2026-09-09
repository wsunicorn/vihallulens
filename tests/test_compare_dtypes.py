"""Tests for the dtype comparison report, added at T31.

The 09/09 ladder run died inside this report rather than inside the GPU work it summarises.
Qwen2.5-1.5B overflows in float16 on *every* one of its 28 layers, so the set of surviving
layers was empty, the array of differences had size zero, and ``np.percentile`` raised
IndexError on it. Cell 6 of the notebook read that non-zero exit code as "the probe is broken"
and aborted the session — taking the four remaining cells of the 3B rung with it, even though
the 3B rung had already finished cleanly.

The report has to treat "no layer survives" as a result it can state, because it is one: it
says the model cannot be read at this dtype at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from compare_dtypes import overall_report, per_layer_report  # noqa: E402

N_LAYERS = 4
N_VALUES = 6


def run(nonfinite_per_sample, offset=0.01):
    """Two runs over the same samples, differing by a constant so |Δ| is predictable."""
    low, high = [], []
    for bad in nonfinite_per_sample:
        total = np.full((N_LAYERS, N_VALUES), 0.5, dtype=np.float32)
        bad = list(bad)
        for layer in bad:
            total[layer] = np.nan
        low.append({"total": total, "nonfinite": set(bad)})
        high.append({"total": np.full((N_LAYERS, N_VALUES), 0.5 + offset, dtype=np.float32),
                     "nonfinite": set()})
    return low, high


def test_every_layer_broken_reports_instead_of_raising(capsys):
    """The 1.5B case: all layers nan on all samples, so there is nothing left to compare."""
    broken = list(range(N_LAYERS))
    low, high = run([broken, broken, broken])

    overall_report(low, high, N_LAYERS, broken)

    printed = capsys.readouterr().out
    assert "KHÔNG còn lớp nào" in printed
    assert f"cả {N_LAYERS} lớp" in printed
    # The advice matters as much as the diagnosis: dtype is a settled decision in CLAUDE.md.
    assert "phải hỏi" in printed


def test_per_layer_report_survives_all_nan(capsys):
    """The table above the summary must not claim a 'worst clean layer' when none is clean."""
    broken = list(range(N_LAYERS))
    low, high = run([broken, broken, broken])

    per_layer_report(low, high, N_LAYERS)

    printed = capsys.readouterr().out
    assert "Không có lớp nào sống sót" in printed
    assert "None" not in printed


def test_some_layers_broken_still_reports_drift(capsys):
    """The 7B case: one bad layer, the rest usable, and the drift figure is over the rest."""
    low, high = run([[3], [3], [3]], offset=0.01)

    overall_report(low, high, N_LAYERS, [3])

    printed = capsys.readouterr().out
    assert "còn 3 lớp" in printed
    assert "0.01000" in printed


def test_no_layer_broken_reports_all_layers(capsys):
    """The 3B case: nothing overflows, so the drift figure covers the whole network."""
    low, high = run([[], [], []], offset=0.02)

    overall_report(low, high, N_LAYERS, [])

    printed = capsys.readouterr().out
    assert f"còn {N_LAYERS} lớp" in printed
    assert "0.02000" in printed


def test_layers_clean_but_no_finite_sample(capsys):
    """A layer can be listed clean yet never yield a finite row on any sample.

    ``nonfinite`` is recorded per layer per sample, so a layer absent from every sample's set
    is 'clean' — but the reference run can still carry a nan that makes the difference nan.
    Reporting zero comparable values beats reporting a mean over nothing.
    """
    low, high = run([[], []])
    for item in high:
        item["total"][1, 0] = np.nan

    overall_report(low, high, N_LAYERS, [])

    printed = capsys.readouterr().out
    assert "không tính được" in printed


@pytest.mark.parametrize("broken", [[], [0], [0, 1, 2, 3]])
def test_report_never_raises(broken, capsys):
    """Whatever the overflow pattern, the summary is a report, not a source of exceptions."""
    low, high = run([broken, broken])
    overall_report(low, high, N_LAYERS, broken)
    per_layer_report(low, high, N_LAYERS)
    capsys.readouterr()
