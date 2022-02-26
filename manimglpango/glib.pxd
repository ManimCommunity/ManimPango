cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef gint gboolean
    ctypedef char gchar
    ctypedef struct GError:
        gint code
        gchar *message

    void g_error_free(GError *error)
    void g_object_unref(gpointer object)
    void g_free(gpointer mem)
