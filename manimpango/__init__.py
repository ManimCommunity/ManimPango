# -*- coding: utf-8 -*-
import os

if os.name == "nt":
    os.environ["PATH"] = (
        f"{os.path.abspath(os.path.dirname(__file__))}"
        f"{os.pathsep}"
        f"{os.environ['PATH']}"
    )
try:
    from .cmanimpango import *  # noqa: F403,F401
except ImportError:
    raise ImportError("Couldn't load the necessary Shared Libraries.")
