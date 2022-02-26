def markup_to_svg(
    markup_str: str,
    file_name: str,
    width: int = 1920,
    height: int = 1080,
    *, # keyword only arguments below
    justify: bool = False,
    indent: int = 0,
    alignment: int = 0,
    line_width: int = -1,
) -> str:
    """
    Render an SVG file from a :class:`manim.mobject.svg.text_mobject.Text` object.
    """
    cdef cairo_surface_t* surface
    cdef cairo_t* context
    cdef cairo_status_t status
    cdef PangoLayout* layout

    file_name_bytes = file_name.encode("utf-8")
    surface = cairo_svg_surface_create(file_name_bytes, width, height)
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

    layout = pango_cairo_create_layout(context)
    if layout == NULL:
        cairo_destroy(context)
        cairo_surface_destroy(surface)
        raise MemoryError("Pango.Layout can't be created from Cairo Context.")

    pango_layout_set_width(layout, line_width)
    pango_layout_set_justify(layout, justify)
    pango_layout_set_indent(layout, indent)
    pango_layout_set_alignment(layout, alignment)

    pango_cairo_update_layout(context, layout)
    pango_layout_set_markup(layout, markup_str.encode("utf-8"), -1)
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


def validate(markup: str) -> str:
    """
    Validates whether markup is a valid Markup
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


cpdef str pango_version():
    return pango_version_string().decode("utf-8")


cpdef str cairo_version():
    return cairo_version_string().decode("utf-8")
