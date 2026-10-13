from pathlib import Path
from pango cimport *

import os
from dataclasses import dataclass

include "utils.pxi"

@dataclass(frozen=True)
class RegisteredFont:
    """A class to represent a font file.

    Attributes
    ----------
    path : :class:`str`
        The path to the font file.
    """

    path: str
    type: "fontconfig" | "win32" | "macos"

cpdef bint _fc_register_font(set registered_fonts, str font_path):
    a = Path(font_path)
    assert a.exists(), f"font doesn't exist at {a.absolute()}"
    font_path = os.fspath(a.absolute())
    font_path_bytes = font_path.encode('utf-8')
    cdef const unsigned char* fontPath = font_path_bytes
    fontAddStatus = FcConfigAppFontAddFile(FcConfigGetCurrent(), fontPath)
    if fontAddStatus:
        registered_fonts.add(RegisteredFont(font_path, "fontconfig"))
        return True
    else:
        return False


cpdef bint _fc_unregister_font(set registered_fonts, str font_path):
    FcConfigAppFontClear(NULL)
    # remove all type "fontconfig" files
    copy = registered_fonts.copy()
    for font in copy:
        if font.type == 'fontconfig':
            registered_fonts.remove(font)

    return True


# Linux, the BSDs and other Unix-like systems use fontconfig directly.
IF UNAME_SYSNAME != "Windows" and UNAME_SYSNAME != "Darwin":
    _register_font = _fc_register_font
    _unregister_font = _fc_unregister_font


ELIF UNAME_SYSNAME == "Windows":
    cpdef bint _register_font(set registered_fonts, str font_path):
        a = Path(font_path)
        assert a.exists(), f"font doesn't exist at {a.absolute()}"
        font_path = os.fspath(a.absolute())
        cdef LPCWSTR wchar_path = PyUnicode_AsWideCharString(font_path, NULL)
        fontAddStatus = AddFontResourceExW(
            wchar_path,
            FR_PRIVATE,
            0
        )

        if fontAddStatus > 0:
            registered_fonts.add(RegisteredFont(font_path, "win32"))
            return True
        else:
            return False


    cpdef bint _unregister_font(set registered_fonts, str font_path):
        a = Path(font_path)
        assert a.exists(), f"font doesn't exist at {a.absolute()}"
        font_path = os.fspath(a.absolute())

        font = RegisteredFont(font_path, "win32")
        if font in registered_fonts:
            registered_fonts.remove(font)

        cdef LPCWSTR wchar_path = PyUnicode_AsWideCharString(font_path, NULL)
        return RemoveFontResourceExW(
            wchar_path,
            FR_PRIVATE,
            0
        )


ELIF UNAME_SYSNAME == "Darwin":
    cpdef bint _register_font(set registered_fonts, str font_path):
        a = Path(font_path)
        assert a.exists(), f"font doesn't exist at {a.absolute()}"
        font_path_bytes_py = str(a.absolute().as_uri()).encode('utf-8')
        cdef unsigned char* font_path_bytes = <bytes>font_path_bytes_py
        b = len(a.absolute().as_uri())
        cdef CFURLRef cf_url = CFURLCreateWithBytes(NULL, font_path_bytes, b, 0x08000100, NULL)
        res = CTFontManagerRegisterFontsForURL(
            cf_url,
            kCTFontManagerScopeProcess,
            NULL
        )
        if res:
            registered_fonts.add(RegisteredFont(os.fspath(a.absolute()), "macos"))
            return True
        else:
            return False


    cpdef bint _unregister_font(set registered_fonts, str font_path):
        a = Path(font_path)
        assert a.exists(), f"font doesn't exist at {a.absolute()}"
        font_path_bytes_py = str(a.absolute().as_uri()).encode('utf-8')
        cdef unsigned char* font_path_bytes = <bytes>font_path_bytes_py
        b = len(a.absolute().as_uri())
        cdef CFURLRef cf_url = CFURLCreateWithBytes(NULL, font_path_bytes, b, 0x08000100, NULL)
        res = CTFontManagerUnregisterFontsForURL(
            cf_url,
            kCTFontManagerScopeProcess,
            NULL
        )
        if res:
            font = RegisteredFont(os.fspath(a.absolute()), "macos")
            if font in registered_fonts:
                registered_fonts.remove(font)
            return True
        else:
            return False


cpdef list _list_fonts(tuple registered_fonts):
    cdef PangoFontMap* fontmap = pango_cairo_font_map_new()
    if fontmap == NULL:
        raise MemoryError("Pango.FontMap can't be created.")

    for font in registered_fonts:
        if font.type == 'win32':
            add_to_fontmap(fontmap, font.path)

    cdef int n_families=0
    cdef PangoFontFamily** families=NULL
    pango_font_map_list_families(
        fontmap,
        &families,
        &n_families
    )
    if families is NULL or n_families == 0:
        raise MemoryError("Pango returned unexpected length on families.")

    family_list = []
    for i in range(n_families):
        name = pango_font_family_get_name(families[i])
        # according to pango's docs, the `char *` returned from
        # `pango_font_family_get_name`is owned by pango, and python
        # shouldn't interfere with it. I hope Cython handles it.
        # https://cython.readthedocs.io/en/stable/src/tutorial/strings.html#dealing-with-const
        family_list.append(name.decode())

    g_free(families)
    g_object_unref(fontmap)
    family_list.sort()
    return family_list
