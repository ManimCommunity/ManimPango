# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

import manimpango

from . import CASES_DIR
from ._manim import markup_to_svg_test
from .svg_tester import SVGStyleTester

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


@pytest.mark.parametrize("text", ["foo", "<b>bar</b>", "வணக்கம்"])
def test_good_markup(text):
    assert not manimpango.validate(text), f"{text} should not fail validation"


@pytest.mark.parametrize("text", ["<b>foo", "<xyz>foo</xyz>"])
def test_bad_markup(text):
    assert manimpango.validate(text), f"{text} should fail validation (unbalanced tags)"


@pytest.mark.parametrize(
    "text,error",
    [
        (
            "<b>foo",
            "Error on line 1 char 23: Element “markup” was closed, "
            "but the currently open element is “b”",
        ),
        (
            "<xyz>foo</xyz>",
            "Unknown tag 'xyz' on line 1 char 14",
        ),
    ],
)
def test_bad_markup_error_message(text, error):
    assert manimpango.validate(text) == error


def test_markup_text(tmpdir):
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    markup_to_svg_test("<span underline='error'><b><i>Hello Manim</i></b></span>", str(loc))
    assert loc.exists()


def test_markup_justify(tmpdir):
    # don't know how to verify this correctly
    # it varies upon diffent system so, we are
    # just check whether it runs
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    markup_to_svg_test(ipsum_text, str(loc), justify=True)
    assert loc.exists()


def test_markup_indent(tmpdir):
    # don't know how to verify this correctly
    # it varies upon diffent system so, we are
    # just check whether it runs
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    markup_to_svg_test(ipsum_text, str(loc), indent=10)
    assert loc.exists()


def test_markup_alignment(tmpdir):
    # don't know how to verify this correctly
    # it varies upon diffent system so, we are
    # just check whether it runs
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    markup_to_svg_test(ipsum_text, str(loc), alignment="CENTER")
    assert loc.exists()


def test_markup_style(tmpdir):
    test_case = CASES_DIR / "hello_blue_world_green.svg"
    expected = tmpdir / "expected.svg"
    text = "<span foreground='BLUE'>Hello</span>\n<span foreground='GREEN'>World</span>"
    markup_to_svg_test(text, str(expected))
    s = SVGStyleTester(gotSVG=expected, expectedSVG=test_case)
    assert len(s.got_svg_style) == len(s.expected_svg_style)
    assert s.got_svg_style == s.expected_svg_style
