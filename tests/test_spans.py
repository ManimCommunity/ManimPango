"""Contracts for v1 structured plain-text styling."""

from __future__ import annotations

import dataclasses

import pytest

import manimpango


def text_span(**kwargs):
    """Fetch lazily so a missing public export is reported as a test failure."""
    return manimpango.TextSpan(**kwargs)


def test_text_span_is_a_frozen_slotted_public_value_object():
    span = text_span(start=1, end=3, foreground="#ff0000")

    assert dataclasses.is_dataclass(span)
    assert getattr(type(span), "__slots__", None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        span.start = 0


def test_span_offsets_are_half_open_python_code_point_offsets():
    text = "AéB"
    span = text_span(start=1, end=2, weight=700)

    result = manimpango.render(text, spans=(span,))

    assert result.lines[0].text[span.start : span.end] == "é"


def test_spans_preserve_plain_special_characters_without_markup_escaping():
    text = "A & B < C"
    result = manimpango.render(
        text,
        spans=(text_span(start=2, end=3, foreground="#cc0000"),),
        disable_ligatures=True,
    )

    assert result.width > 0
    assert result.lines[0].text == text


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


def test_disjoint_span_attributes_compose():
    result = manimpango.render(
        "abc",
        spans=(
            text_span(start=0, end=2, weight=700),
            text_span(start=1, end=3, foreground="#00aa00"),
        ),
    )

    assert result.width > 0
