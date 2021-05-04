# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from shutil import copyfile

import manim
import pytest

import manimpango

from . import FONT_DIR
from ._manim import MarkupText

font_lists = {
    (FONT_DIR / "AdobeVFPrototype.ttf").absolute(): "Adobe Variable Font Prototype",
    (
        FONT_DIR / "BungeeColor-Regular_colr_Windows.ttf"
    ).absolute(): "Bungee Color Regular",
    (FONT_DIR / "MaShanZheng-Regular.ttf").absolute(): "Ma Shan Zheng",
}


def test_unicode_font_name(tmpdir):
    final_font = str(Path(tmpdir, "庞门正.ttf").absolute())
    copyfile(FONT_DIR / "AdobeVFPrototype.ttf", final_font)
    assert manimpango.register_font(final_font)
    assert manimpango.unregister_font(final_font)


@pytest.mark.parametrize("font_name", font_lists)
def test_register_font(font_name):
    intial = manimpango.list_fonts()
    assert manimpango.register_font(str(font_name)), "Invalid Font possibly."
    final = manimpango.list_fonts()
    assert intial != final


@pytest.mark.parametrize("font_name", font_lists.values())
def test_warning(capfd, font_name):
    print(font_name)
    manim.Text("Testing", font=font_name)
    captured = capfd.readouterr()
    assert "Pango-WARNING **" not in captured.err, "Looks like pango raised a warning?"


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
@pytest.mark.parametrize("font_name", font_lists)
def test_unregister_font(font_name):
    intial = manimpango.list_fonts()
    assert manimpango.unregister_font(str(font_name)), "Failed to unregister the font"
    final = manimpango.list_fonts()
    assert intial != final


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
@pytest.mark.parametrize("font_name", font_lists)
def test_register_and_unregister_font(font_name):
    assert manimpango.register_font(str(font_name)), "Invalid Font possibly."
    assert manimpango.unregister_font(str(font_name)), "Failed to unregister the font"


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
@pytest.mark.parametrize("font_name", font_lists)
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="always returns true")
def test_fail_just_unregister(font_name):
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


def test_simple_fonts_render(tmpdir):
    filename = str(Path(tmpdir) / "hello.svg")
    MarkupText("Hello World", filename=filename)
    assert Path(filename).exists()


@pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="unsupported api other than linux"
)
def test_both_fc_and_register_font_are_same():
    assert manimpango.fc_register_font == manimpango.register_font
    assert manimpango.fc_unregister_font == manimpango.unregister_font


@pytest.mark.parametrize("font_file", font_lists)
def test_fc_font_register(setup_fontconfig, font_file):
    intial = manimpango.list_fonts()
    assert manimpango.fc_register_font(str(font_file)), "Invalid Font possibly."
    final = manimpango.list_fonts()
    assert intial != final


def test_fc_font_unregister(setup_fontconfig):
    # it will remove everything
    intial = manimpango.list_fonts()
    manimpango.fc_unregister_font("clear")
    final = manimpango.list_fonts()
    assert intial != final
