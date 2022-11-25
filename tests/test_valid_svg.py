# -*- coding: utf-8 -*-
from pathlib import Path
from xml.parsers.expat import ParserCreate

from ._manim import Text


def test_whether_valid_svg_file(tmpdir):
    loc = Path(tmpdir, "test.svg")
    assert not loc.exists()
    Text("{ }", color="red", filename=str(loc))
    assert loc.exists()
    # verify that it's a valid svg file by parsing it
    with open(loc, "rb") as f:
        p = ParserCreate()
        p.ParseFile(f)
