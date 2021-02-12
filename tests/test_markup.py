# -*- coding: utf-8 -*-
def test_good_markup():
    import manimpango  # noqa: F401

    assert manimpango.MarkupUtils.validate(
        "foo",
    ), '"foo" should not fail validation'
    assert manimpango.MarkupUtils.validate(
        "<b>bar</b>"
    ), '"<b>bar</b>" should not fail validation'
    assert manimpango.MarkupUtils.validate(
        "வணக்கம்",
    ), '"வணக்கம்" should not fail'


def test_bad_markup():
    import manimpango  # noqa: F401

    assert not manimpango.MarkupUtils.validate(
        "<b>foo"
    ), '"<b>foo" should fail validation (unbalanced tags)'
    assert not manimpango.MarkupUtils.validate(
        "<xyz>foo</xyz>"
    ), '"<xyz>foo</xyz>" should fail validation (invalid tag)'
