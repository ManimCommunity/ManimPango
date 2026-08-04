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
   :members:

.. autoclass:: Bounds
   :members:

.. autoclass:: LineInfo
   :members:

.. autoclass:: RenderedText
   :members: line_count, save

Font Management
---------------

.. autofunction:: register_font

.. autoclass:: FontRegistration
   :members: close, path, closed, __enter__, __exit__

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

Version Information
-------------------

.. autofunction:: get_version_info

.. attribute:: __version__

   The installed ManimPango version string.
