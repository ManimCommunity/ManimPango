# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from . import CASES_DIR
from ._manim import markup_to_svg_test
from .svg_tester import SVGStyleTester


def test_invalid_color_fail(tmpdir):
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    with pytest.raises(ValueError):
        markup_to_svg_test(
            "<span color='invalid'>color</span>",
            str(loc)
        )


def test_colors(tmpdir):
    expected = Path(CASES_DIR, "color_red.svg")
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    markup_to_svg_test(
        "<span color='red'>color</span>",
        str(loc)
    )
    assert loc.exists()
    s = SVGStyleTester(gotSVG=loc, expectedSVG=expected)
    assert len(s.got_svg_style) == len(s.expected_svg_style)
    assert s.got_svg_style == s.expected_svg_style
