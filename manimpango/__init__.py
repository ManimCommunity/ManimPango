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
except ImportError as ie:  # pragma: no cover
    py_ver = ".".join(map(str, sys.version_info[:3]))
    msg = f"""

ManimPango could not import and load the necessary shared libraries.
This error may occur when ManimPango and its dependencies are improperly set up.
Please make sure the following versions are what you expect:

    * ManimPango v{__version__}, Python v{py_ver}

If you believe there is a greater problem,
feel free to contact us or create an issue on GitHub:

    * Discord: https://discord.gg/mMRrZQW
    * GitHub: https://github.com/ManimCommunity/ManimPango/issues

Original error: {ie}
"""
    raise ImportError(msg)
