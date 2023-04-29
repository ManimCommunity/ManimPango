Examples
========

Simple Example
--------------

The simplest way to render a text into a image create a new instance of
:class:`Layout` and then a renderer and call the :meth:`Layout.render`.

.. code-block:: python

    from manimpango import *
    l = Layout("Hello World")
    r = ImageRenderer(400, 400, l, "test.png")
    r.render()
    r.save()

This will create a 400x400 image with the text "Hello World" in it at the
position (0, 0) in the image.

Calculating Bounding Box
------------------------

The bounding box of the text can be obtained by calling the
:meth:`Layout.get_bounding_box` method. This will return a tuple of the
form ``(x, y, width, height)``.

.. code-block:: python

    >>> from manimpango import *
    >>> l = Layout("Hello World")
    >>> print(l.get_bounding_box())
    (0, 0, 90, 19)

The bounding box is the smallest rectangle that contains all the glyphs
of the text.
