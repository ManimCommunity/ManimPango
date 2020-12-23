# -*- coding: utf-8 -*-
import argparse
import shlex
from pathlib import Path
from shlex import quote
from subprocess import PIPE, Popen
try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False
from setuptools import Extension, setup

_cflag_parser = argparse.ArgumentParser(add_help=False)
_cflag_parser.add_argument("-I", dest="include_dirs", action="append")
_cflag_parser.add_argument("-L", dest="library_dirs", action="append")
_cflag_parser.add_argument("-l", dest="libraries", action="append")
_cflag_parser.add_argument("-D", dest="define_macros", action="append")
_cflag_parser.add_argument("-R", dest="runtime_library_dirs", action="append")


def parse_cflags(raw_cflags):
    raw_args = shlex.split(raw_cflags.strip())
    args, unknown = _cflag_parser.parse_known_args(raw_args)
    config = {k: v or [] for k, v in args.__dict__.items()}
    for i, x in enumerate(config["define_macros"]):
        parts = x.split("=", 1)
        value = x[1] or None if len(x) == 2 else None
        config["define_macros"][i] = (parts[0], value)
    return config, " ".join(quote(x) for x in unknown)


def get_library_config(name):
    """Get distutils-compatible extension extras for the given library.
    This requires ``pkg-config``.
    """
    try:
        proc = Popen(
            ["pkg-config", "--cflags", "--libs", name],
            stdout=PIPE,
            stderr=PIPE,
        )
    except OSError:
        print("pkg-config is required for building manimpango")
        exit(1)

    raw_cflags, _ = proc.communicate()
    known, unknown = parse_cflags(raw_cflags.decode("utf8"))
    if unknown:
        print(
            "pkg-config returned flags we \
            don't understand: {}".format(
                unknown
            )
        )
    return known

ext = '.pyx' if USE_CYTHON else '.c'
base_file = Path(__file__).parent / "manimpango"
returns = get_library_config("pangocairo")
ext_modules = [
    Extension(
        "manimpango.cmanimpango",
        [str(base_file / ("cmanimpango"+ext))],
        **returns,
    ),
]
if USE_CYTHON:
    ext_modules = cythonize(
        ext_modules,
        language_level=3,
        include_path=["manimpango"]
    )
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="manimpango",
    version="0.1.0",
    author="The Manim Community Developers",
    maintainer="The Manim Community Developers",
    url="https://github.com/ManimCommunity/manimpango",
    description="Bindings for Pango for using with Manim.",
    long_description=long_description,
    zip_safe=False,
    long_description_content_type="text/markdown",
    packages=["manimpango"],
    python_requires=">=3.6",
    platforms=["Linux", "macOS", "Windows"],
    keywords=["cython", "pango", "cairo", "svg", "manim"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
    ],
    ext_modules=ext_modules,
    package_data = {
        'manimpango': ['*.pxd'],
    }
)
