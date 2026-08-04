#ifndef MANIMPANGO_FONT_BACKEND_H
#define MANIMPANGO_FONT_BACKEND_H

/*
 * Register a font for this process.  On failure, *error receives a newly
 * allocated UTF-8 message which the caller must release with g_free().
 */
int manimpango_register_font(const char *utf8_path, char **error);
int manimpango_unregister_font(const char *utf8_path, char **error);

#endif
