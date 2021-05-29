cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    ctypedef char gchar
    void g_object_unref(gpointer object)
    void g_free(gpointer mem)
    void g_set_prgname(const gchar *prgname)
    ctypedef struct GError:
        gint code
        gchar *message
    void g_error_free (GError *error)
