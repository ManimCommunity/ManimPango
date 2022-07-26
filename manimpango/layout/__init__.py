# -*- coding: utf-8 -*-


from ..enums import Alignment
from ..exceptions import MarkupParseError
from ..fonts import FontDescription
from ..utils import validate_markup

__all__ = ["Layout"]


class Layout:
    """A :class:`Layout` class represents an entire paragraph of text.

    :class:`Layout` provides a high-level driver for formatting entire
    paragraphs of text at once. This includes paragraph-level functionality
    such as line breaking, justification, alignment and ellipsization.

    A :class:`Layout` is initialized with a :class:`str`. The layout
    can then be rendered. There are a number of parameters to adjust
    the formatting of a :class:`Layout`.

    When both :attr:`markup` and :attr:`text` is set the behavior is
    unknown.

    Parameters
    ==========
    text:
        The text to be set, by default None.
    markup:
        The text encoded in PangoMarkup, by default None.
    font_desc:
        The font description to be used while rendering.

    Examples
    ========
    >>> import manimpango as mp
    >>> mp.Layout("hello world")
    <Layout text='hello world' markup=None>

    Raises
    ======
    ValueError
        If both ``text`` and ``markup`` is None.
    """

    def __init__(
        self,
        text: str = None,
        markup: str = None,
        font_desc: FontDescription = None,
    ):
        if text:
            self.text = text
        if markup:
            self.markup = markup
        if self.markup is None and self.text is None:
            raise ValueError("Either 'markup' or 'text' is required.")
        if font_desc:
            self.font_desc = font_desc

    def __len__(self):
        return len(self.text) if self.text is not None else len(self.markup)

    @property
    def text(self) -> str:
        """The text to render.

        Raises
        ======
        TypeError
            If ``text`` is not a :class:`str`.
        """
        if hasattr(self, "_text"):
            return self._text
        return None

    @text.setter
    def text(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError("'text' should be a str")
        self._text = val

    @property
    def markup(self) -> str:
        """The markup (in pango markup format) to render.

        Raises
        ======
        TypeError
            If ``text`` is not a :class:`str`.

        MarkupParseError
            If the passed markup is invalid.
        """
        if hasattr(self, "_markup"):
            return self._markup
        return None

    @markup.setter
    def markup(self, val: str) -> None:
        if not isinstance(val, str):
            raise TypeError("'markup' should be a str")
        check = validate_markup(val)
        if check:
            raise MarkupParseError(check)
        self._markup = val

    @property
    def width(self) -> int:
        """The width to which the text should be wrapped or ellipsized.

        Raises
        ======
        TypeError
            If ``width`` is not a :class:`int`.
        """
        if hasattr(self, "_width"):
            return self._width
        return None

    @width.setter
    def width(self, val: int) -> None:
        if not isinstance(val, int):
            raise TypeError("'width' should be an int")
        self._width = val

    @property
    def height(self) -> int:
        """The height to which the text should be ellipsized at.

        Raises
        ======
        TypeError
            If ``height`` is not a :class:`int`.
        """
        if hasattr(self, "_height"):
            return self._height
        return None

    @height.setter
    def height(self, val: int) -> None:
        if not isinstance(val, int):
            raise TypeError("'height' should be an int")
        self._height = val

    @property
    def alignment(self) -> Alignment:
        if hasattr(self, "_alignment"):
            return self._alignment
        return None

    @alignment.setter
    def alignment(self, val: Alignment):
        if not isinstance(val, Alignment):
            raise TypeError("'alignment' should be an Alignment")
        self._alignment = val

    @property
    def font_desc(self) -> FontDescription:
        if hasattr(self, "_font_desc"):
            return self._font_desc
        return FontDescription()

    @font_desc.setter
    def font_desc(self, val: FontDescription):
        if not isinstance(val, FontDescription):
            raise TypeError("'font_desc' should be an FontDescription")
        self._font_desc = val

    def __repr__(self):
        return f"<Layout text={repr(self.text)} markup={repr(self.markup)}>"
