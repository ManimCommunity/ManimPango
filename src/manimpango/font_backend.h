#ifndef MANIMPANGO_FONT_BACKEND_H
#define MANIMPANGO_FONT_BACKEND_H

#include <stddef.h>
#include <pango/pango.h>

/*
 * Register a font for this renderer. On failure, *error receives a newly
 * allocated UTF-8 message which the caller must release with g_free().
 */
int manimpango_register_font(const char *utf8_path, char **error);
int manimpango_unregister_font(const char *utf8_path, char **error);
PangoFontMap *manimpango_build_font_map(const char *const *utf8_paths, size_t count, char **error);

#endif
