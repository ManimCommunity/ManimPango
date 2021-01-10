# -*- coding: utf-8 -*-
def test_good_markup():
    import manimpango  # noqa: F401

    assert manimpango.MarkupUtils.validate("foo")
    assert manimpango.MarkupUtils.validate("<b>bar</b>")


def test_bad_markup():
    import manimpango  # noqa: F401

    assert not manimpango.MarkupUtils.validate("<b>foo")
    assert not manimpango.MarkupUtils.validate("<xyz>foo</xyz>")
