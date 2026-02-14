API Reference
=============

.. module:: manimpango

Rendering
---------

.. autofunction:: render

.. autofunction:: validate_markup

Return Types
------------

.. autoclass:: RenderedText
   :members:
   :undoc-members:

.. autoclass:: LineInfo
   :members:
   :undoc-members:

Font Management
---------------

.. autofunction:: register_font

.. autofunction:: unregister_font

.. autofunction:: list_fonts

Version Information
-------------------

.. autofunction:: get_version_info

.. attribute:: __version__

   The installed ManimPango version string.

Enumerations
------------

.. autoclass:: Style
   :members:
   :undoc-members:

.. autoclass:: Weight
   :members:
   :undoc-members:

.. autoclass:: Alignment
   :members:
   :undoc-members:

Exceptions
----------

.. autoclass:: UnsupportedPangoFeatureError
   :members:

Deprecated
----------

The following functions are provided for backwards compatibility and may be
removed in a future release.

.. autofunction:: pango_version

.. autofunction:: cairo_version
