"""Package-specific exceptions exposed by ManimPango."""

from __future__ import annotations


class ManimPangoError(Exception):
    """Base class for ManimPango-specific failures."""


class RenderError(ManimPangoError):
    """Raised when Pango or Cairo fails during a native render operation.

    Invalid public arguments continue to raise :class:`TypeError` or
    :class:`ValueError`, and invalid markup raises :class:`MarkupError`.
    """


class MarkupError(ValueError, ManimPangoError):
    """Raised when Pango markup is malformed."""


class FontError(ManimPangoError):
    """Base class for font-related failures."""


class FontNotFoundError(FileNotFoundError, FontError):
    """Raised when a requested font file does not exist."""


class FontRegistrationError(FontError):
    """Raised when a font backend rejects a font registration."""
