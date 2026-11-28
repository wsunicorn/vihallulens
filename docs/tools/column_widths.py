"""Column widths of the report's tables, from the measured width of what the cells hold.

Estimating a column from its character count left short columns wide and long ones narrow, so
rows wrapped more than they had to and the tables grew longer. Here every word is measured in the
face it is set in (Times New Roman regular or bold, Consolas for code), each cell is wrapped the
way Word wraps it, and the widths are chosen so that

1. the table is as short as it can be in the text width,
2. then as few body cells as possible wrap (a header may take two lines in a short table),
3. then what is left over is shared out evenly, so no column is loose beside a tight one.

The first pass is a beam search over the widths at which a cell starts to wrap differently; the
second moves small amounts between pairs of columns until nothing improves.
"""

from __future__ import annotations

import re
from functools import cache
from pathlib import Path

from docx.oxml.ns import qn
from PIL import ImageFont

FONTS = Path("C:/Windows/Fonts")
FACES = {("text", False): "times.ttf", ("text", True): "timesbd.ttf",
         ("code", False): "consola.ttf", ("code", True): "consolab.ttf",
         ("math", False): "timesi.ttf", ("math", True): "timesbi.ttf"}
PX = 200                    # measuring size; widths scale linearly with the point size
SAFETY = {"text": 1.02, "code": 1.02, "math": 1.12}     # Cambria Math is wider than Times
STEP = 0.05                 # cm, the grid the search moves on
BEAM = 800
NUMBER = re.compile(r"^[\s\d.,;:/%+−–—\-\[\]()→±=≈<>*]*(?:MB|GB|ms|từ|lần|tỷ|lớp|đầu)?"
                    r"[\s\d.,;:/%+−–—\-\[\]()→±=×]*$")


@cache
def face(kind: str, bold: bool):
    return ImageFont.truetype(str(FONTS / FACES[kind, bold]), PX)


@cache
def width_cm(text: str, kind: str, bold: bool, pt: float) -> float:
    return face(kind, bold).getlength(text) / PX * pt / 72 * 2.54 * SAFETY[kind]


def runs_of(paragraph, header: bool):
    """(text, kind, bold) for every text and math run of a paragraph, in order."""
    for run in paragraph._p.iter(qn("w:r"), qn("m:r")):
        math = run.tag == qn("m:r")
        text = "".join(t.text or "" for t in run.iter(qn("w:t"), qn("m:t")))
        if not text:
            continue
        props = run.find(qn("w:rPr"))
        style = props.find(qn("w:rStyle")) if props is not None else None
        code = style is not None and style.get(qn("w:val")) == "VerbatimChar"
        mark = props.find(qn("w:b")) if props is not None else None
        bold = header or (mark is not None and mark.get(qn("w:val")) not in ("0", "false"))
        yield text, "math" if math else "code" if code else "text", bold


def words_of(paragraph, pt: float, header: bool) -> list[tuple[float, float]]:
    """Width of every unbreakable word, and of the space that follows it."""
    words, current, space = [], 0.0, 0.0
    for text, kind, bold in runs_of(paragraph, header):
        for piece in re.split(r"([ \t\n]+)", text):
            if not piece:
                continue
            if piece.isspace():
                space = width_cm(" ", kind, bold, pt)
                if current:
                    words.append((current, space))
                    current = 0.0
            else:
                current += width_cm(piece, kind, bold, pt)
    if current:
        words.append((current, space))
    return words


def lines_in(words, usable: float) -> tuple[int, float]:
    """Number of lines the words take in ``usable`` cm, and the widest of those lines."""
    lines, line, widest, gap = 1, 0.0, 0.0, 0.0
    for word, space in words:
        if line and line + gap + word > usable + 1e-9:
            lines, line = lines + 1, word
        else:
            line = line + (gap if line else 0.0) + word
        widest, gap = max(widest, line), space
    return lines, widest


