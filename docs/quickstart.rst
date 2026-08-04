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

The Windows and macOS wheels bundle their native dependencies. Source builds
on Windows need Pango 1.56 or newer to register private font files at runtime.
Linux has no binary wheels at present, so installation there builds from
source and requires a C compiler, ``pkg-config``, and the Pango development
headers.

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

Understanding ``RenderedText``
------------------------------

Both rendering functions return a
:class:`~manimpango.RenderedText` object rather than writing a temporary file.
It keeps the SVG document and the layout result together, so callers can
choose whether to keep the SVG in memory, save it, or inspect its geometry.

The basic result contract is executable and independent of the host's font
metrics:

.. doctest::

    >>> import manimpango
    >>> result = manimpango.render("Hello, world!", size=24.0)
    >>> type(result).__name__
    'RenderedText'
    >>> result.line_count
    1
    >>> isinstance(result.svg, str) and result.width > 0 and result.height > 0
    True

For example, one macOS/Pango installation produces the following selected
values.  The exact numbers vary with the selected font and native backend;
the relationships and SVG user-space units do not.

.. code-block:: pycon

    >>> round(result.width, 1), round(result.height, 1), round(result.baseline, 1)
    (173.0, 32.0, 24.0)
    >>> result.ink_bounds
    Bounds(x=0.515625, y=2.0625, width=169.109375, height=26.5)
    >>> result.logical_bounds
    Bounds(x=0.0, y=0.0, width=173.0, height=32.0)

``width`` and ``height`` are the rendered SVG viewport dimensions, and
``baseline`` is the first line's baseline position.  ``ink_bounds`` is tight
to glyph drawing, so it excludes the side bearings and whitespace visible in
``logical_bounds``.  All of these values, as well as font ``size`` and an
optional layout ``width``, are ``float`` values in SVG user-space units—not
raw Pango units or device pixels.  An SVG consumer may subsequently scale the
document.

The complete SVG is available without another render operation, and may be
written only when a file is needed:

.. code-block:: python

    svg = result.svg
    result.save("hello.svg")

``RenderedText`` is immutable and ``result.lines`` is a tuple.  Its
``lines`` describe the parsed text, code-point ranges, bounds, and baselines
for individual lines.  The following section shows how to inspect them.

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

Inspecting Layout Metadata
--------------------------

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
exactly four ASCII characters.  Visible variation-axis effects currently
require Pango's fontconfig backend (normally Linux); macOS and Windows do not
apply them with their default backends.

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
