"""Lookback features read while the model is generating, instead of in a second pass.

Everything else in this project reads a finished response: one teacher-forcing pass over
prompt plus response. A deployed system in which the generating model is also the reading model
does not need that pass. At each decoding step the model computes exactly the attention row the
teacher-forcing pass would have computed for that token, because causal masking hides the
tokens that come later. This module keeps those rows, reduced the same way as
:func:`vihallulens.extract.attention.lookback_from_layer`, so the cost of detection in that
setting can be measured rather than argued (the self-check part of experiment E11).

Only the cost is measured with it. Whether the two routes agree numerically is checked on every
sample by ``scripts/measure_self_check.py``, and the reduction itself is checked on the CPU in
``tests/test_incremental.py``.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.attention import EPSILON, PromptLayout, build_layout
from vihallulens.extract.prompt import CONTEXT_HEADER, SYSTEM_PROMPT, build_user_turn


@dataclass(frozen=True)
class GenerationPrompt:
    """The locked template up to the point where the model starts answering."""

    text: str
    input_ids: list[int]
    offsets: list[tuple[int, int]]
    context_start: int
    context_end: int

    @property
    def n_tokens(self) -> int:
        return len(self.input_ids)


def render_generation_prompt(tokenizer, context: str, question: str) -> GenerationPrompt:
    """Same system and user turn as the detector scores, with the assistant turn left open."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_turn(context, question)},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    start = text.find(CONTEXT_HEADER + context)
    if start < 0:
        raise ValueError("context not found in the rendered prompt; the chat template altered it")
    start += len(CONTEXT_HEADER)
    encoded = tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)
    return GenerationPrompt(
        text=text,
        input_ids=list(encoded["input_ids"]),
        offsets=[tuple(pair) for pair in encoded["offset_mapping"]],
        context_start=start,
        context_end=start + len(context),
    )


def layout_for_tokens(prompt: GenerationPrompt, n_response: int,
                      chunks: list[Chunk]) -> PromptLayout:
    """The layout of prompt plus ``n_response`` generated tokens.

    Generated tokens are placed by index, not by re-tokenising the decoded answer, so both
    routes score exactly the ids the model produced.
    """
    end = len(prompt.text)
    offsets = prompt.offsets + [(end + i, end + i + 1) for i in range(n_response)]
    return build_layout(
        offsets,
        (prompt.context_start, prompt.context_end),
        (end, end + n_response),
        chunks,
        prompt.context_start,
    )


def lookback_from_row(
    row: torch.Tensor, layout: PromptLayout, n_preceding: int
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """One row of :func:`lookback_from_layer`: shape (heads, keys) in, (heads[, chunks]) out.

    ``n_preceding`` is the number of response tokens generated before this one, which is the
    ``t - 1`` divisor of the paper. Keys beyond the prompt are response tokens, and the last of
    them is the token itself, which the definition leaves out.
    """
    if n_preceding < 1:
        raise ValueError("the first response token has nothing before it and is not scored")
    row = row.float()
    first = int(layout.prompt_positions.numel())
    prompt_mean = row[:, :first].sum(-1) / float(first)
    context_mean = row.index_select(1, layout.context_positions).sum(-1) / float(
        layout.context_positions.numel()
    )
    self_mean = row[:, first : first + n_preceding].sum(-1) / float(n_preceding)
    context_denominator = (context_mean + self_mean).clamp(min=EPSILON)
    total = prompt_mean / (prompt_mean + self_mean).clamp(min=EPSILON)
    per_chunk = torch.zeros(row.shape[0], layout.n_chunks, device=row.device)
    if layout.chunk_positions.numel():
        per_chunk.index_add_(1, layout.chunk_ids, row.index_select(1, layout.chunk_positions))
    per_chunk /= layout.chunk_token_counts
    per_chunk /= context_denominator.unsqueeze(-1)
    return per_chunk, total, context_mean / context_denominator, self_mean


class IncrementalReader:
    """Hooks that reduce every decoding step's attention row, layer by layer."""

    def __init__(self, model, layout: PromptLayout, layer_indices: list[int] | None = None):
        self.layers = model.model.layers
        self.layer_indices = (list(range(len(self.layers))) if layer_indices is None
                              else list(layer_indices))
        self.layout = layout.to(next(model.parameters()).device)
        self.rows: dict[int, list[tuple]] = {index: [] for index in self.layer_indices}
        self._handles: list = []

    def __enter__(self) -> IncrementalReader:
        for index in self.layer_indices:
            hook = self._make_hook(index)
            self._handles.append(self.layers[index].self_attn.register_forward_hook(hook))
        return self

    def __exit__(self, *exc) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles = []

    def _make_hook(self, index: int):
        first = int(self.layout.prompt_positions.numel())

        def hook(module, inputs, output):  # noqa: ARG001 - signature fixed by PyTorch
            if not isinstance(output, tuple) or len(output) < 2 or output[1] is None:
                raise RuntimeError("no attention weights in the hook; is the model in eager mode?")
            weights = output[1]
            n_preceding = weights.shape[-1] - first - 1
            # the prompt pass and the first response token carry nothing to score
            if weights.shape[-2] == 1 and n_preceding >= 1:
                self.rows[index].append(
                    lookback_from_row(weights[0, :, 0, :], self.layout, n_preceding)
                )
            return (output[0], None, *output[2:])

        return hook

    def stacked(self) -> dict[str, torch.Tensor]:
        """Arrays in the order the extractor uses: (layers, heads, scored tokens[, chunks])."""
        names = ("per_chunk", "total", "context", "self_mean")
        out: dict[str, list] = {name: [] for name in names}
        for index in self.layer_indices:
            parts = list(zip(*self.rows[index], strict=True))
            for name, values in zip(names, parts, strict=True):
                out[name].append(torch.stack(values, dim=1))
        return {name: torch.stack(values) for name, values in out.items()}


def decode(model, prompt_ids: list[int], max_new_tokens: int, eos_ids: set[int],
           forced: list[int] | None = None) -> tuple[list[int], bool, int]:
    """Greedy decoding, one token at a time, with a KV cache.

    Returns the response ids, whether every logit was finite, and — when ``forced`` is given —
    how many of the model's own choices agreed with it. Replaying a fixed sequence is what makes
    two attention implementations comparable: a single differing token in half precision would
    otherwise send them down answers of different lengths, and the times would not be about the
    implementation any more.

    Every response token is fed to the model, including the last, so a reader sees a row for
    each of them.
    """
    device = next(model.parameters()).device
    limit = len(forced) if forced is not None else max_new_tokens
    ids: list[int] = []
    agreed = 0
    finite = True
    with torch.no_grad():
        output = model(torch.tensor([prompt_ids], device=device), use_cache=True, logits_to_keep=1)
        while True:
            logits = output.logits[0, -1]
            if forced is None:
                finite = finite and bool(torch.isfinite(logits).all())
            choice = int(logits.argmax())
            if forced is not None:
                if len(ids) == limit:
                    break
                agreed += int(choice == forced[len(ids)])
                token = forced[len(ids)]
            else:
                if len(ids) == limit or choice in eos_ids:
                    break
                token = choice
            ids.append(token)
            output = model(torch.tensor([[token]], device=device), use_cache=True,
                           past_key_values=output.past_key_values, logits_to_keep=1)
    return ids, finite, agreed
