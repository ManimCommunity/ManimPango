import os

if os.name == "nt":
    os.environ["PATH"] = (
        os.path.abspath(os.path.dirname(__file__))
        + os.pathsep
        + os.environ["PATH"]  # noqa: E501
    )
try:
    from .cmanimpango import *  # noqa: F401,F403
except ImportError:
    raise ImportError("Couldn't load the necessary Shared Libraries.")
