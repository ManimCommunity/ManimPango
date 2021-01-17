cimport pango
from .enums import *
from .rectangle import Rectangle
from . import FontDescription, Underline, ffi, pango

cdef TextAttribute from_attribute_pointer(pango.PangoAttribute* pointer):
    """
    Instantiates a :class:`TextAttribute` from a pointer.
    :return:
        the Attribute.
    """
    self = <TextAttribute>TextAttribute.__new__()
    self._attribute = pointer
    return self

cdef class TextAttribute:
    """
    The :class:`Attributes` — Font and other attributes for annotating text.
    Attributed text is used in a number of places in Pango.
    It is used as the input to the itemization process and also
    when creating a PangoLayout. The data types and functions in
    this section are used to represent and manipulate sets of
    attributes applied to a portion of text.

    Raises
    ------

    ValueError:
        If :class:`Attribute` is initialised directly.
    """
    cdef pango.PangoAttribute* _attribute

    def __init__(self):
        raise ValueError("Attribute must be initialised from classmethods only.")

#    @classmethod
#    cdef _init_attribute(cls,PangoAttribute* pointer):
#        self = object.__new__(cls)
#        self._attribute = pointer
#        return self

    
    cdef pango.PangoAttribute* get_attribute(self):
        """
        Returns the pointer to the context
        :return:
            the pointer to the context.
        """
        return self._attribute


    def __eq__(self, other: TextAttribute) -> bool:
        if isinstance(other, TextAttribute):
            return bool(
                pango.pango_attribute_equal(
                    self.get_attribute(),
                    other.get_attribute(),
                )
            )
        raise NotImplementedError

    @property
    def start_index(self):
        return self._start_index

    @start_index.setter
    def start_index(self, start_index: int):
        """
        Set's the Start Index of a Attribute.
        :param start_index:
            the start index of the range. Should be >=0.
        :raises: AssertionError
            When ``start_index`` isn't a :class:`int`.
        """
        assert start_index >= pango.PANGO_ATTR_INDEX_FROM_TEXT_BEGINNING, \
            "start_index is too low"
        assert start_index < pango.PANGO_ATTR_INDEX_TO_TEXT_END, \
            "start_index is too high"
        self._attribute.start_index = start_index
        self._start_index = start_index

    @property
    def end_index(self):
        return self._end_index

    @end_index.setter
    def end_index(self, end_index: int):
        """
        Set's the End Index of a Attribute.
        :param end_index:
            end index of the range. The character at this index
            is not included in the range.
        :raises: AssertionError
            When ``end_index`` isn't a :class:`int`.
        """
        assert end_index <= pango.PANGO_ATTR_INDEX_TO_TEXT_END, \
            "end_index is too high"
        self._attribute.end_index = end_index
        self._end_index = end_index
    @classmethod
    def from_language(
        cls, language:str, start_index: int, end_index: int
    ):
        """
        Create a new language tag attribute.

        Parameters
        ----------
        language : :class:`str`
            language tag
        start_index : :class:`int`
            the start index of the range
        end_index : :class:`int`
            end index of the range. 
            The character at this index is not included in the range.
        
        Raises
        ------
        TypeError
            If any parameter doesn't have correct type.
        """
        language_bytes = language.encode('utf-8')
        temp = from_attribute_pointer(
            pango.pango_attr_language_new(
                pango.pango_language_from_string(
                    language_bytes
                )
            )
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_family(
        cls, family: str, start_index: int, end_index: int
    ):
        """
        Create a new font family attribute.

        Parameters
        ----------
        family : :class:`str`
            the font family
        start_index : :class:`int`
            the start index of the range
        end_index : :class:`int`
            end index of the range. 
            The character at this index is not included in the range.

        Returns
        -------
        TextAttribute
            the Attribute.
        """
        family_bytes = family.encode("utf-8")
        temp = from_attribute_pointer(
            pango.pango_attr_family_new(family)
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_style(
        cls, style: Style, start_index: int, end_index: int
    ):
        """
        Create a new font slant style attribute.

        Parameters
        ----------
        style : :class:`Style`
            the slant style
        start_index : :class:`int`
            the start index of the range
        end_index : :class:`int`
            end index of the range. 
            The character at this index is not included in the range.

        Returns
        -------
            the Attribute.
        
        Raises
        ------
        AssertionError
            When ``style`` isn't a :class:`Style`.
        """
        assert isinstance(style, Style), "style isn't a Style"
        temp = from_attribute_pointer(
            pango.pango_attr_style_new(style.value)
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_variant(
        cls, variant: Variant, start_index: int, end_index: int
    ):
        """
        Create a new font variant attribute (normal or small caps)

        Parameters
        ----------
        variant : :Class:`Variant`
            the variant
        start_index : :class:`int`
            the start index of the range
        end_index : :class:`int`
            end index of the range. 
            The character at this index is not included in the range.
        
        Returns
        -------
            the Attribute.
        
        Raises
        ------
        AssertionError
            When ``variant`` isn't a :class:`Variant`.
        """
        assert isinstance(variant, Variant), "variant isn't a Variant"
        temp = from_attribute_pointer(
            pango.pango_attr_variant_new(variant.value)
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    def copy(self) -> "Attribute":
        """
        Make a copy of an attribute.
        :return:
            the Attribute.
        """
        return from_attribute_pointer(
            pango.pango_attribute_copy(self._attribute),
        )

    def __copy__(self) -> "Attribute":
        return self.copy()

    def __deepcopy__(self, memo) -> "Attribute":
        return self.copy()
    
    def __dealloc__(self):
        if self._attribute is not NULL:
            pango.pango_attribute_destroy(self._attribute)
    # TODO: FROM HERE
    @classmethod
    def from_stretch(
        cls, stretch: Stretch, start_index: int = 0, end_index: int = 1
    ) -> "Attribute":
        """
        Create a new font stretch attribute
        :param stretch:
            the stretch
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``stretch`` isn't a :class:`Stretch`.
        """
        assert isinstance(stretch, Stretch), "stretch isn't a Stretch"
        temp = cls._init_attribute(pango.pango_attr_stretch_new(stretch.value))
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_weight(
        cls, weight: Weight, start_index: int = 0, end_index: int = 1
    ) -> "Attribute":
        """
        Create a new font weight attribute.
        :param weight:
            the weight
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``weight`` isn't a :class:`Weight`.
        """
        assert isinstance(weight, Weight), "weight isn't a Weight"
        temp = cls._init_attribute(pango.pango_attr_weight_new(weight.value))
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_size(
        cls, size: int, start_index: int = 0, end_index: int = 1
    ) -> "Attribute":
        """
        Create a new font-size attribute in fractional points.
        :param size:
            the font size, in PANGO_SCALEths of a point.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``size`` isn't a :class:`int`.
        """
        assert isinstance(size, int), "size isn't int"
        size = ffi.cast("int", size)
        temp = cls._init_attribute(pango.pango_attr_size_new(size))
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_size_absolute(
        cls, size: int, start_index: int = 0, end_index: int = 1
    ):
        """
        Create a new font-size attribute in device units.
        :param size:
            the font size, in PANGO_SCALEths of a device unit.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this index
            is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``absolute_size`` isn't a :class:`int`.
        """
        assert isinstance(size, int), "size isn't int"
        size = ffi.cast("int", size)
        temp = cls._init_attribute(
            pango.pango_attr_size_new_absolute(
                size,
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_font_desc(
        cls,
        font_desc: FontDescription,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new font description attribute. This attribute
        allows setting family, style, weight, variant,
        stretch, and size simultaneously.
        :param font_desc:
            the font description
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this index
            is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``font_desc`` isn't a :class:`FontDescription`.
        """
        assert isinstance(
            font_desc, FontDescription
        ), "font_desc isn't a FontDescription"
        temp = cls._init_attribute(
            pango.pango_attr_font_desc_new(
                font_desc._attribute,
            )
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_foreground_color(
        cls,
        red: int,
        green: int,
        blue: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new foreground color attribute.
        :param red:
            the red value (ranging from 0 to 65535)
        :param green:
            the green value (ranging from 0 to 65535)
        :param blue:
            the blue value (ranging from 0 to 65535)
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``red`` or ``blue`` or ``green`` isn't a :class:`int`.
        """
        assert isinstance(red, int), "red isn't a int"
        assert isinstance(green, int), "green isn't a int"
        assert isinstance(blue, int), "blue isn't a int"
        red = ffi.cast("guint16", red)
        green = ffi.cast("guint16", green)
        blue = ffi.cast("guint16", blue)
        temp = cls._init_attribute(
            pango.pango_attr_foreground_new(
                red,
                green,
                blue,
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_background_color(
        cls,
        red: int,
        green: int,
        blue: int,
        start_index: int = 0,
        end_index: int = 1,
    ):
        """
        Create a new background color attribute.
        :param red:
            the red value (ranging from 0 to 65535)
        :param green:
            the green value (ranging from 0 to 65535)
        :param blue:
            the blue value (ranging from 0 to 65535)
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``red`` or ``blue`` or ``green`` isn't a :class:`int`.
        """
        assert isinstance(red, int), "red isn't a int"
        assert isinstance(green, int), "green isn't a int"
        assert isinstance(blue, int), "blue isn't a int"
        red = ffi.cast("guint16", red)
        green = ffi.cast("guint16", green)
        blue = ffi.cast("guint16", blue)
        temp = cls._init_attribute(
            pango.pango_attr_background_new(
                red,
                green,
                blue,
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_strikethrough(
        cls, strikethrough: bool, start_index: int = 0, end_index: int = 1
    ) -> "Attribute":
        """
        Create a new strike-through attribute.
        :param strikethrough:
            True if the text should be struck-through.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this index
            is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``strikethrough`` isn't a :class:`bool`.
        """
        assert isinstance(strikethrough, int), "strikethrough isn't a bool"
        strikethrough = ffi.cast("gboolean", strikethrough)
        temp = cls._init_attribute(
            pango.pango_attr_strikethrough_new(
                strikethrough,
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_strikethrough_color(
        cls,
        red: int,
        green: int,
        blue: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new strikethrough color attribute. This attribute
        modifies the color of strikethrough lines.
        If not set, strikethrough lines will use the foreground color.
        :param red:
            the red value (ranging from 0 to 65535)
        :param green:
            the green value (ranging from 0 to 65535)
        :param blue:
            the blue value (ranging from 0 to 65535)
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``red`` or ``blue`` or ``green`` isn't a :class:`int`.
        """
        assert isinstance(red, int), "red isn't a int"
        assert isinstance(green, int), "green isn't a int"
        assert isinstance(blue, int), "blue isn't a int"
        red = ffi.cast("guint16", red)
        green = ffi.cast("guint16", green)
        blue = ffi.cast("guint16", blue)
        temp = cls._init_attribute(
            pango.pango_attr_strikethrough_color_new(
                red,
                green,
                blue,
            )
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_underline(
        cls,
        underline: Underline,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new underline-style attribute.
        :param underline:
            the underline style.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``underline`` isn't a :class:`Underline`.
        """
        assert isinstance(underline, Underline), "underline isn't a Underline"
        temp = cls._init_attribute(
            pango.pango_attr_underline_new(
                underline.value,
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_underline_color(
        cls,
        red: int,
        green: int,
        blue: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new underline color attribute.
        This attribute modifies the color of underlines.
        If not set, underlines will use the foreground color.
        :param red:
            the red value (ranging from 0 to 65535)
        :param green:
            the green value (ranging from 0 to 65535)
        :param blue:
            the blue value (ranging from 0 to 65535)
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``red`` or ``blue`` or ``green`` isn't a :class:`int`.
        """
        assert isinstance(red, int), "red isn't a int"
        assert isinstance(green, int), "green isn't a int"
        assert isinstance(blue, int), "blue isn't a int"
        red = ffi.cast("guint16", red)
        green = ffi.cast("guint16", green)
        blue = ffi.cast("guint16", blue)
        temp = cls._init_attribute(
            pango.pango_attr_underline_color_new(
                red,
                green,
                blue,
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_shape(
        cls,
        ink_rect: Rectangle,
        logical_rectangle: Rectangle,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new shape attribute. A shape is used to impose
        a particular ink and logical rectangle on the result of
        shaping a particular glyph. This might be used, for
        instance, for embedding a picture or a widget inside a
        PangoLayout.
        :param ink_rect:
            ink rectangle to assign to each character
        :param logical_rectangle:
            logical rectangle to assign to each character
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``ink_rect`` or ``logical_rectangle`` isn't a
            :class:`Rectangle`.
        """
        assert isinstance(ink_rect, Rectangle), "ink_rect isn't a Rectangle"
        assert isinstance(
            logical_rectangle, Rectangle
        ), "logical_rectangle isn't a Rectangle"
        temp = cls._init_attribute(
            pango.pango_attr_shape_new(
                ink_rect.get_attribute(), logical_rectangle.get_attribute()
            ),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    # TODO: pango_attr_shape_new_with_data with data?
    @classmethod
    def from_scale(
        cls,
        scale_factor: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new font size scale attribute.
        The base font for the affected text will
        have its size multiplied by ``scale_factor``.
        :param scale_factor:
            factor to scale the font
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``scale_factor`` isn't a :class:`int`.
        """
        assert isinstance(scale_factor, int), "scale_factor isn't a int"
        scale_factor = ffi.cast("double", scale_factor)
        temp = cls._init_attribute(
            pango.pango_attr_scale_new(scale_factor),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_rise(
        cls,
        rise: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new baseline displacement attribute.
        :param rise:
            the amount that the text should be displaced vertically,
            in Pango units. Positive values displace the text
            upwards.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``rise`` isn't a :class:`int`.
        """
        assert isinstance(rise, int), "rise isn't a int"
        rise = ffi.cast("int", rise)
        temp = cls._init_attribute(
            pango.pango_attr_rise_new(rise),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_letter_spacing(
        cls,
        letter_spacing: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new letter-spacing attribute.
        :param letter_spacing:
            amount of extra space to add between graphemes
            of the text, in Pango units.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``letter_spacing`` isn't a :class:`int`.
        """
        assert isinstance(letter_spacing, int), "rise isn't a int"
        letter_spacing = ffi.cast("int", letter_spacing)
        temp = cls._init_attribute(
            pango.pango_attr_letter_spacing_new(letter_spacing),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_fallback(
        cls,
        enable_fallback: bool,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new font fallback attribute.
        If fallback is disabled, characters will only be used
        from the closest matching font on the system.
        No fallback will be done to other fonts on the system
        that might contain the characters in the text.
        :param enable_fallback:
            True if we should fall back on other fonts for
            characters the active font is missing.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``enable_fallback`` isn't a :class:`bool`.
        """
        assert isinstance(enable_fallback, bool),\
            "enable_fallback isn't a bool"
        enable_fallback = ffi.cast("gboolean", enable_fallback)
        temp = cls._init_attribute(
            pango.pango_attr_fallback_new(enable_fallback),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_gravity(
        cls,
        gravity: Gravity,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new gravity attribute.
        :param gravity:
            the gravity value; should not be :class:`PANGO_GRAVITY_AUTO`.
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``gravity`` isn't a :class:`Gravity`.
        """
        assert isinstance(gravity, Gravity), "gravity isn't a Gravity"
        temp = cls._init_attribute(
            pango.pango_attr_gravity_new(gravity.value),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_gravity_hints(
        cls,
        hint: GravityHint,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new gravity hint attribute.
        :param hint:
            the gravity hint value from :class:`GravityHint`
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``hint`` isn't a :class:`GravityHint`.
        """
        assert isinstance(hint, GravityHint), "hint isn't a GravityHint"
        temp = cls._init_attribute(
            pango.pango_attr_gravity_hint_new(hint.value),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_font_features(
        cls,
        features: str,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new font features tag attribute.
        :param features:
            a string with OpenType font features, in CSS syntax
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``features`` isn't a :class:`str`.
        """
        assert isinstance(features, str), "features isn't a str"
        features = ffi.new("char[]", features.encode("utf8"))
        temp = cls._init_attribute(
            pango.pango_attr_font_features_new(features),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_foreground_alpha(
        cls,
        alpha: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new foreground alpha attribute.
        :param alpha:
            the alpha value, between 1 and 65536
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``alpha`` isn't a :class:`int`.
        """
        assert isinstance(alpha, int), "alpha isn't a int"
        alpha = ffi.cast("guint16", alpha)
        temp = cls._init_attribute(
            pango.pango_attr_foreground_alpha_new(alpha),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp

    @classmethod
    def from_background_alpha(
        cls,
        alpha: int,
        start_index: int = 0,
        end_index: int = 1,
    ) -> "Attribute":
        """
        Create a new background alpha attribute.
        :param alpha:
            the alpha value, between 1 and 65536
        :param start_index:
            the start index of the range. Should be >=0.
        :param end_index:
            end index of the range. The character at this
            index is not included in the range.
        :return:
            the Attribute.
        :raises: AssertionError
            When ``alpha`` isn't a :class:`int`.
        """
        assert isinstance(alpha, int), "alpha isn't a int"
        alpha = ffi.cast("guint16", alpha)
        temp = cls._init_attribute(
            pango.pango_attr_background_alpha_new(alpha),
        )
        temp.start_index = start_index
        temp.end_index = end_index
        return temp