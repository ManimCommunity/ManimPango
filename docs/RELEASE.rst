Release Procedure
=================

This is the **maintainer** note on how to Release.
All versioning is in accordance to
`Semantic Versioning 2.0.0 <https://semver.org/>`_.
This means older version would have a backport of bugs fixes.

1. Check whether the test suite passes on the main branch.

2. Revert any changes which seems to be not working, and check
   for the milestone if PR are merged accordingly.

3. Check whether the `Wheels Build`_,
   against the main branch works as expected.

4. Clone the repository locally.

5. Bump the version in `manimpango/_version`_ accordingly.

6. Make a commit with the changes done, as ``Release v<version here>``

7. Create a tag, locally with

.. code-block:: sh

   git tag -s v<version-number>

.. note::

    Here, ``-s`` is used to sign the tag with gpg so that users
    can later verify it, and a tag shouldn't be created with
    signing because Github shows it unverified.

.. important::

    The message should include the changelog of the release.
    There is a github actions which will creates a draft `release`_
    with the changelog. You can edit them and copy it to the tag you
    create.

8. Push the tag to remote.

9. Go to `Github`_, and `draft a new release`_ with the same tag pushed.
   You can copy the same changelog you copied when you created the tag.

10. Check whether the CI uploads the wheels and the ``.tar.gz`` file to
    PyPi.

11. Finally, test the ``.tar.gz`` which was uploaded to `PyPi`_, and install
    it in a new virtual environment.

.. _Wheels Build: https://github.com/ManimCommunity/ManimPango/actions?query=workflow%3A%22Build+Wheels%22
.. _manimpango/_version: https://github.com/ManimCommunity/ManimPango/blob/main/manimpango/_version.py
.. _Github: https://github.com
.. _draft a new release: https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/managing-releases-in-a-repository#creating-a-release
.. _PyPi: https://pypi.org/project/manimpango/
.. _release: https://github.com/ManimCommunity/ManimPango/releases
