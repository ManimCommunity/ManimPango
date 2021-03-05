# -*- coding: utf-8 -*-
import re

from .enums import Style, Weight


class PangoUtils:
    @staticmethod
    def str2style(string: str) -> Style:
        """Internally used function. Converts text to Pango Understandable Styles."""
        if string == "NORMAL":
            return Style.NORMAL
        elif string == "ITALIC":
            return Style.ITALIC
        elif string == "OBLIQUE":
            return Style.OBLIQUE
        else:
            raise AttributeError("There is no Style Called %s" % string)

    @staticmethod
    def str2weight(string: str) -> Weight:
        """Internally used function. Convert text to Pango Understandable Weight"""
        if string == "NORMAL":
            return Weight.NORMAL
        elif string == "BOLD":
            return Weight.BOLD
        elif string == "THIN":
            return Weight.THIN
        elif string == "ULTRALIGHT":
            return Weight.ULTRALIGHT
        elif string == "LIGHT":
            return Weight.LIGHT
        elif string == "BOOK":
            return Weight.BOOK
        elif string == "MEDIUM":
            return Weight.MEDIUM
        elif string == "SEMIBOLD":
            return Weight.SEMIBOLD
        elif string == "ULTRABOLD":
            return Weight.ULTRABOLD
        elif string == "HEAVY":
            return Weight.HEAVY
        elif string == "ULTRAHEAVY":
            return Weight.ULTRAHEAVY
        else:
            raise AttributeError("There is no Font Weight Called %s" % string)

    @staticmethod
    def remove_last_M(file_name: str) -> None:
        """Remove element from the SVG file in order to allow comparison."""
        with open(file_name, "r") as fpr:
            content = fpr.read()
        content = re.sub(r'Z M [^A-Za-z]*? "\/>', 'Z "/>', content)
        with open(file_name, "w") as fpw:
            fpw.write(content)
