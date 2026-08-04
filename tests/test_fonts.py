# -*- coding: utf-8 -*-
"""Tests for font registration and listing — v2 API."""

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
    def test_register_returns_open_handle_with_normalized_path(self):
        font_path = FONT_DIR / "BungeeOutline-Regular.ttf"

        with manimpango.register_font(font_path) as registration:
            assert isinstance(registration, manimpango.FontRegistration)
            assert Path(registration.path) == font_path.resolve()
            assert registration.closed is False

        assert registration.closed is True

    def test_register_nonexistent_raises(self):
        with pytest.raises(manimpango.FontNotFoundError):
            manimpango.register_font("/nonexistent/font.ttf")

    def test_register_invalid_file_raises_registration_error(self, tmp_path):
        invalid_font = tmp_path / "not-a-font.ttf"
        invalid_font.write_text("not a font", encoding="utf-8")

        with pytest.raises(manimpango.FontRegistrationError):
            manimpango.register_font(invalid_font)

    def test_close_is_idempotent(self):
        registration = manimpango.register_font(FONT_DIR / "AdobeVFPrototype.ttf")

        registration.close()
        registration.close()

        assert registration.closed is True

    def test_registered_family_is_listed_and_used_for_rendering(self):
        font_path = FONT_DIR / "BungeeOutline-Regular.ttf"
        family = "Bungee Outline"
        assert family not in manimpango.list_fonts()

        fallback = manimpango.render("Hello", font="Deliberately Missing Family")
        with manimpango.register_font(font_path):
            assert family in manimpango.list_fonts()
            registered = manimpango.render("Hello", font=family)

        assert registered.width > 0
        assert registered.svg != fallback.svg
        assert family not in manimpango.list_fonts()
        assert manimpango.render("Hello", font=family).svg == fallback.svg

    def test_nested_handles_keep_font_registered_until_last_handle_closes(self):
        font_path = FONT_DIR / "BungeeOutline-Regular.ttf"
        family = "Bungee Outline"
        assert family not in manimpango.list_fonts()

        first = manimpango.register_font(font_path)
        second = manimpango.register_font(font_path)
        try:
            first.close()

            assert first.closed is True
            assert second.closed is False
            assert family in manimpango.list_fonts()
            assert manimpango.render("Hello", font=family).width > 0
        finally:
            second.close()

        assert family not in manimpango.list_fonts()

    def test_closing_one_font_handle_keeps_another_font_available(self):
        first_family = "Bungee Outline"
        second_family = "Ma Shan Zheng"
        assert first_family not in manimpango.list_fonts()
        assert second_family not in manimpango.list_fonts()

        first = manimpango.register_font(FONT_DIR / "BungeeOutline-Regular.ttf")
        second = manimpango.register_font(FONT_DIR / "MaShanZheng-Regular.ttf")
        try:
            assert first_family in manimpango.list_fonts()
            assert second_family in manimpango.list_fonts()
            first.close()

            assert first.closed is True
            assert second.closed is False
            assert first_family not in manimpango.list_fonts()
            assert second_family in manimpango.list_fonts()
            assert manimpango.render("Hello", font=second_family).width > 0
        finally:
            second.close()

        assert second_family not in manimpango.list_fonts()

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
        with manimpango.register_font(FONT_DIR / font_file) as registration:
            assert registration.closed is False
        assert registration.closed is True
