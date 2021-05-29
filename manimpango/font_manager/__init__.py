# -*- coding: utf-8 -*-

import errno
import typing
from pathlib import Path

import attr

from .. import Style, Variant, Weight, list_fonts
from ._register_font import (
    fc_register_font,
    fc_unregister_font,
    register_font,
    unregister_font,
)

__all__ = ["FontProperties", "RegisterFont"]


@attr.s
class FontProperties:
    """A :class:`FontProperties` are used for specifying the characteristics
    of a font to load.

    Attributes
    ----------
    family
        The font family.
    size
        Size of the text. Size should not be zero.
    style : :class:`Style`
        Style of the text.
    variant : :class:`Variant`
        Variant of the text.
    weight : :class:`Weight`
        Weight of the text.

    Parameters
    ----------
    family
        The font family.
    size
        Size of the text. Size should not be zero.
    style : :class:`Style`
        Style of the text.
    variant : :class:`Variant`
        Variant of the text.
    weight : :class:`Weight`
        Weight of the text.


    Raises
    ------
    ValueError
        When the :attr:`size` is set as zero.
    """

    family: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)),
        default=None,
    )
    size: typing.Optional[float] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of((float, int))),
        default=None,
    )
    style: typing.Optional[Style] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Style)),
        default=None,
    )
    variant: typing.Optional[Variant] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Variant)),
        default=None,
    )
    weight: typing.Optional[Weight] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Weight)),
        default=None,
    )
    # stretch
    # gravity
    # variations

    @size.validator
    def check_size(self, attribute, value):
        """Check whether the :attr:`size` isn't zero."""
        if value == 0:
            raise ValueError("Size shouldn't be Zero.")

    # def from_string(self):
    #     pass
    # def to_string(self):
    #     pass


@attr.s(frozen=True)
class RegisterFont(object):
    """A :class:`RegisterFont` object contains utilities
    to temporily add a font file to Pango's search Path.

    .. note::

        This is a frozen object, which means you can't change it's
        attributes after creating it.

    There are two methods to achive this, one using Fontconfig
    and other using native backend. This depends on which backend
    Pango is using. By default, Pango has these backends according to
    platforms,


    | win32      | win32 backend      |

    | macOS      | coretext backend   |

    | fontconfig | fontconfig backend |


    The backends can be changed using an Environment variable called
    ``PANGOCAIRO_BACKEND``. For example, for using fontconfig backend on
    Windows you can set::

        PANGOCAIRO_BACKEND=fc

    and after that fontconfig backend is used. After that you can set
    :attr:`use_fontconfig` to ``True`` which will add to fontconfig search
    path.

    .. warning::

        1. Linux has only fontconfig backend and changing to anything
           else would result in a crash.
        2. On Windows or macOS fontconfig backend can be problematic as
           it wouldn't be able to find it's configuration files in places
           it searches. This would result it no fonts situation.

    Attributes
    ----------
    font_file
        The path of the font file. Can be absolute or relative.
    use_fontconfig
        Whether to use fontconfig API.
    calculate_family
        Calculating the family can sometimes can be slow especially
        with huge number of fonts. You can disable it by setting
        :attr:`calculate_family` to False.
    family
        This is automatically set when :attr:`calculate_family` is ``True``.
        Or else it is None.

    Parameters
    ----------
    font_file
        The path of the font file. Can be absolute or relative.
    use_fontconfig
        Whether to use fontconfig API.
    calculate_family
        Calculating the family can sometimes can be slow especially
        with huge number of fonts. You can disable it by setting
        :attr:`calculate_family` to False.
    family
        This is automatically set when :attr:`calculate_family` is ``True``.
        Or else it is None.

    Raises
    ------
    FileNotFoundError
        When :attr:`font_file` is not found.
    RuntimeError
        This is raised when unable to register the font.
    """

    font_file: typing.Union[str, Path] = attr.ib(
        validator=[attr.validators.instance_of((str, Path))],
    )
    use_fontconfig: bool = attr.ib(
        validator=[attr.validators.instance_of(bool)], default=False, repr=False
    )
    calculate_family: bool = attr.ib(
        validator=[attr.validators.instance_of(bool)], default=True, repr=False
    )
    family: typing.Optional[str] = attr.ib(default=None)

    @font_file.validator
    def check_font_file(self, attribute, value):
        """Check whether :attr:`font_file` exists
        and is a file.
        """
        if not Path(value).exists():
            raise FileNotFoundError(
                errno.ENOENT,
                f"{value} doesn't exists.",
            )
        if not Path(value).is_file():
            raise FileNotFoundError(
                errno.ENOENT,
                f"{value} isn't a valid file",
            )

    def __attrs_post_init__(self):
        if self.calculate_family:
            intial = list_fonts(self.use_fontconfig)
        font_file = self.font_file
        if self.use_fontconfig:
            status = fc_register_font(str(font_file))
            if not status:
                raise RuntimeError(
                    f"Can't register font file {font_file}. "
                    "Maybe it's an invalid file ?"
                )
        else:
            status = register_font(str(font_file))
            if not status:
                raise RuntimeError(
                    f"Can't register font file {font_file}. "
                    "Maybe it's an invalid file ?"
                )
        if self.calculate_family:
            final = list_fonts(self.use_fontconfig)
            family = list(set(final) - set(intial)) or None
            super().__setattr__("family", family)
        else:
            super().__setattr__("family", None)

    def unregister(self) -> None:
        """Unregister the previous registered font.
        After this is called the font is removed
        from the Pango's search path.

        Returns
        -------
        bool
            True when sucessfully unregistered or else false.
        """
        if self.use_fontconfig:
            return fc_unregister_font(str(self.font_file))
        else:
            return unregister_font(str(self.font_file))
