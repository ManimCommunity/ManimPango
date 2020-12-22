cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    ctypedef struct GPtrArray:
        pass

cdef extern from "glib-object.h":
    void g_object_unref (gpointer object)

cdef extern from "cairo.h":
    ctypedef struct cairo_surface_t:
        pass
    ctypedef struct cairo_t:
        pass
    cairo_t* cairo_create(cairo_surface_t* target)
    void cairo_move_to(cairo_t* cr, double x, double y)
    void cairo_destroy(cairo_t* cr)
    void cairo_surface_destroy (cairo_surface_t* surface)
    ctypedef enum cairo_status_t:
        CAIRO_STATUS_SUCCESS
        CAIRO_STATUS_NO_MEMORY
    cairo_status_t cairo_status (cairo_t *cr)
    const char* cairo_status_to_string (cairo_status_t status)

cdef extern from "cairo-svg.h":
    cairo_surface_t* cairo_svg_surface_create(const char* filename,double	width_in_points,double	height_in_points)

cdef extern from "pango/pango-font.h":
    ctypedef struct PangoFontDescription:
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
    PangoFontDescription* pango_font_description_new()
    void pango_font_description_set_size(PangoFontDescription* desc,gint size)
    void pango_font_description_set_family(PangoFontDescription* desc,const char* family)
    void pango_font_description_set_style(PangoFontDescription* desc,PangoStyle style)
    void pango_font_description_set_weight (PangoFontDescription* desc,PangoWeight weight)
    void pango_font_description_set_variant (PangoFontDescription* desc,PangoVariant variant)


cdef extern from "pango/pango-layout.h":
    ctypedef struct PangoLayout:
        pass
    void pango_layout_set_width(PangoLayout* layout,int width)
    void pango_layout_set_font_description (PangoLayout* layout, const PangoFontDescription* desc)
    void pango_layout_set_text (PangoLayout* layout,const char* text,int length)

cdef extern from "pango/pangofc-fontmap.h":
    ctypedef struct PangoFontMap:
        pass

cdef extern from "pango/pangocairo.h":
    ctypedef struct PangoContext:
        pass
    ctypedef enum cairo_font_type_t:
        CAIRO_FONT_TYPE_FT
    ctypedef struct PangoAttrList:
        guint ref_count
        GPtrArray* attributes
    ctypedef struct PangoAttribute:
        int start_index
        int end_index
    ctypedef struct PangoColor:
        guint16 red
        guint16 green
        guint16 blue
    PangoLayout * pango_cairo_create_layout(cairo_t* cr)
    void pango_cairo_show_layout(cairo_t* cr,PangoLayout* layout)
    PangoFontMap * pango_cairo_font_map_new_for_font_type(cairo_font_type_t fonttype)
    PangoContext * pango_font_map_create_context (PangoFontMap* fontmap)
    PangoLayout * pango_layout_new (PangoContext *context)
    void pango_attr_list_insert (PangoAttrList *list,PangoAttribute *attr);
    void pango_cairo_update_context (cairo_t *cr,PangoContext *context)
    void pango_cairo_update_layout(cairo_t *cr,PangoLayout *layout)
cdef extern from "pango/pango.h":
    ctypedef enum PangoWrapMode:
        PANGO_WRAP_WORD
        PANGO_WRAP_CHAR
        PANGO_WRAP_WORD_CHAR
    PangoAttrList* pango_attr_list_new ()
    void pango_attr_list_unref (PangoAttrList *list)
    PangoAttribute* pango_attr_family_new (const char *family)
    bint pango_color_parse (PangoColor *color, const char* spec)
    void pango_attribute_destroy (PangoAttribute *attr)
    void pango_layout_set_attributes (PangoLayout *layout,PangoAttrList *attrs);
    PangoAttribute* pango_attr_style_new (PangoStyle style)
    PangoAttribute* pango_attr_weight_new (PangoWeight weight)
    PangoAttribute* pango_attr_variant_new (PangoVariant variant)
    PangoAttribute* pango_attr_foreground_new (guint16 red, guint16 green, guint16 blue)
    void pango_layout_set_wrap (PangoLayout *layout,PangoWrapMode wrap)
    void pango_layout_set_markup (PangoLayout *layout,const char *markup,int length)

cdef extern from "pango/pango-types.h":
    int PANGO_SCALE
    int pango_units_from_double(double d)
