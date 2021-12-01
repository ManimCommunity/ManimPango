from xml.sax.saxutils import escape
from .utils import *
from .enums import Alignment
import warnings
import typing

class TextSetting:
    """Formatting for slices of a :class:`manim.mobject.svg.text_mobject.Text` object."""
    def __init__(
        self,
        start:int,
        end:int,
        font:str,
        slant,
        weight,
        line_num=-1,
        color: str=None,
    ):
        self.start = start
        self.end = end
        self.font = font
        self.slant = slant
        self.weight = weight
        self.line_num = line_num
        self.color = color


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
    orig_text:str,
    pango_width: typing.Union[int, None] = None,
) -> int:
    """Render an SVG file from a :class:`manim.mobject.svg.text_mobject.Text` object."""
    cdef cairo_surface_t* surface
    cdef cairo_t* cr
    cdef PangoFontDescription* font_desc
    cdef PangoLayout* layout
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

    if layout == NULL:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise MemoryError("Pango.Layout can't be created from Cairo Context.")

    if pango_width is None:
        pango_layout_set_width(layout, pango_units_from_double(width))
    else:
        pango_layout_set_width(layout, pango_units_from_double(pango_width))

    for setting in settings:
        family = setting.font.encode('utf-8')
        style = PangoUtils.str2style(setting.slant)
        weight = PangoUtils.str2weight(setting.weight)
        color = setting.color
        text_str = orig_text[setting.start : setting.end].replace("\n", " ")
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
        markup = escape(text_str)
        if color:
            markup = (f"<span color='{color}'>{markup}</span>")
            if MarkupUtils.validate(markup):
                cairo_destroy(cr)
                cairo_surface_destroy(surface)
                g_object_unref(layout)
                raise ValueError(f"Pango cannot recognize your color '{color}' for text '{text_str}'.")
        if disable_liga:
            markup = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{markup}</span>"
        pango_layout_set_markup(layout, markup.encode('utf-8'), -1)
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
    def validate(markup: str) -> str:
        """Validates whether markup is a valid Markup
        and return the error's if any.

        Parameters
        ==========
        markup : :class:`str`
            The markup which should be checked.

        Returns
        =======
        :class:`str`
            Returns empty string if markup is valid. If markup
            contains error it return the error message.

        """
        cdef GError *err = NULL
        text_bytes = markup.encode("utf-8")
        res = pango_parse_markup(
            text_bytes,
            -1,
            0,
            NULL,
            NULL,
            NULL,
            &err
        )
        if res:
            return ""
        else:
            message = <bytes>err.message
            g_error_free(err)
            return message.decode('utf-8')

    @staticmethod
    def text2svg(
        text: str,
        font: str,
        slant: str,
        weight: str,
        size: int,
        _: int, # for some there was a keyword here.
        disable_liga: bool,
        file_name: str,
        START_X: int,
        START_Y: int,
        width: int,
        height: int,
        *, # keyword only arguments below
        justify: bool = None,
        indent: float = None,
        line_spacing: float = None,
        alignment: Alignment = None,
        pango_width: typing.Union[int, None] = None,
    ) -> int:
        """Render an SVG file from a :class:`manim.mobject.svg.text_mobject.MarkupText` object."""
        cdef cairo_surface_t* surface
        cdef cairo_t* context
        cdef PangoFontDescription* font_desc
        cdef PangoLayout* layout
        cdef cairo_status_t status
        cdef double font_size = size
        cdef int temp_int # a temporary C integer for conversion

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
        if layout == NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise MemoryError("Pango.Layout can't be created from Cairo Context.")

        if pango_width is None:
            pango_layout_set_width(layout, pango_units_from_double(width))
        else:
            pango_layout_set_width(layout, pango_units_from_double(pango_width))

        if justify:
            pango_layout_set_justify(layout, justify)

        if indent:
            temp_int = pango_units_from_double(indent)
            pango_layout_set_indent(layout, temp_int)

        if line_spacing:
            # Typical values are: 0, 1, 1.5, 2.
            ret = set_line_width(layout, line_spacing)
            if not ret:
                # warn that line spacing don't work
                # because of old Pango version they
                # have
                warnings.warn(
                    "Pango Version<1.44 found."
                    "Impossible to set line_spacing."
                    "Expect Ugly Output."
                )

        if alignment:
            pango_layout_set_alignment(layout, alignment.value)

        font_desc = pango_font_description_new()
        if font_desc==NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            g_object_unref(layout)
            raise MemoryError("Pango.FontDesc can't be created.")
        pango_font_description_set_size(font_desc, pango_units_from_double(font_size))
        if font is not None and len(font) != 0:
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
