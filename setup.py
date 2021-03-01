# -*- coding: utf-8 -*-

import argparse
import os
import shlex
import subprocess
import sys
import warnings
from pathlib import Path
from shlex import quote
from subprocess import PIPE, Popen, check_call

from setuptools import Extension, setup

try:
    from Cython.Build import cythonize

    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False

coverage = False
if sys.argv[-1] == "--coverage":
    coverage = True
    sys.argv.pop()


def get_version():
    version_file = "manimpango/_version.py"
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


NAME = "ManimPango"
MANIMPANGO_VERSION = get_version()
MINIMUM_PANGO_VERSION = "1.30.0"
DEBUG = False

if sys.platform == "win32" and sys.version_info >= (3, 10):
    import atexit

    atexit.register(
        lambda: warnings.warn(
            f"ManimPango {MANIMPANGO_VERSION} does not support Python "
            f"{sys.version_info.major}.{sys.version_info.minor} and does not provide "
            "prebuilt Windows binaries. We do not recommend building from source on "
            "Windows.",
            RuntimeWarning,
        )
    )


class RequiredDependencyException(Exception):
    pass


NEEDED_LIBS = [
    "pangocairo-1.0",
    "pango-1.0",
    "gobject-2.0",
    "glib-2.0",
    "intl",
    "harfbuzz",
    "cairo",
]


class PKG_CONFIG:
    """Preform operations with pkg-config.
    Parameters
    ==========
    libname : :class:`str`
        The library name to query.
    """

    def __init__(self, libname: str) -> None:
        self.name = libname
        self.pkg_config = os.environ.get("PKG_CONFIG", "pkg-config")
        self.setup_argparse()
        self.check_pkgconfig = self.check_pkgconfig()

    def check_pkgconfig(self):
        """Check whether pkg-config works.
        If it doesn't work raise a warning.
        """
        try:
            check_call([self.pkg_config, "--version"], stdout=subprocess.DEVNULL)
            return True
        except Exception:
            warnings.warn(
                f"{self.pkg_config} doesn't exists or doesn't seem to work"
                "We assume that you give the compiler flags using"
                "corresponding environment variables.",
                RuntimeWarning,
            )
            return False

    def parse_cflags(self, raw_cflags):
        """Parse the flags from pkg-config using argparse."""
        raw_args = shlex.split(raw_cflags.strip())
        args, unknown = self._cflag_parser.parse_known_args(raw_args)
        config = {k: v or [] for k, v in args.__dict__.items()}
        for i, x in enumerate(config["define_macros"]):
            parts = x.split("=", 1)
            value = x[1] or None if len(x) == 2 else None
            config["define_macros"][i] = (parts[0], value)
        return config, " ".join(quote(x) for x in unknown)

    def setup_argparse(self):
        _cflag_parser = argparse.ArgumentParser(add_help=False)
        _cflag_parser.add_argument("-I", dest="include_dirs", action="append")
        _cflag_parser.add_argument("-L", dest="library_dirs", action="append")
        _cflag_parser.add_argument("-l", dest="libraries", action="append")
        _cflag_parser.add_argument("-D", dest="define_macros", action="append")
        _cflag_parser.add_argument("-R", dest="runtime_library_dirs", action="append")
        self._cflag_parser = _cflag_parser

    def check_min_version(self, version):
        """Check whether the library of that version exists."""
        command = [
            self.pkg_config,
            "--print-errors",
            "--atleast-version",
            version,
            self.name,
        ]
        try:
            check_call(command, stdout=subprocess.DEVNULL)
            return True
        except Exception:
            raise RequiredDependencyException(f"{self.name} >= {version} is required")

    @property
    def libs(self):
        """Get distutils-compatible extension extras for the given library.
        This requires ``pkg-config``.
        """
        if self.check_pkgconfig:
            name = self.name
            command = self.pkg_config
            try:
                proc = Popen(
                    [command, "--libs", name],
                    stdout=PIPE,
                    stderr=PIPE,
                )
            except Exception:
                pass
            raw_libs, _ = proc.communicate()
            known_libs, unknown_libs = self.parse_cflags(raw_libs.decode("utf8"))
            if unknown_libs:
                known_libs["extra_link_args"] = unknown_libs.split()
            return known_libs
        return dict()

    @property
    def cflags(self):
        if self.check_pkgconfig:
            name = self.name
            command = self.pkg_config
            try:
                proc = Popen(
                    [command, "--cflags", name],
                    stdout=PIPE,
                    stderr=PIPE,
                )
            except Exception:
                pass
            raw_cflags, _ = proc.communicate()
            known_cflags, unknown_cflags = self.parse_cflags(raw_cflags.decode("utf8"))
            if unknown_cflags:
                known_cflags["extra_compile_args"] = unknown_cflags.split()
            return known_cflags
        return dict()

    @property
    def setuptools_args(self):
        return update_dict(self.libs, self.cflags)


def update_dict(dict1: dict, dict2: dict):
    for key in dict1:
        if key in dict2:
            dict2[key] = dict1[key] + dict2[key]
        else:
            dict2[key] = dict1[key]
    return dict2


ext = ".pyx" if USE_CYTHON else ".c"
base_file = Path(__file__).parent / "manimpango"
_pkg_config = PKG_CONFIG("pangocairo")
_pkg_config.check_min_version(MINIMUM_PANGO_VERSION)
returns = _pkg_config.setuptools_args
if not _pkg_config.check_pkgconfig:
    returns["libraries"] = NEEDED_LIBS
if sys.platform == "win32":
    returns["libraries"] += ["Gdi32"]
    if hasattr(returns, "define_macros"):
        returns["define_macros"] += [("UNICODE", 1)]
    else:
        returns["define_macros"] = [("UNICODE", 1)]
if coverage:
    returns["define_macros"] += [("CYTHON_TRACE", 1)]
    returns["define_macros"] += [("CYTHON_TRACE_NOGIL", 1)]

ext_modules = [
    Extension(
        "manimpango.cmanimpango",
        [str(base_file / ("cmanimpango" + ext))],
        **returns,
    ),
    Extension(
        "manimpango.enums",
        [str(base_file / ("enums" + ext))],
        **returns,
    ),
    Extension(
        "manimpango.register_font",
        [str(base_file / ("register_font" + ext))],
        **returns,
    ),
]
if USE_CYTHON:
    ext_modules = cythonize(
        ext_modules,
        language_level=3,
        include_path=["manimpango"],
        gdb_debug=DEBUG,
        compiler_directives={"linetrace": coverage},
    )
with open("README.md") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=MANIMPANGO_VERSION,
    author="Naveen M K",
    author_email="naveen@syrusdark.website",
    maintainer="The Manim Community Developers",
    url="https://manimpango.manim.community/",
    description="Bindings for Pango for using with Manim.",
    long_description=long_description,
    zip_safe=False,
    long_description_content_type="text/markdown",
    packages=["manimpango"],
    python_requires=">=3.6",
    platforms=["Linux", "macOS", "Windows"],
    keywords=["cython", "pango", "cairo", "manim"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Cython",
    ],
    project_urls={
        "Documentation": "https://manimpango.manim.community/",
        "Source": "https://github.com/ManimCommunity/manimpango",
        "Release notes": "https://github.com/ManimCommunity/ManimPango/releases/",
    },
    ext_modules=ext_modules,
    package_data={
        "manimpango": ["*.pxd", "*.pyx"],
    },
)
