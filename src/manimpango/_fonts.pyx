#!python
# cython: language_level=3

"""Native font registration and font-family enumeration."""

from __future__ import annotations

import sys
import threading

from manimpango._fonts cimport *


# The public API owns registration reference counts.  This set records only
# paths for which this extension currently owns an actual backend registration.
# It is also needed to rebuild Fontconfig's all-or-nothing app-font set.
_backend_lock = threading.RLock()
_active_paths: set[str] = set()


cdef void _raise_backend_error(char* error) except *:
    cdef str detail
    if error == NULL:
        raise RuntimeError("font backend operation failed without an error message")
    try:
        detail = (<bytes>error).decode("utf-8", "replace")
    finally:
        g_free(error)
    raise RuntimeError(detail)


cpdef tuple active_font_paths():
    """Return an immutable snapshot for the renderer's private font map."""
    with _backend_lock:
        return tuple(sorted(_active_paths))


cpdef bint register_font(str font_path):
    """Perform one native registration for ``font_path``.

    Reference counts deliberately live in the public Python layer, so a call
    for an already active path is a no-op rather than a second backend handle.
    """
    cdef bytes path_bytes = font_path.encode("utf-8")
    cdef char* error = NULL
    cdef int success

    with _backend_lock:
        if font_path in _active_paths:
            return True
        success = manimpango_register_font(<const char*>path_bytes, &error)
        if not success:
            _raise_backend_error(error)
        _active_paths.add(font_path)
    return True


cpdef bint unregister_font(str font_path):
    """Remove one native registration after its final public handle closes."""
    cdef bytes path_bytes = font_path.encode("utf-8")
    cdef bytes active_path_bytes
    cdef char* error = NULL
    cdef char* rollback_error = NULL
    cdef int success
    cdef str active_path
    cdef tuple previous_paths

    with _backend_lock:
        if font_path not in _active_paths:
            return True

        previous_paths = tuple(sorted(_active_paths))

        # On Fontconfig this clears every application font.  Re-add the paths
        # still active while holding the same lock, so closing one handle never
        # drops a different registered family.
        success = manimpango_unregister_font(<const char*>path_bytes, &error)
        if not success:
            _raise_backend_error(error)
        _active_paths.remove(font_path)
        try:
            if sys.platform.startswith("linux"):
                for active_path in sorted(_active_paths):
                    active_path_bytes = active_path.encode("utf-8")
                    error = NULL
                    success = manimpango_register_font(<const char*>active_path_bytes, &error)
                    if not success:
                        _raise_backend_error(error)
        except:
            # Fontconfig removal clears the whole application set.  Restore
            # the exact pre-operation native state before reporting failure.
            rollback_error = NULL
            success = manimpango_unregister_font(<const char*>path_bytes, &rollback_error)
            if not success:
                _raise_backend_error(rollback_error)
            for active_path in previous_paths:
                active_path_bytes = active_path.encode("utf-8")
                rollback_error = NULL
                success = manimpango_register_font(
                    <const char*>active_path_bytes, &rollback_error
                )
                if not success:
                    _raise_backend_error(rollback_error)
            _active_paths.add(font_path)
            raise
    return True
