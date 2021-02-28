cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    void g_object_unref(gpointer object)
    void g_free(gpointer mem)
