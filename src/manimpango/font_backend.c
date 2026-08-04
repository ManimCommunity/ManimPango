#include "font_backend.h"

#include <glib.h>
#include <pango/pangocairo.h>
#include <string.h>

#ifdef __APPLE__
#include <CoreFoundation/CoreFoundation.h>
#include <CoreText/CoreText.h>
#elif defined(_WIN32)
#include <windows.h>
#elif defined(__linux__)
#include <fontconfig/fontconfig.h>
#include <pango/pangofc-fontmap.h>
#endif

static void
set_error(char **error, const char *message)
{
    if (error != NULL) {
        *error = g_strdup(message);
    }
}


#ifdef __APPLE__
static void
set_cferror(char **error, CFErrorRef cferror)
{
    CFStringRef description;
    CFIndex length;
    CFIndex capacity;
    char *utf8;

    if (cferror == NULL) {
        set_error(error, "CoreText rejected the font without an error description");
        return;
    }

    description = CFErrorCopyDescription(cferror);
    if (description == NULL) {
        set_error(error, "CoreText returned an unreadable error description");
        return;
    }
    length = CFStringGetLength(description);
    capacity = CFStringGetMaximumSizeForEncoding(length, kCFStringEncodingUTF8) + 1;
    utf8 = g_malloc((gsize)capacity);
    if (utf8 == NULL || !CFStringGetCString(description, utf8, capacity, kCFStringEncodingUTF8)) {
        g_free(utf8);
        set_error(error, "CoreText returned a non-UTF-8 error description");
    } else if (error != NULL) {
        *error = utf8;
    } else {
        g_free(utf8);
    }
    CFRelease(description);
}

static int
coretext_change_font(const char *utf8_path, gboolean register_font, char **error)
{
    CFURLRef url;
    CFErrorRef cferror = NULL;
    Boolean success;

    url = CFURLCreateFromFileSystemRepresentation(
        kCFAllocatorDefault,
        (const UInt8 *)utf8_path,
        (CFIndex)strlen(utf8_path),
        false);
    if (url == NULL) {
        set_error(error, "could not create a CoreText URL from the font path");
        return 0;
    }
    if (register_font) {
        success = CTFontManagerRegisterFontsForURL(url, kCTFontManagerScopeProcess, &cferror);
    } else {
        success = CTFontManagerUnregisterFontsForURL(url, kCTFontManagerScopeProcess, &cferror);
    }
    CFRelease(url);
    if (!success) {
        set_cferror(error, cferror);
        if (cferror != NULL) {
            CFRelease(cferror);
        }
        return 0;
    }
    return 1;
}
#endif

#ifdef _WIN32
static wchar_t *
utf8_path_to_wide(const char *utf8_path, char **error)
{
    int length;
    wchar_t *wide_path;

    length = MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, utf8_path, -1, NULL, 0);
    if (length == 0) {
        set_error(error, "font path is not valid UTF-8");
        return NULL;
    }
    wide_path = g_new(wchar_t, length);
    if (wide_path == NULL) {
        set_error(error, "could not allocate a wide font path");
        return NULL;
    }
    if (MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, utf8_path, -1, wide_path, length) == 0) {
        g_free(wide_path);
        set_error(error, "could not convert the UTF-8 font path to UTF-16");
        return NULL;
    }
    return wide_path;
}

static void
set_win32_error(char **error, DWORD code)
{
    wchar_t *wide_message = NULL;
    char *utf8_message;
    int length;

    if (FormatMessageW(
            FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
            NULL,
            code,
            0,
            (wchar_t *)&wide_message,
            0,
            NULL) == 0) {
        if (error != NULL) {
            *error = g_strdup_printf("Win32 font API failed (error %lu)", (unsigned long)code);
        }
        return;
    }
    length = WideCharToMultiByte(CP_UTF8, 0, wide_message, -1, NULL, 0, NULL, NULL);
    if (length == 0) {
        LocalFree(wide_message);
        if (error != NULL) {
            *error = g_strdup_printf("Win32 font API failed (error %lu)", (unsigned long)code);
        }
        return;
    }
    utf8_message = g_malloc((gsize)length);
    if (utf8_message == NULL ||
        WideCharToMultiByte(CP_UTF8, 0, wide_message, -1, utf8_message, length, NULL, NULL) == 0) {
        g_free(utf8_message);
        LocalFree(wide_message);
        if (error != NULL) {
            *error = g_strdup_printf("Win32 font API failed (error %lu)", (unsigned long)code);
        }
        return;
    }
    LocalFree(wide_message);
    if (error != NULL) {
        *error = utf8_message;
    } else {
        g_free(utf8_message);
    }
}
#endif

