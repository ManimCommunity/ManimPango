cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    void g_object_unref(gpointer object)
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
cdef extern from "pango/pangocairo.h":
    int PANGO_SCALE
    int pango_units_from_double(double d)
    double pango_units_to_double (int i)
    ctypedef struct PangoFontDescription:
        pass
    ctypedef enum PangoWrapMode:
        PANGO_WRAP_WORD
        PANGO_WRAP_CHAR
        PANGO_WRAP_WORD_CHAR
    ctypedef struct PangoItem:
        gint offset
        gint length
        gint num_chars
    ctypedef struct PangoColor:
        guint16 red
        guint16 green
        guint16 blue
    ctypedef enum PangoUnderline:
        PANGO_UNDERLINE_NONE
        PANGO_UNDERLINE_SINGLE
        PANGO_UNDERLINE_DOUBLE
        PANGO_UNDERLINE_LOW
        PANGO_UNDERLINE_ERROR
    ctypedef enum PangoGravity:
        PANGO_GRAVITY_SOUTH
        PANGO_GRAVITY_EAST
        PANGO_GRAVITY_NORTH
        PANGO_GRAVITY_WEST
        PANGO_GRAVITY_AUTO
    ctypedef enum PangoGravityHint:
        PANGO_GRAVITY_HINT_NATURAL
        PANGO_GRAVITY_HINT_STRONG
        PANGO_GRAVITY_HINT_LINE
    ctypedef enum PangoShowFlags:
        PANGO_SHOW_NONE
        PANGO_SHOW_SPACES
        PANGO_SHOW_LINE_BREAKS
        PANGO_SHOW_IGNORABLES
    PangoItem* pango_item_new()
    PangoFontDescription* pango_font_description_from_string(
        const char *str
    ) # see https://developer.gnome.org/pango/stable/pango-Fonts.html#pango-font-description-from-string
    void pango_color_free(PangoColor *color)
    bint pango_color_parse(
        PangoColor *color,
        const char *spec
    )
    gchar* pango_color_to_string(
        const PangoColor *color
    )
