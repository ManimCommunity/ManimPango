#!python
# cython: language_level=3

"""Cython rendering engine for ManimPango."""

from __future__ import annotations

import cython
import tempfile
import os

from manimpango._render cimport *
from manimpango._fonts cimport acquire_font_map
from manimpango._text import Bounds, LineInfo, RenderedText
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


cdef PangoLayout* _create_managed_layout(cairo_t* cr):
    """Create a layout from the process-managed font map, never Pango's default."""
    cdef PangoFontMap* fontmap = acquire_font_map()
    cdef PangoContext* context = NULL
    cdef PangoLayout* layout = NULL

    if fontmap == NULL:
        raise MemoryError("Failed to acquire managed Pango font map")
    try:
        context = pango_font_map_create_context(fontmap)
        if context == NULL:
            raise MemoryError("Failed to create Pango context")
        pango_cairo_update_context(cr, context)
        layout = pango_layout_new(context)
        if layout == NULL:
            raise MemoryError("Failed to create Pango layout")
        return layout
    finally:
        if context != NULL:
            g_object_unref(context)
        g_object_unref(fontmap)


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


cdef void _insert_ranged_attribute(
    PangoAttrList* attrs,
    PangoAttribute* attribute,
    int start,
    int end,
) except *:
    """Set a validated UTF-8 byte range and transfer ``attribute`` to attrs."""
    if attribute == NULL:
        raise MemoryError("Failed to create Pango text attribute")
    attribute.start_index = <guint>start
    attribute.end_index = <guint>end
    pango_attr_list_insert(attrs, attribute)


cdef void _add_span_attributes(
    PangoAttrList* attrs,
    object spans,
    int text_length,
) except *:
    """Attach normalized structured-span attributes to one Pango attribute list."""
    cdef object span
    cdef object value
    cdef int start, end, style_value, weight_value
    cdef bytes encoded
    cdef bytes feature_string
    cdef bytes variation_string
    cdef PangoColor color
    cdef PangoFontDescription* variation_desc

    for span in spans:
        start = span["start"]
        end = span["end"]
        if start < 0 or end < start or end > text_length:
            raise ValueError("normalized span bounds must be valid UTF-8 byte offsets")

        if "font" in span:
            encoded = span["font"].encode("utf-8")
            _insert_ranged_attribute(
                attrs, pango_attr_family_new(<const char*>encoded), start, end
            )
        if "size" in span:
            _insert_ranged_attribute(
                attrs,
                pango_attr_size_new_absolute(pango_units_from_double(span["size"])),
                start,
                end,
            )
        if "weight" in span:
            weight_value = span["weight"]
            _insert_ranged_attribute(
                attrs, pango_attr_weight_new(<PangoWeight>weight_value), start, end
            )
        if "style" in span:
            value = span["style"]
            style_value = value.value if hasattr(value, "value") else value
            _insert_ranged_attribute(
                attrs, pango_attr_style_new(<PangoStyle>style_value), start, end
            )
        if "foreground" in span:
            encoded = span["foreground"].encode("utf-8")
            if not pango_color_parse(&color, <const char*>encoded):
                raise ValueError(f"Invalid Pango foreground color: {span['foreground']}")
            _insert_ranged_attribute(
                attrs,
                pango_attr_foreground_new(color.red, color.green, color.blue),
                start,
                end,
            )
        if "features" in span:
            feature_string = ",".join(
                f"{tag}={int(enabled)}"
                for tag, enabled in span["features"].items()
            ).encode("ascii")
            _insert_ranged_attribute(
                attrs,
                pango_attr_font_features_new(<const char*>feature_string),
                start,
                end,
            )
        if "variations" in span:
            variation_string = ",".join(
                f"{tag}={axis_value}"
                for tag, axis_value in span["variations"].items()
            ).encode("ascii")
            variation_desc = pango_font_description_new()
            if variation_desc == NULL:
                raise MemoryError("Failed to create Pango variation description")
            try:
                pango_font_description_set_variations(
                    variation_desc, <const char*>variation_string
                )
                _insert_ranged_attribute(
                    attrs,
                    pango_attr_font_desc_new(variation_desc),
                    start,
                    end,
                )
            finally:
                pango_font_description_free(variation_desc)


