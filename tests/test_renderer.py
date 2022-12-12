# -*- coding: utf-8 -*-
import os
from pathlib import Path

import pytest

import manimpango


def test_svg_renderer(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    pth = Path("test.svg")
    _l = manimpango.Layout("h")
    _s = manimpango.SVGRenderer(os.fspath(pth), 200, 200, _l)
    _s.render()
    assert pth.exists()
    assert _s.file_name == "test.svg"
    assert _s.width == 200
    assert _s.height == 200


def test_png_renderer(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    pth = Path("test.png")
    _l = manimpango.Layout("h")
    _s = manimpango.PNGRenderer(os.fspath(pth), 200, 200, _l)
    _s.render()
    assert pth.exists()
    assert _s.file_name == "test.png"
    assert _s.width == 200
    assert _s.height == 200


@pytest.mark.parametrize(
    "attributes",
    [
        [
            manimpango.TextAttribute(0, 5, family="Cursive"),
        ],
        [
            manimpango.TextAttribute(0, 5, background_color="#123456"),
            manimpango.TextAttribute(4, 7, family="Algerian"),
        ],
        [
            manimpango.TextAttribute(4, 7, family="Serif"),
        ],
        [manimpango.TextAttribute(0, 5, fallback=False)],
    ],
)
def test_rendering_with_attributes(tmpdir, monkeypatch, attributes):
    monkeypatch.chdir(tmpdir)
    pth = Path("test.png")
    attribute = manimpango.TextAttribute(0, 5)
    _l = manimpango.Layout("hello world", attributes=attributes)
    _s = manimpango.PNGRenderer(os.fspath(pth), 200, 200, _l)
    # make sure rendering works
    _s.render()
    assert pth.exists()
    assert _s.file_name == "test.png"
    assert _s.width == 200
    assert _s.height == 200
