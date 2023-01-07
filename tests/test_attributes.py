# -*- coding: utf-8 -*-
import pytest

from manimpango import TextAttribute


@pytest.mark.parametrize("values", [(1.0, 2), (1, 2.0), (1.0, 2.0)])
def test_attributes_accepts_only_int(values):
    with pytest.raises(ValueError):
        TextAttribute(*values)


def test_start_index():
    _a = TextAttribute()
    assert _a.start_index == 0
    _a.start_index = 5
    assert _a.start_index == 5


def test_end_index():
    _a = TextAttribute()
    assert _a.end_index == -1
    _a.end_index = 5
    assert _a.end_index == 5


def test_allow_breaks_attribute():
    _a = TextAttribute()
    assert _a.allow_breaks is None
    _a.allow_breaks = False
    assert _a.allow_breaks is False
    _a.allow_breaks = 1
    assert _a.allow_breaks is True


def test_background_alpha():
    _a = TextAttribute()
    assert _a.background_alpha is None
    with pytest.raises(ValueError):
        _a.background_alpha = 5
    _a.background_alpha = 0.6
    assert _a.background_alpha == 0.6


def test_background_color():
    _a = TextAttribute()
    assert _a.background_color is None
    with pytest.raises(ValueError):
        _a.background_color = "#ppppppppppppppppppppppppppppps"
    _a.background_color = "#ffffff"
    assert _a.background_color == (65535, 65535, 65535)
    _a.background_color = (0, 0, 0)
    assert _a.background_color == (0, 0, 0)
    with pytest.raises(ValueError):
        _a.background_color = (0,)
    with pytest.raises(ValueError):
        _a.background_color = (-1, 0, 0)


def test_foreground_alpha():
    _a = TextAttribute()
    assert _a.foreground_alpha is None
    with pytest.raises(ValueError):
        _a.foreground_alpha = 5
    _a.foreground_alpha = 0.6
    assert _a.foreground_alpha == 0.6


def test_foreground_color():
    _a = TextAttribute()
    assert _a.foreground_color is None
    with pytest.raises(ValueError):
        _a.foreground_color = "#ppppppppppppppppppppppppppppps"
    _a.foreground_color = "#ffffff"
    assert _a.foreground_color == (65535, 65535, 65535)
    _a.foreground_color = (0, 0, 0)
    assert _a.foreground_color == (0, 0, 0)
    with pytest.raises(ValueError):
        _a.foreground_color = (0,)
    with pytest.raises(ValueError):
        _a.foreground_color = (-1, 0, 0)


def test_fallback():
    _a = TextAttribute()
    assert _a.fallback is None
    _a.fallback = 1
    assert _a.fallback is True
    _a.fallback = False
    assert _a.fallback is False


def test_family():
    _a = TextAttribute()
    assert _a.family is None
    _a.family = "hello"
    assert _a.family == "hello"
    with pytest.raises(ValueError):
        _a.family = []
