#!python
# cython: language_level=3

"""Font registration and management for ManimPango."""

from __future__ import annotations

import cython

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from manimpango._fonts cimport *


@dataclass(frozen=True)
class RegisteredFont:
    """A class to represent a registered font file."""
    path: str
    platform: str


# Global set of registered fonts
registered_fonts: set[RegisteredFont] = set()


cpdef bint register_font(str font_path):
    """Register a font file so Pango can use it for rendering."""
    path = Path(font_path)
    if not path.exists():
        raise FileNotFoundError(f"Font file not found: {font_path}")

    abs_path = os.fspath(path.resolve())

    if sys.platform == "linux":
        platform = "fontconfig"
    elif sys.platform == "darwin":
        platform = "macos"
    elif sys.platform == "win32":
        platform = "win32"
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")

    font = RegisteredFont(abs_path, platform)

    if font in registered_fonts:
        return True

    cdef bytes path_bytes = abs_path.encode('utf-8')
    cdef bint success = FcConfigAppFontAddFile(NULL, <const FcChar8*><const char*>path_bytes)

    if success:
        registered_fonts.add(font)

    return success


cpdef bint unregister_font(str font_path):
    """Unregister a previously registered font."""
    path = Path(font_path)
    abs_path = os.fspath(path.resolve())

    if sys.platform == "linux":
        platform = "fontconfig"
    elif sys.platform == "darwin":
        platform = "macos"
    elif sys.platform == "win32":
        platform = "win32"
    else:
        return False

    font = RegisteredFont(abs_path, platform)

    if font not in registered_fonts:
        return True

    # On Linux/macOS (fontconfig), we can't easily unregister individual fonts
    # Just clear all app fonts
    FcConfigAppFontClear(NULL)
    registered_fonts.discard(font)
    return True


cpdef list list_fonts():
    """List all font family names available to Pango."""
    cdef PangoFontMap* fontmap = NULL
    cdef PangoFontFamily** families = NULL
    cdef int n_families = 0

    fontmap = pango_cairo_font_map_new()
    if fontmap == NULL:
        raise MemoryError("Failed to create PangoFontMap")

    try:
        pango_font_map_list_families(fontmap, &families, &n_families)

        if families == NULL or n_families == 0:
            raise MemoryError("Failed to get font families")

        family_list = []
        for i in range(n_families):
            name_ptr = pango_font_family_get_name(families[i])
            if name_ptr != NULL:
                family_list.append(name_ptr.decode('utf-8'))

    finally:
        if fontmap != NULL:
            g_object_unref(fontmap)

    family_list.sort()
    return family_list
