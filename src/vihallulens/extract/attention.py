"""Attention extraction under teacher forcing, with a per-layer forward hook.

Section 5 of CLAUDE.md explains why this file cannot simply ask for ``output_attentions``:
one layer's attention matrix at 4,096 tokens costs 0.94 GB, so keeping all 28 layers would
need 26 GB on a 16 GB card. A forward hook on every ``self_attn`` reduces each layer to its
chunk sums and hands back ``None`` in place of the matrix, so only one layer is ever live.

The lookback ratio follows the original definition from Lookback Lens, reproduced in section
1 of docs/REFERENCES.md: attention *averaged per source token*, not summed.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field, replace

import numpy as np
import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.prompt import render_prompt

MB = 1024**2
EPSILON = 1e-9


@dataclass(frozen=True)
class PromptLayout:
    """Token positions of everything the lookback ratio needs.

    Template scaffolding tokens belong to neither region: they are not context the model may
    ground itself in, and they are not text the model produced. They are excluded from both
    the numerator and the denominator.
    """

    response_positions: torch.Tensor  # (R,) query rows to score
    context_positions: torch.Tensor  # (C,) all context tokens
    chunk_positions: torch.Tensor  # (C',) context tokens that fall inside a chunk
    chunk_ids: torch.Tensor  # (C',) which chunk each of those belongs to
    chunk_token_counts: torch.Tensor  # (n_chunks,)
    n_chunks: int
    seq_len: int

    @property
    def n_response_tokens(self) -> int:
        return int(self.response_positions.numel())

    def to(self, device: str | torch.device) -> PromptLayout:
        return PromptLayout(
            response_positions=self.response_positions.to(device),
            context_positions=self.context_positions.to(device),
            chunk_positions=self.chunk_positions.to(device),
            chunk_ids=self.chunk_ids.to(device),
            chunk_token_counts=self.chunk_token_counts.to(device),
            n_chunks=self.n_chunks,
            seq_len=self.seq_len,
        )


@dataclass
class AttentionFeatures:
    """Per-layer, per-head lookback signal for one sample. Fields follow docs/SPEC.md 2.2."""

    lookback_per_chunk: np.ndarray  # (n_layers, n_heads, n_response_tokens, n_chunks)
    lookback_total: np.ndarray  # (n_layers, n_heads, n_response_tokens)
    self_attention: np.ndarray  # (n_layers, n_heads, n_response_tokens)
    n_chunks: int
    truncated: bool
    peak_vram_mb: float
    elapsed_ms: float
    layer_indices: list[int] = field(default_factory=list)


def token_span(offsets: list[tuple[int, int]], char_start: int, char_end: int) -> list[int]:
    """Indices of the tokens overlapping a character span.

    A token counts as inside when it overlaps the span at all, so a token straddling a chunk
    boundary is attributed to every chunk it touches rather than being dropped.
    """
    return [
        index
        for index, (start, end) in enumerate(offsets)
        if end > start and start < char_end and end > char_start
    ]


def build_layout(
    offsets: list[tuple[int, int]],
    context_span: tuple[int, int],
    response_span: tuple[int, int],
    chunks: list[Chunk],
    context_char_offset: int,
) -> PromptLayout:
    """Turn character spans into the token positions the hook needs.

    ``context_char_offset`` is where the raw context begins inside the rendered prompt, so a
    chunk's offsets, which refer to the raw context, can be shifted into prompt coordinates.
    """
    context_positions = token_span(offsets, *context_span)
    response_positions = token_span(offsets, *response_span)
    if not context_positions:
        raise ValueError("no tokens fall inside the context span")
    if not response_positions:
        raise ValueError("no tokens fall inside the response span")

    chunk_positions: list[int] = []
    chunk_ids: list[int] = []
    counts = [0] * len(chunks)
    context_set = set(context_positions)
    for chunk in chunks:
        start = context_char_offset + chunk.char_start
        end = context_char_offset + chunk.char_end
        for index in token_span(offsets, start, end):
            if index in context_set:
                chunk_positions.append(index)
                chunk_ids.append(chunk.index)
                counts[chunk.index] += 1

    return PromptLayout(
        response_positions=torch.tensor(response_positions, dtype=torch.long),
        context_positions=torch.tensor(context_positions, dtype=torch.long),
        chunk_positions=torch.tensor(chunk_positions, dtype=torch.long),
        chunk_ids=torch.tensor(chunk_ids, dtype=torch.long),
        chunk_token_counts=torch.tensor(counts, dtype=torch.float32).clamp(min=1.0),
        n_chunks=len(chunks),
        seq_len=len(offsets),
    )


def drop_middle_chunks(
    context: str, chunks: list[Chunk], n_drop: int
) -> tuple[str, list[Chunk]]:
    """Remove a contiguous block of chunks from the middle of the context.

    Truncation has to be done in whole chunks. Cutting characters instead would leave the
    surviving chunks pointing at offsets in the *original* string, so every per-chunk figure
    afterwards would be attributed to the wrong span without anything failing.

    The middle is chosen because the opening and closing of a document carry more of its
    topic, and because ISE-DSC01 spreads evidence throughout, so neither end may be dropped
    wholesale. Surviving chunks are shifted and re-indexed to stay contiguous.
    """
    if n_drop <= 0 or len(chunks) <= 1:
        return context, chunks
    n_drop = min(n_drop, len(chunks) - 1)
    start = (len(chunks) - n_drop) // 2
    end = start + n_drop

    cut_start = chunks[start].char_start
    cut_end = chunks[end - 1].char_end
    gap = cut_end - cut_start
    new_context = context[:cut_start] + context[cut_end:]

    kept: list[Chunk] = []
    for chunk in chunks[:start]:
        kept.append(replace(chunk, index=len(kept)))
    for chunk in chunks[end:]:
        kept.append(
            replace(
                chunk,
                index=len(kept),
                char_start=chunk.char_start - gap,
                char_end=chunk.char_end - gap,
            )
        )
    return new_context, kept


def lookback_from_layer(
    weights: torch.Tensor, layout: PromptLayout
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Reduce one layer's attention matrix to its lookback statistics.

    ``weights`` has shape (batch, heads, q_len, k_len) and only the first batch item is used,
    since extraction runs one sample at a time. Returns per-chunk ratios (heads, response,
    chunks), the pooled context ratio (heads, response) and the self-attention mean.

    This is the whole numerical core, kept free of models and hooks so it can be checked on
    the CPU against attention matrices with known answers.
    """
    rows = weights[0].index_select(1, layout.response_positions).float()  # (H, R, K)

    context_mean = rows.index_select(2, layout.context_positions).sum(-1) / float(
        layout.context_positions.numel()
    )

    own = rows.index_select(2, layout.response_positions)  # (H, R, R)
    # Causal masking zeroes the future, so summing the row and removing the diagonal leaves
    # exactly the tokens generated before the current one.
    preceding = own.sum(-1) - own.diagonal(dim1=-2, dim2=-1)
    divisor = torch.arange(
        layout.n_response_tokens, device=rows.device, dtype=rows.dtype
    ).clamp(min=1.0)
    self_mean = preceding / divisor

    denominator = (context_mean + self_mean).clamp(min=EPSILON)
    lookback_total = context_mean / denominator

    heads, n_response = context_mean.shape
    per_chunk = torch.zeros(heads, n_response, layout.n_chunks, device=rows.device)
    if layout.chunk_positions.numel():
        per_chunk.index_add_(2, layout.chunk_ids, rows.index_select(2, layout.chunk_positions))
    per_chunk /= layout.chunk_token_counts
    per_chunk /= denominator.unsqueeze(-1)

    return per_chunk, lookback_total, self_mean


