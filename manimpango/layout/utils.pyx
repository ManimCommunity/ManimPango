
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
