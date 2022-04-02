# -*- coding: utf-8 -*-
import pytest

from manimpango import Alignment, Layout
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


def test_alignment():
    _a = Layout("hello")
    assert _a.alignment is None
    _a.alignment = Alignment.LEFT
    assert _a.alignment == Alignment.LEFT
    with pytest.raises(TypeError):
        _a.alignment = 2
