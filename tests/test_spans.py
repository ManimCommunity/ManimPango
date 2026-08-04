"""Contracts for v1 structured plain-text styling."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

import manimpango
from manimpango._spans import normalize_spans

FONT_DIR = Path(__file__).parent / "fonts"


def text_span(**kwargs):
    """Fetch lazily so a missing public export is reported as a test failure."""
    return manimpango.TextSpan(**kwargs)


def test_text_span_is_a_frozen_slotted_public_value_object():
    span = text_span(start=1, end=3, foreground="#ff0000")

    assert dataclasses.is_dataclass(span)
    assert getattr(type(span), "__slots__", None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        span.start = 0


def test_text_span_mapping_attributes_are_immutable_snapshots():
    features = {"kern": True}
    variations = {"wght": 650.0}

    span = text_span(
        start=0,
        end=1,
        features=features,
        variations=variations,
    )
    features["kern"] = False
    variations["wght"] = 300.0

    assert span.features == {"kern": True}
    assert span.variations == {"wght": 650.0}
    assert span == text_span(
        start=0,
        end=1,
        features={"kern": True},
        variations={"wght": 650.0},
    )
    with pytest.raises(TypeError):
        span.features["kern"] = False
    with pytest.raises(TypeError):
        span.variations["wght"] = 300.0


def test_text_span_invalid_mapping_values_remain_render_time_errors():
    span = text_span(start=0, end=1, features=[("kern", True)])

    with pytest.raises(TypeError, match="mapping"):
        manimpango.render("a", spans=(span,))


def test_span_offsets_are_half_open_python_code_point_offsets():
    text = "AéB"
    span = text_span(start=1, end=2, weight=700)

    result = manimpango.render(text, spans=(span,))

    assert result.lines[0].text[span.start : span.end] == "é"


@pytest.mark.parametrize("font", ["\0family", "family\0suffix", "family\0"])
def test_span_font_rejects_embedded_nul(font):
    span = text_span(start=0, end=1, font=font)

    with pytest.raises(ValueError, match="NUL"):
        manimpango.render("a", spans=(span,))


@pytest.mark.parametrize("foreground", ["\0red", "red\0suffix", "red\0"])
def test_span_foreground_rejects_embedded_nul(foreground):
    span = text_span(start=0, end=1, foreground=foreground)

    with pytest.raises(ValueError, match="NUL"):
        manimpango.render("a", spans=(span,))


@pytest.mark.parametrize("tag", ["liga\0", "liga\n", "liga\t", "lig\x1f"])
def test_span_features_reject_control_character_tags(tag):
    span = text_span(start=0, end=1, features={tag: True})

    with pytest.raises(ValueError, match="printable ASCII"):
        manimpango.render("a", spans=(span,))


def test_spans_preserve_plain_special_characters_without_markup_escaping():
    text = "A & B < C"
    result = manimpango.render(
        text,
        spans=(text_span(start=2, end=3, foreground="#cc0000"),),
        disable_ligatures=True,
    )

    assert result.width > 0
    assert result.lines[0].text == text


def test_disable_ligatures_overrides_conflicting_span_features():
    """The global option must win over a span that enables Fira Code calt."""
    text = "-> != ==="
    span = text_span(start=0, end=len(text), features={"calt": True})
    with manimpango.register_font(FONT_DIR / "FiraCode-Regular.ttf"):
        common = {"font": "Fira Code"}
        enabled = manimpango.render(text, spans=(span,), **common)
        disabled = manimpango.render(text, disable_ligatures=True, **common)
        overridden = manimpango.render(
            text,
            spans=(span,),
            disable_ligatures=True,
            **common,
        )

    assert enabled.svg != disabled.svg
    assert overridden.svg == disabled.svg


@pytest.mark.parametrize(
    "start,end",
    [(-1, 1), (0, 4), (2, 1), (1.0, 2)],
)
def test_span_bounds_must_be_valid_python_string_indexes(start, end):
    with pytest.raises((TypeError, ValueError)):
        manimpango.render("abc", spans=(text_span(start=start, end=end),))


def test_conflicting_overlapping_span_values_are_rejected_without_precedence():
    spans = (
        text_span(start=0, end=2, foreground="#ff0000"),
        text_span(start=1, end=3, foreground="#0000ff"),
    )

    with pytest.raises(ValueError, match="conflict|overlap"):
        manimpango.render("abc", spans=spans)


def test_span_normalization_composes_overlaps_into_effective_byte_runs():
    text = "AéBC"
    spans = (
        text_span(start=0, end=4, font="Example Sans"),
        text_span(start=1, end=3, weight=700),
        text_span(start=1, end=4, features={"kern": True}),
        text_span(start=2, end=3, variations={"wght": 650.0}),
    )

    expected = (
        {"start": 0, "end": 1, "font": "Example Sans"},
        {
            "start": 1,
            "end": 3,
            "font": "Example Sans",
            "weight": 700,
            "features": {"kern": True},
        },
        {
            "start": 3,
            "end": 4,
            "font": "Example Sans",
            "weight": 700,
            "features": {"kern": True},
            "variations": {"wght": 650.0},
        },
        {
            "start": 4,
            "end": 5,
            "font": "Example Sans",
            "features": {"kern": True},
        },
    )
    assert normalize_spans(spans, text) == expected
    assert normalize_spans(tuple(reversed(spans)), text) == expected


@pytest.mark.parametrize(
    "attribute,first_value,second_value",
    [
        ("foreground", "#ff0000", "#0000ff"),
        ("features", {"kern": True}, {"kern": False}),
        ("variations", {"wght": 400.0}, {"wght": 700.0}),
    ],
)
def test_span_conflicts_are_independent_of_input_order(
    attribute, first_value, second_value
):
    first = text_span(start=0, end=2, **{attribute: first_value})
    second = text_span(start=1, end=3, **{attribute: second_value})

    for spans in ((first, second), (second, first)):
        with pytest.raises(ValueError, match="conflicting overlapping TextSpan"):
            normalize_spans(spans, "abc")


def test_span_sweep_removes_ends_before_starts_and_ignores_empty_ranges():
    spans = (
        text_span(start=0, end=1, foreground="#ff0000"),
        text_span(start=1, end=2, foreground="#0000ff"),
        text_span(start=1, end=1, foreground="#00aa00"),
    )

    assert normalize_spans(spans, "ab") == (
        {"start": 0, "end": 1, "foreground": "#ff0000"},
        {"start": 1, "end": 2, "foreground": "#0000ff"},
    )


def test_span_sweep_merges_adjacent_equivalent_runs():
    spans = (
        text_span(start=0, end=1, weight=700),
        text_span(start=1, end=2, weight=700),
    )

    assert normalize_spans(spans, "ab") == ({"start": 0, "end": 2, "weight": 700},)


@pytest.mark.parametrize("count", [500, 1_000, 2_000, 4_000])
def test_many_adjacent_spans_normalize_to_one_run(count):
    """A scalable correctness probe; timing belongs in ``benchmarks/``."""
    text = "x" * count
    spans = tuple(
        text_span(start=index, end=index + 1, weight=700) for index in range(count)
    )

    assert normalize_spans(spans, text) == ({"start": 0, "end": count, "weight": 700},)


def test_disjoint_span_attributes_compose():
    result = manimpango.render(
        "abc",
        spans=(
            text_span(start=0, end=2, weight=700),
            text_span(start=1, end=3, foreground="#00aa00"),
        ),
    )

    assert result.width > 0


@pytest.mark.parametrize("style", [manimpango.Style.ITALIC, manimpango.Style.OBLIQUE])
def test_top_level_and_span_styles_use_the_same_pango_slant(style):
    """Both public styling paths must preserve the Pango ``Style`` value."""
    text = "Hamburgefons"
    with manimpango.register_font(FONT_DIR / "AdobeVFPrototype.ttf"):
        common = {"font": "Adobe Variable Font Prototype"}
        normal = manimpango.render(text, **common)
        top_level = manimpango.render(text, style=style, **common)
        span = manimpango.render(
            text,
            spans=(text_span(start=0, end=len(text), style=style),),
            **common,
        )

    assert top_level.svg != normal.svg
    assert span.svg == top_level.svg
