cdef extern from "glib.h":
    ctypedef void* gpointer
    ctypedef int gint
    ctypedef unsigned int guint
    ctypedef gint gboolean
    ctypedef unsigned short guint16
    ctypedef char gchar
    ctypedef struct GError:
        gint code
        gchar *message
    void g_error_free (GError *error)
    void g_object_unref(gpointer object)
    void g_free(gpointer mem)

    # GQueue is used while gathering pango attributes
    # internally. It's way better than implementing one
    # ourselves.

    ctypedef struct GQueue:
        guint length
    GQueue* g_queue_new ()
    void g_queue_free (
        GQueue* queue,
    )
    bint g_queue_is_empty (
        GQueue* queue
    )

    # Insert at last and pop from first
    void g_queue_push_tail (
        GQueue* queue,
        gpointer data,
    )
    gpointer g_queue_pop_head (
        GQueue* queue,
    )
