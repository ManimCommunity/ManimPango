cimport cmanimpango

import re
import warnings
from enum import Enum
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape


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

class PangoUtils:
    @staticmethod
    def str2style(string: str) -> Style:
        """Internally used function. Converts text to Pango Understandable Styles."""
        if string == "NORMAL":
            return Style.NORMAL
        elif string == "ITALIC":
            return Style.ITALIC
        elif string == "OBLIQUE":
            return Style.OBLIQUE
        else:
            raise AttributeError("There is no Style Called %s" % string)

    @staticmethod
    def str2weight(string: str) -> Weight:
        """Internally used function. Convert text to Pango Understandable Weight"""
        if string == "NORMAL":
            return Weight.NORMAL
        elif string == "BOLD":
            return Weight.BOLD
        elif string == "THIN":
            return Weight.THIN
        elif string == "ULTRALIGHT":
            return Weight.ULTRALIGHT
        elif string == "LIGHT":
            return Weight.LIGHT
        elif string == "SEMILIGHT":
            return Weight.SEMILIGHT
        elif string == "BOOK":
            return Weight.BOOK
        elif string == "MEDIUM":
            return Weight.MEDIUM
        elif string == "SEMIBOLD":
            return Weight.SEMIBOLD
        elif string == "ULTRABOLD":
            return Weight.ULTRABOLD
        elif string == "HEAVY":
            return Weight.HEAVY
        elif string == "ULTRAHEAVY":
            return Weight.ULTRAHEAVY
        else:
            raise AttributeError("There is no Font Weight Called %s" % string)

    @staticmethod
    def remove_last_M(file_name: str) -> None:
        with open(file_name, "r") as fpr:
            content = fpr.read()
        content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
        with open(file_name, "w") as fpw:
            fpw.write(content)

class TextSetting(object):
    def __init__(self, start:int, end:int, font:str, slant, weight, line_num=-1):
        self.start = start
        self.end = end
        self.font = font.encode('utf-8')
        self.slant = slant
        self.weight = weight
        self.line_num = line_num
def text2svg(
    settings:list,
    size:int,
    line_spacing:int,
    disable_liga:bool,
    file_name:str,
    START_X:int,
    START_Y:int,
    width:int,
    height:int,
    orig_text:str
) -> int:
    cdef cairo_surface_t* surface
    cdef cairo_t* cr
    cdef PangoFontDescription* font_desc
    cdef PangoLayout* layout
    cdef double width_layout = width
    cdef double font_size_c = size
    cdef cairo_status_t status
    cdef int temp_width

    file_name_bytes = file_name.encode("utf-8")
    surface = cairo_svg_surface_create(file_name_bytes,width,height)

    if surface == NULL:
        raise MemoryError("Cairo.SVGSurface can't be created.")

    cr = cairo_create(surface)
    status = cairo_status(cr)

    if cr == NULL or status == CAIRO_STATUS_NO_MEMORY:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise MemoryError("Cairo.Context can't be created.")
    elif status != CAIRO_STATUS_SUCCESS:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise Exception(cairo_status_to_string(status))

    cairo_move_to(cr,START_X,START_Y)
    offset_x = 0
    last_line_num = 0

    layout = pango_cairo_create_layout(cr)

    if layout==NULL:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise MemoryError("Pango.Layout can't be created from Cairo Context.")

    pango_layout_set_width(layout, pango_units_from_double(width_layout))
    for setting in settings:
        family = setting.font
        style = PangoUtils.str2style(setting.slant)
        weight = PangoUtils.str2weight(setting.weight)
        text_str = orig_text[setting.start : setting.end].replace("\n", " ")
        text = text_str.encode('utf-8')
        font_desc = pango_font_description_new()
        if font_desc==NULL:
            cairo_destroy(cr)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Pango.FontDesc can't be created.")
        pango_font_description_set_size(font_desc, pango_units_from_double(font_size_c))
        if family:
            pango_font_description_set_family(font_desc, family)
        pango_font_description_set_style(font_desc, style.value)
        pango_font_description_set_weight(font_desc, weight.value)
        pango_layout_set_font_description(layout, font_desc)
        pango_font_description_free(font_desc)
        if setting.line_num != last_line_num:
            offset_x = 0
            last_line_num = setting.line_num
        cairo_move_to(cr,START_X + offset_x,START_Y + line_spacing * setting.line_num)

        pango_cairo_update_layout(cr,layout)
        if disable_liga:
            text_bytes = escape(text.decode('utf-8'))
            markup = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{text_bytes}</span>"
            markup_bytes = markup.encode('utf-8')
            pango_layout_set_markup(layout, markup_bytes, -1)
        else:
            pango_layout_set_text(layout,text,-1)
        pango_cairo_show_layout(cr, layout)
        pango_layout_get_size(layout,&temp_width,NULL)
        offset_x += pango_units_to_double(temp_width)

    status = cairo_status(cr)

    if cr == NULL or status == CAIRO_STATUS_NO_MEMORY:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        g_object_unref(layout)
        raise MemoryError("Cairo.Context can't be created.")
    elif status != CAIRO_STATUS_SUCCESS:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        g_object_unref(layout)
        raise Exception(cairo_status_to_string(status).decode())

    cairo_destroy(cr)
    cairo_surface_destroy(surface)
    g_object_unref(layout)
    return file_name

