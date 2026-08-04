Release Procedure
=================

This is the **maintainer** note on how to release ManimPango.
All versioning follows `Semantic Versioning 2.0.0 <https://semver.org/>`_.

1. Check whether the test suite passes on the main branch.

2. Revert any changes that are not working, and verify that milestone PRs
   are merged.

3. Check whether the `Wheels Build`_ against the main branch works as
   expected.

4. Clone the repository locally.

5. Bump the authoritative version in ``meson.build``. ``pyproject.toml``
   deliberately reads the installed version dynamically from the build system.

6. Commit the changes as ``Release v<version>``.

7. Create a signed tag locally:

   .. code-block:: sh

      git tag -s v<version-number>

   .. note::

      The ``-s`` flag signs the tag with GPG so that users can verify it.
      GitHub shows unsigned tags as "unverified".

   .. important::

      Include the changelog in the tag message. A GitHub Action creates a
      draft `release`_ with the changelog — you can copy it into the tag.

8. Push the tag to the remote.

9. Go to `GitHub`_ and `draft a new release`_ using the tag you just pushed.

   .. important::

      Draft a **new** release rather than publishing a previously created
      draft — this is needed to trigger the wheels build workflow.

10. Verify that CI uploads wheels and the ``.tar.gz`` to `PyPI`_.

11. Test the uploaded ``.tar.gz`` in a fresh virtual environment.

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
.. _GitHub: https://github.com
.. _draft a new release: https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository#creating-a-release
.. _PyPI: https://pypi.org/project/manimpango/
.. _release: https://github.com/ManimCommunity/ManimPango/releases
