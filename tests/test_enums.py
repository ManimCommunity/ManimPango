# -*- coding: utf-8 -*-
"""Tests for enums module."""

from manimpango.enums import Alignment, Style, Weight


class TestStyle:
    def test_values(self):
        assert Style.NORMAL.value == 0
        assert Style.ITALIC.value == 1
        assert Style.OBLIQUE.value == 2

    def test_members(self):
        assert len(Style) == 3


class TestWeight:
    def test_standard_values(self):
        assert Weight.THIN == 100
        assert Weight.ULTRALIGHT == 200
        assert Weight.LIGHT == 300
        assert Weight.SEMILIGHT == 350
        assert Weight.BOOK == 380
        assert Weight.NORMAL == 400
        assert Weight.MEDIUM == 500
        assert Weight.SEMIBOLD == 600
        assert Weight.BOLD == 700
        assert Weight.ULTRABOLD == 800
        assert Weight.HEAVY == 900
        assert Weight.ULTRAHEAVY == 1000

    def test_is_int(self):
        assert isinstance(Weight.NORMAL, int)
        assert Weight.BOLD + 0 == 700

    def test_arbitrary_int(self):
        w = Weight(450)
        assert w == 450
        assert isinstance(w, int)

    def test_members(self):
        assert len(Weight) == 12


class TestAlignment:
    def test_values(self):
        assert Alignment.LEFT.value == 0
        assert Alignment.CENTER.value == 1
        assert Alignment.RIGHT.value == 2

    def test_members(self):
        assert len(Alignment) == 3
