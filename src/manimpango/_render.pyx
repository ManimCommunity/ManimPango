#!python
# cython: language_level=3

"""Cython rendering engine for ManimPango."""

from __future__ import annotations

import cython
import tempfile
import os

from manimpango._render cimport *
from manimpango._text import RenderedText, LineInfo
from manimpango.enums import Style, Weight, Alignment


# Cache for Pango version check
cdef str _pango_version_cached = None


cdef str _get_pango_version():
    """Get cached Pango version string."""
    global _pango_version_cached
    if _pango_version_cached is None:
        _pango_version_cached = pango_version_string().decode('utf-8')
    return _pango_version_cached


def get_version_info() -> dict[str, str]:
    """Get version information for ManimPango and dependencies."""
    return {
        "manimpango": _get_manimpango_version(),
        "pango": _get_pango_version(),
        "cairo": cairo_version_string().decode('utf-8'),
    }


cdef str _get_manimpango_version():
    from importlib.metadata import version
    return version("ManimPango")


cpdef str validate_markup(str markup):
    """Validate Pango markup without rendering."""
    cdef GError* err = NULL
    cdef char* text = NULL
    cdef guint32 accel_char = 0
    cdef bytes markup_bytes
    cdef bint res
    cdef str message

    markup_bytes = markup.encode('utf-8')
    res = pango_parse_markup(
        <const char*>markup_bytes,
        -1,
        0,
        NULL,
        &text,
        &accel_char,
        &err
    )

    if text != NULL:
        g_free(text)

    if res:
        return ""
    else:
        if err != NULL:
            message = err.message.decode('utf-8')
            g_error_free(err)
            return message
        else:
            return "Unknown error"


cdef PangoFontDescription* _build_font_description(
    font,
    double size,
    int weight,
    int style,
    variations,
):
    """Build a PangoFontDescription from the given parameters."""
    cdef PangoFontDescription* desc = pango_font_description_new()
    cdef bytes font_bytes
    cdef bytes variations_bytes

    if desc == NULL:
        raise MemoryError("Failed to create PangoFontDescription")

    pango_font_description_set_size(desc, pango_units_from_double(size))

    if font is not None and len(font) > 0:
        font_bytes = font.encode('utf-8')
        pango_font_description_set_family(desc, <const char*>font_bytes)

    pango_font_description_set_weight(desc, <PangoWeight>weight)
    pango_font_description_set_style(desc, <PangoStyle>style)

    if variations is not None and len(variations) > 0:
        variations_bytes = variations.encode('utf-8')
        pango_font_description_set_variations(desc, <const char*>variations_bytes)

    return desc


cdef _set_layout_options(
    PangoLayout* layout,
    double width,
    int alignment,
    double line_spacing,
    bint justify,
    double indent,
):
    """Set layout options on a PangoLayout."""
    if width > 0:
        pango_layout_set_width(layout, pango_units_from_double(width))

    pango_layout_set_alignment(layout, <PangoAlignment>alignment)

    if line_spacing > 0:
        pango_layout_set_line_spacing(layout, <float>line_spacing)

    if justify:
        pango_layout_set_justify(layout, 1)

    if indent != 0:
        pango_layout_set_indent(layout, pango_units_from_double(indent))


cdef tuple _measure_layout(PangoLayout* layout):
    """Measure a PangoLayout to get its dimensions and baseline."""
    cdef int width, height
    cdef int baseline

    pango_layout_get_pixel_size(layout, &width, &height)
    baseline = pango_layout_get_baseline(layout)
    return (<float>width, <float>height, baseline)


