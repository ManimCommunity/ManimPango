"""Immutable public result objects returned by :func:`manimpango.render`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Bounds:
    """A rectangle in the rendered SVG coordinate system.

    Attributes
    ----------
    x, y
        Position of the rectangle's upper-left corner in SVG user-space units.
    width, height
        Non-negative dimensions in the same coordinate system.
    """

    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class LineInfo:
    """Text and geometry for one rendered line.

    For :func:`manimpango.render`, ``start`` and ``end`` are half-open Python
    code-point offsets into the input text.  For
    :func:`manimpango.render_markup`, they index Pango's parsed text rather
    than the markup source.  Newline separators are excluded from every line
    range.

    Attributes
    ----------
    text
        Parsed text rendered on this line, without a trailing newline.
    start, end
        Half-open Python code-point offsets for ``text`` in the appropriate
        rendered-text source.
    bounds
        Logical bounds of this line in SVG user-space coordinates.
    baseline
        Baseline position in SVG user-space coordinates.
    """

    text: str
    start: int
    end: int
    bounds: Bounds
    baseline: float


@dataclass(frozen=True, slots=True)
class RenderedText:
    """Immutable SVG output and layout metadata from one render operation.

    All geometry uses the same SVG user-space coordinate system as ``svg``.
    The object is frozen and ``lines`` is always a tuple.

    Attributes
    ----------
    svg
        Complete SVG document as a Unicode string.
    width, height
        Dimensions of the SVG viewport in user-space units.
    baseline
        Baseline of the first layout line in user-space units.
    lines
        Per-line text and geometry, in rendering order.
    ink_bounds
        Union of the Pango ink extents: the area touched by glyph drawing.
    logical_bounds
        Union of the Pango logical extents, including layout advances such as
        whitespace.
    """

    svg: str
    width: float
    height: float
    baseline: float
    lines: tuple[LineInfo, ...]
    ink_bounds: Bounds
    logical_bounds: Bounds

    def __post_init__(self) -> None:
        # A tuple prevents callers retaining a mutable list passed to the
        # constructor.  It also keeps this invariant for native bridge output.
        object.__setattr__(self, "lines", tuple(self.lines))

    @property
    def line_count(self) -> int:
        """Number of lines in the result."""
        return len(self.lines)

    def save(self, path: str | Path) -> None:
        """Write the SVG as UTF-8.

        Existing files are overwritten.  The destination parent must already
        exist; filesystem errors are propagated to the caller.
        """
        destination = Path(path)
        destination.write_text(self.svg, encoding="utf-8")

    def __str__(self) -> str:
        """Return SVG text for compatibility with string-oriented callers."""
        return self.svg
