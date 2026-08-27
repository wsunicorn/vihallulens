"""What counts as a word, for every part of the project that has to count words.

Kept in one place on purpose. The BM25 index of task T16 and the lexical-overlap feature of
task T17 both need to decide where one word ends and the next begins, and two different answers
to that question inside one project is how two numbers that ought to agree quietly stop
agreeing.
"""

from __future__ import annotations

import re
import unicodedata

# Everything that is not a letter, a digit or whitespace. Vietnamese diacritics survive because
# the class is defined by what it keeps, not by an ASCII range.
_PUNCTUATION = re.compile(r"[^\w\s]", flags=re.UNICODE)


def tokenize(text: str) -> list[str]:
    """Split text into comparable units, lower-cased and stripped of punctuation.

    Vietnamese words are written as separate syllables — "Hà Nội" is two whitespace-separated
    pieces of one word — so this yields syllables rather than words. Grouping them properly
    needs a word segmenter, which is a dependency this project has not taken; section 7 of
    CLAUDE.md requires asking before adding one. Measured at T16, the cost for retrieval is
    small, and the same reasoning carries to lexical overlap.
    """
    folded = unicodedata.normalize("NFC", text).lower()
    return _PUNCTUATION.sub(" ", folded).split()


def word_count(text: str) -> int:
    """Number of whitespace-separated pieces, punctuation included.

    Deliberately *not* the length of :func:`tokenize`. This is the plain reading of "how long
    is this response", and it reproduces the per-label averages published in section 4 of
    docs/EXPERIMENTS.md exactly — 32,9 / 39,5 / 45,9 words. Changing it to the tokenized count
    would move those numbers and break the comparison with the figures already recorded.
    """
    return len(text.split())
