Manimpango 1.0.0a2 (2023-04-30)
===============================

Bugfixes
--------

- Include ``*.pxi`` files in tarball. Without these the package cannot be
  installed from source.
- Raise on invalid ``string`` passed to :class:`FontDescriptor` constructor.
  Previously, it silently crashed.


Manimpango 1.0.0a1 (2023-04-29)
===============================

Features
--------

- The package has undergone a complete rewrite to offer an improved API.
  The new API provides a greater degree of consistency and flexibility compared
  to its predecessor. (#28)
