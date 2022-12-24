from cairo cimport *
from pango cimport *

from ..layout import Layout

include "../attributes/attributes.pxi"

cdef str is_context_fine(cairo_t* context):
    cdef cairo_status_t status
    status = cairo_status(context)
    if status == CAIRO_STATUS_NO_MEMORY:
        cairo_destroy(context)
        raise MemoryError("Cairo returned memory error")
    elif status != CAIRO_STATUS_SUCCESS:
        temp_bytes = <bytes>cairo_status_to_string(status)
        return temp_bytes.decode('utf-8')
    return ""

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
        # TODO: raise specific excpetions
        raise Exception(cairo_status_to_string(status))

    return cr

cdef PangoLayout* create_pango_layout(cairo_t* context):
    # the resulting layout should be freed seperately
    cdef PangoLayout* layout = pango_cairo_create_layout(context)
    if layout is NULL:
        cairo_destroy(context)
        raise MemoryError("Pango.Layout can't be created from Cairo Context.")
    return layout

cdef PangoFontDescription* create_font_desc():
    # the resulting font_desc should be freed seperately
    pango_font_desc = pango_font_description_new()
    if pango_font_desc is NULL:
        raise MemoryError("pango_font_description_new() returned NULL")

    return pango_font_desc

cdef PangoAttrList* create_attr_list():
    # the resulting attr_list should be freed seperately
    attr_list = pango_attr_list_new()
    if attr_list is NULL:
        raise MemoryError("pango_attr_list_new() returned NULL")

    return attr_list

cdef pylayout_to_pango_layout(
    PangoLayout* layout,
    object py_layout,
    PangoAttrList* attr_list,
):
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
    if py_layout.attributes:
        convert_to_pango_attributes(
            py_layout.attributes,
            attr_list,
        )
        pango_layout_set_attributes(
            layout,
            attr_list,
        )

cdef pyfontdesc_to_pango_font_desc(PangoFontDescription* font_desc, object py_font_desc):
    if py_font_desc.family:
        pango_font_description_set_family(
            font_desc, py_font_desc.family.encode())
    if py_font_desc.size:
        pango_font_description_set_size(font_desc,
            py_font_desc.size * PANGO_SCALE)
    pango_font_description_set_style(font_desc,
        py_font_desc.style.value)
    pango_font_description_set_weight(font_desc,
        py_font_desc.weight.value)
    pango_font_description_set_variant(font_desc,
        py_font_desc.variant.value)
