# -*- coding: utf-8 -*-
import os
from pathlib import Path

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
