"""Tests for the numerical core of attention extraction.

No model and no GPU: the lookback arithmetic is checked against attention matrices whose
answers are worked out by hand, which is the only way to know the extractor is right rather
than merely running without crashing.
"""

import pytest
import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.attention import (
    PromptLayout,
    build_layout,
    lookback_from_layer,
    token_span,
)


def make_layout(chunk_sizes=(2, 2)):
    """Layout for an 8-token prompt: 0-3 context, 4 scaffolding, 5-7 response."""
    positions, ids, counts = [], [], []
    cursor = 0
    for chunk_index, size in enumerate(chunk_sizes):
        positions.extend(range(cursor, cursor + size))
        ids.extend([chunk_index] * size)
        counts.append(size)
        cursor += size
    return PromptLayout(
        response_positions=torch.tensor([5, 6, 7]),
        context_positions=torch.tensor(list(range(cursor))),
        chunk_positions=torch.tensor(positions),
        chunk_ids=torch.tensor(ids),
        chunk_token_counts=torch.tensor(counts, dtype=torch.float32),
        n_chunks=len(chunk_sizes),
        seq_len=8,
    )


def make_weights(rows: dict[int, dict[int, float]], heads: int = 2, seq: int = 8):
    """Attention matrix with the given (query, key) -> weight entries, zero elsewhere."""
    weights = torch.zeros(1, heads, seq, seq)
    for query, keys in rows.items():
        for key, value in keys.items():
            weights[0, :, query, key] = value
    return weights


# --- token_span -------------------------------------------------------------------------


def test_token_span_selects_overlapping_tokens():
    offsets = [(0, 3), (3, 7), (7, 10), (10, 14)]
    assert token_span(offsets, 3, 10) == [1, 2]


def test_token_span_includes_a_token_straddling_the_boundary():
    offsets = [(0, 5), (5, 10)]
    assert token_span(offsets, 4, 6) == [0, 1]


def test_token_span_ignores_zero_width_special_tokens():
    offsets = [(0, 0), (0, 4), (4, 4)]
    assert token_span(offsets, 0, 4) == [1]


# --- build_layout -----------------------------------------------------------------------


def test_build_layout_maps_chunks_to_token_positions():
    # Prompt "AA BB CC" where the context starts at character 3 and is "BB CC".
    offsets = [(0, 2), (3, 5), (5, 6), (6, 8), (8, 12)]
    chunks = [Chunk(text="BB", char_start=0, char_end=2, index=0),
              Chunk(text="CC", char_start=3, char_end=5, index=1)]
    layout = build_layout(offsets, (3, 8), (8, 12), chunks, context_char_offset=3)

    assert layout.n_chunks == 2
    assert layout.response_positions.tolist() == [4]
    assert layout.context_positions.tolist() == [1, 2, 3]
    assert layout.chunk_ids.tolist() == [0, 1]


def test_build_layout_rejects_a_context_with_no_tokens():
    offsets = [(0, 4), (4, 8)]
    chunks = [Chunk(text="x", char_start=0, char_end=1, index=0)]
    with pytest.raises(ValueError, match="context"):
        build_layout(offsets, (20, 24), (0, 4), chunks, context_char_offset=20)


# --- lookback_from_layer ----------------------------------------------------------------


def test_first_response_token_has_no_history_so_lookback_is_one():
    """Nothing has been generated yet, so all attention that counts is context attention."""
    layout = make_layout()
    weights = make_weights({5: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1}})
    per_chunk, total, own = lookback_from_layer(weights, layout)

    assert own[0, 0].item() == pytest.approx(0.0)
    assert total[0, 0].item() == pytest.approx(1.0)
    assert per_chunk[0, 0].tolist() == pytest.approx([1.0, 1.0])


def test_context_and_self_attention_are_averaged_per_token():
    """The ratio divides by token counts, per the definition in docs/REFERENCES.md."""
    layout = make_layout()
    weights = make_weights({6: {0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 5: 0.3}})
    _, total, own = lookback_from_layer(weights, layout)

    assert own[0, 1].item() == pytest.approx(0.3)  # one preceding token, divisor 1
    assert total[0, 1].item() == pytest.approx(0.05 / 0.35)


def test_self_attention_divides_by_the_number_of_preceding_tokens():
    layout = make_layout()
    weights = make_weights({7: {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.02, 5: 0.1, 6: 0.2, 7: 0.5}})
    _, total, own = lookback_from_layer(weights, layout)

    assert own[0, 2].item() == pytest.approx((0.1 + 0.2) / 2)  # diagonal excluded
    assert total[0, 2].item() == pytest.approx(0.02 / (0.02 + 0.15))


def test_chunks_are_normalised_by_their_own_length():
    """Two chunks holding the same attention mass but different lengths must not tie."""
    layout = make_layout(chunk_sizes=(1, 3))
    weights = make_weights({5: {0: 0.3, 1: 0.1, 2: 0.1, 3: 0.1}})
    per_chunk, _, _ = lookback_from_layer(weights, layout)

    short, long = per_chunk[0, 0].tolist()
    assert short == pytest.approx(3 * long)


def test_scaffolding_tokens_are_ignored_entirely():
    """Token 4 belongs to the chat template and must count in neither region."""
    layout = make_layout()
    without = make_weights({5: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1}})
    with_scaffold = make_weights({5: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.9}})

    a = lookback_from_layer(without, layout)
    b = lookback_from_layer(with_scaffold, layout)
    assert a[1][0, 0].item() == pytest.approx(b[1][0, 0].item())


def test_output_shapes_follow_the_spec():
    layout = make_layout()
    per_chunk, total, own = lookback_from_layer(make_weights({5: {0: 0.5}}, heads=4), layout)
    assert per_chunk.shape == (4, 3, 2)
    assert total.shape == (4, 3)
    assert own.shape == (4, 3)


def test_all_zero_attention_does_not_divide_by_zero():
    layout = make_layout()
    per_chunk, total, own = lookback_from_layer(make_weights({}), layout)
    assert torch.isfinite(per_chunk).all()
    assert torch.isfinite(total).all()
    assert torch.isfinite(own).all()
