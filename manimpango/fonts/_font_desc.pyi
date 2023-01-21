from __future__ import annotations

from manimpango.fonts.enums import Style, Variant, Weight

class _FontDescription:
    def __init__(
        self,
        family: str = None,
        size: int = None,
        style: Style = None,
        weight: Weight = None,
        variant: Variant = None,
    ) -> None: ...
    @property
    def family(self) -> str | None: ...
    @property
    def size(self) -> int: ...
    @property
    def style(self) -> Style: ...
    @property
    def weight(self) -> Weight: ...
    @property
    def variant(self) -> Variant: ...
    @classmethod
    def from_string(cls, string: str) -> FontDescription: ...
