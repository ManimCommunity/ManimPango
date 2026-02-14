Migration Guide (v1.x → v2.0)
==============================

ManimPango v2.0 is a complete rewrite with a simplified API.  This guide
covers the changes and shows how to update existing code.

Overview of Changes
-------------------

- A single :func:`~manimpango.render` function replaces ``text2svg()``,
  ``MarkupUtils.text2svg()``, and related utilities.
- :func:`~manimpango.render` returns a :class:`~manimpango.RenderedText`
  object containing SVG content **and** layout metadata (dimensions,
  baseline, per-line info).
- Surface dimensions (``width``, ``height``, ``START_X``, ``START_Y``)
  are no longer needed — ManimPango uses a two-pass measure-then-render
  approach internally.
- The ``TextSetting`` class has been removed.  Per-substring styling
  should be expressed as Pango markup.
- ``PangoUtils`` and ``MarkupUtils`` helper classes have been removed.
- Font weight and style are now specified via :class:`~manimpango.Weight`
  and :class:`~manimpango.Style` enums instead of strings.
- Variable font support is new in v2.0 (``weight`` accepts arbitrary
  integers, ``variations`` parameter for custom axes).
- Minimum requirements: Python ≥ 3.11, Pango ≥ 1.44.

Removed Symbols
---------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - v1.x Symbol
     - v2.0 Replacement
   * - ``text2svg(settings, ...)``
     - ``render(markup, is_markup=True, ...)``
   * - ``MarkupUtils.text2svg(...)``
     - ``render(text, is_markup=True, ...)``
   * - ``MarkupUtils.validate(...)``
     - :func:`validate_markup`
   * - ``TextSetting``
     - Removed — use Pango markup
   * - ``PangoUtils.str2style()``
     - Use :class:`Style` enum directly
   * - ``PangoUtils.str2weight()``
     - Use :class:`Weight` enum directly
   * - ``fc_register_font()``
     - :func:`register_font`
   * - ``fc_unregister_font()``
     - :func:`unregister_font`
   * - ``pango_version()``
     - ``get_version_info()["pango"]``
   * - ``cairo_version()``
     - ``get_version_info()["cairo"]``
   * - ``Variant`` enum
     - Removed (unused by Pango layout)

Migration Examples
------------------

Rendering Markup (MarkupText path)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before (v1.x):**

.. code-block:: python

    from manimpango import MarkupUtils, Alignment

    MarkupUtils.text2svg(
        "<span color='blue'>Hello</span>",
        "Arial",           # font
        "NORMAL",          # slant (as string)
        "NORMAL",          # weight (as string)
        24,                # size
        True,              # mystery positional arg
        False,             # disable_liga
        "output.svg",      # file_name
        20, 20,            # START_X, START_Y
        600, 400,          # width, height
        justify=False,
        indent=None,
        line_spacing=None,
        alignment=Alignment.CENTER,
    )

**After (v2.0):**

.. code-block:: python

    import manimpango

    result = manimpango.render(
        "<span color='blue'>Hello</span>",
        is_markup=True,
        font="Arial",
        size=24,
        alignment=manimpango.Alignment.CENTER,
    )
    result.save("output.svg")

Rendering with Per-Substring Styles (Text path)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Before (v1.x):**

.. code-block:: python

    from manimpango import TextSetting, text2svg

    settings = [
        TextSetting(0, 5, font="Arial", slant="NORMAL",
                    weight="BOLD", color="red"),
        TextSetting(5, 11, font="Arial", slant="ITALIC",
                    weight="NORMAL", color="blue"),
    ]
    text2svg(settings, 24, 30, False, "output.svg",
             20, 20, 600, 400, "HelloWorld!")

**After (v2.0):**

.. code-block:: python

    import manimpango

    result = manimpango.render(
        "<span weight='bold' color='red'>Hello</span>"
        "<span style='italic' color='blue'>World!</span>",
        is_markup=True,
        font="Arial",
        size=24,
    )
    result.save("output.svg")

Font Registration
^^^^^^^^^^^^^^^^^

**Before (v1.x):**

.. code-block:: python

    from manimpango import fc_register_font, fc_unregister_font

    fc_register_font("path/to/font.ttf")
    # ...
    fc_unregister_font("path/to/font.ttf")

**After (v2.0):**

.. code-block:: python

    import manimpango

    manimpango.register_font("path/to/font.ttf")
    # ...
    manimpango.unregister_font("path/to/font.ttf")

Getting Layout Dimensions
^^^^^^^^^^^^^^^^^^^^^^^^^

In v1.x, obtaining text dimensions required calling separate utility
functions.  In v2.0, :func:`~manimpango.render` returns all layout
metadata directly:

.. code-block:: python

    result = manimpango.render("Hello World", font="Arial", size=24)

    print(result.width)       # total width in pixels
    print(result.height)      # total height in pixels
    print(result.baseline)    # baseline in Pango units
    print(result.line_count)  # number of lines
    print(result.line_height) # recommended line-to-line distance

    for line in result.lines:
        print(line.width, line.height, line.y_offset)
