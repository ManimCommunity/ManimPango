Quick Start
===========

Installation
------------

Install ManimPango from PyPI::

    pip install manimpango

ManimPango requires **Pango ≥ 1.44** and **Cairo** to be installed on
your system.  On most Linux distributions these are available through the
package manager.  On macOS, install them via `Homebrew
<https://brew.sh/>`_::

    brew install pango cairo

Basic Usage
-----------

Render plain text to SVG:

.. code-block:: python

    import manimpango

    result = manimpango.render("Hello World")

    # Get the SVG content as a string
    svg = result.svg

    # Save directly to a file
    result.save("hello.svg")

Render Pango markup:

.. code-block:: python

    result = manimpango.render(
        "<span color='red' weight='bold'>Important</span>",
        is_markup=True,
        font="Helvetica",
        size=24,
    )

Layout Metadata
---------------

The :class:`~manimpango.RenderedText` object returned by
:func:`~manimpango.render` contains layout metadata useful for
positioning text in animations:

.. code-block:: python

    result = manimpango.render("Line 1\nLine 2\nLine 3", width=200)

    print(f"Size: {result.width} × {result.height} px")
    print(f"Baseline: {result.baseline} Pango units")
    print(f"Lines: {result.line_count}")

    for i, line in enumerate(result.lines):
        print(f"  Line {i}: width={line.width}, y_offset={line.y_offset}")

Variable Fonts
--------------

ManimPango supports `OpenType variable fonts
<https://fonts.google.com/knowledge/introducing_type/introducing_variable_fonts>`_.
You can specify arbitrary integer weights (1–1000) and set custom font
axes via the ``variations`` parameter:

.. code-block:: python

    # Continuous weight (not limited to named values)
    result = manimpango.render(
        "Smooth weight",
        font="Inter",
        weight=450,
    )

    # Multiple variable font axes
    result = manimpango.render(
        "Custom axes",
        font="Amstelvar",
        variations={"wght": 600, "wdth": 85, "opsz": 14},
    )

.. note::

    The ``variations`` parameter requires the PangoFT2/fontconfig backend
    (the default on Linux).  On macOS, Pango's CoreText backend ignores
    font variations.  For weight changes specifically, use the ``weight``
    parameter instead — it works on all platforms.

Custom Fonts
------------

Register a local font file so Pango can use it for rendering:

.. code-block:: python

    manimpango.register_font("path/to/MyFont.ttf")

    result = manimpango.render("Custom font", font="My Font")

    # List all available fonts
    fonts = manimpango.list_fonts()
    print(fonts)

    # Unregister when done
    manimpango.unregister_font("path/to/MyFont.ttf")
