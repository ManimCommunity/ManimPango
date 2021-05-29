import typing as T
from ..exceptions import CairoException
from ..layout import Layout
cdef class CairoRenderer:
    # This class should contain things
    # should provide API to render to an SVG
    # or get the buffer.
    def __init__(self):
        pass
    cdef void* intialise_renderer(self):
        pass
    cdef void* start_rendering(self):
        self.convert_py_font_to_pango_font()
        self.convert_py_layout_to_pango_layout()

    cdef void* finalise_renderer(self):
        pass
    cpdef bint render(self):
        self.intialise_renderer()
        self.start_rendering()
        self.finalise_renderer()
        return True

    cdef str is_context_fine(self, raise_error=True):
        cdef cairo_status_t status
        status = cairo_status(self.context)
        if status == CAIRO_STATUS_NO_MEMORY:
            cairo_destroy(self.context)
            cairo_surface_destroy(self.surface)
            g_object_unref(self.layout)
            raise MemoryError("Cairo isn't finding memory")
        elif status != CAIRO_STATUS_SUCCESS:
            temp_bytes = <bytes>cairo_status_to_string(status)
            if raise_error:
                raise CairoException(temp_bytes.decode('utf-8'))
            return temp_bytes.decode('utf-8')
        return ""

    cdef void* convert_py_font_to_pango_font(self):
        py_fontdesc = self.py_layout.font_properties
        cdef PangoFontDescription* font_desc = pango_font_description_new()
        if not py_fontdesc:
            return NULL
        if py_fontdesc.family:
            pango_font_description_set_family(
                font_desc,
                py_fontdesc.family.encode('utf-8'),
            )
        if py_fontdesc.size:
            pango_font_description_set_size(
                font_desc,
                pango_units_from_double(py_fontdesc.size),
            )
        if py_fontdesc.style:
            pango_font_description_set_style(
                font_desc,
                py_fontdesc.style.value,
            )
        if py_fontdesc.variant:
            pango_font_description_set_variant(
                font_desc,
                py_fontdesc.variant.value
            )
        if py_fontdesc.weight:
            pango_font_description_set_weight(
                font_desc,
                py_fontdesc.weight.value
            )
        self.font_desc = font_desc

    cdef void* convert_py_layout_to_pango_layout(self):
        py_layout = self.py_layout
        layout = self.layout
        if py_layout.text:
            pango_layout_set_text(
                layout,
                py_layout.text.encode('utf-8'),
                -1,
            )
        if py_layout.width:
            pango_layout_set_width(
                layout,
                pango_units_from_double(py_layout.width),
            )
        if py_layout.height:
            if py_layout.height > 0:
                pango_layout_set_height(
                    layout,
                    pango_units_from_double(py_layout.height),
                )
            else:
                pango_layout_set_height(
                    layout,
                    py_layout.height,
                )
        if py_layout.alignment:
            pango_layout_set_alignment(
                layout,
                py_layout.alignment.value,
            )
        if py_layout.auto_dir:
            pango_layout_set_auto_dir(
                layout,
                py_layout.auto_dir,
            )
        if py_layout.markup:
            pango_layout_set_markup(
                layout,
                py_layout.markup.encode('utf-8'),
                -1
            )
        if py_layout.indent:
            pango_layout_set_indent(
                layout,
                pango_units_from_double(py_layout.indent)
            )
        if py_layout.spacing:
            pango_layout_set_spacing(
                layout,
                pango_units_from_double(py_layout.spacing)
            )
        if py_layout.line_spacing:
            pango_layout_set_line_spacing(
                layout,
                py_layout.line_spacing
            )
        if py_layout.justify:
            pango_layout_set_justify(
                layout,
                py_layout.justify
            )

cdef class SVGRenderer(CairoRenderer):
    def __init__(self, file_name: str, width:int, height:int, layout: Layout, move_to: T.Tuple[int,int] = (0,0)):
        self.file_name = file_name
        self.width = width
        self.height = height
        self.move_to = move_to
        self.py_layout = layout

    cdef void* intialise_renderer(self):
        move_to = self.move_to
        file_name = self.file_name
        width = self.width
        height = self.height
        surface = cairo_svg_surface_create(
            file_name.encode("utf-8"),
            width,
            height
        )
        if surface == NULL:
            raise MemoryError("Cairo.SVGSurface can't be created.")
        context = cairo_create(surface)

        # Now set the created things as attributes.
        self.surface = surface
        self.context = context

        self.is_context_fine()

        cairo_move_to(context, move_to[0], move_to[1])

        # Create a Pango layout.
        layout = pango_cairo_create_layout(context)
        if layout==NULL:
            cairo_destroy(context)
            cairo_surface_destroy(surface)
            raise MemoryError("Pango.Layout can't be created from Cairo Context.")
        self.layout = layout

    cdef void* start_rendering(self):
        self.convert_py_font_to_pango_font()
        self.convert_py_layout_to_pango_layout()
        cdef cairo_t* context
        cdef cairo_surface_t* surface
        cdef PangoLayout* layout
        # check whether cairo is happy till now
        # else error out or it may create SegFaults.
        self.is_context_fine()

        context = self.context
        surface = self.surface
        layout = self.layout
        py_layout = self.layout


        pango_cairo_show_layout(context, layout)

        # check for status again
        self.is_context_fine()

    cdef void* finalise_renderer(self):
        g_object_unref(self.layout)
        cairo_destroy(self.context)
        cairo_surface_destroy(self.surface)

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self):
        raise NotImplementedError
