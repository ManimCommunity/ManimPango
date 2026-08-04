"""Public Python API for rendering text with Pango."""

from __future__ import annotations

import os
import threading
from collections.abc import Mapping, Sequence
from importlib.metadata import version as _metadata_version
from math import isfinite
from numbers import Real
from pathlib import Path

# The DLL search path must be adjusted before importing the extension module.
if os.name == "nt":  # pragma: no cover - exercised on Windows wheels
    os.environ["PATH"] = (
        f"{os.path.dirname(__file__)}{os.pathsep}{os.environ.get('PATH', '')}"
    )

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
)

__version__ = _metadata_version("ManimPango")

__all__ = [
    "Alignment",
    "Bounds",
    "FontError",
    "FontNotFoundError",
    "FontRegistration",
    "FontRegistrationError",
    "LineInfo",
    "ManimPangoError",
    "MarkupError",
    "RenderError",
    "RenderedText",
    "Style",
    "TextSpan",
    "Weight",
    "__version__",
    "get_version_info",
    "list_fonts",
    "register_font",
    "render",
    "render_markup",
    "validate_markup",
]


_FONT_REGISTRATION_LOCK = threading.RLock()
_FONT_REGISTRATION_COUNTS: dict[Path, int] = {}
_FONT_REGISTRATION_TOKEN = object()


class FontRegistration:
    """An explicit, reference-counted registration of a font file.

    Instances are returned by :func:`register_font`.  Closing one handle does
    not affect other handles for the same normalized path; native unregistration
    occurs only after the final handle closes.  Use the handle as a context
    manager when the font is needed only for a bounded operation.  Unclosed
    handles intentionally remain active until process exit.

    Do not instantiate this class directly; obtain it from
    :func:`register_font`.
    """

    __slots__ = ("_closed", "_path")

    def __init__(self, path: Path, *, _token: object | None = None) -> None:
        if _token is not _FONT_REGISTRATION_TOKEN:
            raise TypeError(
                "FontRegistration handles must be created by register_font()"
            )
        self._path = path
        self._closed = False

    def __copy__(self) -> None:
        raise TypeError("FontRegistration handles cannot be copied")

    def __deepcopy__(self, memo: dict[int, object]) -> None:
        raise TypeError("FontRegistration handles cannot be copied")

    def __reduce__(self) -> None:
        raise TypeError("FontRegistration handles cannot be pickled")

    def __reduce_ex__(self, protocol: int) -> None:
        raise TypeError("FontRegistration handles cannot be pickled")

    @property
    def path(self) -> Path:
        """The absolute, normalized font-file path."""
        return self._path

    @property
    def closed(self) -> bool:
        """Whether this handle has released its registration reference."""
        return self._closed

    def close(self) -> None:
        """Release this handle's registration reference, idempotently.

        The font remains available while another handle for the same path is
        open.  The final close removes it from subsequent renderer-owned font
        maps and can raise :class:`FontRegistrationError` if the native
        backend cannot complete that transition.
        """
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
            unregistered = False
            try:
                unregistered = _fonts.unregister_font(str(self._path))
                if unregistered:
                    _render.refresh_font_map()
            except Exception as error:
                if unregistered:
                    # The native removal succeeded but the renderer could not
                    # adopt its new map. Restore both states before surfacing
                    # the close failure to the caller.
                    try:
                        _fonts.register_font(str(self._path))
                        _render.refresh_font_map()
                    except Exception:
                        pass
                raise FontRegistrationError(
                    f"failed to unregister font {self._path}"
                ) from error
            if not unregistered:
                raise FontRegistrationError(f"failed to unregister font {self._path}")
            del _FONT_REGISTRATION_COUNTS[self._path]
            self._closed = True

    def __enter__(self) -> FontRegistration:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.close()
        return False


def get_version_info() -> dict[str, str]:
    """Return version strings for ManimPango and its linked libraries.

    Returns
    -------
    dict[str, str]
        A mapping with the stable keys ``"manimpango"``, ``"pango"``, and
        ``"cairo"``.
    """
    return _render.get_version_info()


def validate_markup(markup: str) -> str:
    """Validate a Pango markup string without rendering it.

    Returns an empty string when ``markup`` is valid. Otherwise returns a
    diagnostic explaining why it is invalid. :func:`render_markup` turns that
    diagnostic into :class:`MarkupError`. Embedded NUL characters are
    rejected before Pango parses the source.

    Raises
    ------
    TypeError
        If ``markup`` is not a string.
    """
    if not isinstance(markup, str):
        raise TypeError("markup must be a string")
    if "\0" in markup:
        return "markup must not contain NUL characters"
    return _render.validate_markup(markup)


