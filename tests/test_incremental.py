"""Reading attention during generation must give what the teacher-forcing pass gives."""

import pytest
import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.attention import build_layout, lookback_from_layer
from vihallulens.extract.incremental import (
    GenerationPrompt,
    IncrementalReader,
    decode,
    layout_for_tokens,
    lookback_from_row,
)

HEADS, PROMPT, RESPONSE = 4, 12, 6


def make_prompt() -> GenerationPrompt:
    """Twelve one-character tokens; characters 2..9 are the context, cut in two chunks."""
    return GenerationPrompt(text="x" * PROMPT, input_ids=list(range(1, PROMPT + 1)),
                            offsets=[(i, i + 1) for i in range(PROMPT)],
                            context_start=2, context_end=10)


CHUNKS = [Chunk(text="xxx", char_start=0, char_end=3, index=0),
          Chunk(text="xxxxx", char_start=3, char_end=8, index=1)]


def causal(n: int) -> torch.Tensor:
    scores = torch.rand(1, HEADS, n, n).masked_fill(
        torch.triu(torch.ones(n, n, dtype=torch.bool), 1), float("-inf"))
    return scores.softmax(-1)


def test_row_matches_the_matrix_reduction():
    torch.manual_seed(0)
    layout = layout_for_tokens(make_prompt(), RESPONSE, CHUNKS)
    weights = causal(PROMPT + RESPONSE)
    whole = lookback_from_layer(weights, layout)
    for step in range(1, RESPONSE):
        row = weights[0, :, PROMPT + step, : PROMPT + step + 1]
        for got, want in zip(lookback_from_row(row, layout, step), whole, strict=True):
            torch.testing.assert_close(got, want[:, step - 1], atol=1e-5, rtol=1e-5)


def test_first_response_token_is_refused():
    layout = layout_for_tokens(make_prompt(), RESPONSE, CHUNKS)
    with pytest.raises(ValueError, match="not scored"):
        lookback_from_row(torch.rand(HEADS, PROMPT + 1), layout, 0)


def test_layout_agrees_with_build_layout():
    prompt = make_prompt()
    layout = layout_for_tokens(prompt, RESPONSE, CHUNKS)
    direct = build_layout([(i, i + 1) for i in range(PROMPT + RESPONSE)], (2, 10),
                          (PROMPT, PROMPT + RESPONSE), CHUNKS, 2)
    assert layout.query_positions.tolist() == direct.query_positions.tolist()
    assert layout.chunk_positions.tolist() == direct.chunk_positions.tolist()


def tiny_model(implementation: str):
    from transformers import Qwen2Config, Qwen2ForCausalLM

    torch.manual_seed(1)
    model = Qwen2ForCausalLM(Qwen2Config(
        vocab_size=64, hidden_size=32, intermediate_size=64, num_hidden_layers=2,
        num_attention_heads=HEADS, num_key_value_heads=2, max_position_embeddings=64))
    model.set_attn_implementation(implementation)
    return model.eval()


def full_pass(model, ids, layout):
    """What the extractor's hook computes on the same ids."""
    out = []

    def hook(module, inputs, output):  # noqa: ARG001
        out.append(lookback_from_layer(output[1], layout))
        return output

    handles = [layer.self_attn.register_forward_hook(hook) for layer in model.model.layers]
    try:
        with torch.no_grad():
            model(torch.tensor([ids]), use_cache=False)
    finally:
        for handle in handles:
            handle.remove()
    return [torch.stack(parts) for parts in zip(*out, strict=True)]


def test_reader_matches_a_teacher_forcing_pass():
    model = tiny_model("eager")
    prompt = make_prompt()
    ids, finite, _ = decode(model, prompt.input_ids, RESPONSE, set())
    assert finite and len(ids) == RESPONSE
    layout = layout_for_tokens(prompt, RESPONSE, CHUNKS)
    with IncrementalReader(model, layout) as reader:
        replay, _, agreed = decode(model, prompt.input_ids, RESPONSE, set(), forced=ids)
    assert replay == ids and agreed == RESPONSE
    got = reader.stacked()
    want = full_pass(model, prompt.input_ids + ids, layout)
    for name, reference in zip(("per_chunk", "total", "context", "self_mean"), want, strict=True):
        assert got[name].shape == reference.shape
        torch.testing.assert_close(got[name], reference, atol=1e-4, rtol=1e-4)
    assert not model.model.layers[0].self_attn._forward_hooks


def test_sdpa_and_eager_replay_the_same_tokens():
    prompt = make_prompt()
    model = tiny_model("sdpa")
    ids, _, _ = decode(model, prompt.input_ids, RESPONSE, set())
    model.set_attn_implementation("eager")
    _, _, agreed = decode(model, prompt.input_ids, RESPONSE, set(), forced=ids)
    assert agreed == RESPONSE


def test_sdpa_has_no_weights_to_read():
    model = tiny_model("sdpa")
    layout = layout_for_tokens(make_prompt(), RESPONSE, CHUNKS)
    with IncrementalReader(model, layout), pytest.raises(RuntimeError, match="eager"):
        decode(model, make_prompt().input_ids, RESPONSE, set())


def test_decoding_stops_at_an_end_token():
    model = tiny_model("eager")
    ids, _, _ = decode(model, make_prompt().input_ids, RESPONSE, set())
    stopped, _, _ = decode(model, make_prompt().input_ids, RESPONSE, {ids[2]})
    assert stopped == ids[: ids.index(ids[2])]
