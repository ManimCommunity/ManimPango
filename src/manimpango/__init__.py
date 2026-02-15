"""ManimPango - Pango bindings for rendering text to SVG.

This library provides a simple, robust Python interface to Pango for rendering
text as SVG. It is designed to be used by Manim for text rendering.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from importlib.metadata import version as _metadata_version

__version__ = _metadata_version("ManimPango")
from ._text import RenderedText, LineInfo
from .enums import Style, Weight, Alignment
from . import _render
from . import _fonts


# Platform-specific DLL loading on Windows
if os.name == "nt":  # pragma: no cover
    os.environ["PATH"] = (
        f"{os.path.abspath(os.path.dirname(__file__))}"
        f"{os.pathsep}"
        f"{os.environ.get('PATH', '')}"
    )


# Re-export public API
__all__ = [
    # Version
    "__version__",
    "get_version_info",

    # Rendering
    "render",
    "validate_markup",
    "RenderedText",
    "LineInfo",

    # Font management
    "register_font",
    "unregister_font",
    "list_fonts",

    # Enums
    "Style",
    "Weight",
    "Alignment",

    # Exceptions
    "UnsupportedPangoFeatureError",
]


# === Public API ===

def get_version_info() -> dict[str, str]:
    """Get version information for ManimPango and dependencies.

    Returns
    -------
    dict[str, str]
        Dictionary containing version strings for manimpango, pango, and cairo.
    """
    return _render.get_version_info()


def validate_markup(markup: str) -> str:
    """Validate Pango markup without rendering.

    Parameters
    ----------
    markup : str
        The markup string to validate.

    Returns
    -------
    str
        Empty string if valid; error message if invalid.
    """
    return _render.validate_markup(markup)


def render(
    text: str,
    *,
    # Rendering mode
    is_markup: bool = False,

    # Font
    font: str | None = None,
    size: float = 12.0,
    weight: Weight | int = Weight.NORMAL,
    style: Style = Style.NORMAL,
    variations: dict[str, float] | None = None,

    # Layout
    width: float | None = None,
    alignment: Alignment = Alignment.LEFT,
    line_spacing: float | None = None,
    justify: bool = False,
    indent: float = 0.0,

    # Text features
    disable_ligatures: bool = False,
) -> RenderedText:
    """Render text to SVG.

    Parameters
    ----------
    text : str
        The text to render.
    is_markup : bool, optional
        If True, interpret text as Pango markup. Default is False.
    font : str | None, optional
        Font family name. Uses Pango's default if None. Default is None.
    size : float, optional
        Font size in points. Default is 12.0.
    weight : Weight | int, optional
        Font weight. Accepts Weight enum or any int 1-1000. Default is Weight.NORMAL.
    style : Style, optional
        Font style (normal/italic/oblique). Default is Style.NORMAL.
    variations : dict[str, float] | None, optional
        OpenType variable font axis values, e.g. {"wght": 650, "wdth": 75}. Default is None.

        .. note::

           This parameter requires the PangoFT2/fontconfig backend (default
           on Linux).  On macOS, Pango's CoreText backend ignores font
           variations.  For weight changes specifically, use the ``weight``
           parameter instead — it works on all platforms.  On macOS with
           Homebrew Pango, you can force the fontconfig backend by setting
           ``PANGOCAIRO_BACKEND=fc`` before importing manimpango.
    width : float | None, optional
        Layout width in points. Text wraps at this width. None means no wrapping. Default is None.
    alignment : Alignment, optional
        Text alignment within layout width. Default is Alignment.LEFT.
    line_spacing : float | None, optional
        Line spacing multiplier. None means use Pango default. Default is None.
    justify : bool, optional
        Whether to justify text. Default is False.
    indent : float, optional
        First-line indent in points. Default is 0.0.
    disable_ligatures : bool, optional
        Disable typographic ligatures. Default is False.

    Returns
    -------
    RenderedText
        An object containing SVG content and layout metadata.

    Raises
    ------
    ValueError
        If markup is invalid (when is_markup=True).
    MemoryError
        If Pango/Cairo allocation fails.

    Examples
    --------
    Render plain text::

        >>> result = manimpango.render("Hello World")
        >>> svg = result.svg
        >>> result.save("hello.svg")

    Render markup::

        >>> result = manimpango.render(
        ...     "<span color='red' weight='bold'>Important</span>",
        ...     is_markup=True,
        ...     font="Helvetica",
        ...     size=24,
        ... )

    Variable font with continuous weight::

        >>> result = manimpango.render(
        ...     "Smooth weight",
        ...     font="InterVariable",
        ...     weight=450,
        ...     variations={"wdth": 90, "opsz": 14},
        ... )
    """
    return _render.render(
        text=text,
        is_markup=is_markup,
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


# Font management
def register_font(font_path: str | Path) -> bool:
    """Register a font file so Pango can use it for rendering.

    Uses fontconfig on Linux, CoreText on macOS, Win32 API on Windows.

    Parameters
    ----------
    font_path : str | Path
        Relative or absolute path to font file.

    Returns
    -------
    bool
        True on success, False on failure.

    Raises
    ------
    FileNotFoundError
        If font_path does not exist.
    """
    return _fonts.register_font(str(font_path))


def unregister_font(font_path: str | Path) -> bool:
    """Unregister a previously registered font.

    Parameters
    ----------
    font_path : str | Path
        Relative or absolute path to font file.

    Returns
    -------
    bool
        True on success, False on failure.
    """
    return _fonts.unregister_font(str(font_path))


def list_fonts() -> list[str]:
    """List all font family names available to Pango (sorted).

    Returns
    -------
    list[str]
        List of font family names sorted alphabetically.
    """
    return _fonts.list_fonts()


# === Exception classes ===

class UnsupportedPangoFeatureError(RuntimeError):
    """Raised when a requested feature is not available in the installed Pango version."""
    pass


# === Import-time validation ===

def _validate_runtime() -> None:
    """Check that the linked Pango meets minimum requirements.

    Raises
    ------
    RuntimeError
        If Pango version is below minimum requirement.
    """
    version_info = get_version_info()
    pango_version = version_info["pango"]

    # Parse version
    parts = pango_version.split('.')
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    micro = int(parts[2]) if len(parts) > 2 else 0

    # Minimum required is Pango 1.44
    if (major, minor, micro) < (1, 44, 0):
        raise RuntimeError(
            f"ManimPango requires Pango >= 1.44.0, found {pango_version}. "
            "Please update your Pango installation."
        )


# Run validation
try:
    _validate_runtime()
except Exception as e:
    # If we can't get version info, the library might not be built yet
    # Re-raise other errors
    if not isinstance(e, RuntimeError) or "Pango" not in str(e):
        raise
    # For missing Pango, provide a helpful message
    print(f"Warning: {e}", file=sys.stderr)


# Backwards compatibility: expose pango_version and cairo_version functions
def pango_version() -> str:
    """Get Pango version string.

    .. deprecated::
        Use :func:`get_version_info` instead.
    """
    return get_version_info()["pango"]


def cairo_version() -> str:
    """Get Cairo version string.

    .. deprecated::
        Use :func:`get_version_info` instead.
    """
    return get_version_info()["cairo"]
