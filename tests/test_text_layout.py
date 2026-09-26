# -*- coding: utf-8 -*-
from pathlib import Path
from xml.etree import ElementTree

import pytest

from ._manim import MarkupText, Text


@pytest.mark.parametrize(
    "renderer",
    [Text, MarkupText],
    ids=["text", "markup"],
)
def test_small_text_preserves_fractional_glyph_positions(tmpdir, renderer):
    loc = Path(tmpdir, "small-text.svg")
    renderer("fractional positions", size=0.46, filename=str(loc))

    svg = ElementTree.parse(loc)
    x_positions = [
        float(element.attrib["x"])
        for element in svg.iter()
        if element.tag.endswith("use") and "x" in element.attrib
    ]
    assert any(position % 1 for position in x_positions)
