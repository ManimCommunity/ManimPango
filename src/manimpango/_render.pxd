"""Cython declarations for Pango and Cairo rendering."""

# ============================================================
# Basic types
# ============================================================

cdef extern from "glib.h":
    ctypedef int gboolean
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef unsigned int guint32
    ctypedef void* gpointer

    ctypedef struct GSList:
        gpointer data
        GSList* next

    ctypedef struct GError:
        guint32 domain
        gint code
        char* message

    void g_free(gpointer mem)
    void g_error_free(GError* error)
    void g_object_unref(gpointer object)


# ============================================================
# Cairo declarations
# ============================================================

cdef extern from "cairo.h":
    ctypedef struct cairo_surface_t:
        pass
    ctypedef struct cairo_t:
        pass

    ctypedef enum cairo_status_t:
        CAIRO_STATUS_SUCCESS
        CAIRO_STATUS_NO_MEMORY

    ctypedef enum cairo_format_t:
        CAIRO_FORMAT_ARGB32

    ctypedef cairo_status_t (*cairo_write_func_t)(
        void* closure,
        const unsigned char* data,
        unsigned int length,
    )

    cairo_t* cairo_create(cairo_surface_t* target)
    void cairo_move_to(cairo_t* cr, double x, double y)
    void cairo_destroy(cairo_t* cr)
    void cairo_surface_destroy(cairo_surface_t* surface)
    void cairo_surface_finish(cairo_surface_t* surface)
    cairo_surface_t* cairo_image_surface_create(cairo_format_t format, int width, int height)
    cairo_status_t cairo_status(cairo_t* cr)
    cairo_status_t cairo_surface_status(cairo_surface_t* surface)
    const char* cairo_status_to_string(cairo_status_t status)
    const char* cairo_version_string()


cdef extern from "cairo-svg.h":
    cairo_surface_t* cairo_svg_surface_create(
        const char* filename,
        double width_in_points,
        double height_in_points,
    )
    cairo_surface_t* cairo_svg_surface_create_for_stream(
        cairo_write_func_t write_func,
        void* closure,
        double width_in_points,
        double height_in_points,
    )


# ============================================================
# Pango declarations
# ============================================================

cdef extern from "pango/pango.h":
    int PANGO_SCALE

    # Opaque structs
    ctypedef struct PangoLayout:
        pass
    ctypedef struct PangoContext:
        pass
    ctypedef struct PangoFontMap:
        pass
    ctypedef struct PangoFontDescription:
        pass
    ctypedef struct PangoFontFamily:
        pass

    ctypedef struct PangoRectangle:
        int x
        int y
        int width
        int height

    # Enums
    ctypedef enum PangoStyle:
        PANGO_STYLE_NORMAL
        PANGO_STYLE_ITALIC
        PANGO_STYLE_OBLIQUE

    ctypedef enum PangoWeight:
        PANGO_WEIGHT_THIN = 100
        PANGO_WEIGHT_ULTRALIGHT = 200
        PANGO_WEIGHT_LIGHT = 300
        PANGO_WEIGHT_SEMILIGHT = 350
        PANGO_WEIGHT_BOOK = 380
        PANGO_WEIGHT_NORMAL = 400
        PANGO_WEIGHT_MEDIUM = 500
        PANGO_WEIGHT_SEMIBOLD = 600
        PANGO_WEIGHT_BOLD = 700
        PANGO_WEIGHT_ULTRABOLD = 800
        PANGO_WEIGHT_HEAVY = 900
        PANGO_WEIGHT_ULTRAHEAVY = 1000

    ctypedef enum PangoAlignment:
        PANGO_ALIGN_LEFT
        PANGO_ALIGN_CENTER
        PANGO_ALIGN_RIGHT

    # Unit conversion
    int pango_units_from_double(double d)
    double pango_units_to_double(int i)

    # Font description
    PangoFontDescription* pango_font_description_new()
    void pango_font_description_free(PangoFontDescription* desc)
    void pango_font_description_set_family(PangoFontDescription* desc, const char* family)
    void pango_font_description_set_size(PangoFontDescription* desc, gint size)
    void pango_font_description_set_style(PangoFontDescription* desc, PangoStyle style)
    void pango_font_description_set_weight(PangoFontDescription* desc, PangoWeight weight)
    void pango_font_description_set_variations(PangoFontDescription* desc, const char* variations)

    # Layout
    void pango_layout_set_width(PangoLayout* layout, int width)
    void pango_layout_set_height(PangoLayout* layout, int height)
    void pango_layout_set_markup(PangoLayout* layout, const char* markup, int length)
    void pango_layout_set_text(PangoLayout* layout, const char* text, int length)
    void pango_layout_set_font_description(PangoLayout* layout, const PangoFontDescription* desc)
    void pango_layout_set_alignment(PangoLayout* layout, PangoAlignment alignment)
    void pango_layout_set_justify(PangoLayout* layout, gboolean justify)
    void pango_layout_set_indent(PangoLayout* layout, int indent)
    void pango_layout_set_line_spacing(PangoLayout* layout, float factor)

    # Layout queries
    void pango_layout_get_size(PangoLayout* layout, int* width, int* height)
    void pango_layout_get_pixel_size(PangoLayout* layout, int* width, int* height)
    int pango_layout_get_baseline(PangoLayout* layout)
    int pango_layout_get_line_count(PangoLayout* layout)

    # Font map
    void pango_font_map_list_families(PangoFontMap* fontmap, PangoFontFamily*** families, int* n_families)

    # Markup parsing
    gboolean pango_parse_markup(
        const char* markup_text,
        int length,
        guint32 accel_marker,
        void* attr_list,
        char** text,
        guint32* accel_char,
        GError** error,
    )

    # Version
    const char* pango_version_string()


# PangoLayoutLine needs full struct definition to access members
cdef extern from "pango/pango-layout.h":
    ctypedef struct PangoLayoutLine:
        PangoLayout* layout
        gint start_index
        gint length
        GSList* runs
        guint is_paragraph_start
        guint resolved_dir

    PangoLayoutLine* pango_layout_get_line(PangoLayout* layout, int line)
    void pango_layout_line_get_pixel_extents(
        PangoLayoutLine* line,
        PangoRectangle* ink_rect,
        PangoRectangle* logical_rect,
    )


cdef extern from "pango/pangocairo.h":
    PangoLayout* pango_cairo_create_layout(cairo_t* cr)
    void pango_cairo_show_layout(cairo_t* cr, PangoLayout* layout)
    void pango_cairo_update_layout(cairo_t* cr, PangoLayout* layout)
    PangoFontMap* pango_cairo_font_map_new()
