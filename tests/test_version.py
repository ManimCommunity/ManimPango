# -*- coding: utf-8 -*-
def test_pango_version():
    import manimglpango

    v = manimglpango.pango_version()
    assert type(v) == str


def test_cairo_version():
    import manimglpango

    v = manimglpango.cairo_version()
    assert type(v) == str
