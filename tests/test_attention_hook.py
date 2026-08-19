"""The version-dependent assumptions that task T07 rests on.

Section 5 of CLAUDE.md warns that whether a forward hook on ``self_attn`` receives
``attn_weights`` depends on the transformers version. If a future upgrade changes that, the
extractor would return nothing useful while still running, so it is asserted here rather
than trusted.

The model is built from a config with random weights, so these tests need no download and
no GPU.
"""

import pytest
import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.attention import drop_middle_chunks

HEADS = 4
LAYERS = 2
SEQ = 12


def tiny_model():
    from transformers import Qwen2Config, Qwen2ForCausalLM

    config = Qwen2Config(
        vocab_size=64,
        hidden_size=32,
        intermediate_size=64,
        num_hidden_layers=LAYERS,
        num_attention_heads=HEADS,
        num_key_value_heads=2,
        max_position_embeddings=64,
    )
    model = Qwen2ForCausalLM(config)
    if hasattr(model, "set_attn_implementation"):
        model.set_attn_implementation("eager")
    return model.eval()


def run_with_hook(model, hook):
    handle = model.model.layers[0].self_attn.register_forward_hook(hook)
    try:
        with torch.no_grad():
            model(torch.randint(0, 64, (1, SEQ)), use_cache=False)
    finally:
        handle.remove()


# --- the assumption the whole extractor depends on --------------------------------------


@pytest.mark.parametrize("output_attentions", [False, True])
def test_hook_receives_attention_weights(output_attentions):
    """With eager attention the hook must see the matrix, flag or no flag.

    The extractor deliberately leaves output_attentions off so that all_self_attns never
    accumulates 28 layers. That is only safe while this holds.
    """
    model = tiny_model()
    seen = {}

    def hook(module, inputs, output):
        seen["output"] = output
        return output

    handle = model.model.layers[0].self_attn.register_forward_hook(hook)
    try:
        with torch.no_grad():
            model(
                torch.randint(0, 64, (1, SEQ)),
                use_cache=False,
                output_attentions=output_attentions,
            )
    finally:
        handle.remove()

    output = seen["output"]
    assert isinstance(output, tuple) and len(output) >= 2
    weights = output[1]
    assert weights is not None, (
        "the self_attn hook no longer receives attn_weights; see section 5 of CLAUDE.md "
        "and pin a transformers version that provides them"
    )
    assert weights.shape == (1, HEADS, SEQ, SEQ)


def test_returning_none_in_place_of_the_matrix_does_not_break_the_forward():
    """The hook hands back None to stop the matrices being collected; the model must cope."""
    model = tiny_model()

    def hook(module, inputs, output):
        return (output[0], None, *output[2:])

    run_with_hook(model, hook)  # must not raise


def test_attention_rows_sum_to_one():
    """A sanity check that what the hook sees is post-softmax, not raw scores."""
    model = tiny_model()
    seen = {}

    def hook(module, inputs, output):
        seen["weights"] = output[1]
        return output

    run_with_hook(model, hook)
    rows = seen["weights"][0, :, -1, :]
    assert torch.allclose(rows.sum(-1), torch.ones(HEADS), atol=1e-3)


# --- truncation keeps context and chunks in step ----------------------------------------


def chunks_of(context: str, pieces: list[str]) -> list[Chunk]:
    chunks, cursor = [], 0
    for piece in pieces:
        start = context.index(piece, cursor)
        chunks.append(Chunk(text=piece, char_start=start, char_end=start + len(piece),
                            index=len(chunks)))
        cursor = start + len(piece)
    return chunks


def test_dropping_middle_chunks_keeps_offsets_pointing_at_the_right_text():
    """The bug this guards against loses nothing visibly: offsets simply stop matching."""
    context = "AAA. BBB. CCC. DDD. EEE."
    chunks = chunks_of(context, ["AAA.", "BBB.", "CCC.", "DDD.", "EEE."])

    new_context, kept = drop_middle_chunks(context, chunks, n_drop=2)

    assert len(kept) == 3
    for chunk in kept:
        assert new_context[chunk.char_start : chunk.char_end] == chunk.text


def test_dropping_takes_from_the_middle_not_the_ends():
    context = "AAA. BBB. CCC. DDD. EEE."
    chunks = chunks_of(context, ["AAA.", "BBB.", "CCC.", "DDD.", "EEE."])
    _, kept = drop_middle_chunks(context, chunks, n_drop=3)

    assert [chunk.text for chunk in kept] == ["AAA.", "EEE."]


def test_surviving_chunks_are_reindexed_contiguously():
    context = "AAA. BBB. CCC. DDD. EEE."
    chunks = chunks_of(context, ["AAA.", "BBB.", "CCC.", "DDD.", "EEE."])
    _, kept = drop_middle_chunks(context, chunks, n_drop=2)

    assert [chunk.index for chunk in kept] == [0, 1, 2]


def test_at_least_one_chunk_always_survives():
    context = "AAA. BBB."
    chunks = chunks_of(context, ["AAA.", "BBB."])
    _, kept = drop_middle_chunks(context, chunks, n_drop=99)
    assert len(kept) == 1


def test_dropping_nothing_changes_nothing():
    context = "AAA. BBB."
    chunks = chunks_of(context, ["AAA.", "BBB."])
    new_context, kept = drop_middle_chunks(context, chunks, n_drop=0)
    assert new_context == context
    assert kept == chunks
