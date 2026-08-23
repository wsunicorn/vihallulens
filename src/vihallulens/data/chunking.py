"""Cutting a context into the chunks that attention is attributed to.

This is where the thesis's contribution starts to take shape. Lookback Lens treats the whole
retrieved context as one block; the chunk-aware version asks *which part* of it the model looked
at, and that question only exists once the context has been cut up. How it is cut is therefore
not a detail — section 3 of docs/EXPERIMENTS.md makes the comparison between the two strategies
an experiment in its own right (E05).

Two strategies, per section 2.1 of docs/SPEC.md:

``sentence``      splits on sentence boundaries and merges away the very short pieces. The
                  chunks **tile** the context: every character belongs to exactly one chunk.
``token_window``  fixed windows of ``window_size`` tokens advancing by ``stride``. With the
                  default stride of half a window the chunks **overlap**, so a token can belong
                  to two of them and the per-chunk shares no longer sum to one.

That difference matters downstream: the features of task T21 that treat the per-chunk vector as
a distribution — entropy, Gini — are reading a distribution only under the sentence strategy.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, replace

DEFAULT_MIN_WORDS = 5
STRATEGIES = ("sentence", "token_window")

# A run of sentence-ending punctuation followed by whitespace. The boundary is placed after the
# whitespace so that the chunks tile the context and the next one starts on a real character.
_BOUNDARY = re.compile(r"[.!?…]+[\"'”’)\]]*\s+")

# Words that end in a full stop without ending a sentence. Vietnamese writing is full of them,
# and every one left out here becomes a sentence split in the middle of a name.
ABBREVIATIONS = frozenset(
    {
        # Titles and academic ranks
        "gs", "pgs", "ts", "ths", "bs", "ks", "cn", "nsnd", "nsut", "tskh",
        # Administrative units
        "tp", "tt", "tx", "q", "p", "h", "x", "kp", "kcn", "kdc",
        # Schools and organisations
        "đh", "cđ", "thpt", "thcs", "cty", "tnhh", "cp", "hđqt", "ubnd", "hđnd",
        # Publishing and reference
        "nxb", "tr", "sđd", "vd", "vv", "tk", "stt",
        # Common short forms
        "ông", "bà", "ô", "b", "m", "k", "trh",
    }
)

# Words made only of digits before a full stop: "31." in "31. 12. 2024", or a numbered list.
_DIGITS = re.compile(r"^\d+$")
_WORD_BEFORE = re.compile(r"([^\s]+)$")


@dataclass(frozen=True)
class Chunk:
    """One span of the context that attention is attributed to.

    Character offsets refer to the raw context string, and the invariant that matters is
    ``context[char_start:char_end] == text``. Task T07 lost a day to a truncation that broke it:
    every per-chunk number afterwards was attributed to the wrong span, and nothing failed.

    Token offsets stay ``None`` for the sentence strategy, which knows nothing about tokens.
    """

    text: str
    char_start: int
    char_end: int
    index: int
    token_start: int | None = None
    token_end: int | None = None

    @property
    def n_words(self) -> int:
        return len(self.text.split())


def _is_real_boundary(context: str, punct_start: int) -> bool:
    """Is the punctuation at this position really the end of a sentence?

    Three ways it is not. A decimal point needs no special case — Vietnamese writes 331.212 with
    no space, and the pattern requires whitespace — but an abbreviation, an initial, or a number
    used as a list marker all do, because each is a full stop followed by a space and a capital.
    """
    if context[punct_start] != ".":
        return True  # "!" and "?" do not appear inside abbreviations
    match = _WORD_BEFORE.search(context[:punct_start])
    if not match:
        return True
    word = match.group(1)
    if _DIGITS.match(word):
        # "31. 12. 2024", and numbered list markers. Splitting inside a date is worse than
        # leaving a list item joined to the sentence that introduces it.
        return False
    folded = unicodedata.normalize("NFC", word).lower()
    if folded in ABBREVIATIONS:
        return False
    # A single letter is an initial: "Nguyễn V. A.".
    return not (len(folded) == 1 and folded.isalpha())


def sentence_spans(context: str) -> list[tuple[int, int]]:
    """Character spans of the sentences, tiling the whole context.

    Every character of the context lands in exactly one span, whitespace included, so that no
    token can later fall between two chunks and go uncounted.
    """
    if not context:
        return []
    spans: list[tuple[int, int]] = []
    start = 0
    for match in _BOUNDARY.finditer(context):
        if not _is_real_boundary(context, match.start()):
            continue
        end = match.end()
        if end > start:
            spans.append((start, end))
            start = end
    if start < len(context):
        spans.append((start, len(context)))
    return spans or [(0, len(context))]


def merge_short_spans(
    context: str, spans: list[tuple[int, int]], min_words: int = DEFAULT_MIN_WORDS
) -> list[tuple[int, int]]:
    """Fold spans shorter than ``min_words`` into a neighbour.

    Section 2.1 of docs/SPEC.md says "into the previous one", which leaves the first span with
    nowhere to go. A short opening line — a headline, a dateline, "Theo VnExpress." — is common
    enough in these corpora that it needs an answer, so it merges forward instead of being left
    as a one-word chunk that no attention distribution can say anything useful about.
    """
    if min_words <= 1 or not spans:
        return spans

    merged: list[list[int]] = []
    for start, end in spans:
        if merged and len(context[start:end].split()) < min_words:
            merged[-1][1] = end
        else:
            merged.append([start, end])

    # The first span had no predecessor, so it is dealt with here rather than in the loop.
    while len(merged) > 1 and len(context[merged[0][0] : merged[0][1]].split()) < min_words:
        merged[1][0] = merged[0][0]
        merged.pop(0)

    return [(start, end) for start, end in merged]


def chunk_by_sentence(context: str, min_words: int = DEFAULT_MIN_WORDS) -> list[Chunk]:
    """Cut the context at sentence boundaries. Chunks tile the context exactly."""
    spans = merge_short_spans(context, sentence_spans(context), min_words)
    return [
        Chunk(text=context[start:end], char_start=start, char_end=end, index=index)
        for index, (start, end) in enumerate(spans)
    ]


def chunk_by_token_window(
    context: str, tokenizer, window_size: int, stride: int | None = None
) -> list[Chunk]:
    """Cut the context into fixed windows of tokens, advancing by ``stride``.

    The tokenizer is required rather than approximated by counting words: the windows are meant
    to be comparable with attention positions, and those are token positions. Character spans
    come from the tokenizer's own offset mapping, so the ``context[start:end] == text``
    invariant holds without any arithmetic of ours.

    ``stride`` defaults to half the window, as fixed for experiment E05. Anything below the
    window size makes consecutive chunks overlap, and a token in the overlap is counted by both.
    """
    if window_size < 1:
        raise ValueError(f"window_size phải >= 1, nhận {window_size}")
    stride = window_size // 2 if stride is None else stride
    if stride < 1:
        raise ValueError(f"stride phải >= 1, nhận {stride}")
    if stride > window_size:
        raise ValueError(f"stride ({stride}) không được lớn hơn window_size ({window_size})")
    if tokenizer is None:
        raise ValueError(
            "chiến lược token_window cần tokenizer để biết ranh giới token; "
            "truyền tokenizer=... vào chunk_context"
        )
    if not context:
        return []

    encoded = tokenizer(context, add_special_tokens=False, return_offsets_mapping=True)
    offsets = [tuple(pair) for pair in encoded["offset_mapping"] if pair[1] > pair[0]]
    if not offsets:
        return []

    chunks: list[Chunk] = []
    for token_start in range(0, len(offsets), stride):
        window = offsets[token_start : token_start + window_size]
        if not window:
            break
        start, end = window[0][0], window[-1][1]
        chunks.append(
            Chunk(
                text=context[start:end],
                char_start=start,
                char_end=end,
                index=len(chunks),
                token_start=token_start,
                token_end=token_start + len(window),
            )
        )
        # A final window shorter than the stride would only repeat what the previous one held.
        if token_start + window_size >= len(offsets):
            break
    return chunks


def chunk_context(context: str, strategy: str, **kwargs) -> list[Chunk]:
    """Dispatch to one of the two strategies. Signature per section 2.1 of docs/SPEC.md."""
    if strategy == "sentence":
        return chunk_by_sentence(context, kwargs.get("min_words", DEFAULT_MIN_WORDS))
    if strategy == "token_window":
        return chunk_by_token_window(
            context,
            kwargs.get("tokenizer"),
            kwargs.get("window_size", 128),
            kwargs.get("stride"),
        )
    raise ValueError(f"không biết chiến lược {strategy!r}; chọn một trong {list(STRATEGIES)}")


def reconstruct_context(chunks: list[Chunk]) -> str:
    """Rebuild the context from the chunks' own offsets.

    Works for both strategies: overlapping windows simply write the same characters twice. Used
    so that :func:`locate_evidence_chunk` can keep the two-argument signature docs/SPEC.md gives
    it and still handle evidence that straddles a boundary.
    """
    if not chunks:
        return ""
    buffer = [" "] * max(chunk.char_end for chunk in chunks)
    for chunk in chunks:
        for offset, char in enumerate(chunk.text):
            buffer[chunk.char_start + offset] = char
    return "".join(buffer)


def locate_evidence_chunk(
    chunks: list[Chunk], evidence: str, context: str | None = None
) -> int | None:
    """Index of the chunk holding the evidence, or ``None`` if it is not there.

    Evidence does not respect chunk boundaries, and under the sentence strategy it usually is a
    sentence while under a token window it usually is not. When it straddles two chunks the
    answer is the chunk holding **most** of it: experiment E06 scores hit@1 against a single
    gold chunk, so there has to be exactly one, and "most of the evidence" is the only defensible
    way to pick it.

    Only exact text matching is used, as everywhere else in this project. Evidence that is not
    present verbatim returns ``None`` rather than a nearest guess.
    """
    if not chunks or not evidence.strip():
        return None

    haystack = reconstruct_context(chunks) if context is None else context
    start = haystack.find(evidence)
    if start < 0:
        return None
    end = start + len(evidence)

    best_index, best_overlap = None, 0
    for chunk in chunks:
        overlap = min(end, chunk.char_end) - max(start, chunk.char_start)
        if overlap > best_overlap:
            best_index, best_overlap = chunk.index, overlap
    return best_index


def reindex(chunks: list[Chunk]) -> list[Chunk]:
    """Renumber chunks so ``index`` matches position, after any of them were dropped."""
    return [replace(chunk, index=position) for position, chunk in enumerate(chunks)]