class AttentionExtractor:
    """Load a reading model once, then score samples one at a time.

    Signature follows section 2.2 of docs/SPEC.md.
    """

    def __init__(
        self,
        model_name: str,
        quantization: str = "nf4",
        max_context_tokens: int = 4096,
        device: str = "cuda",
        layers: list[int] | None = None,
    ) -> None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_name)

        kwargs: dict = {"attn_implementation": "eager"}
        if quantization == "nf4":
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            kwargs["device_map"] = {"": 0}
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16, **kwargs)
        except TypeError:  # transformers 4.x still spells it torch_dtype
            model = AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch.float16, **kwargs
            )
        if quantization != "nf4":
            model = model.to(device)

        self._attach(model, tokenizer, max_context_tokens, layers)
        self.model_name = model_name
        self.device = device

    @classmethod
    def from_components(
        cls,
        model,
        tokenizer,
        max_context_tokens: int = 4096,
        layers: list[int] | None = None,
    ) -> AttentionExtractor:
        """Wrap a model that is already in memory, used by the tiny-model probe of task T07."""
        extractor = cls.__new__(cls)
        extractor._attach(model, tokenizer, max_context_tokens, layers)
        extractor.model_name = getattr(model.config, "name_or_path", "<in-memory>")
        extractor.device = str(next(model.parameters()).device)
        return extractor

    def _attach(self, model, tokenizer, max_context_tokens: int, layers: list[int] | None) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.max_context_tokens = max_context_tokens
        self.model.eval()
        self.decoder_layers = self.model.model.layers
        self.layer_indices = (
            list(range(len(self.decoder_layers))) if layers is None else sorted(layers)
        )

    # -- prompt preparation --------------------------------------------------------------

    def _prompt_length(self, context: str, question: str, response: str) -> int:
        rendered = render_prompt(self.tokenizer, context, question, response)
        return len(self.tokenizer(rendered.text, add_special_tokens=False)["input_ids"])

    def _fit_to_budget(
        self, context: str, question: str, response: str, chunks: list[Chunk]
    ) -> tuple[str, list[Chunk], bool]:
        """Shrink the context to the token budget, keeping context and chunks in step.

        Section 2.2 of docs/SPEC.md asks for middle truncation. It is done a whole block of
        chunks at a time so the surviving chunks keep exact offsets; see drop_middle_chunks.
        """
        truncated = False
        for _ in range(6):
            length = self._prompt_length(context, question, response)
            if length <= self.max_context_tokens:
                return context, chunks, truncated
            if len(chunks) <= 1:
                break
            excess = 1.0 - self.max_context_tokens / length
            n_drop = max(1, math.ceil(len(chunks) * (excess + 0.05)))
            context, chunks = drop_middle_chunks(context, chunks, n_drop)
            truncated = True

        if self._prompt_length(context, question, response) > self.max_context_tokens:
            # A single chunk larger than the whole budget. Nothing in the four corpora comes
            # close, but cutting its middle is better than silently blowing the VRAM budget.
            context = self._clip_text(context)
            chunks = [Chunk(text=context, char_start=0, char_end=len(context), index=0)]
            truncated = True
        return context, chunks, truncated

    def _clip_text(self, context: str) -> str:
        """Last-resort character clip, keeping the head and the tail of the context."""
        ids = self.tokenizer(context, add_special_tokens=False)["input_ids"]
        if len(ids) <= self.max_context_tokens:
            return context
        ratio = self.max_context_tokens / len(ids)
        keep = max(1, int(len(context) * ratio * 0.45))
        return context[:keep] + context[-keep:]

    def _encode(self, prompt_text: str):
        encoded = self.tokenizer(
            prompt_text, add_special_tokens=False, return_offsets_mapping=True
        )
        return encoded["input_ids"], [tuple(pair) for pair in encoded["offset_mapping"]]

    # -- hooks ---------------------------------------------------------------------------

    def _register_hooks(self, layout: PromptLayout, sink: dict[int, tuple]) -> list:
        handles = []
        for layer_index in self.layer_indices:
            module = self.decoder_layers[layer_index].self_attn
            handles.append(module.register_forward_hook(self._make_hook(layer_index, layout, sink)))
        return handles

    def _make_hook(self, layer_index: int, layout: PromptLayout, sink: dict[int, tuple]):
        def hook(module, inputs, output):  # noqa: ARG001 - signature fixed by PyTorch
            if not isinstance(output, tuple) or len(output) < 2 or output[1] is None:
                return output
            weights = output[1]
            per_chunk, total, own = lookback_from_layer(weights, layout)
            sink[layer_index] = (
                per_chunk.cpu().numpy(),
                total.cpu().numpy(),
                own.cpu().numpy(),
            )
            del weights, per_chunk, total, own
            # Returning None in place of the matrix is what stops all_self_attns from
            # accumulating 28 layers worth of attention. See section 5 of CLAUDE.md.
            return (output[0], None, *output[2:])

        return hook

    # -- public API ----------------------------------------------------------------------

    def extract(
        self, context: str, question: str, response: str, chunks: list[Chunk]
    ) -> AttentionFeatures:
        """Run one teacher-forcing pass and return the lookback signal for this sample."""
        if not chunks:
            raise ValueError("at least one chunk is required")

        context, chunks, truncated = self._fit_to_budget(context, question, response, chunks)
        rendered = render_prompt(self.tokenizer, context, question, response)
        input_ids, offsets = self._encode(rendered.text)

        layout = build_layout(
            offsets,
            (rendered.context_start, rendered.context_end),
            (rendered.response_start, rendered.response_end),
            chunks,
            rendered.context_start,
        )

        device = next(self.model.parameters()).device
        layout = layout.to(device)
        tensor = torch.tensor([input_ids], dtype=torch.long, device=device)

        sink: dict[int, tuple] = {}
        handles = self._register_hooks(layout, sink)
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        try:
            with torch.no_grad():
                # output_attentions is deliberately NOT set. Measured on transformers 5.15.0:
                # with eager attention the self_attn hook receives attn_weights either way, so
                # leaving the flag off means all_self_attns never accumulates in the first
                # place. See the T07 note in section 5 of CLAUDE.md.
                self.model(tensor, use_cache=False)
                if not sink:
                    # Older versions only fill attn_weights when asked. Retrying with the flag
                    # is still safe: the hook replaces every matrix with None, so the tuple the
                    # model collects stays empty of tensors.
                    self.model(tensor, output_attentions=True, use_cache=False)
        finally:
            for handle in handles:
                handle.remove()
        elapsed_ms = (time.perf_counter() - started) * 1000

        if not sink:
            raise RuntimeError(
                "no layer produced attention weights. The hook output of this transformers "
                f"version ({self._transformers_version()}) does not carry attn_weights; see "
                "section 5 of CLAUDE.md and pin a version that does."
            )
        missing = [index for index in self.layer_indices if index not in sink]
        if missing:
            raise RuntimeError(f"layers produced no attention weights: {missing}")

        order = [sink[index] for index in self.layer_indices]
        peak = torch.cuda.max_memory_allocated() / MB if torch.cuda.is_available() else 0.0
        return AttentionFeatures(
            lookback_per_chunk=np.stack([item[0] for item in order]).astype(np.float16),
            lookback_total=np.stack([item[1] for item in order]).astype(np.float16),
            self_attention=np.stack([item[2] for item in order]).astype(np.float16),
            n_chunks=len(chunks),
            truncated=truncated,
            peak_vram_mb=peak,
            elapsed_ms=elapsed_ms,
            layer_indices=list(self.layer_indices),
        )

    @staticmethod
    def _transformers_version() -> str:
        import transformers

        return transformers.__version__
