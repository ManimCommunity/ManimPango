# -*- coding: utf-8 -*-
from manimpango import FontProperties


def test_init():
    FontProperties()


def test_family_property():
    desc = FontProperties()
    assert desc.family is None
    desc.family = "Roboto"
    assert desc.family == "Roboto"


def test_size_property():
    desc = FontProperties()
    assert desc.size is None
    desc.size = 20
    assert desc.size == 20
