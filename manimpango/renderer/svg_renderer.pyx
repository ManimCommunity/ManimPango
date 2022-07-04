import typing as T
from ..layout import Layout

include "cairo_utils.pxi"

cdef class SVGRenderer:
    def __cinit__(
        self,
        file_name: str,
        width: float,
        height: float,
        layout: Layout
    ):
        surface = cairo_svg_surface_create(
            file_name.encode("utf-8"),
            width,
            height
        )
        if surface == NULL:
            raise MemoryError("Cairo.SVGSurface can't be created.")
        self.cairo_surface = surface
        self.cairo_context = create_cairo_context_from_surface(surface)
        self.pango_layout = create_pango_layout(self.cairo_context)
        self.pango_font_desc = create_font_desc()

    def __init__(
        self,
        file_name: str,
        width: float,
        height: float,
        layout: Layout
    ):
        self.file_name = file_name
        self.width = width
        self.height = height
        self.py_layout = layout
        self.py_font_desc = layout.font_desc

    cdef start_renderering(self):
        pylayout_to_pango_layout(self.pango_layout, self.py_layout)
        pyfontdesc_to_pango_font_desc(self.pango_font_desc, self.py_font_desc)
        pango_layout_set_font_description(
            self.pango_layout,
            self.pango_font_desc
        )
        # Check if the context is fine
        _err = is_context_fine(self.cairo_context)
        if _err != "":
            raise Exception(_err)

        # Assign the font description to the layout
        pango_layout_set_font_description(self.pango_layout,
            self.pango_font_desc)

        # Render the actual layout into the cairo context
        pango_cairo_show_layout(self.cairo_context,
            self.pango_layout)

        # Check if the context is fine again
        _err = is_context_fine(self.cairo_context)
        if _err != "":
            raise Exception(_err)

    cpdef render(self):
        self.start_renderering()

    def __dealloc__(self):
        g_object_unref(self.pango_layout)
        cairo_destroy(self.cairo_context)
        cairo_surface_destroy(self.cairo_surface)
        pango_font_description_free(self.pango_font_desc)
