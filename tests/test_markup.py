# -*- coding: utf-8 -*-
from manim import MarkupText

import manimpango

ipsum_text = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit,"
    "sed do eiusmod tempor incididunt ut labore et dolore"
    "magna aliqua. Ut enim ad minim veniam, quis nostrud"
    "exercitation ullamco laboris nisi ut aliquip"
    "ex ea commodo consequat. Duis aute irure dolor"
    "in reprehenderit in voluptate velit esse cillum"
    "dolore eu fugiat nulla pariatur. Excepteur sint"
    "occaecat cupidatat non proident, sunt in culpa qui"
    "officia deserunt mollit anim id est laborum."
)


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
    MarkupText('<span underline="error"><b><i>Hello Manim</i></b></span>')
