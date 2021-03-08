# -*- coding: utf-8 -*-
from pathlib import Path

import manimpango

from ._manim import MarkupText

ipsum_text = (
    "<b>Lorem ipsum dolor</b> sit amet, <i>consectetur</i> adipiscing elit,"
    "sed do eiusmod tempor incididunt ut labore et dolore"
    "magna aliqua. Ut enim <b>ad</b> minim veniam, quis nostrud"
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


def test_markup_text(tmpdir):
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    MarkupText(
        '<span underline="error"><b><i>Hello Manim</i></b></span>', filename=str(loc)
    )
    assert loc.exists()


def test_markup_justify(tmpdir):
    # don't know how to verify this correctly
    # it varies upon diffent system so, we are
    # just check whether it runs
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    MarkupText(ipsum_text, justify=True, filename=str(loc))
    assert loc.exists()


def test_markup_indent(tmpdir):
    # don't know how to verify this correctly
    # it varies upon diffent system so, we are
    # just check whether it runs
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    MarkupText(ipsum_text, indent=10, filename=str(loc))
    assert loc.exists()


def test_markup_alignment(tmpdir):
    # don't know how to verify this correctly
    # it varies upon diffent system so, we are
    # just check whether it runs
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    MarkupText(
        ipsum_text,
        alignment=manimpango.Alignment.CENTER,
        filename=str(loc),
    )
    assert loc.exists()