def register_font(font_path: str | Path) -> FontRegistration:
    """Register a font file and return an explicit lifetime handle.

    Each call returns a distinct handle.  The file path is expanded and
    resolved strictly before entering the native backend.  The font becomes
    visible to this renderer's font map immediately and remains available
    until the final handle for that normalized path is closed.

    Use the returned handle as a context manager for temporary registrations.
    Multiple handles for the same file are reference-counted, so closing one
    cannot remove a font still used by another.

    Raises
    ------
    FontNotFoundError
        If the path does not exist.
    FontRegistrationError
        If the path is not a regular file or the native backend rejects the
        registration.
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
                if registered:
                    _render.refresh_font_map()
            except Exception as error:
                # Keep the native backend and renderer map transactional.
                # A failed map refresh must not leave a registration without a
                # corresponding renderer-visible font map.
                try:
                    _fonts.unregister_font(str(normalized_path))
                    _render.refresh_font_map()
                except Exception:
                    pass
                raise FontRegistrationError(
                    f"failed to register font {normalized_path}"
                ) from error
            if not registered:
                raise FontRegistrationError(
                    f"failed to register font {normalized_path}"
                )
        _FONT_REGISTRATION_COUNTS[normalized_path] = count + 1
        return FontRegistration(normalized_path, _token=_FONT_REGISTRATION_TOKEN)


def list_fonts() -> list[str]:
    """Return sorted unique family names visible to the renderer's font map.

    The result includes currently registered custom fonts and is a snapshot;
    closing a :class:`FontRegistration` can change later calls.
    """
    return _render.list_fonts()


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
    reject_nul_text: bool = True,
) -> None:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if reject_nul_text and "\0" in text:
        raise ValueError("text must not contain NUL characters")
    if font is not None and not isinstance(font, str):
        raise TypeError("font must be a string or None")
    if font is not None and "\0" in font:
        raise ValueError("font must not contain NUL characters")
    _finite(size, "size", positive=True)
    if (
        isinstance(weight, bool)
        or not isinstance(weight, int)
        or not 1 <= weight <= 1000
    ):
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


def _render_native(text: str, **options: object) -> RenderedText:
    """Call the native renderer and translate backend render failures."""
    try:
        return _render.render(text, **options)
    except (MemoryError, RuntimeError) as error:
        message = str(error) or "native renderer failed"
        raise RenderError(message) from error


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
    """Render literal plain text to SVG and structured layout metadata.

    ``text`` is never interpreted as markup.  Use :func:`render_markup` for
    Pango markup, or use ``spans`` to style ranges of plain text in the same
    native layout.

    Parameters
    ----------
    text
        Literal Unicode text to render, without embedded NUL characters.
    spans
        :class:`TextSpan` instances for half-open code-point ranges of
        ``text``.  Compatible overlaps compose; conflicting values raise
        :class:`ValueError`.
    font
        Font family name without embedded NUL characters, or ``None`` for
        Pango's default family. To use a font file that is not installed
        system-wide, register it first with :func:`register_font`.
    size
        Positive absolute font size in SVG user-space units.
    weight, style
        Base :class:`Weight`/integer and :class:`Style` for text not
        overridden by a span.
    variations
        Mapping of four-printable-ASCII-character OpenType variation-axis tags to
        finite numeric values.  Settings are forwarded to Pango; visible
        effects depend on the selected font, axis, and renderer backend.
    width
        Positive wrapping width in SVG user-space units, or ``None`` for no
        width constraint.
    alignment
        Horizontal alignment within ``width``.
    line_spacing
        Positive Pango line-spacing multiplier, or ``None`` for Pango's
        default line spacing.
    justify
        Whether Pango justifies wrapped lines.
    indent
        Pango indentation in SVG user-space units; negative values create a
        hanging indentation.
    disable_ligatures
        Disable Pango's standard, discretionary, contextual, historical, and
        contextual-alternate features (``liga``, ``dlig``, ``clig``,
        ``hlig``, and ``calt``).  This setting takes precedence over
        conflicting feature declarations in ``spans`` or markup.

    Returns
    -------
    RenderedText
        SVG output plus viewport, bounds, baseline, and per-line metadata.

    Raises
    ------
    TypeError, ValueError
        If an option or span is invalid.
    RenderError
        If Pango or Cairo fails while creating the native render result.
    """
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
    return _render_native(
        text=text,
        is_markup=False,
        spans=native_spans,
        **_native_options(
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
        ),
    )


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
    """Render Pango markup to SVG and structured layout metadata.

    ``markup`` is parsed by Pango; do not pass markup to :func:`render`.
    The layout options have the same meanings as in :func:`render`, except
    range styling is expressed in markup rather than with ``TextSpan``.
    Line offsets in the returned :class:`RenderedText` refer to Pango's
    parsed text, not character offsets in the markup source.

    Parameters
    ----------
    markup
        A Unicode string using Pango markup, without embedded NUL characters.

    Notes
    -----
    All remaining options have the same contracts as in :func:`render`;
    markup expresses range styling instead of accepting ``TextSpan`` objects.

    Returns
    -------
    RenderedText
        SVG output plus viewport, bounds, baseline, and per-line metadata.

    Raises
    ------
    MarkupError
        If Pango rejects ``markup``.
    TypeError, ValueError
        If an option is invalid.
    RenderError
        If Pango or Cairo fails while creating the native render result.
    """
    _validate_options(
        markup,
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
        reject_nul_text=False,
    )
    if "\0" in markup:
        raise MarkupError(
            "Invalid Pango markup: markup must not contain NUL characters"
        )
    try:
        return _render_native(
            text=markup,
            is_markup=True,
            **_native_options(
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
            ),
        )
    except ValueError as error:
        raise MarkupError(str(error)) from error
