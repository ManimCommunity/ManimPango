from cairo cimport *
from glib cimport *


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
    ctypedef enum PangoAlignment:
        PANGO_ALIGN_LEFT
        PANGO_ALIGN_CENTER
        PANGO_ALIGN_RIGHT
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
    void pango_layout_set_justify(
        PangoLayout *layout,
        gboolean justify
    )
    void pango_layout_set_indent(
        PangoLayout *layout,
        int indent
    )
    void pango_layout_set_alignment(
        PangoLayout *layout,
        PangoAlignment alignment
    )

cdef extern from *:
    """
    #if PANGO_VERSION_CHECK(1,44,0)
        int set_line_width(PangoLayout *layout,float spacing)
        {
          pango_layout_set_line_spacing(layout, spacing);
          return 1;
        }
    #else
        int set_line_width(PangoLayout *layout,float spacing){return 0;}
    #endif
    """
    # The above docs string is C which is used to
    # check for the Pango Version there at run time.
    # pango_layout_set_line_spacing is only avaiable only for
    # pango>=1.44.0 but we support pango>=1.30.0 that why this
    # conditionals.
    bint set_line_width(PangoLayout *layout,float spacing)
