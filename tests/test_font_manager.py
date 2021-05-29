# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import pytest
from attr.exceptions import FrozenInstanceError

from manimpango import FontProperties, RegisterFont, Style, Variant, Weight, list_fonts

from .test_fonts import font_lists


def test_invalid_size():
    with pytest.raises(ValueError):
        FontProperties(size=0)


def test_font_properties_attributes():
    fp = FontProperties(
        family="Hello",
        size=10,
        style=Style.ITALIC,
        variant=Variant.NORMAL,
        weight=Weight.BOLD,
    )
    assert fp.family == "Hello"
    assert fp.size == 10
    assert fp.style == Style.ITALIC
    assert fp.variant == Variant.NORMAL
    assert fp.weight == Weight.BOLD


def test_Register_Font_wrapper_frozen():
    a = RegisterFont(list(font_lists.keys())[0])
    with pytest.raises(FrozenInstanceError):
        a.family = ""
    a.unregister()


def test_Register_Font():
    a = RegisterFont(list(font_lists.keys())[1])
    fonts = list_fonts()
    assert a.family[0] in fonts
    assert isinstance(a.family, list)
    a.unregister()
    # below one fails due to caching in Pango.
    # Maybe we can disable it?
    # assert a.family[0] not in fonts


@pytest.mark.skipif(sys.platform.startswith("linux"), reason="uses fc by default.")
def test_fc_in_Register_Font():
    a = RegisterFont(list(font_lists.keys())[1], use_fontconfig=True)
    fonts = list_fonts()
    assert a.family is not None
    assert list(font_lists.values())[1] not in fonts
    assert a.family[0] not in fonts
    a.unregister()


def test_fc_in_Register_Font_with_rendering(setup_fontconfig):
    a = RegisterFont(list(font_lists.keys())[1], use_fontconfig=True)
    fonts = list_fonts()
    assert a.family is not None
    assert a.family[0] in fonts
    a.unregister()


def test_Register_Font_without_calculating_family():
    a = RegisterFont(list(font_lists.keys())[1], calculate_family=False)
    assert a.family is None
    a.unregister()


@pytest.mark.parametrize("fontconfig", [True, False])
def test_Register_Font_invalid_font_raise(tmpdir, fontconfig):
    tmpfile = Path(tmpdir) / "nice.ttf"
    with tmpfile.open("w") as f:
        f.write("test font")
    with pytest.raises(RuntimeError):
        RegisterFont(tmpfile, use_fontconfig=fontconfig)


def test_Register_Font_file_not_found(tmpdir):
    with pytest.raises(FileNotFoundError):
        RegisterFont(Path(tmpdir) / "test")
    with pytest.raises(FileNotFoundError):
        RegisterFont(Path(tmpdir))
