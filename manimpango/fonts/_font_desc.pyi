from manimpango.fonts.enums import Style, Variant, Weight


class FontDescription:
    @property
    def family(self) -> str:
        ...

    @property
    def size(self) -> int:
        ...

    @property
    def style(self) -> Style:
        ...

    @property
    def weight(self) -> Weight:
        ...

    @property
    def variant(self) -> Variant:
        ...
