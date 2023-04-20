"""
Helper to preload windows dlls to prevent dll not found errors.
Once a DLL is preloaded, its namespace is made available to any
subsequent DLL. This file is created as part of the scripts that
build the wheel.
"""
import glob
import os

if os.name == "nt":
    # convention for storing / loading the DLL from
    # ManimPango/.libs/, if present
    basedir = os.path.dirname(__file__)
    libs_dir = os.path.abspath(os.path.join(basedir, ".libs"))

    # first add them to os.add_dll_directory
    try:
        if hasattr(os, "add_dll_directory"):
            libs_dir = os.path.abspath(os.path.join(basedir, ".libs"))
            if os.path.isdir(libs_dir):
                os.add_dll_directory(libs_dir)
    except Exception:
        pass

    try:
        from ctypes import WinDLL
    except Exception:
        pass
    else:
        DLL_filenames = []
        if os.path.isdir(libs_dir):
            for filename in glob.glob(os.path.join(libs_dir, "*openblas*dll")):
                # NOTE: would it change behavior to load ALL
                # DLLs at this path vs. the name restriction?
                WinDLL(os.path.abspath(filename))
                DLL_filenames.append(filename)
