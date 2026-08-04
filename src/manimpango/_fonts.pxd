"""Cython declarations for font management."""

from libc.stddef cimport size_t

cdef extern from "pango/pango.h":
    ctypedef struct PangoFontMap:
        pass
    ctypedef struct PangoFontFamily:
        pass

    void pango_font_map_list_families(PangoFontMap* fontmap, PangoFontFamily*** families, int* n_families)
    const char* pango_font_family_get_name(PangoFontFamily* family)


cdef extern from "pango/pangocairo.h":
    PangoFontMap* pango_cairo_font_map_new()


cdef extern from "font_backend.h":
    int manimpango_register_font(const char* utf8_path, char** error)
    int manimpango_unregister_font(const char* utf8_path, char** error)
    void* manimpango_build_font_map(const char* const* utf8_paths, size_t count, char** error)

cdef PangoFontMap* acquire_font_map() except NULL


cdef extern from *:
    void* g_object_ref(void* object)
    void g_object_unref(void* object)
    void g_free(void* mem)
