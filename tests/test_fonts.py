# -*- coding: utf-8 -*-
import sys
from pathlib import Path

import manim
import pytest

import manimpango

if sys.platform.startswith("darwin"):
    pytest.skip(allow_module_level=True)

FONT_DIR = Path(__file__).parent / "fonts"
font_lists = {
    (FONT_DIR / "AdobeVFPrototype.ttf").absolute(): "Adobe Variable Font Prototype",
    (
        FONT_DIR / "BungeeColor-Regular_colr_Windows.ttf"
    ).absolute(): "Bungee Color Regular",
    (FONT_DIR / "NotoNastaliqUrdu-Regular.ttf").absolute(): "Noto Nastaliq Urdu",
}


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
def test_fail_just_unregister():
    for font_name in font_lists:
        assert not manimpango.unregister_font(
            str(font_name)
        ), "Failed to unregister the font"


@pytest.mark.skipif(
    sys.platform.startswith("win32"), reason="unsupported api for linux"
)
def test_unregister_linux():
    manimpango.unregister_font("random")
