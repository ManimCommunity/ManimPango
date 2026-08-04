Release notes: 1.0
==================

ManimPango 1.0 is a hard break from the 0.6.x API: callers should migrate
rather than expect a compatibility layer.  This page summarizes the design
and migration surface for review; the :doc:`reference` is the authoritative
API contract, and the :doc:`migration` guide contains runnable replacements.

Design overview
---------------

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

Public API changes
------------------

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

Breaking changes from 0.6.x
---------------------------

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

Migration
---------

Read the :doc:`migration` guide first when updating a 0.6.x caller.  For new
code, use the :doc:`quickstart` and then the :doc:`reference` for parameter,
result, and exception contracts.

Scope
-----

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
