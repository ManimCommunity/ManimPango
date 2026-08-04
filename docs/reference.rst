API Reference
=============

.. module:: manimpango

Rendering
---------

.. autofunction:: render

.. autofunction:: render_markup

.. autofunction:: validate_markup

Text Models
-----------

.. autoclass:: TextSpan

.. autoclass:: Bounds

.. autoclass:: LineInfo

.. autoclass:: RenderedText
   :members: line_count, save

Font Management
---------------

.. autofunction:: register_font

.. autoclass:: FontRegistration
   :members: close, path, closed

.. autofunction:: list_fonts

Enumerations
------------

.. autoclass:: Style

.. autoclass:: Weight

.. autoclass:: Alignment

Exceptions
----------

.. autoexception:: ManimPangoError

.. autoexception:: RenderError

.. autoexception:: MarkupError

.. autoexception:: FontError

.. autoexception:: FontNotFoundError

.. autoexception:: FontRegistrationError

.. autoexception:: UnsupportedPangoFeatureError

Version Information
-------------------

.. autofunction:: get_version_info

.. attribute:: __version__

   The installed ManimPango version string.
