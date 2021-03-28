# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from shutil import copyfile

import manim
import pytest

import manimpango

from . import FONT_DIR, main_font
from ._manim import MarkupText

font_lists = {
    (FONT_DIR / "AdobeVFPrototype.ttf").absolute(): "Adobe Variable Font Prototype",
    (
        FONT_DIR / "BungeeColor-Regular_colr_Windows.ttf"
    ).absolute(): "Bungee Color Regular",
    (FONT_DIR / "NotoNastaliqUrdu-Regular.ttf").absolute(): "Noto Nastaliq Urdu",
}


def test_unicode_font_name(tmpdir):
    final_font = str(Path(tmpdir, "庞门正.ttf").absolute())
    copyfile(FONT_DIR / "AdobeVFPrototype.ttf", final_font)
    assert manimpango.register_font(final_font)
    assert manimpango.unregister_font(final_font)


def test_register_font():
    for font_name in font_lists:
        assert manimpango.register_font(str(font_name)), "Invalid Font possibly."


def test_warning(capfd):
    for font_name in font_lists.values():
        manim.Text("Testing", font=font_name)
        captured = capfd.readouterr()
        assert (
            "Pango-WARNING **" not in captured.err
        ), "Looks like pango raised a warning?"


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
def test_unregister_font():
    for font_name in font_lists:
        assert manimpango.unregister_font(
            str(font_name)
        ), "Failed to unregister the font"


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
def test_register_and_unregister_font():
    for font_name in font_lists:
        assert manimpango.register_font(str(font_name)), "Invalid Font possibly."
        assert manimpango.unregister_font(
            str(font_name)
        ), "Failed to unregister the font"


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="always returns true")
def test_fail_just_unregister():
    for font_name in font_lists:
        assert not manimpango.unregister_font(
            str(font_name)
        ), "Failed to unregister the font"


@pytest.mark.skipif(
    sys.platform.startswith("win32"), reason="unsupported api for win32"
)
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="unsupported api for mac")
def test_unregister_linux():
    assert manimpango.unregister_font("random")


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
def test_adding_dummy_font(tmpdir):
    dummy = tmpdir / "font.ttf"
    with open(dummy, "wb") as f:
        f.write(b"dummy")
    assert not manimpango.register_font(str(dummy)), "Registered a dummy font?"


def test_fonts_render(tmpdir):
    filename = str(Path(tmpdir) / "hello.svg")
    MarkupText("Hello World", font=main_font, filename=filename)
    assert Path(filename).exists()