int
manimpango_register_font(const char *utf8_path, char **error)
{
    if (error != NULL) {
        *error = NULL;
    }
#ifdef __APPLE__
    return coretext_change_font(utf8_path, TRUE, error);
#elif defined(_WIN32)
    wchar_t *wide_path = utf8_path_to_wide(utf8_path, error);
    int font_count;
    if (wide_path == NULL) {
        return 0;
    }
    font_count = AddFontResourceExW(wide_path, FR_PRIVATE, NULL);
    g_free(wide_path);
    if (font_count == 0) {
        set_win32_error(error, GetLastError());
        return 0;
    }
    return 1;
#elif defined(__linux__)
    /* Linux registrations are materialized into a renderer-private
     * Fontconfig configuration in manimpango_build_font_map().  Touching the
     * process default configuration here would make one renderer's lifetime
     * affect application fonts owned by unrelated libraries. */
    (void)utf8_path;
    return 1;
#else
    set_error(error, "font registration is unsupported on this platform");
    return 0;
#endif
}

int
manimpango_unregister_font(const char *utf8_path, char **error)
{
    (void)utf8_path;
    if (error != NULL) {
        *error = NULL;
    }
#ifdef __APPLE__
    return coretext_change_font(utf8_path, FALSE, error);
#elif defined(_WIN32)
    wchar_t *wide_path = utf8_path_to_wide(utf8_path, error);
    BOOL removed;
    if (wide_path == NULL) {
        return 0;
    }
    removed = RemoveFontResourceExW(wide_path, FR_PRIVATE, NULL);
    g_free(wide_path);
    if (!removed) {
        set_win32_error(error, GetLastError());
        return 0;
    }
    return 1;
#elif defined(__linux__)
    /* See manimpango_register_font(): Linux font state belongs to the map. */
    return 1;
#else
    set_error(error, "font unregistration is unsupported on this platform");
    return 0;
#endif
}

PangoFontMap *
manimpango_build_font_map(const char *const *utf8_paths, size_t count, char **error)
{
    PangoFontMap *new_map;
    size_t i;

#if defined(_WIN32) && PANGO_VERSION_CHECK(1, 56, 0)
    GError *gerror = NULL;
#endif

    if (error != NULL) {
        *error = NULL;
    }
    new_map = pango_cairo_font_map_new();
    if (new_map == NULL) {
        set_error(error, "could not create the managed Pango Cairo font map");
        return NULL;
    }
#if defined(__linux__)
    {
        FcConfig *config = FcConfigCreate();

        if (config == NULL) {
            set_error(error, "could not create a private Fontconfig configuration");
            g_object_unref(new_map);
            return NULL;
        }
        /* NULL loads the same default configuration files that FcInit uses,
         * but into this independent configuration.  Build its system-font
         * database before adding our transient application fonts. */
        if (!FcConfigParseAndLoad(config, NULL, FcTrue) ||
            !FcConfigBuildFonts(config)) {
            set_error(error, "could not load the private Fontconfig configuration");
            FcConfigDestroy(config);
            g_object_unref(new_map);
            return NULL;
        }
        for (i = 0; i < count; i++) {
            if (!FcConfigAppFontAddFile(config, (const FcChar8 *)utf8_paths[i])) {
                set_error(error, "Fontconfig rejected the font file");
                FcConfigDestroy(config);
                g_object_unref(new_map);
                return NULL;
            }
        }
        /* On Linux PangoCairo's map is a PangoFcFontMap.  The setter retains
         * its own config reference, so release our construction reference. */
        pango_fc_font_map_set_config(PANGO_FC_FONT_MAP(new_map), config);
        FcConfigDestroy(config);
        return new_map;
    }
#endif
    for (i = 0; i < count; i++) {
#if defined(_WIN32) && PANGO_VERSION_CHECK(1, 56, 0)
        if (!pango_font_map_add_font_file(new_map, utf8_paths[i], &gerror)) {
            if (error != NULL && gerror != NULL) {
                *error = g_strdup(gerror->message);
            } else {
                set_error(error, "Pango could not load a registered font file");
            }
            if (gerror != NULL) {
                g_error_free(gerror);
            }
            g_object_unref(new_map);
            return NULL;
        }
#elif defined(_WIN32)
        /* PangoWin32 needs the 1.56 DirectWrite font-map API to keep private
         * files usable after its process-wide DirectWrite cache is initialized. */
        set_error(error, "Windows private fonts require Pango 1.56 or newer");
        g_object_unref(new_map);
        return NULL;
#else
        /* Native Fontconfig/CoreText registration is visible to a newly
         * created map on older supported Pango versions. */
        (void)utf8_paths[i];
#endif
    }

    return new_map;
}
