# -*- coding: utf-8 -*-
import pytest

import manimpango

from . import FONT_DIR


def pytest_report_header(config):
    return (
        f"ManimPango version {manimpango.__version__}\n"
        f"Pango version {manimpango.pango_version()}\n"
        f"Cairo version {manimpango.cairo_version()}"
    )


@pytest.fixture
def register_font():
    font = str(FONT_DIR / "CormorantUnicase-Regular.ttf")
    orig = manimpango.list_fonts()
    manimpango.register_font(font)
    final = manimpango.list_fonts()
    yield list(set(final) - set(orig))[0]
    manimpango.unregister_font(font)
