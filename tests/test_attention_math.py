"""Tests for the numerical core of attention extraction.

No model and no GPU: the lookback arithmetic is checked against attention matrices whose
answers are worked out by hand, which is the only way to know the extractor is right rather
than merely running without crashing.

The layout used throughout is an eight-token prompt::

    0 1 2 3   context, split into chunks
    4         chat template scaffolding
    5 6 7     response

Token 5 is the first response token and is never scored, so the results have two columns.
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
    positions, ids, counts = [], [], []
    cursor = 0
    for chunk_index, size in enumerate(chunk_sizes):
        positions.extend(range(cursor, cursor + size))
        ids.extend([chunk_index] * size)
        counts.append(size)
        cursor += size
    return PromptLayout(
        query_positions=torch.tensor([6, 7]),
        response_positions=torch.tensor([5, 6, 7]),
        prompt_positions=torch.tensor([0, 1, 2, 3, 4]),
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


def build_small_layout():
    # Prompt "AA BB CC DDD EEE": context is "BB CC" at characters 3..8, response at 8..16.
    offsets = [(0, 2), (3, 5), (5, 6), (6, 8), (8, 12), (12, 16)]
    chunks = [
        Chunk(text="BB", char_start=0, char_end=2, index=0),
        Chunk(text="CC", char_start=3, char_end=5, index=1),
    ]
    return build_layout(offsets, (3, 8), (8, 16), chunks, context_char_offset=3)


def test_build_layout_maps_chunks_to_token_positions():
    layout = build_small_layout()
    assert layout.n_chunks == 2
    assert layout.context_positions.tolist() == [1, 2, 3]
    assert layout.chunk_ids.tolist() == [0, 1]


def test_build_layout_drops_the_first_response_token_from_the_queries():
    """The first response token has no history, so its ratio is 1 whatever the model did."""
    layout = build_small_layout()
    assert layout.response_positions.tolist() == [4, 5]
    assert layout.query_positions.tolist() == [5]


def test_prompt_positions_cover_everything_before_the_response():
    """The paper's X is the whole input, scaffolding included, not just the context."""
    layout = build_small_layout()
    assert layout.prompt_positions.tolist() == [0, 1, 2, 3]


def test_build_layout_rejects_a_context_with_no_tokens():
    offsets = [(0, 4), (4, 8)]
    chunks = [Chunk(text="x", char_start=0, char_end=1, index=0)]
    with pytest.raises(ValueError, match="context"):
        build_layout(offsets, (20, 24), (0, 8), chunks, context_char_offset=20)


def test_build_layout_rejects_a_single_token_response():
    offsets = [(0, 4), (4, 8)]
    chunks = [Chunk(text="x", char_start=0, char_end=4, index=0)]
    with pytest.raises(ValueError, match="single token"):
        build_layout(offsets, (0, 4), (4, 8), chunks, context_char_offset=0)


# --- lookback_from_layer ----------------------------------------------------------------


def test_output_shapes_drop_the_unscored_first_token():
    layout = make_layout()
    per_chunk, total, context_only, own = lookback_from_layer(
        make_weights({6: {0: 0.5}}, heads=4), layout
    )
    assert per_chunk.shape == (4, 2, 2)
    assert total.shape == (4, 2)
    assert context_only.shape == (4, 2)
    assert own.shape == (4, 2)


def test_context_and_self_attention_are_averaged_per_token():
    """The ratio divides by token counts, per the definition in docs/REFERENCES.md."""
    layout = make_layout()
    weights = make_weights({6: {0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 5: 0.3}})
    _, _, context_only, own = lookback_from_layer(weights, layout)

    assert own[0, 0].item() == pytest.approx(0.3)  # one preceding token, divisor 1
    assert context_only[0, 0].item() == pytest.approx(0.05 / 0.35)


def test_self_attention_divides_by_the_number_of_preceding_tokens():
    layout = make_layout()
    weights = make_weights({7: {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.02, 5: 0.1, 6: 0.2, 7: 0.5}})
    _, _, context_only, own = lookback_from_layer(weights, layout)

    assert own[0, 1].item() == pytest.approx((0.1 + 0.2) / 2)  # own column excluded
    assert context_only[0, 1].item() == pytest.approx(0.02 / (0.02 + 0.15))


def test_the_two_denominators_differ_by_the_scaffolding():
    """lookback_total counts the whole prompt as in the paper; lookback_context does not."""
    layout = make_layout()
    weights = make_weights({6: {0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.4, 5: 0.3}})
    _, total, context_only, _ = lookback_from_layer(weights, layout)

    prompt_mean = (0.05 * 4 + 0.4) / 5
    assert total[0, 0].item() == pytest.approx(prompt_mean / (prompt_mean + 0.3))
    assert context_only[0, 0].item() == pytest.approx(0.05 / 0.35)
    assert total[0, 0].item() != pytest.approx(context_only[0, 0].item())


def test_scaffolding_does_not_touch_the_context_ratio():
    layout = make_layout()
    without = make_weights({6: {0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 5: 0.3}})
    with_scaffold = make_weights({6: {0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.9, 5: 0.3}})

    _, total_a, context_a, _ = lookback_from_layer(without, layout)
    _, total_b, context_b, _ = lookback_from_layer(with_scaffold, layout)

    assert context_a[0, 0].item() == pytest.approx(context_b[0, 0].item())
    assert total_a[0, 0].item() != pytest.approx(total_b[0, 0].item())


def test_chunks_are_normalised_by_their_own_length():
    """Two chunks holding the same attention mass but different lengths must not tie."""
    layout = make_layout(chunk_sizes=(1, 3))
    weights = make_weights({6: {0: 0.3, 1: 0.1, 2: 0.1, 3: 0.1}})
    per_chunk, _, _, _ = lookback_from_layer(weights, layout)

    short, long = per_chunk[0, 0].tolist()
    assert short == pytest.approx(3 * long)


def test_all_zero_attention_does_not_divide_by_zero():
    layout = make_layout()
    per_chunk, total, context_only, own = lookback_from_layer(make_weights({}), layout)
    for tensor in (per_chunk, total, context_only, own):
        assert torch.isfinite(tensor).all()


def test_every_ratio_stays_inside_the_unit_interval():
    layout = make_layout()
    weights = make_weights(
        {
            6: {0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.4, 5: 0.3},
            7: {0: 0.02, 1: 0.02, 2: 0.02, 3: 0.02, 4: 0.1, 5: 0.1, 6: 0.2, 7: 0.5},
        }
    )
    _, total, context_only, _ = lookback_from_layer(weights, layout)
    for tensor in (total, context_only):
        assert float(tensor.min()) >= 0.0
        assert float(tensor.max()) <= 1.0
