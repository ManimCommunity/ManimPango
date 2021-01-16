# -*- coding: utf-8 -*-
import sys

import manimpango

from .test_fonts import font_lists


def test_whether_list():
    a = manimpango.list_fonts()
    assert type(a) is list
    assert len(a) > 0


def test_resgister_font_with_list():
    for i in font_lists:
        manimpango.register_font(str(i))
        a = manimpango.list_fonts()
        assert font_lists[i] in a
        if sys.platform.startswith("win32"):
            manimpango.unregister_font(str(i))
        else:
            manimpango.unregister_font()
