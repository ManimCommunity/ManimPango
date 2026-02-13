# -*- coding: utf-8 -*-
import os
import sys
import threading

from ._version import __version__  # noqa: F403,F401

if os.name == "nt":  # pragma: no cover
    os.environ["PATH"] = (
        f"{os.path.abspath(os.path.dirname(__file__))}"
        f"{os.pathsep}"
        f"{os.environ['PATH']}"
    )

# Module-level lock for thread safety. Pango/Cairo use global state (the default
# PangoCairoFontMap, Fontconfig config, etc.) that is not thread-safe. Additionally,
# the `registered_fonts` set is shared mutable state read during rendering and written
# during font registration. This lock serializes all access to these shared resources.
_pango_lock = threading.Lock()

try:
    from .register_font import *  # isort:skip # noqa: F403,F401
    from .cmanimpango import *  # noqa: F403,F401
    from .enums import *  # noqa: F403,F401
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
else:
    # Wrap public API functions with the lock for thread safety.
    # The star imports above bring in the unlocked implementations;
    # the definitions below shadow them with locked versions.

    from .cmanimpango import text2svg as _text2svg_impl
    from .cmanimpango import MarkupUtils as _MarkupUtils
    from .register_font import (
        register_font as _register_font_impl,
        unregister_font as _unregister_font_impl,
        fc_register_font as _fc_register_font_impl,
        fc_unregister_font as _fc_unregister_font_impl,
        list_fonts as _list_fonts_impl,
    )

    def text2svg(*args, **kwargs):
        with _pango_lock:
            return _text2svg_impl(*args, **kwargs)

    def register_font(font_path):
        with _pango_lock:
            return _register_font_impl(font_path)

    def unregister_font(font_path):
        with _pango_lock:
            return _unregister_font_impl(font_path)

    def fc_register_font(font_path):
        with _pango_lock:
            return _fc_register_font_impl(font_path)

    def fc_unregister_font(font_path):
        with _pango_lock:
            return _fc_unregister_font_impl(font_path)

    def list_fonts():
        with _pango_lock:
            return _list_fonts_impl()

    # Wrap MarkupUtils.text2svg (a @staticmethod on a plain Python class)
    _markup_text2svg_impl = _MarkupUtils.text2svg

    def _locked_markup_text2svg(*args, **kwargs):
        with _pango_lock:
            return _markup_text2svg_impl(*args, **kwargs)

    _MarkupUtils.text2svg = staticmethod(_locked_markup_text2svg)
