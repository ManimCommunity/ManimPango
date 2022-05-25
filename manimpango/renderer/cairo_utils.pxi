from cairo cimport *
from pango cimport *
from ..layout import Layout

cdef cairo_t* create_cairo_context_from_surface(cairo_surface_t* surface):
    cr = cairo_create(surface)
    status = cairo_status(cr)

    if cr is NULL or status == CAIRO_STATUS_NO_MEMORY:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise MemoryError("Cairo.Context can't be created.")
    elif status != CAIRO_STATUS_SUCCESS:
        cairo_destroy(cr)
        cairo_surface_destroy(surface)
        raise Exception(cairo_status_to_string(status))

    return cr

cdef PangoLayout* create_pango_layout(cairo_t* context):
    # the resulting layout should be freed seperately
    cdef PangoLayout* layout = pango_cairo_create_layout(context)
    if layout is NULL:
        cairo_destroy(context)
        raise MemoryError("Pango.Layout can't be created from Cairo Context.")
    return layout

cdef pylayout_to_pango_layout(PangoLayout* layout, object py_layout):
    if py_layout.text:
        pango_layout_set_text(
            layout,
            py_layout.text.encode('utf-8'),
            -1,
        )
    if py_layout.markup:
        pango_layout_set_markup(
            layout,
            py_layout.markup.encode('utf-8'),
            -1,
        )
    if py_layout.width:
        pango_layout_set_width(
            layout,
            pango_units_from_double(py_layout.width),
        )
    if py_layout.height:
        if py_layout.height > 0:
            pango_layout_set_height(
                layout,
                pango_units_from_double(py_layout.height),
            )
        else:
            pango_layout_set_height(
                layout,
                py_layout.height,
            )
    if py_layout.alignment:
        pango_layout_set_alignment(
            layout,
            py_layout.alignment.value,
        )
