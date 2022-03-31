# from ._attributes import *

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
        """start_index is the start of the range.

        Returns
        -------
        int
            The start index saved.
        """
        return self._start_index

    @start_index.setter
    def start_index(self, val: int) -> None:
        if not isinstance(val, int):
            raise ValueError("'start_index' should be an int")
        self._start_index = val

    @property
    def end_index(self) -> int:
        return self._end_index

    @end_index.setter
    def end_index(self, val: int) -> None:
        if not isinstance(val, int):
            raise ValueError("'end_index' should be an int")
        self._end_index = val
