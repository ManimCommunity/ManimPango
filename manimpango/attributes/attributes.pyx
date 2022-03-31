from pango_attributes cimport *
from pango cimport *

def parse_color(color_hex: str):
    cdef PangoColor color
    if not pango_color_parse(&color, color_hex.encode('utf-8')):
        raise ValueError('Invalid color specfied.')
    return color.red, color.green, color.blue
