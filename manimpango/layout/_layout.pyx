from cairo cimport *
from pango cimport *

from . import Layout

include "../renderer/cairo_utils.pxi"

def get_bbox(py_layout: Layout) -> tuple:
    cdef cairo_surface_t* surface = cairo_image_surface_create(
        CAIRO_FORMAT_ARGB32,
        10,
        10
    )
    if surface == NULL:
        raise MemoryError("Cairo.ImageSurface can't be created.")

    cdef cairo_t* cairo_context = create_cairo_context_from_surface(surface)
    if cairo_context == NULL:
        raise MemoryError("Cairo.Context can't be created.")

    cdef PangoLayout* pango_layout = create_pango_layout(cairo_context)
    if pango_layout == NULL:
        raise MemoryError("Pango.Layout can't be created.")

    cdef PangoAttrList* pango_attr_list = create_attr_list()
    if pango_attr_list == NULL:
        raise MemoryError("Pango.AttrList can't be created.")

    cdef PangoFontDescription* pango_font_desc = create_font_desc()
    if pango_font_desc == NULL:
        raise MemoryError("Pango.FontDescription can't be created.")

    pylayout_to_pango_layout(
        pango_layout,
        py_layout,
        pango_attr_list
    )

    pyfontdesc_to_pango_font_desc(pango_font_desc, py_layout.font_desc)

    pango_layout_set_font_description(
        pango_layout,
        pango_font_desc
    )

    cdef PangoRectangle ink_rect, logical_rect
    pango_layout_get_pixel_extents (pango_layout, &ink_rect, &logical_rect)

    pango_font_description_free(pango_font_desc)
    pango_attr_list_unref(pango_attr_list)
    g_object_unref(pango_layout)
    cairo_destroy(cairo_context)
    cairo_surface_destroy(surface)

    return (
        logical_rect.x,
        logical_rect.y,
        logical_rect.width,
        logical_rect.height
    )
