Quick Start
===========

Installation
------------

Install ManimPango from PyPI::

    pip install manimpango

ManimPango requires Pango 1.44 or newer and Cairo.  On most Linux
distributions these are available through the package manager.  On macOS,
install them with `Homebrew <https://brew.sh/>`_::

    brew install pango cairo

Rendering Plain Text
--------------------

Use :func:`~manimpango.render` for plain text.  It returns a
:class:`~manimpango.RenderedText` object containing SVG and layout metadata.

.. code-block:: python

    import manimpango

    result = manimpango.render("Hello, world!", size=24.0)
    svg = result.svg
    result.save("hello.svg")

``save()`` writes to an existing parent directory; it does not create missing
directories.

Rendering Markup
----------------

Pango markup has its own entry point.  Do not pass markup to ``render()``.

.. code-block:: python

    result = manimpango.render_markup(
        "<span foreground='red' weight='bold'>Important</span>",
        font="Helvetica",
        size=24.0,
    )

Styling Plain Text with Spans
-----------------------------

Use :class:`~manimpango.TextSpan` for styled ranges in plain text.  Span
offsets are Python code-point offsets and are half-open, just like string
slices.  Spans and markup are deliberately separate APIs.

.. code-block:: python

    text = "Hello, world!"
    result = manimpango.render(
        text,
        spans=(
            manimpango.TextSpan(0, 5, weight=manimpango.Weight.BOLD),
            manimpango.TextSpan(7, 12, foreground="#3366cc"),
        ),
    )

Layout Metadata
---------------

All geometry exposed by ManimPango is a ``float`` in SVG user-space units.
``Bounds`` records an ``x``, ``y``, ``width``, and ``height`` in that same
coordinate system.  ``LineInfo`` contains the rendered line text, its
half-open code-point range, bounds, and baseline.

.. code-block:: python

    result = manimpango.render("Line 1\nLine 2", width=200.0)

    print(result.width, result.height, result.baseline)
    print(result.ink_bounds, result.logical_bounds)
    for line in result.lines:
        print(line.text, line.start, line.end, line.bounds, line.baseline)

Variable Fonts
--------------

``weight`` accepts a :class:`~manimpango.Weight` member or an integer from
1 through 1000.  Use ``variations`` for OpenType axes; axis tags contain
exactly four ASCII characters.

.. code-block:: python

    result = manimpango.render(
        "Smooth weight",
        font="Inter",
        weight=450,
        variations={"wght": 650, "wdth": 90},
    )

Custom Fonts
------------

:func:`~manimpango.register_font` returns a
:class:`~manimpango.FontRegistration` handle.  Use it as a context manager
so the registration closes predictably.  Multiple handles for a path are
reference-safe; closing one does not release the font while another remains
open.

.. code-block:: python

    with manimpango.register_font("path/to/MyFont.ttf") as registration:
        assert not registration.closed
        result = manimpango.render("Custom font", font="My Font")

    assert registration.closed
