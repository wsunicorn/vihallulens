"""Chunk representation.

Only the data structure lives here. The two splitting strategies and
``locate_evidence_chunk`` are task T15; this module exists early because
``vihallulens.extract`` needs the type in its signatures from task T07 on.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """One span of the context that attention is attributed to.

    Character offsets refer to the raw context string. Token offsets are filled in by the
    extractor once the context has been placed inside the prompt template, and stay ``None``
    until then, because a chunk has no token position until a tokenizer has seen the prompt.
    """

    text: str
    char_start: int
    char_end: int
    index: int
    token_start: int | None = None
    token_end: int | None = None
