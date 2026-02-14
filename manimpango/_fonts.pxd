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


cdef extern from "fontconfig/fontconfig.h":
    # FontConfig types
    ctypedef unsigned char FcChar8

    # FontConfig functions
    bint FcConfigAppFontAddFile(void* config, const FcChar8* file)
    void FcConfigAppFontClear(void* config)


cdef extern from *:
    void g_object_unref(void* object)
