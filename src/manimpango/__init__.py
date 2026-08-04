"""Public Python API for rendering text with Pango."""

from __future__ import annotations

import os
import threading
from importlib.metadata import version as _metadata_version
from math import isfinite
from numbers import Real
from pathlib import Path
from typing import Mapping, Sequence

# The DLL search path must be adjusted before importing the extension module.
if os.name == "nt":  # pragma: no cover - exercised on Windows wheels
    os.environ["PATH"] = f"{os.path.dirname(__file__)}{os.pathsep}{os.environ.get('PATH', '')}"

from . import _fonts, _render
from ._spans import TextSpan, normalize_spans, validate_variations
from ._text import Bounds, LineInfo, RenderedText
from .enums import Alignment, Style, Weight
from .exceptions import (
    FontError,
    FontNotFoundError,
    FontRegistrationError,
    ManimPangoError,
    MarkupError,
    RenderError,
    UnsupportedPangoFeatureError,
)

__version__ = _metadata_version("ManimPango")

__all__ = [
    "__version__",
    "get_version_info",
    "render",
    "render_markup",
    "validate_markup",
    "RenderedText",
    "LineInfo",
    "Bounds",
    "TextSpan",
    "FontRegistration",
    "register_font",
    "list_fonts",
    "Style",
    "Weight",
    "Alignment",
    "ManimPangoError",
    "RenderError",
    "MarkupError",
    "FontError",
    "FontNotFoundError",
    "FontRegistrationError",
    "UnsupportedPangoFeatureError",
]


_FONT_REGISTRATION_LOCK = threading.RLock()
_FONT_REGISTRATION_COUNTS: dict[Path, int] = {}


class FontRegistration:
    """An explicit, reference-counted registration of a font file.

    Instances are returned by :func:`register_font`.  Closing one handle does
    not affect other handles for the same normalized path; native unregistration
    occurs only after the final handle closes.  Unclosed handles intentionally
    remain active until process exit.
    """

    __slots__ = ("_closed", "_path")

    def __init__(self, path: Path) -> None:
        self._path = path
        self._closed = False

    @property
    def path(self) -> Path:
        """The absolute, normalized font-file path."""
        return self._path

    @property
    def closed(self) -> bool:
        """Whether this handle has released its registration reference."""
        return self._closed

    def close(self) -> None:
        """Release this handle's registration reference, idempotently."""
        with _FONT_REGISTRATION_LOCK:
            if self._closed:
                return
            count = _FONT_REGISTRATION_COUNTS.get(self._path)
            if count is None:
                raise FontRegistrationError(
                    f"font registration state is missing for {self._path}"
                )
            if count > 1:
                _FONT_REGISTRATION_COUNTS[self._path] = count - 1
                self._closed = True
                return
            try:
                unregistered = _fonts.unregister_font(str(self._path))
            except Exception as error:
                raise FontRegistrationError(
                    f"failed to unregister font {self._path}"
                ) from error
            if not unregistered:
                raise FontRegistrationError(f"failed to unregister font {self._path}")
            del _FONT_REGISTRATION_COUNTS[self._path]
            self._closed = True

    def __enter__(self) -> "FontRegistration":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.close()
        return False


def get_version_info() -> dict[str, str]:
    """Return versions of ManimPango and its linked dependencies."""
    return _render.get_version_info()


def validate_markup(markup: str) -> str:
    """Return an empty string for valid Pango markup, otherwise an error."""
    if not isinstance(markup, str):
        raise TypeError("markup must be a string")
    return _render.validate_markup(markup)


def register_font(font_path: str | Path) -> FontRegistration:
    """Register a font file and return an explicit lifetime handle.

    Each call returns a distinct handle.  The file path is expanded and
    resolved strictly before entering the native backend.
    """
    try:
        normalized_path = Path(font_path).expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise FontNotFoundError(str(font_path)) from error
    if not normalized_path.is_file():
        raise FontRegistrationError(f"font path is not a file: {normalized_path}")

    with _FONT_REGISTRATION_LOCK:
        count = _FONT_REGISTRATION_COUNTS.get(normalized_path, 0)
        if count == 0:
            try:
                registered = _fonts.register_font(str(normalized_path))
            except Exception as error:
                raise FontRegistrationError(
                    f"failed to register font {normalized_path}"
                ) from error
            if not registered:
                raise FontRegistrationError(f"failed to register font {normalized_path}")
        _FONT_REGISTRATION_COUNTS[normalized_path] = count + 1
        return FontRegistration(normalized_path)


def list_fonts() -> list[str]:
    """Return font family names currently known to the native backend."""
    return _fonts.list_fonts()