cpdef object _render_to_svg(
    text,
    is_markup,
    font,
    size,
    weight,
    style,
    variations,
    width,
    alignment,
    line_spacing,
    justify,
    indent,
    disable_ligatures,
):
    """Render text to SVG."""
    # All cdef declarations at the top
    cdef cairo_surface_t* surface = NULL
    cdef cairo_t* cr = NULL
    cdef PangoLayout* layout = NULL
    cdef PangoFontDescription* font_desc = NULL
    cdef cairo_status_t status

    cdef double surface_width, surface_height
    cdef int final_width, final_height, final_baseline, line_count
    cdef str text_to_render
    cdef bytes text_bytes
    cdef bytes tmp_path_bytes

    cdef list lines
    cdef int i
    cdef PangoLayoutLine* line
    cdef PangoRectangle ink_rect, logical_rect

    # Build the text/markup string with ligature disabling if needed
    if disable_ligatures and not is_markup:
        text_to_render = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{text}</span>"
        is_markup = True
    elif disable_ligatures and is_markup:
        text_to_render = f"<span font_features='liga=0,dlig=0,clig=0,hlig=0'>{text}</span>"
    else:
        text_to_render = text

    text_bytes = text_to_render.encode('utf-8')

    # === Measure pass ===
    # Need a real surface for pango_cairo_create_layout to work;
    # a minimal image surface is cheapest.
    surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, 1, 1)
    if surface == NULL:
        raise MemoryError("Failed to create Cairo image surface for measuring")

    cr = cairo_create(surface)
    if cr == NULL:
        cairo_surface_destroy(surface)
        raise MemoryError("Failed to create Cairo context")

    try:
        layout = pango_cairo_create_layout(cr)
        if layout == NULL:
            raise MemoryError("Failed to create Pango layout")

        font_desc = _build_font_description(font, size, weight, style, variations)
        pango_layout_set_font_description(layout, font_desc)
        pango_font_description_free(font_desc)
        font_desc = NULL

        _set_layout_options(layout, width, alignment, line_spacing, justify, indent)

        if is_markup:
            pango_layout_set_markup(layout, <const char*>text_bytes, -1)
        else:
            pango_layout_set_text(layout, <const char*>text_bytes, -1)

        final_width, final_height, final_baseline = _measure_layout(layout)
        surface_width = final_width + 2
        surface_height = final_height + 2

    finally:
        if layout != NULL:
            g_object_unref(layout)
            layout = NULL
        if cr != NULL:
            cairo_destroy(cr)
            cr = NULL
        if surface != NULL:
            cairo_surface_destroy(surface)
            surface = NULL

    # === Render pass ===
    with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        tmp_path_bytes = tmp_path.encode('utf-8')
        surface = cairo_svg_surface_create(<const char*>tmp_path_bytes, surface_width, surface_height)

        if surface == NULL:
            raise MemoryError("Failed to create SVG surface")

        status = cairo_surface_status(surface)
        if status != CAIRO_STATUS_SUCCESS:
            cairo_surface_destroy(surface)
            raise RuntimeError(f"Cairo error: {cairo_status_to_string(status).decode()}")

        cr = cairo_create(surface)
        if cr == NULL:
            cairo_surface_destroy(surface)
            raise MemoryError("Failed to create Cairo context")

        try:
            layout = pango_cairo_create_layout(cr)
            if layout == NULL:
                raise MemoryError("Failed to create Pango layout")

            font_desc = _build_font_description(font, size, weight, style, variations)
            pango_layout_set_font_description(layout, font_desc)
            pango_font_description_free(font_desc)
            font_desc = NULL

            _set_layout_options(layout, width, alignment, line_spacing, justify, indent)

            if is_markup:
                pango_layout_set_markup(layout, <const char*>text_bytes, -1)
            else:
                pango_layout_set_text(layout, <const char*>text_bytes, -1)

            cairo_move_to(cr, 1, 1)
            pango_cairo_update_layout(cr, layout)
            pango_cairo_show_layout(cr, layout)

            final_width, final_height, final_baseline = _measure_layout(layout)
            line_count = pango_layout_get_line_count(layout)

            # Extract line info
            lines = []
            for i in range(line_count):
                line = pango_layout_get_line(layout, i)
                if line == NULL:
                    continue
                pango_layout_line_get_pixel_extents(line, &ink_rect, &logical_rect)
                info = LineInfo(
                    text="",
                    start_index=line.start_index,
                    width=<float>logical_rect.width,
                    height=<float>logical_rect.height,
                    baseline=0,
                    y_offset=logical_rect.y,
                )
                lines.append(info)

            # Update baseline
            for info in lines:
                info._baseline = final_baseline - info.y_offset

        finally:
            if layout != NULL:
                g_object_unref(layout)
            if cr != NULL:
                cairo_destroy(cr)
            if surface != NULL:
                cairo_surface_destroy(surface)

        with open(tmp_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return RenderedText(
        _svg=svg_content,
        _width=<float>final_width,
        _height=<float>final_height,
        _baseline=final_baseline,
        _line_count=line_count,
        _lines=lines,
    )


def render(
    text,
    *,
    is_markup=False,
    font=None,
    size=12.0,
    weight=Weight.NORMAL,
    style=Style.NORMAL,
    variations=None,
    width=None,
    alignment=Alignment.LEFT,
    line_spacing=None,
    justify=False,
    indent=0.0,
    disable_ligatures=False,
):
    """Render text to SVG."""
    # Convert weight to int if it's a Weight enum
    weight_value = int(weight)

    # Convert variations dict to Pango format string
    variations_str = ""
    if variations is not None:
        parts = []
        for k, v in variations.items():
            parts.append(f"{k}={v}")
        variations_str = ",".join(parts)

    # Convert width: None -> -1 for "no wrapping"
    layout_width = -1.0
    if width is not None:
        layout_width = width

    # Convert line_spacing: None -> -1 for "not set"
    spacing = -1.0
    if line_spacing is not None:
        spacing = line_spacing

    if is_markup:
        error = validate_markup(text)
        if error:
            raise ValueError(f"Invalid Pango markup: {error}")

    return _render_to_svg(
        text=text,
        is_markup=is_markup,
        font=font if font else "",
        size=size,
        weight=weight_value,
        style=style.value,
        variations=variations_str if variations_str else "",
        width=layout_width,
        alignment=alignment.value,
        line_spacing=spacing,
        justify=justify,
        indent=indent,
        disable_ligatures=disable_ligatures,
    )
