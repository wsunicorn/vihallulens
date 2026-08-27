"""Vietnamese word segmentation, needed by PhoBERT and by nothing else.

Vietnamese writes each syllable separately, so "Hà Nội" is two whitespace-separated pieces of
one word. PhoBERT was pre-trained on text where those pieces had already been joined —
``Hà_Nội`` — so feeding it raw text puts it in front of a vocabulary it never saw and its score
drops for a reason that has nothing to do with the task.

XLM-R and InfoXLM use SentencePiece over raw text and must **not** be given segmented input:
the underscores would be tokenised as ordinary characters.

Decided at T18 with the user, since section 7 of CLAUDE.md requires asking before adding a
dependency. ``pyvi`` was chosen for being small — one CRF model, no Java, no large download.
"""

from __future__ import annotations

from functools import lru_cache

# Segmentation costs about 12 seconds over the 5.598 ViHallu training samples, which is nothing
# beside the fine-tuning it feeds, but the cache is free and the corpora do repeat contexts.
# Measured at T18: on the pairs actually built it earns few hits, because the left side is the
# context *and* the question concatenated and that combination is nearly unique per sample. It
# pays off wherever the same text is segmented twice, such as re-running with another seed.
_CACHE_SIZE = 8192


@lru_cache(maxsize=_CACHE_SIZE)
def segment(text: str) -> str:
    """Join the syllables of each word with an underscore, PhoBERT's expected input form.

    >>> segment("Hà Nội là thủ đô")
    'Hà_Nội là thủ_đô'
    """
    if not text.strip():
        return text
    from pyvi import ViTokenizer

    return ViTokenizer.tokenize(text)


def segment_all(texts) -> list[str]:
    """Segment a sequence of texts, reusing the cache across repeated ones."""
    return [segment(str(text)) for text in texts]


def cache_info():
    """Hits and misses, so a run can report how much the repetition actually saved."""
    return segment.cache_info()
