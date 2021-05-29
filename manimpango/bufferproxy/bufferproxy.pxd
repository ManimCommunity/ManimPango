cdef class BaseBuffer:
    cdef size_t _buffer_size(self)
    cdef void* _buffer_ptr(self)
    cdef bint _buffer_writable(self)


cdef class ImageBuffer(Buffer):
    cdef int size
    cdef unsigned char *buf
    cdef cairo_t* cr
    cdef cairo_surface_t* surface
    cdef int set_cairo_data(
        self,
        cairo_t* cr,
        cairo_surface_t* surface
    )
    cdef size_t _buffer_size(self)
    cdef void* _buffer_ptr(self)
    cdef bint _buffer_writable(self)
