# -*- coding: utf-8 -*-
import os
import platform
import shutil
from pathlib import Path


def set_dll_search_path():
    # Python 3.8 no longer searches for DLLs in PATH, so we have to add
    # everything in PATH manually.
    if (
        os.name != "nt"
        or "GCC" in platform.python_compiler()
        or not hasattr(os, "add_dll_directory")
    ):
        return
    for p in os.environ.get("PATH", "").split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except OSError:
            pass


def delete_media_dir():
    a = Path("media")  # absolute to the running dir
    if a.exists():
        shutil.rmtree(a)


set_dll_search_path()
delete_media_dir()
CASES_DIR = Path(Path(__file__).parent, "cases").absolute()
FONT_DIR = Path(__file__).parent / "fonts"

import manimpango  # noqa: E402

font = str((FONT_DIR / "BungeeOutline-Regular.ttf").absolute())
orig = manimpango.list_fonts()
assert manimpango.register_font(font)
final = manimpango.list_fonts()
main_font = list(set(final) - set(orig))[0]
