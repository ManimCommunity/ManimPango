from enum import Enum

from pango cimport *


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

class Weight(Enum):
    """
    An enumeration specifying the weight (boldness) of a font.
    This is a numerical value ranging from 100 to 1000, but there are some predefined values
    Using numerical value other then that defined here is not supported.

    Attributes
    ----------

    NORMAL :
        the default weight (= 400)

    BOLD :
        the bold weight( = 700)

    THIN :
        the thin weight( = 100; Since: 1.24)

    ULTRALIGHT :
        the ultralight weight( = 200)

    LIGHT :
        the light weight( = 300)

    BOOK :
        the book weight( = 380; Since: 1.24)

    MEDIUM :
        the normal weight( = 500; Since: 1.24)

    SEMIBOLD :
        the semibold weight( = 600)

    ULTRABOLD :
        the ultrabold weight( = 800)

    HEAVY :
        the heavy weight( = 900)

    ULTRAHEAVY :
        the ultraheavy weight( = 1000; Since: 1.24)
    """
    NORMAL = PANGO_WEIGHT_NORMAL
    BOLD = PANGO_WEIGHT_BOLD
    THIN = PANGO_WEIGHT_THIN
    ULTRALIGHT = PANGO_WEIGHT_ULTRALIGHT
    LIGHT = PANGO_WEIGHT_LIGHT
    BOOK = PANGO_WEIGHT_BOOK
    MEDIUM = PANGO_WEIGHT_MEDIUM
    SEMIBOLD = PANGO_WEIGHT_SEMIBOLD
    ULTRABOLD = PANGO_WEIGHT_ULTRABOLD
    HEAVY = PANGO_WEIGHT_HEAVY
    ULTRAHEAVY = PANGO_WEIGHT_ULTRAHEAVY

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

class Alignment(Enum):
    """
    An enumeration specifying alignment.

    Attributes
    ----------

    NORMAL :
        A normal font.

    SMALL_CAPS :
        A font with the lower case characters replaced by smaller variants
        of the capital characters.
    """
    LEFT = PANGO_ALIGN_LEFT
    CENTER = PANGO_ALIGN_CENTER
    RIGHT = PANGO_ALIGN_RIGHT
