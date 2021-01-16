cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    void g_object_unref(gpointer object)
    void g_free(gpointer mem)

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
    void cairo_surface_destroy (cairo_surface_t* surface)

    cairo_status_t cairo_status (cairo_t *cr)
    const char* cairo_status_to_string (cairo_status_t status)
    const char* cairo_version_string()

cdef extern from "cairo-svg.h":
    cairo_surface_t* cairo_svg_surface_create(
        const char* filename,
        double	width_in_points,
        double	height_in_points
    )

cdef extern from "pango/pangocairo.h":
    int PANGO_SCALE
    int pango_units_from_double(double d)
    double pango_units_to_double (int i)
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
    ctypedef enum PangoStyle:
        PANGO_STYLE_NORMAL
        PANGO_STYLE_OBLIQUE
        PANGO_STYLE_ITALIC
    ctypedef enum PangoWeight:
        PANGO_WEIGHT_THIN
        PANGO_WEIGHT_ULTRALIGHT
        PANGO_WEIGHT_LIGHT
        PANGO_WEIGHT_BOOK
        PANGO_WEIGHT_NORMAL
        PANGO_WEIGHT_MEDIUM
        PANGO_WEIGHT_SEMIBOLD
        PANGO_WEIGHT_BOLD
        PANGO_WEIGHT_ULTRABOLD
        PANGO_WEIGHT_HEAVY
        PANGO_WEIGHT_ULTRAHEAVY
    ctypedef enum PangoVariant:
        PANGO_VARIANT_NORMAL
        PANGO_VARIANT_SMALL_CAPS
    ctypedef enum PangoWrapMode:
        PANGO_WRAP_WORD
        PANGO_WRAP_CHAR
        PANGO_WRAP_WORD_CHAR
    PangoLayout* pango_cairo_create_layout(cairo_t* cr)
    void pango_cairo_show_layout(
        cairo_t* cr,
        PangoLayout* layout
    )
    void pango_cairo_update_layout(
        cairo_t* cr,
        PangoLayout* layout
    )
    PangoFontDescription* pango_font_description_new()
    void pango_font_description_set_size(
        PangoFontDescription* desc,
        gint size
    )
    void pango_font_description_set_family(
        PangoFontDescription* desc,
        const char* family
    )
    void pango_font_description_set_style(
        PangoFontDescription* desc,
        PangoStyle style
    )
    void pango_font_description_set_weight(
        PangoFontDescription* desc,
        PangoWeight weight
    )
    void pango_font_description_set_variant(
        PangoFontDescription* desc,
        PangoVariant variant
    )

    void pango_layout_set_width(
        PangoLayout* layout,
        int width
    )
    void pango_layout_set_font_description(
        PangoLayout* layout,
        const PangoFontDescription* desc
    )
    void pango_layout_set_text(
        PangoLayout* layout,
        const char* text,
        int length
    )
    void pango_layout_set_wrap(
        PangoLayout *layout,
        PangoWrapMode wrap
    )
    void pango_layout_set_markup(
        PangoLayout *layout,
        const char *markup,
        int length
    )
    void pango_layout_get_size(
        PangoLayout* layout,
        int* width,
        int* height
    )
    const char* pango_version_string()
    void pango_font_description_free(
        PangoFontDescription *desc
    )
    gboolean pango_parse_markup(
       const char *markup_text,
       int length,
       unsigned int accel_marker,
       void* attr_list,
       void* text,
       void* accel_char,
       void* error
    )
    PangoFontMap* pango_cairo_font_map_new()
    void pango_font_map_list_families(
        PangoFontMap *fontmap,
        PangoFontFamily ***families,
        int *n_families
    )
    PangoFontFamily* pango_font_map_get_family(
        PangoFontMap *fontmap,
        const char *name
    )
    const char* pango_font_family_get_name(
        PangoFontFamily *family
    )
IF UNAME_SYSNAME == "Linux":
    cdef extern from "fontconfig/fontconfig.h":
        ctypedef int FcBool
        ctypedef struct FcConfig:
            pass
        FcBool FcConfigAppFontAddFile(
            FcConfig* config,
            const unsigned char* file_name
        )
        FcConfig* FcConfigGetCurrent()
        void FcConfigAppFontClear(void*)
ELIF UNAME_SYSNAME == "Windows":
    cdef extern from "windows.h":
        ctypedef const char* LPCSTR
        ctypedef enum DWORD:
            FR_PRIVATE
        int AddFontResourceExA(
            LPCSTR name,
            DWORD fl,
            unsigned int res
        )
        bint RemoveFontResourceExA(
            LPCSTR name,
            DWORD  fl,
            unsigned int pdv
        )
