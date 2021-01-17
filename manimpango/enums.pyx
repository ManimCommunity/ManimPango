"""
    enums.pyx
    ~~~~~~~~~

    This module contains enum functions, needed
    to be used with Pango.

    :licence: GPLv3, See LICENSE for details.
"""
from enum import Enum
from _manimpango cimport *
class Underline(Enum):
    NONE = PANGO_UNDERLINE_NONE
    SINGLE = PANGO_UNDERLINE_SINGLE
    DOUBLE = PANGO_UNDERLINE_DOUBLE
    LOW = PANGO_UNDERLINE_LOW
    ERROR = PANGO_UNDERLINE_ERROR
class Gravity(Enum):
    SOUTH = PANGO_GRAVITY_SOUTH
    EAST = PANGO_GRAVITY_EAST
    NORTH = PANGO_GRAVITY_NORTH
    WEST = PANGO_GRAVITY_WEST
    AUTO = PANGO_GRAVITY_AUTO
class GravityHint(Enum):
    NATURAL = PANGO_GRAVITY_HINT_NATURAL
    STRONG = PANGO_GRAVITY_HINT_STRONG
    LINE = PANGO_GRAVITY_HINT_LINE
class Show(Enum):
    NONE = PANGO_SHOW_NONE
    SPACES = PANGO_SHOW_SPACES
    LINE_BREAKS = PANGO_SHOW_LINE_BREAKS
    IGNORABLES=PANGO_SHOW_IGNORABLES
class Style(Enum):
    """
    An enumeration specifying the various slant styles possible for a font.

    Attributes
    ----------

    NORMAL :
        the font is upright.

    ITALIC :
        the font is slanted, but in a roman style.

    OBLIQUE:
        the font is slanted in an italic style.
    """
    NORMAL = PANGO_STYLE_NORMAL
    ITALIC = PANGO_STYLE_ITALIC
    OBLIQUE = PANGO_STYLE_OBLIQUE

class Variant(Enum):
    """
    An enumeration specifying capitalization variant of the font.

    Attributes
    ----------

    NORMAL :
        A normal font.

    SMALL_CAPS :
        A font with the lower case characters replaced by smaller variants
        of the capital characters.
    """
    NORMAL = PANGO_VARIANT_NORMAL
    SMALL_CAPS = PANGO_VARIANT_SMALL_CAPS