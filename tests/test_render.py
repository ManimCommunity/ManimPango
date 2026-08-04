"""Tests for manimpango.render() — the core v2 API."""

import sys
from pathlib import Path
from xml.parsers.expat import ParserCreate

import pytest

import manimpango
from manimpango import Alignment, Bounds, MarkupError, Style, Weight
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
    assert isinstance(result.width, float)
    assert isinstance(result.height, float)
    assert isinstance(result.baseline, float)
    assert result.width > 0
    assert result.height > 0
    assert result.baseline > 0
    assert result.line_count >= 1
    assert isinstance(result.lines, tuple)
    assert len(result.lines) == result.line_count
    assert isinstance(result.ink_bounds, Bounds)
    assert isinstance(result.logical_bounds, Bounds)
    assert isinstance(result.svg, str)
    assert len(result.svg) > 0
    assert_valid_svg(result.svg)


def assert_svg_has_visible_drawing(svg: str) -> None:
    """Cairo SVG glyph output uses definitions plus ``<use>`` operations."""
    assert "<use" in svg or "<path" in svg, "nonempty text must draw glyphs"


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
        result = manimpango.render_markup("<b>Bold</b>")
        assert_valid_result(result)
        assert result.lines[0].text == "Bold"

    def test_italic_markup(self):
        result = manimpango.render_markup("<i>Italic</i>")
        assert_valid_result(result)

    def test_color_markup(self):
        result = manimpango.render_markup(
            "<span color='red'>Red</span> and <span color='blue'>Blue</span>",
        )
        assert_valid_result(result)
        assert result.lines[0].text == "Red and Blue"

    def test_nested_markup(self):
        result = manimpango.render_markup(
            "<b><i>Bold Italic</i></b>",
        )
        assert_valid_result(result)

    def test_invalid_markup_raises_markup_error(self):
        with pytest.raises(MarkupError, match="[Mm]arkup"):
            manimpango.render_markup("<b>unclosed")

    def test_invalid_markup_unmatched_tag(self):
        with pytest.raises(MarkupError):
            manimpango.render_markup("<b><i>mismatched</b></i>")

    def test_markup_with_ampersand(self):
        result = manimpango.render_markup("A &amp; B")
        assert_valid_result(result)
        assert result.lines[0].text == "A & B"

    def test_plain_text_with_angle_brackets(self):
        """Plain text mode should NOT interpret markup."""
        result = manimpango.render("<b>not bold</b>")
        assert_valid_result(result)
        assert result.lines[0].text == "<b>not bold</b>"


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

    @pytest.mark.parametrize("alignment", [Alignment.CENTER, Alignment.RIGHT])
    def test_wide_layout_alignment_keeps_short_text_visible(self, alignment):
        result = manimpango.render("Test", width=200, alignment=alignment)

        assert_svg_has_visible_drawing(result.svg)

    def test_plain_special_characters_with_ligatures_disabled_remain_plain_text(self):
        result = manimpango.render("A & B < C", disable_ligatures=True)

        assert result.width > 0
        assert_svg_has_visible_drawing(result.svg)

    def test_markup_with_ligatures_disabled_remains_valid(self):
        result = manimpango.render_markup(
            "<b>A &amp; B</b>",
            disable_ligatures=True,
        )

        assert result.width > 0
        assert_svg_has_visible_drawing(result.svg)

    def test_disable_ligatures_overrides_markup_font_features(self):
        """The global option must also override Pango markup attributes."""
        text = "-> != ==="
        markup = f'<span font_features="calt=1">{text}</span>'
        with manimpango.register_font(FONT_DIR / "FiraCode-Regular.ttf"):
            common = {"font": "Fira Code"}
            enabled = manimpango.render_markup(markup, **common)
            disabled = manimpango.render_markup(
                markup,
                disable_ligatures=True,
                **common,
            )
            plain_disabled = manimpango.render(
                text,
                disable_ligatures=True,
                **common,
            )

        assert enabled.svg != disabled.svg
        assert disabled.svg == plain_disabled.svg


# ── Variable fonts ───────────────────────────────────────────────────────


class TestVariableFonts:
    """Tests for variable font support using AdobeVFPrototype.ttf.

    This font has two axes:
      - wght: 200–900 (weight)
      - CNTR: 0–100  (contrast)

    ManimPango forwards variation settings to Pango, while visible effects
    remain axis-, font-, and backend-specific.  The fixture's ``wght`` axis
    currently changes output on Linux, macOS, and Windows.  Its ``CNTR`` axis
    currently changes output on Linux and Windows, but not through the
    current macOS Pango/CoreText/Cairo stack.  This is a fixture-and-renderer
    observation, not a general CoreText limitation.
    """

    FONT_NAME = "Adobe Variable Font Prototype"

    @pytest.fixture(autouse=True)
    def register_variable_font(self):
        """Ensure the variable font is properly registered for testing."""
        with manimpango.register_font(
            FONT_DIR / "AdobeVFPrototype.ttf"
        ) as registration:
            yield registration

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

    def test_variations_wght_produces_different_svg(self):
        """Changing the wght axis via variations= produces different glyphs."""
        light = manimpango.render(
            "Test",
            font=self.FONT_NAME,
            variations={"wght": 200},
        )
        heavy = manimpango.render(
            "Test",
            font=self.FONT_NAME,
            variations={"wght": 900},
        )
        assert_valid_result(light)
        assert_valid_result(heavy)
        assert light.svg != heavy.svg

    @pytest.mark.xfail(
        sys.platform == "darwin",
        strict=True,
        reason="The current macOS Pango/CoreText/Cairo stack does not visibly "
        "apply the Adobe fixture's CNTR variation axis",
    )
    def test_variations_cntr_produces_different_svg(self):
        """Changing the CNTR axis via variations= produces different glyphs."""
        low = manimpango.render(
            "Test",
            font=self.FONT_NAME,
            variations={"wght": 900, "CNTR": 0},
        )
        high = manimpango.render(
            "Test",
            font=self.FONT_NAME,
            variations={"wght": 900, "CNTR": 100},
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
        assert isinstance(result.baseline, float)
        assert result.baseline > 0

    def test_line_count(self):
        result = manimpango.render("A\nB\nC")
        assert result.line_count == 3

    def test_lines_info(self):
        result = manimpango.render("Line A\nLine B")
        assert len(result.lines) == 2
        for line in result.lines:
            assert isinstance(line, LineInfo)
            assert isinstance(line.start, int)
            assert isinstance(line.end, int)
            assert isinstance(line.bounds, Bounds)
            assert isinstance(line.baseline, float)

    def test_line_start_indices(self):
        result = manimpango.render("ABC\nDEF\nGHI")
        assert [(line.start, line.end) for line in result.lines] == [
            (0, 3),
            (4, 7),
            (8, 11),
        ]

    def test_str_returns_svg(self):
        result = manimpango.render("Test")
        assert str(result) == result.svg

    def test_repr(self):
        result = manimpango.render("Test")
        r = repr(result)
        assert "RenderedText" in r
        assert "baseline=" in r

    def test_save(self, tmp_path):
        out = tmp_path / "test.svg"
        result = manimpango.render("Hello")
        result.save(str(out))
        assert out.exists()
        assert out.read_text() == result.svg

    def test_save_requires_existing_parent(self, tmp_path):
        out = tmp_path / "a" / "b" / "c" / "test.svg"
        result = manimpango.render("Hello")
        with pytest.raises(FileNotFoundError):
            result.save(str(out))

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
