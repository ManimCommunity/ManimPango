# -*- coding: utf-8 -*-
"""Tests for manimpango.render() — the core v2 API."""

import os
import sys
from pathlib import Path
from xml.parsers.expat import ParserCreate

import pytest

import manimpango
from manimpango import Alignment, Style, Weight
from manimpango._text import LineInfo, RenderedText

FONT_DIR = Path(__file__).parent / "fonts"


# ── Helpers ──────────────────────────────────────────────────────────────

def assert_valid_svg(svg: str) -> None:
    """Assert that the given string is valid XML (SVG)."""
    p = ParserCreate()
    p.Parse(svg, True)


def assert_valid_result(result: RenderedText) -> None:
    """Assert basic invariants of a RenderedText."""
    assert isinstance(result, RenderedText)
    assert result.width > 0
    assert result.height > 0
    assert result.baseline > 0
    assert result.line_count >= 1
    assert len(result.lines) == result.line_count
    assert isinstance(result.svg, str)
    assert len(result.svg) > 0
    assert_valid_svg(result.svg)


# ── Basic rendering ─────────────────────────────────────────────────────

class TestRenderBasic:
    def test_plain_text(self):
        result = manimpango.render("Hello World")
        assert_valid_result(result)
        assert result.line_count == 1

    def test_empty_string(self):
        result = manimpango.render("")
        assert isinstance(result, RenderedText)
        assert result.line_count >= 1  # Pango produces 1 line even for ""
        assert isinstance(result.svg, str)

    def test_unicode(self):
        result = manimpango.render("வணக்கம்")
        assert_valid_result(result)

    def test_multiline_newlines(self):
        result = manimpango.render("Line 1\nLine 2\nLine 3")
        assert_valid_result(result)
        assert result.line_count == 3
        assert len(result.lines) == 3

    def test_single_character(self):
        result = manimpango.render("A")
        assert_valid_result(result)

    def test_whitespace_only(self):
        result = manimpango.render("   ")
        assert isinstance(result, RenderedText)
        assert isinstance(result.svg, str)

    def test_special_characters(self):
        result = manimpango.render("{ } < > & \" '")
        assert_valid_result(result)

    def test_long_text(self):
        text = "word " * 500
        result = manimpango.render(text, width=200)
        assert_valid_result(result)
        assert result.line_count > 1


# ── Markup ───────────────────────────────────────────────────────────────

class TestRenderMarkup:
    def test_bold_markup(self):
        result = manimpango.render("<b>Bold</b>", is_markup=True)
        assert_valid_result(result)

    def test_italic_markup(self):
        result = manimpango.render("<i>Italic</i>", is_markup=True)
        assert_valid_result(result)

    def test_color_markup(self):
        result = manimpango.render(
            "<span color='red'>Red</span> and <span color='blue'>Blue</span>",
            is_markup=True,
        )
        assert_valid_result(result)

    def test_nested_markup(self):
        result = manimpango.render(
            "<b><i>Bold Italic</i></b>",
            is_markup=True,
        )
        assert_valid_result(result)

    def test_invalid_markup_raises_valueerror(self):
        with pytest.raises(ValueError, match="[Mm]arkup"):
            manimpango.render("<b>unclosed", is_markup=True)

    def test_invalid_markup_unmatched_tag(self):
        with pytest.raises(ValueError):
            manimpango.render("<b><i>mismatched</b></i>", is_markup=True)

    def test_markup_with_ampersand(self):
        result = manimpango.render("A &amp; B", is_markup=True)
        assert_valid_result(result)

    def test_plain_text_with_angle_brackets(self):
        """Plain text mode should NOT interpret markup."""
        result = manimpango.render("<b>not bold</b>", is_markup=False)
        assert_valid_result(result)


# ── Font parameters ──────────────────────────────────────────────────────

class TestRenderFont:
    def test_font_family(self):
        result = manimpango.render("Test", font="Helvetica")
        assert_valid_result(result)

    def test_font_size(self):
        small = manimpango.render("Test", size=8.0)
        large = manimpango.render("Test", size=48.0)
        assert_valid_result(small)
        assert_valid_result(large)
        assert large.width > small.width
        assert large.height > small.height

    def test_weight_enum(self):
        normal = manimpango.render("Test", weight=Weight.NORMAL)
        bold = manimpango.render("Test", weight=Weight.BOLD)
        assert_valid_result(normal)
        assert_valid_result(bold)
        # Bold text is typically wider
        assert bold.width >= normal.width

    def test_weight_int(self):
        """Arbitrary integer weight (for variable fonts)."""
        result = manimpango.render("Test", weight=450)
        assert_valid_result(result)

    def test_style_italic(self):
        result = manimpango.render("Test", style=Style.ITALIC)
        assert_valid_result(result)

    def test_style_oblique(self):
        result = manimpango.render("Test", style=Style.OBLIQUE)
        assert_valid_result(result)


