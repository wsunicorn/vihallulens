"""Locating the evidence by cutting the context apart. Experiment E19.

E06 asked where the model *looked*: the chunk receiving the most attention is the chunk it
relied on. ContextCite (Cohen-Wang et al., NeurIPS 2024) argues that attention weights are often
not faithful for attributing a response to its sources, and that the reliable test is causal:
remove a source and measure how much the model's output changes. ARC-JSD does this per chunk
with the Jensen–Shannon divergence between the next-token distributions over the response,
with and without the chunk.

This module implements that baseline on the samples, model, prompt and chunking E08 used, so
its hit@1 can stand next to the attention heads' on the same 300 samples:

    score(chunk k) = sum over response tokens t of JSD( p(t | full context), p(t | context - k) )

The chunk with the largest score is the one the response depends on most. One sample costs
``1 + n_chunks`` forward passes against attention's one, which is the trade-off E19 reports.

Logits need a dtype that does not overflow: Qwen2.5-7B in float16 sends layer 27's overflow
into the language-model head and returns nan probabilities (measured at T40), so the reader runs
in bfloat16 here. Attention never needed the head, which is why E08 could run in float16.
"""

from __future__ import annotations

import hashlib
import math
import time

import numpy as np
import torch

from vihallulens.data.chunking import Chunk
from vihallulens.extract.attention import token_span
from vihallulens.extract.prompt import render_prompt
from vihallulens.revisions import revision_for

N_SAMPLES = 300
SELECTION_SEED = 42
COMPUTE_DTYPE = "bfloat16"

# Written before the ablation run (22/10/2026), locked by tests/test_attribution.py so a result
# that goes the other way cannot quietly be re-described as a confirmation.
#   1. ablation reaches a higher hit@1 than the best attention head on the same samples;
#   2. but the gain is smaller than the cost: hit@1(ablation) / hit@1(best head) stays below the
#      ratio of forward passes per sample (about 10.8 to 1).
PREDICTION = {
    "ablation_hit1_above_best_head": True,
    "hit1_ratio_below_forward_ratio": True,
}


def context_digest(context: str) -> str:
    """SHA-256 of a context, to check a rebuilt context is the one the shard was extracted on."""
    return hashlib.sha256(context.encode("utf-8")).hexdigest()


def select_samples(
    candidates: list[str], n: int = N_SAMPLES, seed: int = SELECTION_SEED
) -> list[str]:
    """A seeded random subset of sample ids, independent of the order they arrive in."""
    pool = sorted(set(candidates))
    rng = np.random.default_rng(seed)
    picked = rng.choice(len(pool), size=min(n, len(pool)), replace=False)
    return sorted(pool[i] for i in picked)


def drop_chunk(context: str, chunk: Chunk) -> str:
    """The context with one chunk cut out and the gap closed to a single space."""
    if context[chunk.char_start : chunk.char_end] != chunk.text:
        raise ValueError(f"đoạn {chunk.index} không khớp vị trí của nó trong ngữ cảnh")
    left = context[: chunk.char_start].rstrip()
    right = context[chunk.char_end :].lstrip()
    if not left or not right:
        return left + right
    return f"{left} {right}"


def jensen_shannon(logp: torch.Tensor, logq: torch.Tensor) -> torch.Tensor:
    """Jensen–Shannon divergence in nats between rows of two log-distributions, shape (T, V)."""
    logp, logq = logp.float(), logq.float()
    logm = torch.logaddexp(logp, logq) - math.log(2.0)
    kl_pm = (logp.exp() * (logp - logm)).sum(dim=-1)
    kl_qm = (logq.exp() * (logq - logm)).sum(dim=-1)
    return 0.5 * (kl_pm + kl_qm)


def gold_rank_of(scores, gold: int) -> int:
    """0-based rank of the gold chunk, ties broken pessimistically as in E06's ``gold_rank``."""
    scores = np.asarray(scores, dtype=np.float64)
    if not 0 <= gold < len(scores):
        raise ValueError(f"đoạn vàng {gold} nằm ngoài {len(scores)} đoạn")
    return int((scores >= scores[gold]).sum() - 1)


class AblationAttributor:
    """The reading model, loaded to return next-token distributions over the response."""

    def __init__(self, model_name: str, compute_dtype: str = COMPUTE_DTYPE, device: str = "cuda"):
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if str(device).startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("cắt bỏ ngữ cảnh cần CUDA — NF4 không chạy trên CPU")
        revision = revision_for(model_name)
        torch_dtype = getattr(torch, compute_dtype)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
        kwargs = {
            "attn_implementation": "sdpa",
            "revision": revision,
            "quantization_config": BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch_dtype,
                bnb_4bit_use_double_quant=True,
            ),
            "device_map": {"": 0},
        }
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch_dtype, **kwargs)
        except TypeError:  # transformers 4.x still spells it torch_dtype
            model = AutoModelForCausalLM.from_pretrained(
                model_name, torch_dtype=torch_dtype, **kwargs
            )
        model.eval()
        self.model = model
        self.model_name = model_name
        self.compute_dtype = compute_dtype
        self.device = device

    def response_logprobs(self, context: str, question: str, response: str):
        """Log-distribution predicting each response token, and the response token ids."""
        prompt = render_prompt(self.tokenizer, context, question, response)
        encoded = self.tokenizer(prompt.text, add_special_tokens=False, return_offsets_mapping=True)
        ids = encoded["input_ids"]
        offsets = [tuple(pair) for pair in encoded["offset_mapping"]]
        positions = token_span(offsets, prompt.response_start, prompt.response_end)
        if not positions or positions[0] == 0:
            raise ValueError("không tìm thấy token phản hồi trong prompt")
        first = positions[0]
        input_ids = torch.tensor([ids], device=self.device)
        # Logits at position p - 1 predict token p, so only the tail from ``first - 1`` is needed.
        keep = len(ids) - (first - 1)
        with torch.inference_mode():
            try:
                logits = self.model(input_ids=input_ids, logits_to_keep=keep).logits[0]
            except TypeError:  # older transformers without logits_to_keep
                logits = self.model(input_ids=input_ids).logits[0]
            # Row i of the returned logits sits at absolute position len(ids) - len(logits) + i,
            # whether or not logits_to_keep was honoured, so the rows are computed from that.
            offset = len(ids) - logits.shape[0]
            rows = [p - 1 - offset for p in positions]
            logp = torch.log_softmax(logits[rows].float(), dim=-1)
        if not torch.isfinite(logp).all():
            raise FloatingPointError("phân phối đầu ra có giá trị không hữu hạn")
        return logp, [ids[p] for p in positions]

    def attribute(self, context: str, question: str, response: str, chunks: list[Chunk]) -> dict:
        """JSD score of every chunk, plus the cost of computing them."""
        started = time.perf_counter()
        full, tokens = self.response_logprobs(context, question, response)
        scores = []
        for chunk in chunks:
            ablated, ablated_tokens = self.response_logprobs(
                drop_chunk(context, chunk), question, response
            )
            if ablated_tokens != tokens:
                raise ValueError("phản hồi bị tách token khác nhau khi cắt bỏ một đoạn")
            scores.append(float(jensen_shannon(full, ablated).sum()))
        return {
            "scores": scores,
            "n_forward": len(chunks) + 1,
            "n_response_tokens": len(tokens),
            "elapsed_ms": (time.perf_counter() - started) * 1000,
        }
