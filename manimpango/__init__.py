# -*- coding: utf-8 -*-
import os

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
    raise ImportError("Couldn't load the necessary Shared Libraries.")