# ── Layout parameters ────────────────────────────────────────────────────

class TestRenderLayout:
    def test_width_wrapping(self):
        text = "This is a long sentence that should wrap when given a narrow width"
        narrow = manimpango.render(text, width=100)
        wide = manimpango.render(text, width=1000)
        assert_valid_result(narrow)
        assert_valid_result(wide)
        assert narrow.line_count > wide.line_count
        assert narrow.height > wide.height

    def test_no_width_no_wrap(self):
        text = "A single very long line that should not wrap at all"
        result = manimpango.render(text)
        assert_valid_result(result)
        assert result.line_count == 1

    def test_alignment_left(self):
        result = manimpango.render("Test", width=200, alignment=Alignment.LEFT)
        assert_valid_result(result)

    def test_alignment_center(self):
        result = manimpango.render("Test", width=200, alignment=Alignment.CENTER)
        assert_valid_result(result)

    def test_alignment_right(self):
        result = manimpango.render("Test", width=200, alignment=Alignment.RIGHT)
        assert_valid_result(result)

    def test_justify(self):
        text = "This is a sentence that is long enough to produce wrapping."
        result = manimpango.render(text, width=150, justify=True)
        assert_valid_result(result)

    def test_indent(self):
        result = manimpango.render("Indented text", indent=20.0)
        assert_valid_result(result)

    def test_line_spacing(self):
        text = "Line 1\nLine 2"
        normal = manimpango.render(text)
        spaced = manimpango.render(text, line_spacing=3.0)
        assert_valid_result(normal)
        assert_valid_result(spaced)
        assert spaced.height > normal.height

    def test_disable_ligatures(self):
        result = manimpango.render("fi fl ffi", disable_ligatures=True)
        assert_valid_result(result)


# ── Variable fonts ───────────────────────────────────────────────────────

class TestVariableFonts:
    """Tests for variable font support using AdobeVFPrototype.ttf.

    This font has two axes:
      - wght: 200–900 (weight)
      - CNTR: 0–100  (contrast)

    Note on ``variations=`` parameter and Pango backends:

    ``pango_font_description_set_variations()`` only produces visible
    results with the PangoFT2/fontconfig backend (default on Linux).

    On macOS, the PangoCoreText backend stores the variations string
    in the font key and passes it to ``cairo_font_options_set_variations()``,
    but the underlying ``CTFontCreateWithFontDescriptor()`` call does not
    apply them (Pango source: ``pangocoretext-fontmap.c`` line ~1601
    explicitly warns "variations are ignored" in ``reload_font``).  Cairo's
    Quartz font backend also does not read the variations option.

    The ``weight=`` parameter works on all platforms because Pango maps it
    through each backend's native font matching (CoreText understands weight
    natively).

    On macOS with Homebrew Pango, setting ``PANGOCAIRO_BACKEND=fc`` forces
    the fontconfig backend and makes ``variations=`` work.
    """

    FONT_NAME = "Adobe Variable Font Prototype"

    @pytest.fixture(autouse=True)
    def register_variable_font(self):
        """Ensure the variable font is properly registered for testing."""
        font_path = str(FONT_DIR / "AdobeVFPrototype.ttf")
        manimpango.register_font(font_path)
        yield
        manimpango.unregister_font(font_path)

    def test_variations_dict(self):
        result = manimpango.render(
            "Variable",
            font=self.FONT_NAME,
            variations={"wght": 650},
        )
        assert_valid_result(result)

    def test_variations_multiple_axes(self):
        result = manimpango.render(
            "Multi-axis",
            font=self.FONT_NAME,
            variations={"wght": 500, "CNTR": 50},
        )
        assert_valid_result(result)

    def test_continuous_weight(self):
        result = manimpango.render(
            "Weight 450",
            font=self.FONT_NAME,
            weight=450,
        )
        assert_valid_result(result)

    @pytest.mark.xfail(
        sys.platform != "linux",
        reason="Font variations are not supported on non-fontconfig backends (macOS CoreText, Windows)",
    )
    def test_variations_wght_produces_different_svg(self):
        """Changing the wght axis via variations= produces different glyphs."""
        light = manimpango.render(
            "Test", font=self.FONT_NAME, variations={"wght": 200},
        )
        heavy = manimpango.render(
            "Test", font=self.FONT_NAME, variations={"wght": 900},
        )
        assert_valid_result(light)
        assert_valid_result(heavy)
        assert light.svg != heavy.svg

    @pytest.mark.xfail(
        sys.platform != "linux",
        reason="Font variations are not supported on non-fontconfig backends (macOS CoreText, Windows)",
    )
    def test_variations_cntr_produces_different_svg(self):
        """Changing the CNTR axis via variations= produces different glyphs."""
        low = manimpango.render(
            "Test", font=self.FONT_NAME, variations={"wght": 900, "CNTR": 0},
        )
        high = manimpango.render(
            "Test", font=self.FONT_NAME, variations={"wght": 900, "CNTR": 100},
        )
        assert_valid_result(low)
        assert_valid_result(high)
        assert low.svg != high.svg

    def test_weight_param_produces_different_svg(self):
        """The weight= parameter affects rendering on all platforms."""
        light = manimpango.render("Test", font=self.FONT_NAME, weight=200)
        heavy = manimpango.render("Test", font=self.FONT_NAME, weight=900)
        assert_valid_result(light)
        assert_valid_result(heavy)
        assert light.svg != heavy.svg


