from pango cimport *
from cairo cimport *

cpdef int initialize_glib():
    g_set_prgname('ManimPango')
    return 1

cpdef str pango_version():
    return pango_version_string().decode('utf-8')

cpdef str cairo_version():
    return cairo_version_string().decode('utf-8')
