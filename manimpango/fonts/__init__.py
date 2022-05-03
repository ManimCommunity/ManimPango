# -*- coding: utf-8 -*-
"""This module contains the definition of :class:`FontDescription`,
and other enums related to it.
"""
from __future__ import annotations

__all__ = ["FontDescription", "Style", "Weight", "Variant"]
from ._font_desc import _FontDescription
from .enums import Style, Variant, Weight


class FontDescription:
    """A :class:`FontDescription` describes a font.

    This describes the characteristics of a font to load.

    Parameters
    ----------
    family:
        Sets :attr:`family`.
    size:
        Sets :attr:`size`.
    style:
        Sets :attr:`style`.
    weight:
        Sets :attr:`weight`.
    variant:
        Sets :attr:`variant`.

    Attributes
    ----------
    _font_desc:
        Reference to the C-implementation of
        font description.
    """

    _font_desc: _FontDescription

    def __init__(
        self,
        family: str = None,
        size: int = None,
        style: Style = None,
        weight: Weight = None,
        variant: Variant = None,
    ):
        self._font_desc = _FontDescription(
            family=family,
            size=size,
            style=style,
            weight=weight,
            variant=variant,
        )

    @property
    def family(self) -> str:
        """The family name of the font.

        The family name represents a family of related font styles,
        and will resolve to a particular family. It is also
        possible to use a comma separated list of family names for
        this field.
        """
        return self._font_desc.family

    @family.setter
    def family(self, family: str) -> None:
        self._font_desc.family = family

    @property
    def size(self) -> int:
        """The size of the font of the text."""
        return self._font_desc.size

    @size.setter
    def size(self, size: int):
        self._font_desc.size = size

    @property
    def style(self) -> Style:
        """The style of the font of the text.

        It should be one of :class:`.Style`. Most fonts will either have a
        italic style or an oblique style, but not both, and font matching
        in Pango will match italic specifications with oblique fonts and
        vice-versa if an exact match is not found.
        """
        return self._font_desc.style

    @style.setter
    def style(self, style: Style):
        self._font_desc.style = style

    @property
    def weight(self) -> Weight:
        """The weight of the font of the text.

        The weight field specifies how bold or light the font should be.
        Should be one of :class:`.Weight`.
        """
        return self._font_desc.weight

    @weight.setter
    def weight(self, weight: Weight):
        self._font_desc.weight = weight

    @property
    def variant(self):
        """The variant of the font of the text.

        Should be one of :class:`.Variant`.
        """
        return self._font_desc.variant

    @variant.setter
    def variant(self, variant):
        self._font_desc.variant = variant

    @classmethod
    def from_string(cls, string: str):
        """Parse a string and form :class:`FontDescription` from it.

        See
        https://docs.gtk.org/Pango/type_func.FontDescription.from_string.html#description
        for the syntax of the string.

        Parameters
        ----------
        string : str
            The string to be parsed.

        Returns
        -------
        FontDescription
            The :class:`FontDescription` that is based on the string.
        """
        _t = FontDescription()
        _t._font_desc = _FontDescription.from_string(string)
        return _t

    def __repr__(self):
        return repr(self._font_desc)

    def __str__(self):
        return repr(self._font_desc)

    def __eq__(self, other: FontDescription):
        return self._font_desc == other._font_desc

    def __deepcopy__(self, memo):
        _a = FontDescription()
        _a._font_desc = self._font_desc.__deepcopy__(memo)
        return _a
