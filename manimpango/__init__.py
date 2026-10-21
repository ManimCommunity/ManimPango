# -*- coding: utf-8 -*-
import os
import sys
import threading
from functools import wraps

from ._version import __version__  # noqa: F401

if os.name == "nt":  # pragma: no cover
    os.environ["PATH"] = (
        f"{os.path.abspath(os.path.dirname(__file__))}"
        f"{os.pathsep}"
        f"{os.environ['PATH']}"
    )

# Module-level lock for thread safety. Pango/Cairo access global state (the default
# PangoCairoFontMap, Fontconfig config, etc.) and the `registered_fonts` set is shared
# mutable state read during rendering and written during font registration. This lock
# serializes all access to these shared resources.
_pango_lock = threading.Lock()


def _synchronized(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with _pango_lock:
            return func(*args, **kwargs)
    return wrapper


try:
    from .register_font import (  # noqa: F401
        registered_fonts,
        RegisteredFont,
    )
    from .cmanimpango import (  # noqa: F401
        TextSetting,
        MarkupUtils,
        pango_version,
        cairo_version,
    )
    from .cmanimpango import text2svg as _text2svg_impl
    from .register_font import (
        register_font as _register_font_impl,
        unregister_font as _unregister_font_impl,
        fc_register_font as _fc_register_font_impl,
        fc_unregister_font as _fc_unregister_font_impl,
        list_fonts as _list_fonts_impl,
    )
    from .enums import (  # noqa: F401
        Style,
        Weight,
        Variant,
        Alignment,
    )
except ImportError as ie:  # pragma: no cover
    py_ver = ".".join(map(str, sys.version_info[:3]))
    msg = f"""

ManimPango could not import and load the necessary shared libraries.
This error may occur when ManimPango and its dependencies are improperly set up.
Please make sure the following versions are what you expect:

    * ManimPango v{__version__}, Python v{py_ver}

If you believe there is a greater problem,
feel free to contact us or create an issue on GitHub:

    * Discord: https://www.manim.community/discord/
    * GitHub: https://github.com/ManimCommunity/ManimPango/issues

Original error: {ie}
"""
    raise ImportError(msg)

text2svg = _synchronized(_text2svg_impl)
register_font = _synchronized(_register_font_impl)
unregister_font = _synchronized(_unregister_font_impl)
fc_register_font = _synchronized(_fc_register_font_impl)
fc_unregister_font = _synchronized(_fc_unregister_font_impl)
list_fonts = _synchronized(_list_fonts_impl)
MarkupUtils.text2svg = staticmethod(_synchronized(MarkupUtils.text2svg))
