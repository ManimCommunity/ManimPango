from pango cimport *
from pango_attributes cimport *

from manimpango.attributes import TextAttribute


cdef PangoAttribute* raise_on_null_attr(PangoAttribute* ptr):
    if not ptr:
        raise MemoryError("Could not allocate memory for attribute")
    return ptr

cdef set_indexes(PangoAttribute* attr, start_index: int, end_index: int):
    """Sets the start and end indexes of a PangoAttribute.

    Parameters
    ----------
    attr
        The PangoAttribute to set the indexes for.
    start_index
        The start index.
    end_index
        The end index.
    """
    if start_index is not None:
        attr.start_index = start_index
    if end_index != -1:
        attr.end_index = end_index

cdef insert_into_queue(
    GQueue* queue,
    PangoAttribute* attr,
    start_index: int,
    end_index: int,
):
    """Inserts a PangoAttribute into a PangoAttrList.

    Parameters
    ----------
    queue
        The GQueue to insert the attribute into.
    attr
        The PangoAttribute to insert.
    """
    set_indexes(attr, start_index, end_index)
    g_queue_push_tail(queue, attr)

cdef GQueue* create_attr_list_for_attribute (
    attr: TextAttribute,
):
    """Creates a GQueue from a TextAttribute. The Queue will contain a list
    of PangoAttributes.

    Multiple PangoAttributes are to be created for a single TextAttribute. That's
    because for a given `start` and `end` index value, the user can set various
    attributes like `color`, `font`, `size`, etc. So, we need to create a
    PangoAttribute for each of these attributes. Finally, we add all these
    PangoAttributes to a Queue and return it.

    Note: the caller is responsible for freeing the returned GQueue as well as
    the created attributes.

    Parameters
    ----------
    attr
        The TextAttribute to convert.
    """
    cdef PangoAttribute* pango_attr = NULL
    cdef GQueue* queue = g_queue_new()
    if not queue:
        raise MemoryError("Could not allocate memory for GQueue.")

    # allow_breaks
    if attr.allow_breaks is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_allow_breaks_new(attr.allow_breaks))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # background_alpha
    if attr.background_alpha is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_background_alpha_new(attr.background_alpha))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # background_color
    if attr.background_color is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_background_new(
                attr.background_color[0],
                attr.background_color[1],
                attr.background_color[2],
            ),
        )
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # foreground_alpha
    if attr.foreground_alpha is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_foreground_alpha_new(attr.foreground_alpha))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # foreground_color
    if attr.foreground_color is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_foreground_new(
                attr.foreground_color[0],
                attr.foreground_color[1],
                attr.foreground_color[2],
            ),
        )
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # fallback
    if attr.fallback is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_fallback_new(attr.fallback))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # family
    if attr.family is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_family_new(
                attr.family.encode("utf-8")
        ))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # weight
    if attr.weight is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_weight_new(attr.weight.value))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    # line height
    if attr.line_height is not None:
        pango_attr = raise_on_null_attr(
            pango_attr_line_height_new(attr.line_height))
        insert_into_queue(
            queue,
            pango_attr,
            attr.start_index,
            attr.end_index,
        )

    return queue


cdef convert_to_pango_attributes(
    attrs: list[TextAttribute],
    PangoAttrList* pango_attr_list
):
    """Converts a list of TextAttributes to a PangoAttribute.

    Note: the caller owns pango_attrlist and is responsible for freeing it.

    Parameters
    ----------
    attrs
        The list of TextAttributes to convert.
    pango_attrlist
        The PangoAttrList to add the attributes to.
    """
    cdef GQueue* temp_queue = NULL;
    cdef PangoAttribute* temp_attr = NULL;

    if not pango_attr_list:
        raise ValueError("pango_attr_list must not be NULL.")

    # Use pango_attr_list_change() to add the attributes to the list.
    for attr in attrs:
        temp_queue = create_attr_list_for_attribute(attr)
        if not temp_queue:
            raise MemoryError("holy shit")
        while not g_queue_is_empty(temp_queue):
            temp_attr = <PangoAttribute*>g_queue_pop_head(temp_queue)
            pango_attr_list_insert(
                pango_attr_list,
                temp_attr
            )
            # Don't free the attribute
        g_queue_free (temp_queue)
