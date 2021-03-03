# -*- coding: utf-8 -*-
from manim import MarkupText

import manimpango


def test_good_markup():

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

    assert not manimpango.MarkupUtils.validate(
        "<b>foo"
    ), '"<b>foo" should fail validation (unbalanced tags)'
    assert not manimpango.MarkupUtils.validate(
        "<xyz>foo</xyz>"
    ), '"<xyz>foo</xyz>" should fail validation (invalid tag)'


def test_markup_text():
    MarkupText("<span>Hello Manim</span>")
