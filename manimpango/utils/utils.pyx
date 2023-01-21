from pango cimport *


cpdef str validate_markup(str text):
    cdef GError *err = NULL
    text_bytes = text.encode("utf-8")
    res = pango_parse_markup(
        text_bytes,
        -1,
        0,
        NULL,
        NULL,
        NULL,
        &err
    )
    if res:
        return ""
    else:
        message = <bytes>err.message
        g_error_free(err)
        return message.decode('utf-8')

def covert_hex_to_rbg(color_hex: str):
    cdef PangoColor color
    if not pango_color_parse(&color, color_hex.encode('utf-8')):
        raise ValueError('Invalid color specfied.')
    return color.red, color.green, color.blue
