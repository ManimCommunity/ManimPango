# -*- coding: utf-8 -*-
import re

from .enums import Style, Weight


class PangoUtils:
    @staticmethod
    def str2style(string: str) -> Style:
        """Internally used function. Converts text to Pango Understandable Styles."""
        styles = {
            "NORMAL": Style.NORMAL,
            "ITALIC": Style.ITALIC,
            "OBLIQUE": Style.OBLIQUE,
        }
        try:
            return styles[string]
        except KeyError:
            raise AttributeError("There is no Style Called %s" % string)

    @staticmethod
    def str2weight(string: str) -> Weight:
        """Internally used function. Convert text to Pango Understandable Weight"""
        weights = {
            "NORMAL": Weight.NORMAL,
            "BOLD": Weight.BOLD,
            "THIN": Weight.THIN,
            "ULTRALIGHT": Weight.ULTRALIGHT,
            "LIGHT": Weight.LIGHT,
            "BOOK": Weight.BOOK,
            "MEDIUM": Weight.MEDIUM,
            "SEMIBOLD": Weight.SEMIBOLD,
            "ULTRABOLD": Weight.ULTRABOLD,
            "HEAVY": Weight.HEAVY,
            "ULTRAHEAVY": Weight.ULTRAHEAVY,
        }
        try:
            return weights[string]
        except KeyError:
            raise AttributeError("There is no Font Weight Called %s" % string)

    @staticmethod
    def remove_last_M(file_name: str) -> None:
        """Remove element from the SVG file in order to allow comparison."""
        with open(file_name, "r") as fpr:
            content = fpr.read()
        content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
        with open(file_name, "w") as fpw:
            fpw.write(content)
