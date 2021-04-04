# -*- coding: utf-8 -*-
import os
import sys

from ._version import __version__  # noqa: F403,F401

if os.name == "nt":  # pragma: no cover
    os.environ["PATH"] = (
        f"{os.path.abspath(os.path.dirname(__file__))}"
        f"{os.pathsep}"
        f"{os.environ['PATH']}"
    )
try:
    from .cmanimpango import *  # noqa: F403,F401
    from .enums import *  # noqa: F403,F401
    from .register_font import *  # noqa: F403,F401
except ImportError:  # pragma: no cover
    py_ver = ".".join(map(str, sys.version_info[:3]))
    error = "Couldn't load the necessary shared libraries.\n"
    error += f"ManimPango v{__version__}, Python v{py_ver}\n\n"
    error += "Please contact us at https://discord.gg/mMRrZQW or "
    error += "create an issue at https://github.com/ManimCommunity/ManimPango/issues\n"
    raise ImportError(error)