cdef void _set_layout_text_and_attributes(
    PangoLayout* layout,
    bytes source,
    bint is_markup,
    bint disable_ligatures,
    object spans,
) except *:
    """Set one layout's plain text and its Pango attributes.

    Markup is parsed explicitly rather than passed to ``pango_layout_set_markup``
    so both markup and plain text follow the same text-plus-attributes pipeline.
    This also lets ligature settings be expressed as an attribute, avoiding
    generated markup around unescaped plain text.
    """
    cdef PangoAttrList* attrs = NULL
    cdef PangoAttribute* features = NULL
    cdef char* parsed_text = NULL
    cdef GError* err = NULL
    cdef guint32 accel_char = 0
    cdef bint parsed
    cdef str message

    if is_markup:
        parsed = pango_parse_markup(
            <const char*>source,
            -1,
            0,
            &attrs,
            &parsed_text,
            &accel_char,
            &err,
        )
        if not parsed:
            if err != NULL:
                message = err.message.decode("utf-8", "replace")
                g_error_free(err)
            else:
                message = "Unknown error"
            if attrs != NULL:
                pango_attr_list_unref(attrs)
            if parsed_text != NULL:
                g_free(parsed_text)
            raise ValueError(f"Invalid Pango markup: {message}")

        # pango_parse_markup returns an allocated, NUL-terminated UTF-8 string.
        pango_layout_set_text(layout, <const char*>parsed_text, -1)
        g_free(parsed_text)
        parsed_text = NULL
    else:
        pango_layout_set_text(layout, <const char*>source, -1)

    if disable_ligatures or spans:
        if attrs == NULL:
            attrs = pango_attr_list_new()
            if attrs == NULL:
                raise MemoryError("Failed to create Pango attribute list")

    if spans:
        _add_span_attributes(attrs, spans, len(source))

    if disable_ligatures:
        features = pango_attr_font_features_new(b"liga=0,dlig=0,clig=0,hlig=0")
        if features == NULL:
            pango_attr_list_unref(attrs)
            raise MemoryError("Failed to create Pango ligature attribute")
        pango_attr_list_insert(attrs, features)

    if attrs != NULL:
        pango_layout_set_attributes(layout, attrs)
        pango_attr_list_unref(attrs)


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
    spans,
):
    """Render text to SVG."""
    # All cdef declarations at the top
    cdef cairo_surface_t* surface = NULL
    cdef cairo_t* cr = NULL
    cdef PangoLayout* layout = NULL
    cdef PangoFontDescription* font_desc = NULL
    cdef PangoLayoutIter* layout_iter = NULL
    cdef cairo_status_t status

    cdef double surface_width, surface_height
    cdef int final_width, final_height, final_baseline, line_count
    cdef int viewport_left, viewport_top, viewport_right, viewport_bottom
    cdef int viewport_width, viewport_height
    cdef bytes text_bytes
    cdef bytes tmp_path_bytes
    cdef bytes rendered_text_bytes
    cdef str rendered_text
    cdef int next_start_index, end_index
    cdef double baseline_svg

    cdef list lines
    cdef int i
    cdef PangoLayoutLine* line
    cdef PangoRectangle ink_rect, logical_rect

    text_bytes = text.encode('utf-8')

    # === Measure pass ===
    # Need a real surface to update the explicitly managed Pango context;
    # a minimal image surface is cheapest.
    surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, 1, 1)
    if surface == NULL:
        raise MemoryError("Failed to create Cairo image surface for measuring")

    cr = cairo_create(surface)
    if cr == NULL:
        cairo_surface_destroy(surface)
        raise MemoryError("Failed to create Cairo context")

    try:
        layout = _create_managed_layout(cr)
        if layout == NULL:
            raise MemoryError("Failed to create Pango layout")

        font_desc = _build_font_description(font, size, weight, style, variations)
        pango_layout_set_font_description(layout, font_desc)
        pango_font_description_free(font_desc)
        font_desc = NULL

        _set_layout_options(layout, width, alignment, line_spacing, justify, indent)

        _set_layout_text_and_attributes(
            layout, text_bytes, is_markup, disable_ligatures, spans
        )

        final_width, final_height, final_baseline = _measure_layout(layout)
        # Layout and iterator extents are Pango units.  Keep the viewport in
        # the same units until the Cairo surface and public metadata boundary.
        pango_layout_get_extents(layout, &ink_rect, &logical_rect)
        viewport_left = logical_rect.x
        if ink_rect.x < viewport_left:
            viewport_left = ink_rect.x
        viewport_top = logical_rect.y
        if ink_rect.y < viewport_top:
            viewport_top = ink_rect.y
        viewport_right = logical_rect.x + logical_rect.width
        if ink_rect.x + ink_rect.width > viewport_right:
            viewport_right = ink_rect.x + ink_rect.width
        viewport_bottom = logical_rect.y + logical_rect.height
        if ink_rect.y + ink_rect.height > viewport_bottom:
            viewport_bottom = ink_rect.y + ink_rect.height
        viewport_width = viewport_right - viewport_left
        viewport_height = viewport_bottom - viewport_top
        surface_width = pango_units_to_double(viewport_width)
        surface_height = pango_units_to_double(viewport_height)

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
            layout = _create_managed_layout(cr)
            if layout == NULL:
                raise MemoryError("Failed to create Pango layout")

            font_desc = _build_font_description(font, size, weight, style, variations)
            pango_layout_set_font_description(layout, font_desc)
            pango_font_description_free(font_desc)
            font_desc = NULL

            _set_layout_options(layout, width, alignment, line_spacing, justify, indent)

            _set_layout_text_and_attributes(
                layout, text_bytes, is_markup, disable_ligatures, spans
            )

            cairo_move_to(
                cr,
                -pango_units_to_double(viewport_left),
                -pango_units_to_double(viewport_top),
            )
            pango_cairo_update_layout(cr, layout)
            pango_cairo_show_layout(cr, layout)

            final_width, final_height, final_baseline = _measure_layout(layout)
            line_count = pango_layout_get_line_count(layout)
            rendered_text_bytes = <bytes>pango_layout_get_text(layout)
            rendered_text = rendered_text_bytes.decode("utf-8")
            baseline_svg = (
                pango_units_to_double(final_baseline)
                - pango_units_to_double(viewport_top)
            )

            lines = []
            layout_iter = pango_layout_get_iter(layout)
            if layout_iter == NULL:
                raise MemoryError("Failed to create Pango layout iterator")
            for i in range(line_count):
                line = pango_layout_iter_get_line_readonly(layout_iter)
                if line == NULL:
                    continue
                pango_layout_iter_get_line_extents(
                    layout_iter, &ink_rect, &logical_rect
                )
                if i + 1 < line_count:
                    next_start_index = pango_layout_get_line(layout, i + 1).start_index
                else:
                    next_start_index = len(rendered_text_bytes)
                end_index = next_start_index
                line_text = rendered_text_bytes[line.start_index:end_index].decode("utf-8")
                if line_text.endswith("\n"):
                    line_text = line_text[:-1]
                    end_index -= 1
                lines.append(LineInfo(
                    text=line_text,
                    start=len(rendered_text_bytes[:line.start_index].decode("utf-8")),
                    end=len(rendered_text_bytes[:end_index].decode("utf-8")),
                    bounds=Bounds(
                        pango_units_to_double(logical_rect.x - viewport_left),
                        pango_units_to_double(logical_rect.y - viewport_top),
                        pango_units_to_double(logical_rect.width),
                        pango_units_to_double(logical_rect.height),
                    ),
                    baseline=(
                        pango_units_to_double(
                            pango_layout_iter_get_baseline(layout_iter)
                        )
                        - pango_units_to_double(viewport_top)
                    ),
                ))
                if i + 1 < line_count:
                    pango_layout_iter_next_line(layout_iter)

        finally:
            if layout_iter != NULL:
                pango_layout_iter_free(layout_iter)
                layout_iter = NULL
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
        svg=svg_content,
        width=pango_units_to_double(viewport_width),
        height=pango_units_to_double(viewport_height),
        baseline=(
            pango_units_to_double(final_baseline)
            - pango_units_to_double(viewport_top)
        ),
        lines=tuple(lines),
        ink_bounds=Bounds(
            0.0, 0.0,
            pango_units_to_double(viewport_width),
            pango_units_to_double(viewport_height),
        ),
        logical_bounds=Bounds(
            0.0, 0.0,
            pango_units_to_double(viewport_width),
            pango_units_to_double(viewport_height),
        ),
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
    spans=(),
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
        spans=spans,
    )
