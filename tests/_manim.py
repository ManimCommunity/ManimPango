# -*- coding: utf-8 -*-
"""This file contains helpers for the tests copied and modified
from Manim.
"""

import os
from pathlib import Path

from manimpango import Alignment, MarkupUtils


class MarkupText:
    def __init__(
        self,
        text: str,
        *,
        size: int = 1,
        line_spacing: int = None,
        font: str = None,
        slant: str = "NORMAL",
        weight: str = "NORMAL",
        tab_width: int = 4,
        disable_ligatures: bool = False,
        justify: bool = None,
        indent: float = None,
        alignment: Alignment = None,
        # for the tests
        filename: str = "test.svg",
        **kwargs,
    ):
        self.text = text
        self.size = size
        self.line_spacing = line_spacing
        self.font = font
        self.slant = slant
        self.weight = weight
        self.tab_width = tab_width
        self.filename = filename
        self.original_text = text
        self.disable_ligatures = disable_ligatures

        self.justify = justify
        self.indent = indent
        self.alignment = alignment
        if not MarkupUtils.validate(self.text):
            raise ValueError(
                f"Pango cannot parse your markup in {self.text}. "
                "Please check for typos, unmatched tags or unescaped "
                "special chars like < and &."
            )
        self.text2svg()

    def text2svg(self):
        """Convert the text to SVG using Pango."""
        size = self.size * 10
        dir_name = Path(self.filename).parent
        disable_liga = self.disable_ligatures
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_name = self.filename
        return MarkupUtils.text2svg(
            f"{self.text}",
            self.font,
            self.slant,
            self.weight,
            size,
            True,  # stray positional argument
            disable_liga,
            file_name,
            20,
            20,
            600,  # width
            400,  # height
            justify=self.justify,
            indent=self.indent,
            line_spacing=self.line_spacing,
            alignment=self.alignment,
        )

    def __repr__(self):
        return f"MarkupText({repr(self.original_text)})"
