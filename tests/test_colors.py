# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from . import CASES_DIR
from ._manim import Text
from .svg_tester import SVGStyleTester


def test_invalid_color_fail(tmpdir):
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    with pytest.raises(ValueError):
        Text("color", color="invalid", filename=str(loc))


def test_colors(tmpdir):
    expected = Path(CASES_DIR, "color_red.svg")
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    Text("color", color="red", filename=str(loc))
    assert loc.exists()
    s = SVGStyleTester(gotSVG=loc, expectedSVG=expected)
    assert len(s.got_svg_style) == len(s.expected_svg_style)
    assert s.got_svg_style == s.expected_svg_style