# ── RenderedText object ──────────────────────────────────────────────────

class TestRenderedText:
    def test_svg_property(self):
        result = manimpango.render("Test")
        assert isinstance(result.svg, str)
        assert "svg" in result.svg.lower()

    def test_dimensions(self):
        result = manimpango.render("Test")
        assert isinstance(result.width, float)
        assert isinstance(result.height, float)
        assert result.width > 0
        assert result.height > 0

    def test_baseline(self):
        result = manimpango.render("Test")
        assert isinstance(result.baseline, int)
        assert result.baseline > 0

    def test_line_count(self):
        result = manimpango.render("A\nB\nC")
        assert result.line_count == 3

    def test_lines_info(self):
        result = manimpango.render("Line A\nLine B")
        assert len(result.lines) == 2
        for line in result.lines:
            assert isinstance(line, LineInfo)
            assert isinstance(line.start_index, int)
            assert isinstance(line.width, float)
            assert isinstance(line.height, float)

    def test_line_start_indices(self):
        result = manimpango.render("ABC\nDEF\nGHI")
        assert result.lines[0].start_index == 0
        # "ABC\n" is 4 bytes, so line 2 starts at 4
        assert result.lines[1].start_index == 4
        # "ABC\nDEF\n" is 8 bytes, so line 3 starts at 8
        assert result.lines[2].start_index == 8

    def test_line_height(self):
        result = manimpango.render("Test")
        assert result.line_height > 0

    def test_line_height_multiline(self):
        result = manimpango.render("A\nB\nC")
        assert result.line_height > 0

    def test_str_returns_svg(self):
        result = manimpango.render("Test")
        assert str(result) == result.svg

    def test_repr(self):
        result = manimpango.render("Test")
        r = repr(result)
        assert "RenderedText" in r
        assert "line(s)" in r
        assert "baseline=" in r

    def test_save(self, tmp_path):
        out = tmp_path / "test.svg"
        result = manimpango.render("Hello")
        result.save(str(out))
        assert out.exists()
        assert out.read_text() == result.svg

    def test_save_creates_parents(self, tmp_path):
        out = tmp_path / "a" / "b" / "c" / "test.svg"
        result = manimpango.render("Hello")
        result.save(str(out))
        assert out.exists()

    def test_save_pathlib(self, tmp_path):
        out = tmp_path / "test.svg"
        result = manimpango.render("Hello")
        result.save(out)
        assert out.exists()


# ── validate_markup ──────────────────────────────────────────────────────

class TestValidateMarkup:
    def test_valid_simple(self):
        assert manimpango.validate_markup("<b>ok</b>") == ""

    def test_valid_nested(self):
        assert manimpango.validate_markup("<b><i>ok</i></b>") == ""

    def test_valid_span(self):
        assert manimpango.validate_markup("<span color='red'>ok</span>") == ""

    def test_valid_plain_text(self):
        assert manimpango.validate_markup("just text") == ""

    def test_valid_unicode(self):
        assert manimpango.validate_markup("வணக்கம்") == ""

    def test_invalid_unclosed(self):
        error = manimpango.validate_markup("<b>bad")
        assert error != ""

    def test_invalid_mismatched(self):
        error = manimpango.validate_markup("<b><i>bad</b></i>")
        assert error != ""

    def test_invalid_unknown_entity(self):
        error = manimpango.validate_markup("&badentity;")
        assert error != ""
