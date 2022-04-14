from pango cimport *

cdef class FontDescription:
    cdef PangoFontDescription* pango_font_desc
