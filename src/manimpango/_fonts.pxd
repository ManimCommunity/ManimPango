"""Cython declarations for font management."""


cdef extern from "pango/pango.h":
    ctypedef struct PangoFontMap:
        pass
    ctypedef struct PangoFontFamily:
        pass

    void pango_font_map_list_families(PangoFontMap* fontmap, PangoFontFamily*** families, int* n_families)
    const char* pango_font_family_get_name(PangoFontFamily* family)


cdef extern from "pango/pangocairo.h":
    PangoFontMap* pango_cairo_font_map_new()
    PangoFontMap* pango_cairo_font_map_get_default()
    void pango_cairo_font_map_set_default(PangoFontMap* fontmap)


cdef extern from "font_backend.h":
    int manimpango_register_font(const char* utf8_path, char** error)
    int manimpango_unregister_font(const char* utf8_path, char** error)
    void manimpango_invalidate_font_backend()
    int manimpango_load_font_into_default_map(const char* utf8_path, char** error)


cdef extern from *:
    void g_object_unref(void* object)
    void g_free(void* mem)
