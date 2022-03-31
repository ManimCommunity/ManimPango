# -*- coding: utf-8 -*-
import typing as T

__all__ = ["TextAttribute"]


class TextAttribute:
    """:class:`TextAttribute` defines the properties/attributes of the
    text within a specific range of the text.


    A :class:`TextAttribute` object can define multiple properties at
    the same time, for example, it can change the :attr:`background_color`,
    as well as, :attr:`foreground_color`. Also, a :class:`TextAttribute` can
    be used for multiple times for different texts.
    By default, an attribute has an inclusive range from ``0`` to the
    end of the text ``-1``, ie. ``[0, -1]``.
    """

    def __init__(self, start_index: int = 0, end_index: int = -1) -> None:
        """Initialize :class:`TextAttribute`.

        Parameters
        ----------
        start_index : int, optional
            The start index of the range, by default 0 (start of the string).
        end_index : int, optional
            End index of the range. The character at this index is not included
            in the range, by default -1 (end of the string).
        """
        self.start_index = start_index
        self.end_index = end_index

    @property
    def start_index(self) -> int:
        """It is the end index of the range.

        Raises
        ------
        ValueError
            If the value is not an :class:`int`.
        """
        return self._start_index

    @start_index.setter
    def start_index(self, val: int) -> None:
        if not isinstance(val, int):
            raise ValueError("'start_index' should be an int")
        self._start_index = val

    @property
    def end_index(self) -> int:
        """It is the start of the range. The character at this index is not
        included in the range.

        Raises
        ------
        ValueError
            If the value is not an :class:`int`.
        """
        return self._end_index

    @end_index.setter
    def end_index(self, val: int) -> None:
        if not isinstance(val, int):
            raise ValueError("'end_index' should be an int")
        self._end_index = val

    @property
    def allow_breaks(self) -> T.Union[bool, None]:
        """Whether to break text or not.

        If breaks are disabled, the range will be kept in a single run,
        as far as possible.
        """
        if hasattr(self, "_allow_breaks"):
            return self._allow_breaks
        return None

    @allow_breaks.setter
    def allow_breaks(self, val: bool) -> None:
        self._allow_breaks = bool(val)

    @property
    def background_alpha(self) -> float:
        """The background_alpha of the text.

        Raises
        ------
        ValueError
            If the value is not between 0 and 1.
        """
        if hasattr(self, "_background_alpha"):
            return self._background_alpha
        return None

    @background_alpha.setter
    def background_alpha(self, val: float) -> None:
        if not (0 <= val <= 1):
            raise ValueError("'val' should be between 0 and 1")
        self._background_alpha = val
