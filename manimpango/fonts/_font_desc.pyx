from .enums import Style, Variant, Weight


cdef class _FontDescription:
    def __cinit__(self):
        self.pango_font_desc = pango_font_description_new()
        if self.pango_font_desc is NULL:
            raise MemoryError("pango_font_description_new() returned NULL")

    def __init__(
        self,
        family=None,
        size=None,
        style=None,
        weight=None,
        variant=None
    ):
        if family:
            self.family = family
        if size:
            self.size = size
        if style:
            self.style = style
        if weight:
            self.weight = weight
        if variant:
            self.variant = variant

    @property
    def family(self):
        cdef const char* _family = \
            pango_font_description_get_family(self.pango_font_desc)
        if _family is NULL:
            return None
        return _family.decode()

    @family.setter
    def family(self, family: str):
        pango_font_description_set_family(
            self.pango_font_desc, family.encode())

    @property
    def size(self):
        return pango_font_description_get_size(self.pango_font_desc) // PANGO_SCALE

    @size.setter
    def size(self, size: int):
        pango_font_description_set_size(self.pango_font_desc, size * PANGO_SCALE)

    @property
    def style(self):
        return Style(
            pango_font_description_get_style(self.pango_font_desc))

    @style.setter
    def style(self, style: Style):
        pango_font_description_set_style(self.pango_font_desc, style.value)

    @property
    def weight(self):
        return Weight(
            pango_font_description_get_weight(self.pango_font_desc))

    @weight.setter
    def weight(self, weight: Weight):
        pango_font_description_set_weight(
            self.pango_font_desc, weight.value)

    @property
    def variant(self):
        return Variant(
            pango_font_description_get_variant(self.pango_font_desc))

    @variant.setter
    def variant(self, variant):
        pango_font_description_set_variant(
            self.pango_font_desc, variant.value)

    @classmethod
    def from_string(cls, string: str):
        _t = _FontDescription()
        _t.pango_font_desc = \
            pango_font_description_from_string(string.encode())
        return _t

    def __repr__(self):
        cdef char* desc = \
            pango_font_description_to_string(self.pango_font_desc)
        p_desc = <bytes>desc
        g_free(desc)
        return p_desc.decode()

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other: _FontDescription):
        return bool(pango_font_description_equal(
            self.pango_font_desc, other.pango_font_desc))

    def __copy__(self):
        _t = _FontDescription()
        pango_font_description_free(_t.pango_font_desc)
        _t.pango_font_desc = \
            pango_font_description_copy(self.pango_font_desc)
        return _t

    def __deepcopy__(self, memo):
        return self.__copy__()

    def __dealloc__(self):
        pango_font_description_free(self.pango_font_desc)
