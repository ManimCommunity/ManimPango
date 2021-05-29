# -*- coding: utf-8 -*-
import sys

from . import _distributor_init  # noqa: F401
from ._version import __version__  # noqa: F403,F401

try:
    from .utils import *  # noqa: F403,F401

    initialize_glib()  # noqa: F405

    # utils should be imported first
    from .font_manager import *  # noqa: F403,F401
    from .layout import *  # noqa: F403,F401
    from .renderer import *  # noqa: F403,F401


except ImportError as ie:  # pragma: no cover
    py_ver = ".".join(map(str, sys.version_info[:3]))
    msg = f"""
ManimPango could not import and initialize itself.
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
