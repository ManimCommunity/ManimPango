from ..layout import Layout

class SVGRenderer:
    def __init__(
        self,
        file_name: str,
        width: int,
        height: int,
        layout: Layout,
    ): ...
    @property
    def file_name(self) -> str: ...
    @property
    def width(self) -> float: ...
    def height(self) -> float: ...
    def render(self) -> bool: ...
    def save(self, file_name: str = None) -> str: ...
