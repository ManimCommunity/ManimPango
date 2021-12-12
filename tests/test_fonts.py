# -*- coding: utf-8 -*-
import os
import subprocess
import sys
import textwrap
from contextlib import contextmanager
from pathlib import Path
from shutil import copyfile

import pytest

import manimpango

from . import FONT_DIR
from ._manim import MarkupText


@contextmanager
def register_font(font_file: Path):
    font_file = os.fspath(font_file)
    init = manimpango.list_fonts()
    assert manimpango.register_font(font_file), "Invalid Font possibly."
    final = manimpango.list_fonts()
    yield list(set(final) - set(init))[0]
    assert manimpango.unregister_font(font_file), "Can't unregister Font"


def font_list():
    _t = [
        (FONT_DIR / "AdobeVFPrototype.ttf").absolute(),
        (FONT_DIR / "BungeeColor-Regular_colr_Windows.ttf").absolute(),
        (FONT_DIR / "MaShanZheng-Regular.ttf").absolute(),
    ]
    _d = {}
    for i in _t:
        with register_font(i) as f:
            _d[i] = f
    return _d


font_lists_dict = font_list()


def test_unicode_font_name(tmpdir):
    final_font = str(Path(tmpdir, "庞门正.ttf").absolute())
    copyfile(FONT_DIR / "AdobeVFPrototype.ttf", final_font)
    assert manimpango.register_font(final_font)
    assert manimpango.unregister_font(final_font)


@pytest.mark.parametrize("font_name", font_lists_dict)
def test_register_and_unregister_font(font_name):
    intial = manimpango.list_fonts()
    assert manimpango.register_font(str(font_name)), "Invalid Font possibly."
    final = manimpango.list_fonts()
    assert intial != final
    assert manimpango.unregister_font(os.fspath(font_name)), "Can't unregister font."
    assert intial == manimpango.list_fonts()


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="no warning are raised for linux"
)
@pytest.mark.parametrize("font_file,font_name", font_lists_dict.items())
def test_warning(font_file, font_name):
    # this tests need to be run in a separate subprocess because
    # of fontmap cache in Pango.
    command = textwrap.dedent(
        f"""\
            from tests import set_dll_search_path
            set_dll_search_path() # this is needed on Windows to run
            import manimpango
            import os
            from tests._manim import Text
            font_file = r'{os.fspath(font_file)}'
            font_name = r'{font_name}'
            intial = manimpango.list_fonts()
            manimpango.register_font(os.fspath(font_file))
            final = manimpango.list_fonts()
            assert intial != final
            Text("Testing", font=font_name)
            manimpango.unregister_font(os.fspath(font_file))
        """
    )
    a = subprocess.run(
        [sys.executable, "-c", command],
        check=True,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent.parent,
    )
    captured = a.stderr.decode()
    assert "Pango-WARNING **" not in captured, "Looks like Pango raised a warning?"


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
@pytest.mark.parametrize("font_name", font_lists_dict)
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="always returns true")
def test_fail_just_unregister(font_name):
    assert not manimpango.unregister_font(
        str(font_name)
    ), "Failed to unregister the font"


@pytest.mark.skipif(
    sys.platform.startswith("win32"), reason="unsupported api for win32"
)
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="unsupported api for mac")
def test_unregister_not_fail_linux():
    assert manimpango.unregister_font("random")


@pytest.mark.skipif(
    sys.platform.startswith("linux"), reason="unsupported api for linux"
)
def test_adding_dummy_font(tmpdir):
    dummy = tmpdir / "font.ttf"
    with open(dummy, "wb") as f:
        f.write(b"dummy")
    assert not manimpango.register_font(str(dummy)), "Registered a dummy font?"
    assert not manimpango.fc_register_font(str(dummy)), "Registered a dummy font?"


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


@pytest.mark.parametrize("font_file", font_lists_dict)
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
