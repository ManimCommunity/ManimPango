from cairo cimport *
from pango cimport *
from glib cimport *

from ..layout import Layout

cdef class SVGRenderer:
    cdef cairo_surface_t* cairo_surface
    cdef cairo_t* cairo_context
    cdef PangoLayout* pango_layout

    cdef str file_name
    cdef float width
    cdef float height
    cdef object py_layout

    cdef start_renderering(self)