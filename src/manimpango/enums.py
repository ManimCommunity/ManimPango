"""Enumerations for text rendering options.

This module provides Python enums for text style options that mirror
Pango's constants. The :class:`Weight` enum inherits from both :class:`int`
and :class:`Enum` to allow arbitrary integer values for variable font support.
"""

from __future__ import annotations

from enum import Enum


class Style(Enum):
    """Font slant style.

    Attributes
    ----------
    NORMAL
        The font is upright.
    ITALIC
        The font is slanted in a roman style.
    OBLIQUE
        The font is slanted in an italic style.
    """

    NORMAL = 0
    ITALIC = 1
    OBLIQUE = 2


class Weight(int, Enum):
    """Font weight (boldness).

    This enum inherits from both ``int`` and ``Enum`` to allow arbitrary
    integer values (1-1000) for variable font support. The named members
    are convenience aliases for standard CSS/OpenType weight values.

    Examples
    --------
    Using named weights::

        Weight.NORMAL   # 400
        Weight.BOLD    # 700

    Using arbitrary integer values (useful for variable fonts)::

        Weight(450)    # 450
        550            # directly passed to render()

    Attributes
    ----------
    THIN : int
        Weight 100 (Since: Pango 1.24)
    ULTRALIGHT : int
        Weight 200
    LIGHT : int
        Weight 300
    SEMILIGHT : int
        Weight 350 (Since: Pango 1.36.7)
    BOOK : int
        Weight 380 (Since: Pango 1.24)
    NORMAL : int
        Weight 400
    MEDIUM : int
        Weight 500 (Since: Pango 1.24)
    SEMIBOLD : int
        Weight 600
    BOLD : int
        Weight 700
    ULTRABOLD : int
        Weight 800
    HEAVY : int
        Weight 900
    ULTRAHEAVY : int
        Weight 1000 (Since: Pango 1.24)
    """

    THIN = 100
    ULTRALIGHT = 200
    LIGHT = 300
    SEMILIGHT = 350
    BOOK = 380
    NORMAL = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
    ULTRABOLD = 800
    HEAVY = 900
    ULTRAHEAVY = 1000

    @classmethod
    def _missing_(cls, value: object) -> Weight | None:
        if isinstance(value, int) and 1 <= value <= 1000:
            obj = int.__new__(cls, value)
            obj._name_ = str(value)
            obj._value_ = value
            return obj
        return None


class Alignment(Enum):
    """Text alignment within a layout.

    Attributes
    ----------
    LEFT
        Align text to the left.
    CENTER
        Align text to the center.
    RIGHT
        Align text to the right.
    """

    LEFT = 0
    CENTER = 1
    RIGHT = 2
