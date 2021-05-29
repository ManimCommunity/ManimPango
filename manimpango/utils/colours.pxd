from pango cimport *

cdef class Color:
    cdef int red
    cdef int green
    cdef int blue
    cdef PangoColor* color
    cpdef Color copy(self)
    cpdef void parse_color(self, char* spec)
    cpdef str to_string(self)
