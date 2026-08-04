Changelog
=========

1.0
---

Architecture and breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ManimPango 1.0 is a hard break from the 0.6.x API: callers should migrate
rather than expect a compatibility layer.  This section summarizes the design
surface for review; the :doc:`reference` is the authoritative API contract.

The public API separates user-facing validation and immutable result models
from the native Pango and Cairo implementation.  Rendering follows one layout
pipeline:

* :func:`~manimpango.render` accepts plain text and optional
  :class:`~manimpango.TextSpan` objects.  Spans are normalized into Pango
  attributes for one layout, preserving shaping across styled ranges.
* :func:`~manimpango.render_markup` accepts raw Pango markup.  Markup is
  validated before it enters the same layout and SVG-rendering pipeline.
* Both functions return :class:`~manimpango.RenderedText`, an immutable object
  containing the SVG and layout metadata in SVG user-space units.
* :func:`~manimpango.register_font` returns a reference-counted
  :class:`~manimpango.FontRegistration` handle.  The native backend registers
  the font and the renderer updates its visible font map when registration
  state changes.

This division keeps generic text rendering in ManimPango while leaving
Manim-specific text selection and object integration to Manim.

**Public API.**

``render()`` accepts plain text only.  It has keyword-only options and returns
an in-memory result instead of requiring an output path.  Use
``render_markup()`` for raw Pango markup; structured spans and markup cannot
be mixed in one call.

``TextSpan`` offsets are half-open Python code-point ranges, just like string
slices.  Overlapping spans compose when they set different attributes;
conflicting values for the same attribute raise ``ValueError`` rather than
depending on span order.

All public geometry is represented by ``float`` values in SVG user-space
units.  ``RenderedText`` includes SVG text, overall dimensions and baseline,
ink and logical bounds, and per-line text, ranges, bounds, and baselines.

Custom fonts have explicit ownership.  A registration remains active until its
handle is closed; use the handle as a context manager for scoped registration.
Repeated registrations of the same normalized path are reference-counted.

**Breaking changes from 0.6.x.**

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - 0.6.x API or pattern
     - 1.0 replacement
   * - ``text2svg(settings, ..., file_name, ...)``
     - :func:`~manimpango.render`, which returns
       :class:`~manimpango.RenderedText`
   * - ``MarkupUtils.text2svg(...)``
     - :func:`~manimpango.render_markup`
   * - ``MarkupUtils.validate(markup)``
     - :func:`~manimpango.validate_markup`
   * - Mutable ``TextSetting`` objects
     - Immutable :class:`~manimpango.TextSpan` objects for plain text
   * - ``register_font(path)`` returning a boolean and
       ``unregister_font(path)``
     - :func:`~manimpango.register_font` returning a
       :class:`~manimpango.FontRegistration` handle; call ``close()`` or use a
       context manager
   * - ``pango_version()`` and ``cairo_version()``
     - :func:`~manimpango.get_version_info`

``RenderedText.save(path)`` is the explicit opt-in for writing SVG.  It writes
UTF-8 content to an existing parent directory and propagates filesystem errors.

**Scope.**

Version 1.0 intentionally does not provide:

* a compatibility facade for the 0.6.x utility classes and path-based font
  unregistration;
* rendering backends other than SVG;
* a Manim ``Text`` or ``MarkupText`` integration layer; or
* Linux binary wheels.  Linux users continue to install from source with the
  required native build dependencies.

These boundaries keep the package focused on a small, testable SVG text
rendering interface.  Future work can build on that interface without changing
its core contracts.

Migration
~~~~~~~~~

``render()`` accepts plain text only.  Use ``render_markup()`` for raw Pango
markup; plain and markup rendering are separate entry points.  Use
``TextSpan`` objects with ``render()`` for range styling.

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

Both rendering functions return a frozen, slotted
:class:`~manimpango.RenderedText`.  Geometry is always expressed in SVG
user-space units, not pixels or raw Pango units.  The former synthetic
line-spacing *metadata value* and mutable underscore-backed fields have been
removed; ``line_spacing=`` remains a Pango layout multiplier.

.. code-block:: python

    result = manimpango.render("one\ntwo", width=200.0)

    print(result.width, result.height, result.baseline)
    print(result.ink_bounds, result.logical_bounds)
    for line in result.lines:
        # Ranges exclude newline separators.
        print(line.text, line.start, line.end, line.bounds, line.baseline)

``result.lines`` is a tuple of :class:`~manimpango.LineInfo` instances.
For markup, line ranges refer to parsed text rather than the markup source.
Both layout bounds and per-line bounds use the same transformed coordinate
system as the SVG.

``RenderedText.save(path)`` writes UTF-8 SVG to ``path``.  The parent
directory must already exist; missing parents raise ``FileNotFoundError``.

Custom-font registration has explicit ownership:

.. code-block:: python

    with manimpango.register_font("path/to/font.ttf") as registration:
        result = manimpango.render("Example", font="My Font")

    assert registration.closed

Missing files raise :class:`~manimpango.FontNotFoundError`; other backend
registration failures raise :class:`~manimpango.FontRegistrationError`.
