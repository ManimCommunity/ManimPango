from glib cimport *
from pango cimport *


cdef extern from "pango/pango.h":
    ctypedef struct PangoAttribute:
        guint start_index
        guint end_index
    ctypedef struct PangoLanguage:
        pass
    ctypedef enum PangoGravityHint:
        PANGO_GRAVITY_HINT_NATURAL
        PANGO_GRAVITY_HINT_STRONG
        PANGO_GRAVITY_HINT_LINE
    ctypedef enum PangoGravity:
        PANGO_GRAVITY_SOUTH
        PANGO_GRAVITY_EAST
        PANGO_GRAVITY_NORTH
        PANGO_GRAVITY_WEST
    ctypedef enum PangoOverline:
        PANGO_OVERLINE_NONE
        PANGO_OVERLINE_SINGLE
    ctypedef enum PangoShowFlags:
        PANGO_SHOW_NONE
        PANGO_SHOW_SPACES
        PANGO_SHOW_LINE_BREAKS
        PANGO_SHOW_IGNORABLES
    ctypedef enum PangoStretch:
        PANGO_STRETCH_ULTRA_CONDENSED
        PANGO_STRETCH_EXTRA_CONDENSED
        PANGO_STRETCH_CONDENSED
        PANGO_STRETCH_SEMI_CONDENSED
        PANGO_STRETCH_NORMAL
        PANGO_STRETCH_SEMI_EXPANDED
        PANGO_STRETCH_EXPANDED
        PANGO_STRETCH_EXTRA_EXPANDED
        PANGO_STRETCH_ULTRA_EXPANDED
    ctypedef enum PangoUnderline:
        PANGO_UNDERLINE_NONE
        PANGO_UNDERLINE_SINGLE
        PANGO_UNDERLINE_DOUBLE
        PANGO_UNDERLINE_LOW
        PANGO_UNDERLINE_ERROR
        PANGO_UNDERLINE_SINGLE_LINE
        PANGO_UNDERLINE_DOUBLE_LINE
        PANGO_UNDERLINE_ERROR_LINE
    PangoAttribute* pango_attr_allow_breaks_new (
        gboolean allow_breaks
    )
    PangoAttribute* pango_attr_background_alpha_new (
        guint16 alpha
    )
    PangoAttribute* pango_attr_background_new (
        guint16 red,
        guint16 green,
        guint16 blue
    )
    PangoAttribute* pango_attr_fallback_new (
        gboolean enable_fallback
    )
    PangoAttribute* pango_attr_family_new (
        const char* family
    )
    PangoAttribute* pango_attr_font_desc_new (
        const PangoFontDescription* desc
    )
    PangoAttribute* pango_attr_font_features_new (
        const char* features
    )
    PangoAttribute* pango_attr_foreground_alpha_new (
        guint16 alpha
    )
    PangoAttribute* pango_attr_foreground_new (
        guint16 red,
        guint16 green,
        guint16 blue
    )
    PangoAttribute* pango_attr_gravity_hint_new (
        PangoGravityHint hint
    )
    PangoAttribute* pango_attr_gravity_new (
        PangoGravity gravity
    )
    PangoAttribute* pango_attr_insert_hyphens_new (
        gboolean insert_hyphens
    )
    PangoAttribute* pango_attr_language_new (
        PangoLanguage* language
    )
    PangoAttribute* pango_attr_letter_spacing_new (
        int letter_spacing
    )
    PangoAttribute* pango_attr_overline_color_new (
        guint16 red,
        guint16 green,
        guint16 blue
    )
    PangoAttribute* pango_attr_overline_new (
        PangoOverline overline
    )
    PangoAttribute* pango_attr_rise_new (
        int rise
    )
    PangoAttribute* pango_attr_scale_new (
        double scale_factor
    )
    # PangoAttribute* pango_attr_shape_new (
    #     const PangoRectangle* ink_rect,
    #     const PangoRectangle* logical_rect
    # )
    # PangoAttribute* pango_attr_shape_new_with_data (
    #     const PangoRectangle* ink_rect,
    #     const PangoRectangle* logical_rect,
    #     gpointer data,
    #     PangoAttrDataCopyFunc copy_func,
    #     GDestroyNotify destroy_func
    # )
    PangoAttribute* pango_attr_show_new (
        PangoShowFlags flags
    )
    PangoAttribute* pango_attr_size_new (
        int size
    )
    PangoAttribute* pango_attr_size_new_absolute (
        int size
    )
    PangoAttribute* pango_attr_stretch_new (
        PangoStretch stretch
    )
    PangoAttribute* pango_attr_strikethrough_color_new (
        guint16 red,
        guint16 green,
        guint16 blue
    )
    PangoAttribute* pango_attr_strikethrough_new (
        gboolean strikethrough
    )
    PangoAttribute* pango_attr_style_new (
        PangoStyle style
    )
    PangoAttribute* pango_attr_underline_color_new (
        guint16 red,
        guint16 green,
        guint16 blue
    )
    PangoAttribute* pango_attr_underline_new (
        PangoUnderline underline
    )
    PangoAttribute* pango_attr_variant_new (
        PangoVariant variant
    )
    PangoAttribute* pango_attr_weight_new (
        PangoWeight weight
    )
    PangoAttribute* pango_attr_line_height_new (
        double factor
    )
    void pango_attribute_destroy (
        PangoAttribute* attr
    )

# Functions related to PangoAttrList
cdef extern from "pango/pango.h":
    ctypedef struct PangoAttrList:
        pass
    PangoAttrList* pango_attr_list_new ()
    void pango_attr_list_change (
        PangoAttrList* list,
        PangoAttribute* attr,
    )
    PangoAttrList* pango_attr_list_ref (
        PangoAttrList* list
    )
    void pango_attr_list_unref (
        PangoAttrList* list
    )
    void pango_attr_list_insert (
        PangoAttrList* list,
        PangoAttribute* attr
    )
    # for debugging
    char* pango_attr_list_to_string (
        PangoAttrList* list
    )
