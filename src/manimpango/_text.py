"""Immutable public result objects returned by :func:`manimpango.render`."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Bounds:
    """A rectangle in SVG user-space coordinates."""

    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class LineInfo:
    """Text and geometry for one rendered line.

    ``start`` and ``end`` are half-open Python code-point offsets into the
    rendered plain-text input.
    """

    text: str
    start: int
    end: int
    bounds: Bounds
    baseline: float


@dataclass(frozen=True, slots=True)
class RenderedText:
    """SVG output and its layout metadata in one coordinate system."""

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

        The destination parent must already exist; filesystem errors are
        propagated to the caller.
        """
        destination = Path(path)
        destination.write_text(self.svg, encoding="utf-8")

    def __str__(self) -> str:
        """Return SVG text for compatibility with string-oriented callers."""
        return self.svg
