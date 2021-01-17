cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    ctypedef char gchar
    void g_free(gpointer mem)
    void g_object_unref(gpointer object)