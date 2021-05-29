from pango cimport *
from cairo cimport *

cpdef list list_fonts(fontconfig=False):
    """Lists the fonts available to Pango.
    This is usually same as system fonts but it also
    includes the fonts added through :func:`register_font`.

    Returns
    -------

    :class:`list` :
        List of fonts sorted alphabetically.
    """
    cdef PangoFontMap* fontmap
    if fontconfig:
        fontmap = pango_cairo_font_map_new_for_font_type(CAIRO_FONT_TYPE_FT)
    else:
        fontmap = pango_cairo_font_map_new()
    if fontmap is NULL:
        raise MemoryError("Pango.FontMap can't be created.")
    cdef int n_families = 0
    cdef PangoFontFamily** families = NULL
    pango_font_map_list_families(
        fontmap,
        &families,
        &n_families
    )
    if families is NULL or n_families==0:
        raise MemoryError("Pango returned unexpected length for families.")
    family_list=[]
    for i in range(n_families):
        name = <bytes>pango_font_family_get_name(families[i])
        # according to pango's docs, the `char *` returned from
        # `pango_font_family_get_name`is owned by pango, and python
        # shouldn't interfere with it. So, rather we are making a
        # deepcopy so that we don't worry about it.
        family_list.append(name.decode('utf-8'))
    g_free(families)
    g_object_unref(fontmap)
    family_list.sort()
    return family_list
