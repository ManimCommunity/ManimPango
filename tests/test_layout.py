# -*- coding: utf-8 -*-
import pytest

from manimpango import Alignment, Layout, TextAttribute
from manimpango.exceptions import MarkupParseError


def test_layout_init():
    _a = Layout("hello")
    assert _a.text == "hello"
    assert _a.markup is None
    with pytest.raises(ValueError):
        Layout()


def test_invalid_markup():
    with pytest.raises(MarkupParseError):
        Layout(markup="<test")


def test_length_attr():
    text = "hello"
    _a = Layout(text)
    assert _a.text == text
    assert len(_a) == len(text)
    _a = Layout(markup=text)
    assert _a.markup == text
    assert len(_a) == len(text)


def test_text_and_markup_not_str():
    with pytest.raises(TypeError):
        Layout([1])
    with pytest.raises(TypeError):
        Layout(markup=[1])


def test_width_and_height():
    _a = Layout("hello")
    assert _a.width is None
    assert _a.height is None
    _a.width = 100
    assert _a.width == 100
    _a.height = 100
    assert _a.height == 100
    with pytest.raises(TypeError):
        _a.height = 9.0
    with pytest.raises(TypeError):
        _a.width = 9.0
    _b = Layout("hello", width=100, height=100)
    assert _b.width == 100
    assert _b.height == 100


def test_alignment():
    _a = Layout("hello")
    assert _a.alignment is None
    _a.alignment = Alignment.LEFT
    assert _a.alignment == Alignment.LEFT
    with pytest.raises(TypeError):
        _a.alignment = 2
    _b = Layout("hello", alignment=Alignment.LEFT)
    assert _b.alignment == Alignment.LEFT


def test_layout_with_attributes():
    _a = Layout(
        "hello",
    )
    assert _a.attributes == []
    _a = Layout("hello", attributes=[TextAttribute(0, 5)])
    assert _a.attributes[0].start_index == 0
    assert _a.attributes[0].end_index == 5


@pytest.mark.parametrize(
    "values",
    [
        [1],
        [TextAttribute(0, 5), 1],
        (1,),
        (TextAttribute(0, 5), 1),
        "hello",
    ],
)
def test_layout_attribute_parameter(values):
    with pytest.raises(TypeError):
        Layout("hi", attributes=values)
