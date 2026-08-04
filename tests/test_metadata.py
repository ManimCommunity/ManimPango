"""Public v1 result metadata contracts."""

from __future__ import annotations

import dataclasses

import pytest

import manimpango


def test_public_result_models_are_frozen_slotted_dataclasses():
    for name in ("Bounds", "LineInfo", "RenderedText"):
        model = getattr(manimpango, name)
        assert dataclasses.is_dataclass(model), f"{name} must be a dataclass"
        assert getattr(model, "__slots__", None), f"{name} must use slots"

    bounds = manimpango.Bounds(0.0, 0.0, 1.0, 1.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        bounds.width = 2.0


def test_result_metadata_uses_public_fields_and_real_missing_attributes_raise():
    result = manimpango.render("metadata")

    assert isinstance(result.lines, tuple)
    assert result.line_count == len(result.lines)
    with pytest.raises(AttributeError):
        result.wdith


def test_empty_text_has_one_empty_line_and_a_valid_nonnegative_viewport():
    result = manimpango.render("")

    assert result.line_count == 1
    assert result.lines[0].text == ""
    assert result.width >= 0.0
    assert result.height >= 0.0


def test_lines_report_actual_text_and_code_point_offsets():
    text = "é\n漢"
    result = manimpango.render(text)

    assert [(line.text, line.start, line.end) for line in result.lines] == [
        ("é", 0, 1),
        ("漢", 2, 3),
    ]


def test_line_ranges_exclude_newline_separators():
    result = manimpango.render("first\nsecond")

    assert [(line.text, line.start, line.end) for line in result.lines] == [
        ("first", 0, 5),
        ("second", 6, 12),
    ]


def test_markup_line_offsets_are_in_parsed_rendered_text():
    result = manimpango.render_markup("<b>é</b>\n<span foreground='red'>漢</span>")

    assert [(line.text, line.start, line.end) for line in result.lines] == [
        ("é", 0, 1),
        ("漢", 2, 3),
    ]


def test_line_baselines_and_bounds_use_svg_coordinate_space():
    result = manimpango.render("small\nlarge", spans=(
        manimpango.TextSpan(start=6, end=11, size=36.0),
    ))

    assert all(isinstance(value, float) for value in (result.width, result.height, result.baseline))
    assert result.lines[1].baseline > result.lines[0].baseline
    assert result.lines[1].bounds.height > result.lines[0].bounds.height
    for bounds in (result.ink_bounds, result.logical_bounds, *(line.bounds for line in result.lines)):
        assert bounds.x >= 0.0
        assert bounds.y >= 0.0
        assert bounds.x + bounds.width <= result.width
        assert bounds.y + bounds.height <= result.height


@pytest.mark.parametrize("alignment", [manimpango.Alignment.CENTER, manimpango.Alignment.RIGHT])
def test_wide_multiline_alignment_preserves_relative_line_placement(alignment):
    result = manimpango.render("x\nlonger", width=200.0, alignment=alignment)
    short, long = result.lines

    assert short.bounds.x > long.bounds.x
    if alignment is manimpango.Alignment.CENTER:
        assert short.bounds.x + short.bounds.width / 2 == pytest.approx(
            long.bounds.x + long.bounds.width / 2,
            abs=1.0,
        )
    else:
        assert short.bounds.x + short.bounds.width == pytest.approx(
            long.bounds.x + long.bounds.width,
            abs=1.0,
        )


def test_save_does_not_create_missing_parent_directories(tmp_path):
    result = manimpango.render("save contract")

    with pytest.raises(FileNotFoundError):
        result.save(tmp_path / "missing" / "result.svg")
