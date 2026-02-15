"""Rendered text result classes.

This module contains the :class:`RenderedText` class which is returned by
:func:`manimpango.render`, and the :class:`LineInfo` class which provides
per-line information.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


@dataclasses.dataclass
class LineInfo:
    """Information about a single line in rendered text.

    Attributes
    ----------
    text : str
        Text content of this line.
    start_index : int
        Character index in original string where line starts.
    width : float
        Line width in pixels.
    height : float
        Line height in pixels.
    baseline : int
        Baseline position in Pango units from line top.
    y_offset : int
        Y offset from layout top in Pango units.
    """

    text: str
    start_index: int
    width: float
    height: float
    baseline: int
    y_offset: int


@dataclasses.dataclass
class RenderedText:
    """Result of a :func:`manimpango.render` call.

    Contains SVG content and layout metadata for positioning text in animations.

    Attributes
    ----------
    svg : str
        SVG content as a string.
    width : float
        Total width in pixels.
    height : float
        Total height in pixels.
    baseline : int
        Baseline position in Pango units (1/1024 of a point) from top of layout.
        This is the distance from the top of the layout to the text baseline.
        Use this to position subsequent lines of text correctly.
    line_count : int
        Number of lines in the rendered text.
    lines : list[LineInfo]
        Information about each line, in order.
    line_height : int
        Recommended line-to-line distance in Pango units.

    Examples
    --------
    Basic usage::

        import manimpango

        result = manimpango.render("Hello World")

        # Get SVG content
        svg = result.svg

        # Save to file
        result.save("hello.svg")

        # Get layout info for positioning
        print(f"Width: {result.width}, Height: {result.height}")
        print(f"Baseline: {result.baseline} Pango units")
        print(f"Lines: {result.line_count}")

        for i, line in enumerate(result.lines):
            print(f"  Line {i}: '{line.text}', y_offset={line.y_offset}")

        # Position subsequent text
        next_y = result.baseline + int(result.line_height * 1.5)  # 1.5x line height
    """

    # Internal data (set by Cython)
    _svg: str
    _width: float
    _height: float
    _baseline: int
    _line_count: int
    _lines: list[LineInfo]

    @property
    def svg(self) -> str:
        """SVG content as a string."""
        return self._svg

    @property
    def width(self) -> float:
        """Total width in pixels."""
        return self._width

    @property
    def height(self) -> float:
        """Total height in pixels."""
        return self._height

    @property
    def baseline(self) -> int:
        """Baseline position in Pango units (1/1024 of a point).

        This is the distance from the top of the layout to the text baseline.
        Use this to position subsequent lines of text correctly.

        Examples
        --------
        ::

            result1 = render("First line")
            result2 = render("Second line")
            y_offset = result1.baseline + int(result1.line_height * 1.5)
        """
        return self._baseline

    @property
    def line_count(self) -> int:
        """Number of lines in the rendered text."""
        return self._line_count

    @property
    def lines(self) -> list[LineInfo]:
        """Information about each line, in order."""
        return self._lines

    @property
    def line_height(self) -> int:
        """Recommended line-to-line distance in Pango units.

        Computed as the difference between baselines of consecutive lines.
        """
        if self._line_count <= 1:
            return int(self._height * 1024)
        total_height = 0
        for i, line in enumerate(self._lines):
            if i < len(self._lines) - 1:
                next_line = self._lines[i + 1]
                total_height += next_line.y_offset - line.y_offset
            else:
                total_height += line.height * 1024
        return total_height // max(1, self._line_count - 1)

    def save(self, path: str | Path) -> None:
        """Save SVG content to a file.

        Parameters
        ----------
        path
            File path to write to. Parent directories are created if needed.

        Raises
        ------
        OSError
            If the file cannot be written.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._svg)

    def __str__(self) -> str:
        """Returns SVG content for backwards compatibility."""
        return self._svg

    def __repr__(self) -> str:
        return (
            f"RenderedText("
            f"{self.width:.1f}x{self.height:.1f}, "
            f"{self.line_count} line(s), "
            f"baseline={self.baseline})"
        )

    def __getattribute__(self, name: str) -> Any:
        """Allow dict-style access for backwards compatibility."""
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return None
