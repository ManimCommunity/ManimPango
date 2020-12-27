# -*- coding: utf-8 -*-
import os
import platform


def set_dll_search_path():
    # Python 3.8 no longer searches for DLLs in PATH, so we have to add
    # everything in PATH manually.
    if (
        os.name != "nt"
        or "GCC" not platform.python_compiler()
        or not hasattr(os, "add_dll_directory")
    ):
        return
    for p in os.environ.get("PATH", "").split(os.pathsep):
        try:
            os.add_dll_directory(p)
        except OSError:
            pass


set_dll_search_path()
