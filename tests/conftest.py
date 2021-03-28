# -*- coding: utf-8 -*-
import manimpango


def pytest_report_header(config):
    return (
        f"ManimPango version {manimpango.__version__}\n"
        f"Pango version {manimpango.pango_version()}\n"
        f"Cairo version {manimpango.cairo_version()}"
    )
