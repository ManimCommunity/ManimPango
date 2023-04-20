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
