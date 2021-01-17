from glib cimport *
from cairo cimport *
cdef extern from "pango/pangocairo.h":
    int PANGO_SCALE
    int pango_units_from_double(double d)
    double pango_units_to_double (int i)
    ctypedef struct PangoFontDescription:
        pass
    ctypedef struct PangoLanguage:
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
    ctypedef struct PangoAttrList:
        guint ref_count
    ctypedef struct PangoAttribute:
        guint start_index
        guint end_index
    ctypedef enum PangoStyle:
        PANGO_STYLE_NORMAL
        PANGO_STYLE_OBLIQUE
        PANGO_STYLE_ITALIC
    ctypedef enum PangoVariant:
        PANGO_VARIANT_NORMAL
        PANGO_VARIANT_SMALL_CAPS
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
    PangoAttrList* pango_attr_list_new()
    PangoAttrList* pango_attr_list_ref(
        PangoAttrList *list
    )
    void pango_attr_list_unref(PangoAttrList *list)
    void pango_attr_list_insert(
        PangoAttrList *list,
        PangoAttribute *attr
    )
    int PANGO_ATTR_INDEX_FROM_TEXT_BEGINNING
    int PANGO_ATTR_INDEX_TO_TEXT_END
    gboolean pango_attribute_equal(
        const PangoAttribute *attr1,
        const PangoAttribute *attr2
    )
    PangoAttribute* pango_attr_language_new(
        PangoLanguage *language
    )
    PangoLanguage* pango_language_from_string(
        const char *language
    )
    PangoAttribute* pango_attr_family_new(const char *family)
    PangoAttribute* pango_attr_style_new(PangoStyle style)
    PangoAttribute* pango_attr_variant_new (PangoVariant variant)
    void pango_attribute_destroy(PangoAttribute *attr)
    PangoAttribute* pango_attribute_copy(const PangoAttribute *attr)