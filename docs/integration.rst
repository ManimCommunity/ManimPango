Integrations
============

ManimPango is designed to be used with other libraries. It provides
utilities for rendering text to images, but only supports rendering
PNG or SVG images. For renderering to other formats, you can use
various other libraries such as `PIL <https://pillow.readthedocs.io/en/stable/>`_.

Integration with Pillow
-----------------------

The following example shows how to create a Pillow image from a
:class:`Layout` object.

.. code-block:: python

    import manimpango as mp
    from PIL import Image

    layout = mp.Layout(
        "Hello World",
        font_desc=mp.FontDescription.from_string("Georgia 80")
    )
    bbox = layout.get_bounding_box()
    renderer = mp.ImageRenderer(*bbox[2:], layout)

    renderer.render()
    img = Image.frombuffer(
        "RGBA",
        (renderer.width, renderer.height),
        bytes(renderer.get_buffer()),
        "raw",
        "BGRa",
        renderer.stride,
    )

    # Now you can save the image or open it
    img.show()

Integration with NumPy
----------------------

The following example shows how to create a NumPy array from a
:class:`Layout` object.

.. code-block:: python

    import manimpango as mp
    import numpy as np

    layout = mp.Layout(
        "Hello World",
        font_desc=mp.FontDescription.from_string("Georgia 80")
    )
    bbox = layout.get_bounding_box()

    renderer = mp.ImageRenderer(*bbox[2:], layout)
    renderer.render()

    # Create a numpy array from the buffer
    arr = np.ndarray(
        shape=(renderer.height, renderer.width),
        dtype=np.uint32,
        buffer=renderer.get_buffer(),
    )

    print(arr)

Integration with ModernGL
-------------------------

The following example shows how to create a ModernGL texture from a
:class:`Layout` object.

.. code-block:: python

    import manimpango as mp
    import moderngl

    layout = mp.Layout(
        "Hello World",
        font_desc=mp.FontDescription.from_string("Georgia 80")
    )
    bbox = layout.get_bounding_box()

    renderer = mp.ImageRenderer(*bbox[2:], layout)
    renderer.render()

    # Create a ModernGL texture from the buffer
    ctx = moderngl.create_standalone_context(standalone=True)
    texture = ctx.texture(
        (renderer.width, renderer.height),
        4,
        renderer.get_buffer(),
    )
