# -*- coding: utf-8 -*-
import manimpango


def pytest_report_header(config):
    info = manimpango.get_version_info()
    return (
        f"ManimPango version {info['manimpango']}\n"
        f"Pango version {info['pango']}\n"
        f"Cairo version {info['cairo']}"
    )
