cdef extern from "cairo.h":
    ctypedef struct cairo_surface_t:
        pass
    ctypedef struct cairo_t:
        pass
    ctypedef enum cairo_status_t:
        CAIRO_STATUS_SUCCESS
        CAIRO_STATUS_NO_MEMORY
    cairo_t* cairo_create(cairo_surface_t* target)
    void cairo_move_to(
        cairo_t* cr,
        double x,
        double y
    )
    void cairo_destroy(cairo_t* cr)
    void cairo_surface_destroy(cairo_surface_t* surface)

    cairo_status_t cairo_status(cairo_t *cr)
    const char* cairo_status_to_string(cairo_status_t status)
    const char* cairo_version_string()

cdef extern from "cairo-svg.h":
    cairo_surface_t* cairo_svg_surface_create(
        const char* filename,
        double width_in_points,
        double height_in_points
    )
