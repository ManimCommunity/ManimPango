# -*- coding: utf-8 -*-
import pytest

from manimpango.enums import Style, Weight
from manimpango.utils import PangoUtils


def test_str2style():
    p = PangoUtils()

    assert p.str2style("NORMAL") == Style.NORMAL
    assert p.str2style("ITALIC") == Style.ITALIC
    assert p.str2style("OBLIQUE") == Style.OBLIQUE

    with pytest.raises(AttributeError) as exc_info:
        p.str2style("DNE")
    exception_raised = exc_info.value
    assert "There is no Style Called DNE" == str(exception_raised)


def test_str2weight():
    p = PangoUtils()

    assert p.str2weight("NORMAL") == Weight.NORMAL
    assert p.str2weight("BOLD") == Weight.BOLD
    assert p.str2weight("THIN") == Weight.THIN
    assert p.str2weight("THIN") == Weight.THIN
    assert p.str2weight("ULTRALIGHT") == Weight.ULTRALIGHT
    assert p.str2weight("LIGHT") == Weight.LIGHT
    assert p.str2weight("BOOK") == Weight.BOOK
    assert p.str2weight("MEDIUM") == Weight.MEDIUM
    assert p.str2weight("SEMIBOLD") == Weight.SEMIBOLD
    assert p.str2weight("ULTRABOLD") == Weight.ULTRABOLD
    assert p.str2weight("HEAVY") == Weight.HEAVY
    assert p.str2weight("ULTRAHEAVY") == Weight.ULTRAHEAVY

    with pytest.raises(AttributeError) as exc_info:
        p.str2weight("DNE")
    exception_raised = exc_info.value
    assert "There is no Font Weight Called DNE" == str(exception_raised)
