# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from __future__ import annotations

from importlib.metadata import version as distribution_version
from pathlib import Path

# -- Project information -----------------------------------------------------

project = "ManimPango"
copyright = "2021–2026, The Manim Community Dev Team"
author = "The Manim Community Dev Team"

release = distribution_version("ManimPango")
version = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinxext.opengraph",
]

templates_path = ["_templates"]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

html_theme = "furo"

html_static_path = ["_static"]
html_favicon = str(Path("_static/favicon.ico"))
autosummary_generate = True

# generate documentation from type hints
autodoc_typehints = "description"
autoclass_content = "both"

# controls whether functions documented by the autofunction directive
# appear with their full module names
add_module_names = False

intersphinx_mapping = {
    "manim": ("https://docs.manim.community/en/stable", None),
    "python": ("https://docs.python.org/3", None),
}

ogp_image = "https://www.manim.community/logo.png"
ogp_site_name = "ManimPango | Documentation"
ogp_site_url = "https://manimpango.manim.community/"
