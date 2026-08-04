Release Procedure
=================

This is the **maintainer** note on how to release ManimPango.
All versioning follows `Semantic Versioning 2.0.0 <https://semver.org/>`_.

1. Ensure the main branch is green and the intended changes are merged.

2. Update the ``1.0`` entry in ``docs/changelog.rst`` and bump the
   authoritative version in ``meson.build``. ``pyproject.toml`` deliberately
   reads the installed version dynamically from the build system.

3. Open and merge the release-preparation pull request. Confirm CI passes on
   its merge commit.

4. Create and publish a GitHub release targeting that merge commit. In the
   release form, create the ``v<version-number>`` tag; GitHub creates and
   pushes it as part of publishing the release. Draft releases are inert;
   publishing the release starts the package build and publication.

5. Monitor the `Wheels Build`_ workflow. It builds the supported wheels and
   source distribution, publishes them to `PyPI`_, and attaches the artifacts
   to the GitHub release only after every build succeeds.

6. In a fresh virtual environment, install the published package and run a
   small rendering smoke test on each platform for which a wheel was released.


Build System
------------

ManimPango v1.0 uses **Meson** (via ``meson-python``) as its build
backend.  The Cython extensions are compiled by Meson.  See
``pyproject.toml`` and the top-level ``meson.build`` for details.

Minimum requirements:

- Python ≥ 3.11
- Pango ≥ 1.44
- Cairo ≥ 1.14
- GLib ≥ 2.0
- Cython ≥ 3.0.0

.. _Wheels Build: https://github.com/ManimCommunity/ManimPango/actions?query=workflow%3A%22Build+Wheels%22
.. _PyPI: https://pypi.org/project/manimpango/
