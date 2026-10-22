"""E19: context ablation, the pure parts and the logit bookkeeping, on CPU."""

import math
from types import SimpleNamespace

import pytest
import torch

from vihallulens.attribution import (
    PREDICTION,
    AblationAttributor,
    drop_chunk,
    gold_rank_of,
    jensen_shannon,
    select_samples,
)
from vihallulens.data.chunking import chunk_context

CONTEXT = "Câu một nói về Hà Nội. Câu hai nói về Huế cổ. Câu ba nói về Đà Nẵng."


def chunks():
    return chunk_context(CONTEXT, strategy="sentence", min_words=2)


def test_prediction_is_locked():
    # Changing these after the run would turn a failed prediction into a "confirmation".
    assert PREDICTION == {
        "ablation_hit1_above_best_head": True,
        "hit1_ratio_below_forward_ratio": True,
    }


def test_drop_chunk_removes_exactly_one_sentence():
    parts = chunks()
    assert len(parts) == 3
    assert drop_chunk(CONTEXT, parts[1]) == "Câu một nói về Hà Nội. Câu ba nói về Đà Nẵng."
    assert drop_chunk(CONTEXT, parts[0]) == "Câu hai nói về Huế cổ. Câu ba nói về Đà Nẵng."
    assert drop_chunk(CONTEXT, parts[2]) == "Câu một nói về Hà Nội. Câu hai nói về Huế cổ."


def test_drop_chunk_refuses_a_chunk_from_another_context():
    with pytest.raises(ValueError):
        drop_chunk("một ngữ cảnh khác hẳn, dài hơn nhiều chữ", chunks()[1])


def test_jensen_shannon_bounds():
    p = torch.log_softmax(torch.tensor([[2.0, 0.0, -1.0]]), dim=-1)
    q = torch.log_softmax(torch.tensor([[-1.0, 0.0, 2.0]]), dim=-1)
    assert jensen_shannon(p, p).item() == pytest.approx(0.0, abs=1e-7)
    assert jensen_shannon(p, q).item() == pytest.approx(jensen_shannon(q, p).item())
    disjoint_p = torch.log(torch.tensor([[1.0 - 1e-9, 1e-9]]))
    disjoint_q = torch.log(torch.tensor([[1e-9, 1.0 - 1e-9]]))
    assert jensen_shannon(disjoint_p, disjoint_q).item() == pytest.approx(math.log(2), rel=1e-4)


def test_gold_rank_breaks_ties_pessimistically():
    assert gold_rank_of([0.1, 0.9, 0.3], 1) == 0
    assert gold_rank_of([0.1, 0.9, 0.3], 2) == 1
    assert gold_rank_of([0.5, 0.5, 0.1], 0) == 1  # a tie does not count as a hit
    with pytest.raises(ValueError):
        gold_rank_of([0.1, 0.2], 2)


def test_selection_is_seeded_and_order_free():
    ids = [f"s{i:04d}" for i in range(1000)]
    first = select_samples(ids, n=300)
    assert len(first) == 300 and len(set(first)) == 300
    assert select_samples(list(reversed(ids)), n=300) == first
    assert select_samples(ids, n=300, seed=7) != first
    assert select_samples(ids[:10], n=300) == sorted(ids[:10])


class CharTokenizer:
    """One token per character, so offsets are trivial to reason about."""

    def apply_chat_template(self, messages, tokenize=False, add_generation_prompt=False):
        return "".join(f"<{m['role']}>{m['content']}</{m['role']}>" for m in messages)

    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        return {"input_ids": [ord(c) % 97 for c in text],
                "offset_mapping": [(i, i + 1) for i in range(len(text))]}


class NextCharModel(torch.nn.Module):
    """Logits at position i put all mass on (id_i + 1) % 97, and honour logits_to_keep."""

    def __init__(self, honour_keep: bool):
        super().__init__()
        self.honour_keep = honour_keep

    def forward(self, input_ids, logits_to_keep=None):
        ids = input_ids[0]
        logits = torch.full((len(ids), 97), -30.0)
        logits[torch.arange(len(ids)), (ids + 1) % 97] = 30.0
        if self.honour_keep and logits_to_keep:
            logits = logits[-logits_to_keep:]
        return SimpleNamespace(logits=logits[None])


@pytest.mark.parametrize("honour_keep", [True, False])
def test_response_rows_line_up_with_the_tokens_they_predict(honour_keep):
    attributor = AblationAttributor.__new__(AblationAttributor)
    attributor.tokenizer = CharTokenizer()
    attributor.model = NextCharModel(honour_keep)
    attributor.device = "cpu"
    response = "đáp án"
    logp, tokens = attributor.response_logprobs(CONTEXT, "", response)
    assert logp.shape == (len(response), 97)
    assert tokens == CharTokenizer()(response)["input_ids"]
    # Row t was computed at the position just before response token t, so for every token after
    # the first it predicts "next character" of the previous response token. An off-by-one in the
    # row bookkeeping, with or without logits_to_keep, breaks this.
    predicted = logp.argmax(dim=-1).tolist()
    for previous, guess in zip(tokens[:-1], predicted[1:], strict=True):
        assert guess == (previous + 1) % 97
