cdef class ImageBuffer:
    cdef unsigned char * data
    cdef int height
    cdef int stride

    def __getbuffer__(self, Py_buffer *buffer, int flags):
        buffer.buf = self.data
        buffer.format = 'B'
        buffer.len = self.height * self.stride
        buffer.obj = self
        buffer.readonly = 1

    def __releasebuffer__(self, Py_buffer *buffer):
        pass
