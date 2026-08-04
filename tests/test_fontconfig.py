"""Linux Fontconfig isolation regression tests."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

import pytest

FONT_DIR = Path(__file__).parent / "fonts"


@pytest.mark.skipif(platform.system() != "Linux", reason="requires Fontconfig")
def test_closing_registration_preserves_foreign_fontconfig_app_font():
    """A renderer-private map must not clear default Fontconfig app fonts.

    The subprocess deliberately owns the process-default configuration, so no
    Fontconfig cleanup can affect the pytest process or another test.
    """
    foreign_font = FONT_DIR / "MaShanZheng-Regular.ttf"
    managed_font = FONT_DIR / "BungeeOutline-Regular.ttf"
    script = f"""\
import ctypes
import os
from pathlib import Path

import manimpango

class FcFontSet(ctypes.Structure):
    _fields_ = [("nfont", ctypes.c_int), ("sfont", ctypes.c_int),
                ("fonts", ctypes.POINTER(ctypes.c_void_p))]

fontconfig = ctypes.CDLL("libfontconfig.so.1")
fontconfig.FcInit.argtypes = []
fontconfig.FcInit.restype = ctypes.c_int
fontconfig.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
fontconfig.FcConfigAppFontAddFile.restype = ctypes.c_int
fontconfig.FcConfigGetFonts.argtypes = [ctypes.c_void_p, ctypes.c_int]
fontconfig.FcConfigGetFonts.restype = ctypes.POINTER(FcFontSet)
fontconfig.FcPatternGetString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int,
                                           ctypes.POINTER(ctypes.c_char_p)]
fontconfig.FcPatternGetString.restype = ctypes.c_int

foreign = Path({str(foreign_font)!r})
managed = Path({str(managed_font)!r})
assert fontconfig.FcInit()
assert fontconfig.FcConfigAppFontAddFile(None, os.fsencode(foreign))

def default_app_font_contains(path):
    font_set = fontconfig.FcConfigGetFonts(None, 1)  # FcSetApplication
    for index in range(font_set.contents.nfont):
        value = ctypes.c_char_p()
        if fontconfig.FcPatternGetString(
            font_set.contents.fonts[index], b"file", 0, ctypes.byref(value)
        ) == 0 and Path(os.fsdecode(value.value)).samefile(path):
            return True
    return False

assert default_app_font_contains(foreign)
with manimpango.register_font(managed):
    pass
assert default_app_font_contains(foreign)
"""
    subprocess.run([sys.executable, "-c", script], check=True, text=True)
