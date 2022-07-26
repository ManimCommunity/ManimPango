from cairo cimport *
from pango cimport *
from glib cimport *

from ..layout import Layout
from ..fonts import FontDescription

cdef class PNGRenderer:
    cdef cairo_surface_t* cairo_surface
    cdef cairo_t* cairo_context
    cdef PangoLayout* pango_layout
    cdef PangoFontDescription* pango_font_desc

    cdef str _file_name
    cdef float _width
    cdef float _height
    cdef object py_layout
    cdef object py_font_desc

    cdef bint start_renderering(self)
    cpdef bint render(self)
