"""Minimal SVG building blocks shared by the report figure generators.

The figures in ``docs/media`` are generated, not hand-drawn, so that a change to
a component name in the code base can be mirrored in the report by re-running
one script.  Rendering to PNG is done separately with headless Chrome.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from xml.sax.saxutils import escape

LOGO_DIR = Path(__file__).resolve().parent.parent / "logos"

# Character width factors relative to font size, good enough for Arial-like
# faces; used only to break labels into lines. Measured on the rendered figures,
# Vietnamese text in Arial runs ~0,44 em a character; 0,47 leaves room for bold.
_AVG_CHAR_W = 0.47


def esc(text: str) -> str:
    return escape(text)


# --------------------------------------------------------------------------
# logos
# --------------------------------------------------------------------------


@dataclass
class Logo:
    """A Simple Icons glyph, ready to be dropped into a 24x24 unit square."""

    name: str
    fill: str
    paths: list[str]

    @classmethod
    def load(cls, name: str) -> Logo:
        raw = (LOGO_DIR / f"{name}.svg").read_text(encoding="utf-8")
        fill_match = re.search(r'fill="(#[0-9A-Fa-f]{3,8})"', raw)
        fill = fill_match.group(1) if fill_match else "#222222"
        paths = re.findall(r'<path[^>]*\sd="([^"]+)"', raw)
        if not paths:
            raise ValueError(f"no path found in logo {name}")
        return cls(name=name, fill=fill, paths=paths)

    def render(self, x: float, y: float, size: float, fill: str | None = None) -> str:
        scale = size / 24.0
        color = fill or self.fill
        body = "".join(f'<path d="{d}"/>' for d in self.paths)
        return (
            f'<g transform="translate({x:.1f},{y:.1f}) scale({scale:.4f})" '
            f'fill="{color}">{body}</g>'
        )


_LOGO_CACHE: dict[str, Logo] = {}


def logo(name: str) -> Logo:
    if name not in _LOGO_CACHE:
        _LOGO_CACHE[name] = Logo.load(name)
    return _LOGO_CACHE[name]


# --------------------------------------------------------------------------
# text
# --------------------------------------------------------------------------


try:
    # measure with the face headless Chrome draws these figures in on this machine
    from PIL import ImageFont
    _FACES = {False: ImageFont.truetype("arial.ttf", 200),
              True: ImageFont.truetype("arialbd.ttf", 200)}
except (ImportError, OSError):          # no PIL or no Arial: fall back to the estimate
    _FACES = None


def text_width(text: str, font_size: float, bold: bool = False) -> float:
    """Rendered width of one line of Arial, in px."""
    if _FACES:
        return _FACES[bold].getlength(text) * font_size / 200
    return len(text) * font_size * _AVG_CHAR_W


def _greedy(words: list[str], limit: float, font_size: float, bold: bool) -> list[str]:
    lines, current = [], words[0]
    for word in words[1:]:
        if text_width(f"{current} {word}", font_size, bold) <= limit:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def wrap(text: str, width_px: float, font_size: float, bold: bool = False,
         balance: bool = False) -> list[str]:
    """Greedy word wrap on measured widths. Honours explicit newlines first.

    With balance, a paragraph that needs several lines gets lines of near-equal length
    instead of a full first line and a stray last word — the narrowest width that still
    gives the same number of lines."""
    lines: list[str] = []
    limit = width_px * 0.97               # slack for hinting and rounding in the browser
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        para = _greedy(words, limit, font_size, bold)
        if balance and len(para) > 1:
            lo = max(text_width(w, font_size, bold) for w in words)
            hi = limit
            for _ in range(24):
                mid = (lo + hi) / 2
                if len(_greedy(words, mid, font_size, bold)) <= len(para):
                    hi = mid
                else:
                    lo = mid
            para = _greedy(words, hi, font_size, bold)
        lines += para
    return lines


def text_block(
    cx: float,
    cy: float,
    text: str,
    width_px: float,
    font_size: float = 15.0,
    weight: str = "normal",
    fill: str = "#111111",
    style: str = "normal",
    family: str | None = None,
) -> str:
    # centred labels read best with even lines and no stray last word
    lines = wrap(text, width_px, font_size, bold=weight == "bold", balance=True)
    line_h = font_size * 1.28
    start = cy - (len(lines) - 1) * line_h / 2
    fam = f' font-family="{family}"' if family else ""
    out = [
        f'<text x="{cx:.1f}" y="{start:.1f}" font-size="{font_size:g}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}"{fam} '
        f'text-anchor="middle" dominant-baseline="middle">'
    ]
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else line_h
        out.append(f'<tspan x="{cx:.1f}" dy="{dy:.1f}">{esc(line)}</tspan>')
    out.append("</text>")
    return "".join(out)


# --------------------------------------------------------------------------
# shapes
# --------------------------------------------------------------------------


@dataclass
class Node:
    """A placed shape; exposes edge anchors so arrows never need raw numbers."""

    x: float
    y: float
    w: float
    h: float
    svg: str = ""

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def top(self) -> tuple[float, float]:
        return (self.cx, self.y)

    @property
    def bottom(self) -> tuple[float, float]:
        return (self.cx, self.y + self.h)

    @property
    def left(self) -> tuple[float, float]:
        return (self.x, self.cy)

    @property
    def right(self) -> tuple[float, float]:
        return (self.x + self.w, self.cy)


@dataclass
class Canvas:
    width: float
    height: float
    background: str = "#ffffff"
    font_family: str = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    parts: list[str] = field(default_factory=list)

    # -- primitives --------------------------------------------------------

    def add(self, svg: str) -> None:
        self.parts.append(svg)

    def group_box(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str = "",
        dash: str = "8 6",
        stroke: str = "#111111",
        stroke_width: float = 1.6,
        radius: float = 14,
        fill: str = "none",
        title_size: float = 19,
        title_weight: str = "bold",
        title_dy: float = 26,
    ) -> Node:
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{radius}" ry="{radius}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}" stroke-dasharray="{dash}"/>'
        )
        if title:
            self.add(
                text_block(
                    x + w / 2,
                    y + title_dy,
                    title,
                    w - 24,
                    font_size=title_size,
                    weight=title_weight,
                )
            )
        return Node(x, y, w, h)

    def box(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str,
        font_size: float = 15,
        weight: str = "normal",
        fill: str = "#ffffff",
        stroke: str = "#111111",
        stroke_width: float = 1.5,
        radius: float = 3,
        text_fill: str = "#111111",
        style: str = "normal",
    ) -> Node:
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{radius}" ry="{radius}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"/>'
        )
        self.add(
            text_block(
                x + w / 2,
                y + h / 2,
                label,
                w - 14,
                font_size=font_size,
                weight=weight,
                fill=text_fill,
                style=style,
            )
        )
        return Node(x, y, w, h)

    def diamond(
        self,
        cx: float,
        cy: float,
        w: float,
        h: float,
        label: str,
        font_size: float = 13,
        fill: str = "#ffffff",
        stroke: str = "#111111",
    ) -> Node:
        pts = (f"{cx:.1f},{cy - h / 2:.1f} {cx + w / 2:.1f},{cy:.1f} "
               f"{cx:.1f},{cy + h / 2:.1f} {cx - w / 2:.1f},{cy:.1f}")
        self.add(
            f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        self.add(text_block(cx, cy, label, w * 0.72, font_size=font_size))
        return Node(cx - w / 2, cy - h / 2, w, h)

    def cylinder(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        label: str,
        font_size: float = 14,
        ry: float = 14,
        fill: str = "#ffffff",
        stroke: str = "#111111",
    ) -> Node:
        body_top = y + ry
        body_h = h - 2 * ry
        self.add(
            f'<path d="M {x:.1f} {body_top:.1f} v {body_h:.1f} '
            f'a {w / 2:.1f} {ry:.1f} 0 0 0 {w:.1f} 0 v {-body_h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        self.add(
            f'<ellipse cx="{x + w / 2:.1f}" cy="{body_top:.1f}" rx="{w / 2:.1f}" '
            f'ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        self.add(text_block(x + w / 2, y + h / 2 + ry * 0.35, label, w - 16, font_size=font_size))
        return Node(x, y, w, h)

    # -- connectors --------------------------------------------------------

    def arrow(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        via: list[tuple[float, float]] | None = None,
        stroke: str = "#111111",
        stroke_width: float = 1.5,
        dash: str | None = None,
        marker: str = "arrow",
    ) -> None:
        pts = [start] + (via or []) + [end]
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(
            f" L {px:.1f} {py:.1f}" for px, py in pts[1:]
        )
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}"'
            f'{dash_attr} marker-end="url(#{marker})"/>'
        )

    def elbow_v(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        **kw,
    ) -> None:
        """Vertical-first elbow: down/up from start, across, then into end."""
        mid_y = (start[1] + end[1]) / 2
        self.arrow(start, end, via=[(start[0], mid_y), (end[0], mid_y)], **kw)

    def elbow_h(self, start: tuple[float, float], end: tuple[float, float], **kw) -> None:
        mid_x = (start[0] + end[0]) / 2
        self.arrow(start, end, via=[(mid_x, start[1]), (mid_x, end[1])], **kw)

    def label(
        self,
        x: float,
        y: float,
        text: str,
        font_size: float = 12.5,
        weight: str = "normal",
        fill: str = "#111111",
        style: str = "normal",
        width: float = 400,
    ) -> None:
        self.add(
            text_block(x, y, text, width, font_size=font_size, weight=weight, fill=fill,
                       style=style)
        )

    def logo(self, name: str, x: float, y: float, size: float, fill: str | None = None) -> None:
        self.add(logo(name).render(x, y, size, fill))

    def logo_label(
        self,
        name: str,
        x: float,
        y: float,
        size: float,
        text: str,
        font_size: float = 13,
        gap: float = 6,
    ) -> None:
        """Logo glyph with its wordmark to the right, baseline-centred."""
        self.logo(name, x, y, size)
        self.add(
            f'<text x="{x + size + gap:.1f}" y="{y + size / 2:.1f}" font-size="{font_size:g}" '
            f'fill="#111111" dominant-baseline="middle">{esc(text)}</text>'
        )

    # -- output ------------------------------------------------------------

    def render(self) -> str:
        defs = (
            '<defs>'
            '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#111111"/></marker>'
            '<marker id="arrowlight" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#6b7280"/></marker>'
            '<marker id="none" viewBox="0 0 1 1" refX="0" refY="0" '
            'markerWidth="0.01" markerHeight="0.01"><path d="M0 0"/></marker>'
            '</defs>'
        )
        body = "".join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width:g}" '
            f'height="{self.height:g}" viewBox="0 0 {self.width:g} {self.height:g}" '
            f'font-family="{self.font_family}">'
            f'{defs}'
            f'<rect width="{self.width:g}" height="{self.height:g}" fill="{self.background}"/>'
            f'{body}</svg>'
        )

    def save(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path


    # -- extras used by the concept figures ---------------------------------

    def raw_text(
        self,
        x: float,
        y: float,
        content: str,
        font_size: float = 15,
        anchor: str = "start",
        fill: str = "#111111",
        weight: str = "normal",
        style: str = "normal",
        family: str | None = None,
        opacity: float = 1.0,
    ) -> None:
        """One line of text, no wrapping, anchored where asked."""
        fam = f' font-family="{family}"' if family else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{font_size:g}" '
            f'text-anchor="{anchor}" fill="{fill}" font-weight="{weight}" '
            f'font-style="{style}" opacity="{opacity:g}"{fam} '
            f'dominant-baseline="middle">{esc(content)}</text>'
        )

    def band(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: str,
        radius: float = 4,
        opacity: float = 1.0,
        stroke: str = "none",
    ) -> None:
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{radius}" ry="{radius}" fill="{fill}" opacity="{opacity:g}" '
            f'stroke="{stroke}"/>'
        )

    def brace(self, x: float, y1: float, y2: float, depth: float = 12,
              stroke: str = "#111111") -> None:
        """A left-pointing curly brace spanning y1..y2 at abscissa x."""
        mid = (y1 + y2) / 2
        self.add(
            f'<path d="M {x:.1f} {y1:.1f} q {-depth} 0 {-depth} {depth} '
            f'L {x - depth:.1f} {mid - depth:.1f} q 0 {depth} {-depth} {depth} '
            f'q {depth} 0 {depth} {depth} L {x - depth:.1f} {y2 - depth:.1f} '
            f'q 0 {depth} {depth} {depth}" fill="none" stroke="{stroke}" '
            f'stroke-width="1.4"/>'
        )
