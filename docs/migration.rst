Migration Guide
===============

ManimPango 1.0 is a hard API break.  The former utility classes and
path-based font-unregistration API are gone; migrate callers to the public
functions and immutable result models below.

Rendering APIs
--------------

``render()`` accepts plain text only.  Use ``render_markup()`` for raw Pango
markup; plain and markup rendering are separate entry points.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Previous pattern
     - 1.0 replacement
   * - Plain text renderer
     - :func:`render`
   * - Markup renderer
     - :func:`render_markup`
   * - Markup validation
     - :func:`validate_markup` or :class:`MarkupError` from ``render_markup``
   * - Range styling
     - :class:`TextSpan` passed to :func:`render`

.. code-block:: python

    # Plain text with structured styling.
    result = manimpango.render(
        "Hello world",
        spans=(
            manimpango.TextSpan(0, 5, foreground="#3366cc"),
            manimpango.TextSpan(6, 11, style=manimpango.Style.ITALIC),
        ),
    )

    # Raw Pango markup uses a different entry point.
    marked = manimpango.render_markup("<b>Hello</b> <i>world</i>")

``TextSpan.start`` and ``TextSpan.end`` are half-open Python code-point
offsets.  Overlapping spans compose when they affect different attributes;
conflicting values for the same attribute raise ``ValueError``.

Result Metadata
---------------

``render()`` and ``render_markup()`` return a frozen, slotted
:class:`~manimpango.RenderedText`.  Geometry is always expressed in SVG
user-space units, not pixels or raw Pango units.  The former synthetic
line-spacing value and mutable underscore-backed fields have been removed.

.. code-block:: python

    result = manimpango.render("one\ntwo", width=200.0)

    print(result.width, result.height, result.baseline)
    print(result.ink_bounds, result.logical_bounds)
    for line in result.lines:
        # Ranges exclude newline separators.
        print(line.text, line.start, line.end, line.bounds, line.baseline)

``result.lines`` is a tuple of :class:`~manimpango.LineInfo` instances.
``result.line_count`` is derived from its length.  Both layout bounds and
per-line bounds use the same transformed coordinate system as the SVG.

Saving SVG
----------

``RenderedText.save(path)`` writes UTF-8 SVG to ``path``.  The parent
directory must already exist; missing parents raise ``FileNotFoundError``.

Font Registration
-----------------

Registration has explicit ownership through a handle.

.. code-block:: python

    with manimpango.register_font("path/to/font.ttf") as registration:
        result = manimpango.render("Example", font="My Font")

    assert registration.closed

Missing files raise :class:`~manimpango.FontNotFoundError`; other backend
registration failures raise :class:`~manimpango.FontRegistrationError`.
