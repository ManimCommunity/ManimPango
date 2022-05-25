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

    def __init__(
        self,
        file_name: str,
        width: float,
        height: float,
        layout: Layout,
        font_desc: FontDescription
    ):
        self.file_name = file_name
        self.width = width
        self.height = height
        self.py_layout = layout

    cdef start_renderering(self):
        pylayout_to_pango_layout(self.pango_layout, self.py_layout)
        pango_layout_set_font_description(
            self.pango_layout,
            const PangoFontDescription* desc
        )


    def __dealloc__(self):
        cairo_destroy(self.cairo_context)
        cairo_surface_destroy(self.cairo_surface)
        g_object_unref(self.pango_layout)

