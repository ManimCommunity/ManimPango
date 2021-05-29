from cairo cimport *
from glib cimport *
from pango cimport *

from ..layout import Layout
from ..font_manager import FontProperties

cdef class CairoRenderer:
    cdef object py_layout
    cdef PangoLayout* layout
    cdef cairo_surface_t* surface
    cdef cairo_t* context
    cdef PangoFontDescription* font_desc
    cdef void* intialise_renderer(self)
    cdef void* start_rendering(self)
    cdef void* finalise_renderer(self)
    cpdef bint render(self)
    cdef str is_context_fine(self, raise_error=*)
    cdef void* convert_py_font_to_pango_font(self)
    cdef void* convert_py_layout_to_pango_layout(self)


cdef class SVGRenderer(CairoRenderer):
    cdef str file_name
    cdef float width
    cdef float height
    cdef object move_to
