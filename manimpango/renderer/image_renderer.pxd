from cairo cimport *
from glib cimport *
from pango cimport *

from ..fonts import FontDescription
from ..layout import Layout


cdef class ImageRenderer:
    cdef cairo_surface_t* cairo_surface
    cdef cairo_t* cairo_context
    cdef PangoLayout* pango_layout
    cdef PangoFontDescription* pango_font_desc
    cdef PangoAttrList* pango_attr_list

    cdef str _file_name
    cdef int _width
    cdef int _height
    cdef object py_layout
    cdef object py_font_desc

    cdef bint start_renderering(self)
    cpdef bint render(self)
