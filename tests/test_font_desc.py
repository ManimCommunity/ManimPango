# -*- coding: utf-8 -*-
import copy

from manimpango.fonts import FontDescription


def test_init():
    _a = FontDescription()
    assert repr(_a) == "Normal"


def test_copy():
    _a = FontDescription()
    _b = copy.copy(_a)
    assert _a == _b
