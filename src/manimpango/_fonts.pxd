"""Private Cython declarations for font management; no public Cython ABI is promised."""


cdef extern from "font_backend.h":
    int manimpango_register_font(const char* utf8_path, char** error)
    int manimpango_unregister_font(const char* utf8_path, char** error)


cdef extern from *:
    void g_free(void* mem)
