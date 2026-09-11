"""A minimal RAG system around the detector (task T40): retrieve, answer, score.

Twenty-one short Vietnamese documents, BM25 retrieval, an answer from Qwen2.5-7B, and the
detector's verdict on that answer.

**The answer comes from a second copy of the reading model, loaded in bfloat16.** The first
version of this module generated with the detector's own extractor — one model, zero extra
VRAM — and the Kaggle run of 11/09/2026 returned ``![](https://cdn…!-!-!-`` for every question.
That is not a hallucination, it is ``argmax`` over NaN logits: token id 0 of Qwen2.5 is ``!``.
T07 measured layer 27 overflowing in float16 on every sample; the detector sidesteps it by not
hooking that layer, but the residual stream still runs through layer 27 into the LM head. Teacher
forcing never reads the logits, so scoring is unaffected. Generation reads nothing else.

So the configuration that makes the detector cheap — float16, layer 27 dropped — is the one that
makes the same model unable to write. ``bfloat16`` has float32's exponent range and does not
overflow (T31 measured 0 non-finite layers), at the price of a second 5,5 GB copy and, on a T4
without native bfloat16, roughly four times slower decoding. On Ampere and later the cost
vanishes. The marginal-cost argument of Bảng 8 therefore carries a hardware clause, recorded
there.

The generation prompt is the locked template of CLAUDE.md §8 with ``add_generation_prompt``
instead of a filled assistant turn, so the answer is produced from exactly the string the
detector will later score. Greedy decoding, so the demo is reproducible.

Deliberately small. The point is not the retriever — ``docs/DATA.md`` §8 already chose BM25 for
the same reason at E08 — but that a question typed into the page comes back with an answer
*and* a risk score, end to end, with the context tinted by where the model looked.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from vihallulens.data.retrieval import EvidenceIndex, Hit
from vihallulens.extract.prompt import SYSTEM_PROMPT, build_user_turn

DEMO_CORPUS = Path(__file__).parent / "demo_corpus.jsonl"
DEFAULT_TOP_K = 3
MAX_NEW_TOKENS = 160
GENERATOR_DTYPE = "bfloat16"


def load_corpus(path: Path | str = DEMO_CORPUS) -> pd.DataFrame:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()]
    if not rows:
        raise ValueError(f"kho demo rỗng: {path}")
    return pd.DataFrame(rows)


def corpus_documents(corpus: pd.DataFrame) -> list[dict]:
    return [{"id": r.evidence_id, "title": r.title, "text": r.text}
            for r in corpus.itertuples(index=False)]


def join_context(hits: list[Hit]) -> str:
    """One context string from the retrieved documents, best first, blank line between."""
    return "\n\n".join(hit.text for hit in hits)


class AnswerGenerator:
    """The reading model's weights, loaded a second time in a dtype that can generate.

    NF4 like the extractor, but ``bfloat16`` compute, ``sdpa`` attention (no hooks, nothing to
    read), and the model's own generation config. Built with :meth:`from_pretrained`; the
    constructor takes an already-loaded ``(model, tokenizer)`` so tests can pass fakes.
    """

    def __init__(self, model, tokenizer, model_name: str = "",
                 compute_dtype: str = GENERATOR_DTYPE):
        self.model = model
        self.tokenizer = tokenizer
        self.model_name = model_name
        self.compute_dtype = compute_dtype

    @classmethod
    def from_pretrained(cls, model_name: str, compute_dtype: str = GENERATOR_DTYPE,
                        device: str = "cuda") -> AnswerGenerator:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if str(device).startswith("cuda") and not torch.cuda.is_available():
            raise RuntimeError("bộ sinh cần CUDA — NF4 qua bitsandbytes không chạy trên CPU")
        torch_dtype = getattr(torch, compute_dtype)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        kwargs = {
            "attn_implementation": "sdpa",
            "quantization_config": BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch_dtype, bnb_4bit_use_double_quant=True,
            ),
            "device_map": {"": 0},
        }
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch_dtype, **kwargs)
        except TypeError:  # transformers 4.x still spells it torch_dtype
            model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch_dtype,
                                                         **kwargs)
        model.eval()
        return cls(model, tokenizer, model_name, compute_dtype)

    def generate(self, context: str, question: str,
                 max_new_tokens: int = MAX_NEW_TOKENS) -> str:
        """Answer from the context, with the locked template and greedy decoding."""
        import torch

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_turn(context, question)},
        ]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False,
                                                    add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            output = self.model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id,
            )
        new_tokens = output[0, inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    def describe(self) -> str:
        return f"{self.model_name} · nf4 · {self.compute_dtype} · sdpa, không hook"


@dataclass
class RagAnswer:
    question: str
    retrieved: list[dict]
    context: str
    answer: str
    score: dict
    elapsed_ms: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"question": self.question, "retrieved": self.retrieved, "context": self.context,
                "answer": self.answer, "score": self.score, "elapsed_ms": self.elapsed_ms}


class DemoRAG:
    """Retrieve → answer → score, over the bundled demo corpus.

    ``generator`` is anything with ``generate(context, question) -> str``. Absent, an
    :class:`AnswerGenerator` is loaded **lazily on the first question**, with the same model
    name as the detector's reading model and ``bfloat16`` compute — a second 5,5 GB copy, for
    the reason in the module docstring. Tests pass a fake.
    """

    def __init__(self, detector, corpus: pd.DataFrame | None = None, top_k: int = DEFAULT_TOP_K,
                 generator=None, generator_dtype: str = GENERATOR_DTYPE):
        self.detector = detector
        self.corpus = corpus if corpus is not None else load_corpus()
        self.index = EvidenceIndex(self.corpus)
        self.top_k = top_k
        self._generator = generator
        self.generator_dtype = generator_dtype

    @property
    def generator(self):
        if self._generator is None:
            name = self.detector.bundle.config.get("extractor", {}).get("model_name")
            if not name:
                raise ValueError("bundle không ghi model_name của mô hình đọc — không biết nạp "
                                 "bộ sinh nào")
            device = getattr(self.detector.extractor, "device", "cuda")
            self._generator = AnswerGenerator.from_pretrained(name, self.generator_dtype, device)
        return self._generator

    @property
    def generator_loaded(self) -> bool:
        return self._generator is not None

    def retrieve(self, question: str, top_k: int | None = None) -> list[Hit]:
        return self.index.search(question, k=top_k or self.top_k)

    def ask(self, question: str, top_k: int | None = None) -> RagAnswer:
        timings = {}
        t = time.perf_counter()
        hits = self.retrieve(question, top_k)
        timings["retrieve"] = (time.perf_counter() - t) * 1000
        if not hits:
            raise ValueError("không truy xuất được tài liệu nào cho câu hỏi này")
        context = join_context(hits)

        t = time.perf_counter()
        answer = self.generator.generate(context, question)
        timings["generate"] = (time.perf_counter() - t) * 1000
        if not answer:
            raise ValueError("mô hình không sinh được câu trả lời")

        t = time.perf_counter()
        result = self.detector.score(context, question, answer)
        timings["score"] = (time.perf_counter() - t) * 1000

        return RagAnswer(
            question=question,
            retrieved=[{"id": h.evidence_id, "title": h.title, "score": round(h.score, 3),
                        "rank": h.rank} for h in hits],
            context=context,
            answer=answer,
            score=result.to_dict(),
            elapsed_ms=timings,
        )

    def documents(self) -> list[dict]:
        return corpus_documents(self.corpus)
