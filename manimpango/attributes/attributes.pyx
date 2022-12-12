from pango cimport *
from pango_attributes cimport *


def covert_hex_to_rbg(color_hex: str):
    cdef PangoColor color
    if not pango_color_parse(&color, color_hex.encode('utf-8')):
        raise ValueError('Invalid color specfied.')
    return color.red, color.green, color.blue
