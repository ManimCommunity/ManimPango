#!python
# cython: language_level=3

"""Native font registration and font-family enumeration."""

from __future__ import annotations

import sys
import threading

from cpython.mem cimport PyMem_Free, PyMem_Malloc
from manimpango._fonts cimport *


# The public API owns registration reference counts.  This set records only
# paths for which this extension currently owns an actual backend registration.
# It is also needed to rebuild Fontconfig's all-or-nothing app-font set.
_backend_lock = threading.RLock()
_active_paths: set[str] = set()
cdef PangoFontMap* _managed_fontmap = NULL


cdef void _raise_backend_error(char* error) except *:
    cdef str detail
    if error == NULL:
        raise RuntimeError("font backend operation failed without an error message")
    try:
        detail = (<bytes>error).decode("utf-8", "replace")
    finally:
        g_free(error)
    raise RuntimeError(detail)


cdef void _rebuild_managed_font_map() except *:
    """Atomically replace the shared map with all active application fonts."""
    global _managed_fontmap
    cdef const char** paths = NULL
    cdef char* error = NULL
    cdef int success
    cdef Py_ssize_t count = len(_active_paths)
    cdef Py_ssize_t i
    cdef str active_path
    cdef list path_bytes = []
    cdef PangoFontMap* new_fontmap = NULL
    cdef PangoFontMap* old_fontmap = NULL

    try:
        for active_path in sorted(_active_paths):
            path_bytes.append(active_path.encode("utf-8"))
        if count:
            paths = <const char**>PyMem_Malloc(count * sizeof(const char*))
            if paths == NULL:
                raise MemoryError("could not allocate managed font-map paths")
            for i in range(count):
                paths[i] = <const char*>path_bytes[i]
        new_fontmap = manimpango_build_font_map(paths, <size_t>count, &error)
        if new_fontmap == NULL:
            _raise_backend_error(error)
        old_fontmap = _managed_fontmap
        _managed_fontmap = new_fontmap
        if old_fontmap != NULL:
            g_object_unref(old_fontmap)
    finally:
        if paths != NULL:
            PyMem_Free(paths)


cdef PangoFontMap* acquire_font_map() except NULL:
    """Return a referenced snapshot of the process-managed font map."""
    global _managed_fontmap
    cdef char* error = NULL
    cdef PangoFontMap* fontmap

    with _backend_lock:
        if _managed_fontmap == NULL:
            fontmap = manimpango_build_font_map(NULL, 0, &error)
            if fontmap == NULL:
                _raise_backend_error(error)
            _managed_fontmap = fontmap
        g_object_ref(_managed_fontmap)
        return _managed_fontmap


cpdef bint register_font(str font_path):
    """Perform one native registration for ``font_path``.

    Reference counts deliberately live in the public Python layer, so a call
    for an already active path is a no-op rather than a second backend handle.
    """
    cdef bytes path_bytes = font_path.encode("utf-8")
    cdef char* error = NULL
    cdef char* rollback_error = NULL
    cdef int success

    with _backend_lock:
        if font_path in _active_paths:
            return True
        success = manimpango_register_font(<const char*>path_bytes, &error)
        if not success:
            _raise_backend_error(error)
        _active_paths.add(font_path)
        try:
            _rebuild_managed_font_map()
        except:
            # A native registration without a managed-map entry would let a
            # later registration observe state for which no public handle was
            # returned.  Undo it before propagating the map error.
            _active_paths.remove(font_path)
            rollback_error = NULL
            success = manimpango_unregister_font(<const char*>path_bytes, &rollback_error)
            if rollback_error != NULL:
                g_free(rollback_error)
            if sys.platform.startswith("linux"):
                for active_path in sorted(_active_paths):
                    active_path_bytes = active_path.encode("utf-8")
                    rollback_error = NULL
                    success = manimpango_register_font(
                        <const char*>active_path_bytes, &rollback_error
                    )
                    if rollback_error != NULL:
                        g_free(rollback_error)
            raise
    return True


cpdef bint unregister_font(str font_path):
    """Remove one native registration after its final public handle closes."""
    cdef bytes path_bytes = font_path.encode("utf-8")
    cdef bytes active_path_bytes
    cdef char* error = NULL
    cdef char* rollback_error = NULL
    cdef int success
    cdef str active_path

    with _backend_lock:
        if font_path not in _active_paths:
            return True

        # On Fontconfig this clears every application font.  Re-add the paths
        # still active while holding the same lock, so closing one handle never
        # drops a different registered family.
        success = manimpango_unregister_font(<const char*>path_bytes, &error)
        if not success:
            _raise_backend_error(error)
        _active_paths.remove(font_path)
        if sys.platform.startswith("linux"):
            for active_path in sorted(_active_paths):
                active_path_bytes = active_path.encode("utf-8")
                error = NULL
                success = manimpango_register_font(<const char*>active_path_bytes, &error)
                if not success:
                    _raise_backend_error(error)
        try:
            # Construct this only after native removal.  CoreText font maps
            # snapshot the process registry during construction.
            _rebuild_managed_font_map()
        except:
            _active_paths.add(font_path)
            if sys.platform.startswith("linux"):
                # The failed native unregister cleared every app font; rebuild
                # the native set from the restored active-path snapshot.
                rollback_error = NULL
                manimpango_unregister_font(<const char*>path_bytes, &rollback_error)
                if rollback_error != NULL:
                    g_free(rollback_error)
                for active_path in sorted(_active_paths):
                    active_path_bytes = active_path.encode("utf-8")
                    rollback_error = NULL
                    manimpango_register_font(
                        <const char*>active_path_bytes, &rollback_error
                    )
                    if rollback_error != NULL:
                        g_free(rollback_error)
            else:
                rollback_error = NULL
                manimpango_register_font(<const char*>path_bytes, &rollback_error)
                if rollback_error != NULL:
                    g_free(rollback_error)
            raise
    return True


cpdef list list_fonts():
    """Return unique UTF-8 family names known to a fresh Pango font map."""
    cdef PangoFontMap* fontmap = NULL
    cdef PangoFontFamily** families = NULL
    cdef int n_families = 0
    cdef int i
    cdef const char* name_ptr
    cdef set family_names = set()

    with _backend_lock:
        fontmap = acquire_font_map()
        if fontmap == NULL:
            raise MemoryError("Failed to create PangoFontMap")
        try:
            pango_font_map_list_families(fontmap, &families, &n_families)
            for i in range(n_families):
                name_ptr = pango_font_family_get_name(families[i])
                if name_ptr != NULL:
                    family_names.add((<bytes>name_ptr).decode("utf-8", "replace"))
        finally:
            # Pango transfers the GList-style pointer array to the caller.
            if families != NULL:
                g_free(families)
            if fontmap != NULL:
                g_object_unref(fontmap)

    return sorted(family_names)
