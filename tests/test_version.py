# -*- coding: utf-8 -*-
def test_pango_version():
    import manimpango

    v = manimpango.pango_version()
    assert type(v) == str


def test_cairo_version():
    import manimpango

    v = manimpango.cairo_version()
    assert type(v) == str