def _finite(value: object, name: str, *, positive: bool = False) -> None:
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValueError(f"{name} must be greater than zero")


def _validate_options(
    text: str,
    *,
    font: str | None,
    size: float,
    weight: Weight | int,
    style: Style,
    variations: Mapping[str, float] | None,
    width: float | None,
    alignment: Alignment,
    line_spacing: float | None,
    justify: bool,
    indent: float,
    disable_ligatures: bool,
) -> None:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if font is not None and not isinstance(font, str):
        raise TypeError("font must be a string or None")
    _finite(size, "size", positive=True)
    if isinstance(weight, bool) or not isinstance(weight, int) or not 1 <= weight <= 1000:
        raise ValueError("weight must be an integer between 1 and 1000")
    if not isinstance(style, Style):
        raise TypeError("style must be a Style")
    validate_variations(variations)
    if width is not None:
        _finite(width, "width", positive=True)
    if not isinstance(alignment, Alignment):
        raise TypeError("alignment must be an Alignment")
    if line_spacing is not None:
        _finite(line_spacing, "line_spacing", positive=True)
    if not isinstance(justify, bool):
        raise TypeError("justify must be a bool")
    _finite(indent, "indent")
    if not isinstance(disable_ligatures, bool):
        raise TypeError("disable_ligatures must be a bool")


def _native_options(
    *,
    font: str | None,
    size: float,
    weight: Weight | int,
    style: Style,
    variations: Mapping[str, float] | None,
    width: float | None,
    alignment: Alignment,
    line_spacing: float | None,
    justify: bool,
    indent: float,
    disable_ligatures: bool,
) -> dict[str, object]:
    return {
        "font": font,
        "size": size,
        "weight": weight,
        "style": style,
        "variations": variations,
        "width": width,
        "alignment": alignment,
        "line_spacing": line_spacing,
        "justify": justify,
        "indent": indent,
        "disable_ligatures": disable_ligatures,
    }


def render(
    text: str,
    *,
    spans: Sequence[TextSpan] = (),
    font: str | None = None,
    size: float = 12.0,
    weight: Weight | int = Weight.NORMAL,
    style: Style = Style.NORMAL,
    variations: Mapping[str, float] | None = None,
    width: float | None = None,
    alignment: Alignment = Alignment.LEFT,
    line_spacing: float | None = None,
    justify: bool = False,
    indent: float = 0.0,
    disable_ligatures: bool = False,
) -> RenderedText:
    """Render plain text with structured spans in one native layout."""
    _validate_options(
        text,
        font=font,
        size=size,
        weight=weight,
        style=style,
        variations=variations,
        width=width,
        alignment=alignment,
        line_spacing=line_spacing,
        justify=justify,
        indent=indent,
        disable_ligatures=disable_ligatures,
    )
    native_spans = normalize_spans(spans, text)
    return _render.render(text, is_markup=False, spans=native_spans, **_native_options(
        font=font, size=size, weight=weight, style=style, variations=variations,
        width=width, alignment=alignment, line_spacing=line_spacing,
        justify=justify, indent=indent, disable_ligatures=disable_ligatures,
    ))


def render_markup(
    markup: str,
    *,
    font: str | None = None,
    size: float = 12.0,
    weight: Weight | int = Weight.NORMAL,
    style: Style = Style.NORMAL,
    variations: Mapping[str, float] | None = None,
    width: float | None = None,
    alignment: Alignment = Alignment.LEFT,
    line_spacing: float | None = None,
    justify: bool = False,
    indent: float = 0.0,
    disable_ligatures: bool = False,
) -> RenderedText:
    """Render Pango markup through the native markup pipeline."""
    _validate_options(
        markup,
        font=font, size=size, weight=weight, style=style, variations=variations,
        width=width, alignment=alignment, line_spacing=line_spacing,
        justify=justify, indent=indent, disable_ligatures=disable_ligatures,
    )
    markup_error = validate_markup(markup)
    if markup_error:
        raise MarkupError(f"Invalid Pango markup: {markup_error}")
    return _render.render(markup, is_markup=True, **_native_options(
        font=font, size=size, weight=weight, style=style, variations=variations,
        width=width, alignment=alignment, line_spacing=line_spacing,
        justify=justify, indent=indent, disable_ligatures=disable_ligatures,
    ))


def pango_version() -> str:
    """Return the linked Pango version (compatibility helper)."""
    return get_version_info()["pango"]


def cairo_version() -> str:
    """Return the linked Cairo version (compatibility helper)."""
    return get_version_info()["cairo"]