class MarkupUtils:
    @staticmethod
    def validate(text: str) -> bool:
       text_bytes = text.encode("utf-8")
       return pango_parse_markup(text_bytes, len(text_bytes), NULL, NULL, NULL, NULL, NULL)

    @staticmethod
    def text2svg(
        text: str,
        font: str,
        slant: str,
        weight: str,
        size: int,
        line_spacing: int,
        disable_liga: bool,
        file_name: str,
        START_X: int,
        START_Y: int,
        width: int,
        height: int,
    ) -> int:
        cdef cairo_surface_t* surface
        cdef cairo_t* context
        cdef PangoFontDescription* font_desc
        cdef PangoLayout* layout
        cdef cairo_status_t status
        cdef double width_layout = width
        cdef double font_size = size

        file_name_bytes = file_name.encode("utf-8")

        if disable_liga:
            text_bytes = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{text}</span>".encode("utf-8")
        else:
            text_bytes = text.encode("utf-8")

        surface = cairo_svg_surface_create(file_name_bytes,width,height)
        if surface == NULL:
            raise MemoryError("Cairo.SVGSurface can't be created.")
        context = cairo_create(surface)
        status = cairo_status(context)
        if context == NULL or status == CAIRO_STATUS_NO_MEMORY:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise MemoryError("Cairo.Context can't be created.")
        elif status != CAIRO_STATUS_SUCCESS:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise Exception(cairo_status_to_string(status))

        cairo_move_to(context,START_X,START_Y)
        layout = pango_cairo_create_layout(context)
        if layout==NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise MemoryError("Pango.Layout can't be created from Cairo Context.")
        pango_layout_set_width(layout, pango_units_from_double(width_layout))

        font_desc = pango_font_description_new()
        if font_desc==NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Pango.FontDesc can't be created.")
        pango_font_description_set_size(font_desc, pango_units_from_double(font_size))
        if font:
            pango_font_description_set_family(font_desc, font.encode("utf-8"))
        pango_font_description_set_style(font_desc, PangoUtils.str2style(slant).value)
        pango_font_description_set_weight(font_desc, PangoUtils.str2weight(weight).value)
        pango_layout_set_font_description(layout, font_desc)
        pango_font_description_free(font_desc)

        cairo_move_to(context,START_X,START_Y)
        pango_cairo_update_layout(context,layout)
        pango_layout_set_markup(layout,text_bytes,-1)
        pango_cairo_show_layout(context, layout)

        status = cairo_status(context)
        if context == NULL or status == CAIRO_STATUS_NO_MEMORY:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Cairo.Context can't be created.")
        elif status != CAIRO_STATUS_SUCCESS:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise Exception(cairo_status_to_string(status).decode())

        cairo_destroy(context)
        cairo_surface_destroy(surface)
        g_object_unref(layout)
        return file_name

cpdef str pango_version():
    return pango_version_string().decode('utf-8')

cpdef str cairo_version():
    return cairo_version_string().decode('utf-8')

IF UNAME_SYSNAME == "Linux":
    cpdef bint register_font(str font_path):
        """This function registers the font file using ``fontconfig`` so that
        it is available for use by Pango.
        Parameters
        ==========
        font_path : :class:`str`
            Relative or absolute path to font file.
        Returns
        =======
        :class:`bool`
                True means it worked without any error.
                False means there was an unknown error
        Examples
        --------
        >>> register_font("/home/roboto.tff")
        1
        Raises
        ------
        AssertionError
            Font is missing.
        """
        a=Path(font_path)
        assert a.exists(), f"font doesn't exist at {a.absolute()}"
        font_path = str(a.absolute())
        font_path_bytes=font_path.encode('ascii')
        cdef const unsigned char* fontPath = font_path_bytes
        fontAddStatus = FcConfigAppFontAddFile(FcConfigGetCurrent(), fontPath)
        if fontAddStatus:
            return True
        else:
            return False
