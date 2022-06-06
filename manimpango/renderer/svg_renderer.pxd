from cairo cimport *
from pango cimport *
from glib cimport *

from ..layout import Layout
from ..fonts import FontDescription

cdef class SVGRenderer:
    cdef cairo_surface_t* cairo_surface
    cdef cairo_t* cairo_context
    cdef PangoLayout* pango_layout
    cdef PangoFontDescription* pango_font_desc

    cdef str file_name
    cdef float width
    cdef float height
    cdef object py_layout
    cdef object py_font_desc

    cdef start_renderering(self)
    cpdef render(self)
