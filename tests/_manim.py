# -*- coding: utf-8 -*-
"""This file contains helpers for the tests copied and modified
from Manim.
"""
import copy
import os
import re
from pathlib import Path
from typing import Sequence

from manimpango import Alignment, MarkupUtils, TextSetting, text2svg


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
        wrap_text: bool = True,
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
        self.wrap_text = wrap_text
        if MarkupUtils.validate(self.text):
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
        if self.wrap_text:
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
        else:
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
                pango_width=-1,
            )
            # -1 for no wrapping
            # default is full width and then wrap.

    def __repr__(self):
        return f"MarkupText({repr(self.original_text)})"


class Text:
    def __init__(
        self,
        text: str,
        fill_opacity: float = 1.0,
        stroke_width: int = 0,
        size: int = 1,
        line_spacing: int = -1,
        font: str = "",
        slant: str = "NORMAL",
        weight: str = "NORMAL",
        gradient: tuple = None,
        tab_width: int = 4,
        disable_ligatures: bool = False,
        filename: str = "text.svg",
        color: str = "white",
        **kwargs,
    ) -> None:
        self.color = color
        self.size = size
        self.filename = filename
        self.line_spacing = line_spacing
        self.font = font
        self.slant = slant
        self.weight = weight
        self.gradient = gradient
        self.tab_width = tab_width
        self.original_text = text
        self.disable_ligatures = disable_ligatures
        text_without_tabs = text
        self.t2f = self.t2s = self.t2w = self.t2c = {}
        if text.find("\t") != -1:
            text_without_tabs = text.replace("\t", " " * self.tab_width)
        self.text = text_without_tabs
        if self.line_spacing == -1:
            self.line_spacing = self.size + self.size * 0.3
        else:
            self.line_spacing = self.size + self.size * self.line_spacing
        self.text2svg()

    def _merge_settings(
        self, left_setting: TextSetting, right_setting: TextSetting, args: Sequence[str]
    ) -> TextSetting:
        contained = right_setting.end < left_setting.end
        new_setting = copy.copy(left_setting) if contained else copy.copy(right_setting)

        new_setting.start = right_setting.end if contained else left_setting.end
        left_setting.end = right_setting.start
        if not contained:
            right_setting.end = new_setting.start

        for arg in args:
            left = getattr(left_setting, arg)
            right = getattr(right_setting, arg)
            default = getattr(self, arg)
            if left != default and getattr(right_setting, arg) != default:
                raise ValueError(
                    "Ambiguous style for text"
                    f"'{self.text[right_setting.start:right_setting.end]}':"
                    f"'{arg}' cannot be both '{left}' and '{right}'."
                )
            setattr(right_setting, arg, left if left != default else right)
        return new_setting

    def text2settings(self):
        """Internally used function. Converts the texts and styles
        to a setting for parsing."""
        settings = []
        t2xs = [
            (self.t2f, "font"),
            (self.t2s, "slant"),
            (self.t2w, "weight"),
            (self.t2c, "color"),
        ]
        t2xwords = {
            *self.t2f.keys(),
            *self.t2s.keys(),
            *self.t2w.keys(),
            *self.t2c.keys(),
        }
        for word in t2xwords:
            setting_args = {
                arg: t2x[word] if word in t2x else getattr(self, arg)
                for t2x, arg in t2xs
            }

            for start, end in self.find_indexes(word, self.text):
                settings.append(TextSetting(start, end, **setting_args))

        # Handle overlaps
        setting_args = {arg: getattr(self, arg) for _, arg in t2xs}

        settings.sort(key=lambda setting: setting.start)
        index = 0
        for setting in settings:
            index += 1
            if index == len(settings):
                break

            next_setting = settings[index]
            if setting.end > next_setting.start:
                new_setting = self._merge_settings(setting, next_setting, setting_args)
                new_index = index
                while (
                    new_index < len(settings)
                    and settings[new_index].start < new_setting.start
                ):
                    new_index += 1
                settings.insert(new_index, new_setting)

        # Set all text settings (default font, slant, weight)
        temp_settings = settings.copy()
        start = 0
        for setting in settings:
            if setting.start != start:
                temp_settings.append(TextSetting(start, setting.start, **setting_args))
            start = setting.end
        if start != len(self.text):
            temp_settings.append(TextSetting(start, len(self.text), **setting_args))
        settings = sorted(temp_settings, key=lambda setting: setting.start)

        if re.search(r"\n", self.text):
            line_num = 0
            for start, end in self.find_indexes("\n", self.text):
                for setting in settings:
                    if setting.line_num == -1:
                        setting.line_num = line_num
                    if start < setting.end:
                        line_num += 1
                        new_setting = copy.copy(setting)
                        setting.end = end
                        new_setting.start = end
                        new_setting.line_num = line_num
                        settings.append(new_setting)
                        settings.sort(key=lambda setting: setting.start)
                        break
        for setting in settings:
            if setting.line_num == -1:
                setting.line_num = 0
        return settings

    def text2svg(self):
        """Internally used function.
        Convert the text to SVG using Pango
        """
        size = self.size * 10
        line_spacing = self.line_spacing * 10
        dir_name = Path(self.filename).parent
        disable_liga = self.disable_ligatures
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_name = self.filename
        settings = self.text2settings()
        width = 600
        height = 400

        return text2svg(
            settings,
            size,
            line_spacing,
            disable_liga,
            file_name,
            30,
            30,
            width,
            height,
            self.text,
        )
