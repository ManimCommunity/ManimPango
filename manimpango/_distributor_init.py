""" Distributor init file

While in development, this file will contain code to support development
on windows. This code will be removed before the package is released.
"""
import os

if os.name == "nt":  # pragma: no cover
    os.environ["PATH"] = (
        f"{os.path.abspath(os.path.dirname(__file__))}"
        f"{os.pathsep}"
        f"{os.environ['PATH']}"
    )
    if hasattr(os, "add_dll_directory"):
        _path = r"C:\cibw\vendor\bin"
        if os.path.exists(_path):
            os.add_dll_directory(_path)
