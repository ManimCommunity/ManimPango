from pango cimport *


cdef class _FontDescription:
    cdef PangoFontDescription* pango_font_desc