class Layout:
    """A table's words, measured once; widths are tried against them."""

    def __init__(self, table, pt: float, pad: float, body_pt: float | None = None):
        self.pad = pad
        self.cells = []
        for r, row in enumerate(table.rows):
            size = pt if r == 0 else body_pt or pt
            self.cells.append([[words_of(p, size, r == 0) for p in c.paragraphs]
                               for c in row.cells])
        self.n = len(self.cells[0])
        self.memo = {}

    def minimum(self) -> list[float]:
        return [max((w for row in self.cells for words in row[k] for w, _ in words), default=0.3)
                + self.pad for k in range(self.n)]

    def column(self, k: int, width: float):
        """Lines of every row in column ``k`` at this width, and the width really needed."""
        key = (k, int(width / STEP + 1e-6))
        if key not in self.memo:
            lines, need = [], 0.0
            for row in self.cells:
                parts = [lines_in(words, width - self.pad) for words in row[k]]
                lines.append(sum(p[0] for p in parts))
                need = max([need, *(p[1] for p in parts)])
            self.memo[key] = (lines, need + self.pad)
        return self.memo[key]

    def row_lines(self, widths) -> list[int]:
        columns = [self.column(k, w)[0] for k, w in enumerate(widths)]
        return [max(c[r] for c in columns) for r in range(len(self.cells))]

    def score(self, widths):
        columns = [self.column(k, w) for k, w in enumerate(widths)]
        height = sum(max(c[0][r] for c in columns) for r in range(len(self.cells)))
        wraps = sum(sum(c[0][1:]) for c in columns)
        slack = sum((w - c[1]) ** 2 for w, c in zip(widths, columns, strict=True))
        return height, wraps, round(slack, 3)

    def choices(self, k: int, least: float, most: float) -> list[tuple[float, tuple[int, ...]]]:
        """The widths worth giving column ``k``: the least one for each way its cells can wrap."""
        out, width = [], least
        while True:
            lines, need = self.column(k, width)
            if not out or tuple(lines) != out[-1][1]:
                out.append((max(need, least), tuple(lines)))
            if width >= most or sum(lines) == sum(max(len(row[k]), 1) for row in self.cells):
                return out
            width += STEP


def best_widths(layout: Layout, total: float) -> list[float]:
    mins = layout.minimum()
    if sum(mins) >= total:                      # cannot keep every word whole
        return [m * total / sum(mins) for m in mins]
    room = total - sum(mins)
    options = [layout.choices(k, m, m + room) for k, m in enumerate(mins)]
    order = sorted(range(layout.n), key=lambda k: -len(options[k]))
    # one column at a time: (extra width used, lines of each row so far, cells wrapped, widths)
    beam = [(0.0, (1,) * len(layout.cells), 0, {})]
    for k in order:
        grown = {}
        for used, lines, wraps, chosen in beam:
            for width, column in options[k]:
                extra = used + width - mins[k]
                if extra > room + 1e-9:
                    continue
                key = tuple(map(max, lines, column))
                state = (extra, key, wraps + sum(column[1:]), {**chosen, k: width})
                old = grown.get(key)
                if old is None or (state[2], state[0]) < (old[2], old[0]):
                    grown[key] = state
                    if old is not None and old[0] < state[0]:
                        grown[key, "narrow"] = old      # costs more lines, leaves more room
        beam = sorted(grown.values(), key=lambda t: (sum(t[1]), t[0], t[2]))
        # the shortest so far, and the narrowest so far: either can win once the rest is in
        beam = beam[:BEAM] + sorted(beam[BEAM:], key=lambda t: (t[0], sum(t[1])))[:BEAM]
    _, _, _, chosen = min(beam, key=lambda t: (sum(t[1]), t[2], t[0]))
    needs = [chosen[k] for k in range(layout.n)]
    share = (total - sum(needs)) / layout.n
    starts = [[w * total / sum(needs) for w in needs], [w + share for w in needs]]
    return min((polished(layout, start, mins) for start in starts), key=layout.score)


def polished(layout: Layout, widths: list[float], mins: list[float]) -> list[float]:
    score, moved = layout.score(widths), True
    while moved:
        moved = False
        for amount in (1.0, 0.5, 0.25, 0.1, STEP):
            for a in range(layout.n):
                for b in range(layout.n):
                    if a == b or widths[a] - amount < mins[a]:
                        continue
                    trial = list(widths)
                    trial[a] -= amount
                    trial[b] += amount
                    trial_score = layout.score(trial)
                    if trial_score < score:
                        widths, score, moved = trial, trial_score, True
    return widths


def numeric_columns(texts: list[list[str]]) -> list[bool]:
    """Which columns hold mostly figures in the body rows, and so read better centred."""
    out = []
    for k, column in enumerate(zip(*texts[1:], strict=True)):
        filled = [t.strip() for t in column if t.strip()]
        numbers = [t for t in filled if NUMBER.match(t)]
        out.append(k > 0 and bool(filled) and len(numbers) >= 0.5 * len(filled)
                   and max(map(len, filled)) <= 34)
    return out
