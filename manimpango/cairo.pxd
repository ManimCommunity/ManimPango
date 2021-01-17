cdef extern from "cairo.h":
    ctypedef struct cairo_surface_t:
        pass
    ctypedef struct cairo_t:
        pass
    ctypedef enum cairo_status_t:
        CAIRO_STATUS_SUCCESS
        CAIRO_STATUS_NO_MEMORY
    ctypedef enum cairo_format_t:
        CAIRO_FORMAT_INVALID   = -1
        CAIRO_FORMAT_ARGB32    = 0
        CAIRO_FORMAT_RGB24     = 1
        CAIRO_FORMAT_A8        = 2
        CAIRO_FORMAT_A1        = 3
        CAIRO_FORMAT_RGB16_565 = 4
    cairo_t* cairo_create(cairo_surface_t* target)
    void cairo_move_to(
        cairo_t* cr,
        double x,
        double y
    )
    void cairo_destroy(cairo_t* cr)
    void cairo_surface_destroy (cairo_surface_t* surface)
    cairo_status_t cairo_status (cairo_t *cr)
    const char* cairo_status_to_string (cairo_status_t status)
    const char* cairo_version_string()
    cairo_surface_t* cairo_image_surface_create(
        cairo_format_t format,
        int width,
        int height
    )