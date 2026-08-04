"""Validation and exception contracts at the Python public boundary."""

from __future__ import annotations

import math

import pytest

import manimpango


@pytest.mark.parametrize("text", [None, 12, b"text"])
def test_render_rejects_non_string_text_before_native_rendering(text):
    with pytest.raises(TypeError):
        manimpango.render(text)


@pytest.mark.parametrize("text", ["\0text", "text\0suffix", "text\0"])
def test_render_rejects_embedded_nul_literal_text(text):
    with pytest.raises(ValueError, match="NUL"):
        manimpango.render(text)


@pytest.mark.parametrize("font", ["\0family", "family\0suffix", "family\0"])
def test_render_rejects_embedded_nul_font_family(font):
    with pytest.raises(ValueError, match="NUL"):
        manimpango.render("text", font=font)


@pytest.mark.parametrize("size", [0, -1, math.inf, -math.inf, math.nan])
def test_render_rejects_non_positive_or_non_finite_sizes(size):
    with pytest.raises(ValueError):
        manimpango.render("text", size=size)


@pytest.mark.parametrize("width", [0, -1, math.inf, math.nan])
def test_render_rejects_invalid_layout_widths(width):
    with pytest.raises(ValueError):
        manimpango.render("text", width=width)


@pytest.mark.parametrize("line_spacing", [0, -1, math.inf, math.nan])
def test_render_rejects_invalid_line_spacing(line_spacing):
    with pytest.raises(ValueError):
        manimpango.render("text", line_spacing=line_spacing)


@pytest.mark.parametrize("indent", [math.inf, -math.inf, math.nan])
def test_render_rejects_non_finite_indent(indent):
    with pytest.raises(ValueError):
        manimpango.render("text", indent=indent)


@pytest.mark.parametrize("weight", [True, False, 0, 1001, 1.5])
def test_render_rejects_invalid_weights(weight):
    with pytest.raises((TypeError, ValueError)):
        manimpango.render("text", weight=weight)


@pytest.mark.parametrize("keyword,value", [("style", 0), ("alignment", "left")])
def test_render_requires_public_enum_instances(keyword, value):
    with pytest.raises(TypeError):
        manimpango.render("text", **{keyword: value})


@pytest.mark.parametrize(
    "variations",
    [
        {"bad": 1.0},
        {"wght!": 1.0},
        {"wgéé": 1.0},
        {"wght": math.inf},
        {"wght": math.nan},
    ],
)
def test_render_validates_opentype_axis_tags_and_values(variations):
    with pytest.raises((TypeError, ValueError)):
        manimpango.render("text", variations=variations)


@pytest.mark.parametrize("tag", ["wg\0t", "wg\nt", "wg\tt", "wg\x1ft"])
def test_render_rejects_control_characters_in_variation_tags(tag):
    with pytest.raises(ValueError, match="printable ASCII"):
        manimpango.render("text", variations={tag: 500})


def test_public_exception_hierarchy_is_package_specific():
    assert issubclass(manimpango.RenderError, manimpango.ManimPangoError)
    assert issubclass(manimpango.MarkupError, (ValueError, manimpango.ManimPangoError))
    assert issubclass(manimpango.FontError, manimpango.ManimPangoError)
    assert issubclass(
        manimpango.FontNotFoundError, (FileNotFoundError, manimpango.FontError)
    )
    assert issubclass(manimpango.FontRegistrationError, manimpango.FontError)


@pytest.mark.parametrize(
    ("entry_point", "arguments"),
    [
        (manimpango.render, ("text",)),
        (manimpango.render_markup, ("<b>text</b>",)),
    ],
)
def test_native_render_failures_raise_render_error(monkeypatch, entry_point, arguments):
    native_error = RuntimeError("Cairo error: out of memory")

    def fail_render(*args, **options):
        raise native_error

    monkeypatch.setattr(manimpango._render, "render", fail_render)

    with pytest.raises(manimpango.RenderError, match="Cairo error") as error:
        entry_point(*arguments)

    assert error.value.__cause__ is native_error


def test_validation_errors_are_not_translated_to_render_error():
    with pytest.raises(ValueError) as error:
        manimpango.render("text", size=0)

    assert not isinstance(error.value, manimpango.RenderError)


def test_render_markup_is_a_separate_entry_point_and_invalid_markup_raises_markup_error():
    assert callable(manimpango.render_markup)
    with pytest.raises((manimpango.MarkupError, ValueError)):
        manimpango.render_markup("<b>unclosed")


@pytest.mark.parametrize(
    "markup", ["\0<b>text</b>", "<b>text</b>\0<b>bad", "<b>text</b>\0"]
)
def test_validate_markup_reports_embedded_nul_deterministically(markup):
    assert (
        manimpango.validate_markup(markup) == "markup must not contain NUL characters"
    )


@pytest.mark.parametrize(
    "markup", ["\0<b>text</b>", "<b>text</b>\0<b>bad", "<b>text</b>\0"]
)
def test_render_markup_turns_embedded_nul_diagnostic_into_markup_error(markup):
    with pytest.raises(manimpango.MarkupError, match="NUL"):
        manimpango.render_markup(markup)


def test_invalid_markup_does_not_emit_native_warnings_to_stderr(capfd):
    with pytest.raises((manimpango.MarkupError, ValueError)):
        manimpango.render_markup("<b>unclosed")

    assert capfd.readouterr().err == ""
