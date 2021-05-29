# This should contain the buffer proxy to get the data
# from cairo to say a numpy array.

# Have a look at how I previouslt implemented this
# https://github.com/naveen521kk/text2svg/blob/feat-numpy/text2svg/buf.pyx
# https://github.com/naveen521kk/text2svg/blob/feat-numpy/text2svg/ctext2np.pyx


from libc.string cimport memcpy
from cpython cimport PyBuffer_FillInfo, PyBUF_WRITABLE

cdef class BaseBuffer:
    """A base for Buffer which can be read using Pillow
    or converted to an array using Numpy.

    Note
    ====
    The buffer or array isn't writable.
    So, you should make a copy of the buffer to
    write.
    """
    cdef size_t _buffer_size(self):
        return 0

    cdef void* _buffer_ptr(self):
        return NULL

    cdef bint _buffer_writable(self):
        return True

    def __getbuffer__(self, Py_buffer *view, int flags):
        if flags & PyBUF_WRITABLE and not self._buffer_writable():
            raise ValueError('buffer is not writable')
        PyBuffer_FillInfo(view, self, self._buffer_ptr(), self._buffer_size(), 0, flags)

    @property
    def buffer_size(self):
        """The size of the buffer in bytes."""
        return self._buffer_size()

    @property
    def buffer_ptr(self):
        """The memory address of the buffer."""
        return <size_t>self._buffer_ptr()

    def to_bytes(self):
        """Return the contents of this buffer as ``bytes``.
        """
        return <bytes>(<char*>self._buffer_ptr())[:self._buffer_size()]

cdef class ImageBuffer(Buffer):
    # This will give the ImageBuffer from Cairo.
    # The Cairo's surface shouldn't be destroyed
    # before reading this or else it would create
    # SegFaults. Now, we don't plan to depend on
    # Numpy so we are going to get a reference of
    # the Cairo's surface and free it up only when
    # this buffer is garbage collected.
    cdef int size
    cdef unsigned char *buf
    cdef cairo_t* cr
    cdef cairo_surface_t* surface

    def __init__(self):
        pass

    def __dealloc__(self):
        # destroy the surface and context we have
        cairo_destroy(self.cr)
        cairo_surface_destroy(self.surface)

    cdef int set_cairo_data(
        self,
        cairo_t* cr,
        cairo_surface_t* surface
    ):
        cdef int height
        cdef int stride
        self.cr = cr
        self.surface = surface
        self.buf = cairo_image_surface_get_data (surface)
        height = cairo_image_surface_get_height (surface)
        stride = cairo_image_surface_get_stride (surface)
        self.size = height * stride

    cdef size_t _buffer_size(self):
        return self.size

    cdef void * _buffer_ptr(self):
        return self.buf

    cdef bint _buffer_writable(self):
        return False
