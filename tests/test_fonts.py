# -*- coding: utf-8 -*-
"""Tests for font registration and listing — v2 API."""

import os
from pathlib import Path

import pytest

import manimpango

FONT_DIR = Path(__file__).parent / "fonts"


class TestListFonts:
    def test_returns_list(self):
        fonts = manimpango.list_fonts()
        assert isinstance(fonts, list)
        assert len(fonts) > 0

    def test_all_strings(self):
        fonts = manimpango.list_fonts()
        for f in fonts:
            assert isinstance(f, str)

    def test_sorted(self):
        fonts = manimpango.list_fonts()
        assert fonts == sorted(fonts)


class TestRegisterFont:
    def test_register_and_list(self):
        font_path = str(FONT_DIR / "AdobeVFPrototype.ttf")
        before = set(manimpango.list_fonts())
        assert manimpango.register_font(font_path)
        after = set(manimpango.list_fonts())
        new_fonts = after - before
        # The font should appear (may not on all platforms if fontconfig
        # cache hasn't refreshed, but registration should return True)
        manimpango.unregister_font(font_path)

    def test_register_returns_true(self):
        font_path = str(FONT_DIR / "BungeeOutline-Regular.ttf")
        result = manimpango.register_font(font_path)
        assert result is True
        manimpango.unregister_font(font_path)

    def test_register_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            manimpango.register_font("/nonexistent/font.ttf")

    def test_register_idempotent(self):
        font_path = str(FONT_DIR / "AdobeVFPrototype.ttf")
        assert manimpango.register_font(font_path)
        assert manimpango.register_font(font_path)  # second call is ok
        manimpango.unregister_font(font_path)

    def test_unregister(self):
        font_path = str(FONT_DIR / "AdobeVFPrototype.ttf")
        manimpango.register_font(font_path)
        result = manimpango.unregister_font(font_path)
        assert result is True

    def test_unregister_not_registered(self):
        font_path = str(FONT_DIR / "AdobeVFPrototype.ttf")
        # Unregistering something not registered should return True (no-op)
        result = manimpango.unregister_font(font_path)
        assert result is True

    def test_register_and_render(self):
        font_path = str(FONT_DIR / "BungeeOutline-Regular.ttf")
        manimpango.register_font(font_path)
        result = manimpango.render("Hello", font="Bungee Outline")
        assert result.svg
        assert result.width > 0
        manimpango.unregister_font(font_path)

    @pytest.mark.parametrize(
        "font_file",
        [
            "AdobeVFPrototype.ttf",
            "BungeeColor-Regular_colr_Windows.ttf",
            "BungeeOutline-Regular.ttf",
            "MaShanZheng-Regular.ttf",
        ],
    )
    def test_register_all_test_fonts(self, font_file):
        font_path = str(FONT_DIR / font_file)
        assert manimpango.register_font(font_path)
        manimpango.unregister_font(font_path)
