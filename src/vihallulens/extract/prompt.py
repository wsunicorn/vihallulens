"""The single prompt template fed to the reading model.

Section 8 of CLAUDE.md locks this template at task T07. It decides the token position of the
context, the question and the response, and therefore every attention figure the project
produces. Changing anything here invalidates every feature extracted so far.

The template uses the model's own chat template, so the reading model works in the mode it
was instruction-tuned for, which is also how a deployed RAG system would call it.
"""

from __future__ import annotations

from dataclasses import dataclass

SYSTEM_PROMPT = "Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp."
CONTEXT_HEADER = "Ngữ cảnh:\n"
QUESTION_HEADER = "\n\nCâu hỏi: "


@dataclass(frozen=True)
class PromptText:
    """The rendered prompt plus the character spans of the two regions that matter."""

    text: str
    context_start: int
    context_end: int
    response_start: int
    response_end: int

    @property
    def context(self) -> str:
        return self.text[self.context_start : self.context_end]

    @property
    def response(self) -> str:
        return self.text[self.response_start : self.response_end]


def build_user_turn(context: str, question: str) -> str:
    """Content of the user turn: the context, then the question when the dataset has one.

    Three of the four corpora are fact-checking sets with no question at all (section 1 of
    docs/DATA.md). Emitting an empty "Câu hỏi:" line for them would add tokens that carry no
    information yet shift every position, so the block is omitted instead.
    """
    user = f"{CONTEXT_HEADER}{context}"
    if question.strip():
        user += f"{QUESTION_HEADER}{question.strip()}"
    return user


def render_prompt(tokenizer, context: str, question: str, response: str) -> PromptText:
    """Render the locked template and locate the context and response inside the result.

    The spans are found by searching the rendered string rather than by counting template
    characters, so a change in the model's chat template cannot silently misalign them.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_turn(context, question)},
        {"role": "assistant", "content": response},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)

    context_start = text.find(context)
    if context_start < 0:
        raise ValueError("context not found in the rendered prompt; the chat template altered it")
    response_start = text.rfind(response)
    if response_start < 0 or response_start < context_start:
        raise ValueError("response not found after the context in the rendered prompt")

    return PromptText(
        text=text,
        context_start=context_start,
        context_end=context_start + len(context),
        response_start=response_start,
        response_end=response_start + len(response),
    )
