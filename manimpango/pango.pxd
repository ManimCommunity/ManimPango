from glib cimport *
from cairo cimport *


cdef extern from "pango/pangocairo.h":
    ctypedef struct PangoLayout:
        pass
    ctypedef struct PangoFontMap:
        pass
    ctypedef struct PangoFontFamily:
        pass

    PangoLayout* pango_cairo_create_layout(cairo_t* cr)
    void pango_layout_set_width(
        PangoLayout* layout,
        int width
    )
    void pango_layout_set_justify(
        PangoLayout *layout,
        gboolean justify
    )
    void pango_layout_set_indent(
        PangoLayout *layout,
        int indent
    )
    void pango_layout_set_alignment(
        PangoLayout *layout,
        int alignment
    )
    void pango_cairo_update_layout(
        cairo_t* cr,
        PangoLayout* layout
    )
    void pango_layout_set_markup(
        PangoLayout *layout,
        const char *markup,
        int length
    )
    void pango_cairo_show_layout(
        cairo_t* cr,
        PangoLayout* layout
    )
    gboolean pango_parse_markup(
       const char *markup_text,
       int length,
       unsigned int accel_marker,
       void* attr_list,
       void* text,
       void* accel_char,
       void* error
    )
    const char* pango_version_string()
    PangoFontMap* pango_cairo_font_map_new()
    void pango_font_map_list_families(
        PangoFontMap *fontmap,
        PangoFontFamily ***families,
        int *n_families
    )
    const char* pango_font_family_get_name(
        PangoFontFamily *family
    )
