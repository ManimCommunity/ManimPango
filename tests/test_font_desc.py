# -*- coding: utf-8 -*-
import copy

from manimpango.fonts import FontDescription
from manimpango.fonts.enums import Style, Variant, Weight


class TestFontDescription:
    def test_init(self):
        _a = FontDescription()
        assert _a.family is None
        assert repr(_a) == "Normal"
        _a = FontDescription(
            family="hello",
            size=30,
            style=Style.OBLIQUE,
            weight=Weight.BOOK,
            variant=Variant.NORMAL,
        )
        assert _a.family == "hello"
        assert _a.size == 30
        assert _a.style == Style.OBLIQUE
        assert _a.weight == Weight.BOOK
        assert _a.variant == Variant.NORMAL

    def test_copy(self):
        _a = FontDescription(family="nice", size=90)
        _b = copy.copy(_a)
        assert _a == _b
        _c = copy.deepcopy(_a)
        assert _a == _c

    def test_from_string(self):
        _a = FontDescription.from_string("OhNO 12")
        assert _a.family == "OhNO"
        assert _a.size == 12
        _a = FontDescription.from_string("Cantarell Italic Light 15")
        assert _a.family == "Cantarell"
        assert _a.size == 15
        assert _a.style == Style.ITALIC
        assert _a.weight == Weight.LIGHT
        assert _a.variant == Variant.NORMAL

    def test_str_same_as_repr(self):
        _a = FontDescription.from_string("Cantarell Italic Light 15")
        assert repr(_a) == str(_a)
