import manimpango
import pytest
from . import FONT_DIR


def pytest_report_header(config):
    return (
        f"ManimPango version {manimpango.__version__}\n"
        f"Pango version {manimpango.pango_version()}\n"
        f"Cairo version {manimpango.cairo_version()}"
    )
