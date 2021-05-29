# -*- coding: utf-8 -*-
import typing

import attr

from ..exceptions import MarkupParseError
from ..font_manager import FontProperties
from ..utils import Alignment
from .utils import validate_markup

__all__ = ["Layout", "validate_markup"]


@attr.s
class Layout:
    text: typing.Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)),
        default=None,
    )
    width: typing.Optional[int] = attr.ib(
        default=None,
        validator=attr.validators.optional(
            attr.validators.instance_of(int),
        ),
    )
    height: typing.Optional[int] = attr.ib(
        default=None,
        validator=attr.validators.optional(
            attr.validators.instance_of(int),
        ),
    )
    alignment: Alignment = attr.ib(
        default=Alignment.CENTER,
        validator=[attr.validators.instance_of(Alignment)],
    )
    auto_dir: bool = attr.ib(
        default=True,
        validator=[attr.validators.instance_of(bool)],
    )
    markup: typing.Optional[str] = attr.ib(
        default=None,
        validator=attr.validators.optional(
            attr.validators.instance_of(str),
        ),
    )
    indent: int = attr.ib(
        default=0,
        validator=attr.validators.optional(
            attr.validators.instance_of(int),
        ),
    )
    spacing: int = attr.ib(
        default=0,
        validator=attr.validators.optional(
            attr.validators.instance_of(int),
        ),
    )
    line_spacing: float = attr.ib(
        default=0,
        validator=attr.validators.optional(
            attr.validators.instance_of((float, int)),
        ),
    )
    justify: bool = attr.ib(
        default=None,
        validator=attr.validators.optional(
            attr.validators.instance_of(bool),
        ),
    )
    font_properties: FontProperties = attr.ib(
        default=None,
        validator=attr.validators.optional(
            attr.validators.instance_of(FontProperties),
        ),
    )
    # single_paragraph_mode
    # tab_length :int = attr.ib(
    #     default=8,
    #     validator=[
    #         attr.validators.instance_of(int),
    #     ],
    # )
    # direction
    # wrap
    # ellipsize
    # attributes = attr.ib(default=None)
    # font_description = attr.ib(default=None)

    @markup.validator
    def check_markup(self, attribute, value):
        if value is not None:
            check = validate_markup(value)
            if check:
                raise MarkupParseError(check)

    def __attrs_post_init__(self):
        if self.markup is None and self.text is None:
            raise ValueError("Either of Markup or Text is required.")

    def __len__(self):
        return len(self.text) if self.text is not None else len(self.markup)

    # def is_wrapped
