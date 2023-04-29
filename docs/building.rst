.. _building:

Building ManimPango
===================

Linux/MacOS
-----------

For building **ManimPango**, you need

* a C compiler
* Python's development headers
* `pkg-config <https://www.freedesktop.org/wiki/Software/pkg-config/>`_
* `Pango <https://pango.gnome.org>`_ along with its development headers and its dependencies.

If you are on MacOS, you can use `brew <https://brew.sh/>`_ to install those. Using
`MacPorts <https://www.macports.org/>`_ is also possible.

.. code-block::

    brew install pango pkg-config


If you are on Linux, you can use a system package manager to do so. For example, if you
are on Debian based system, you can use ``apt``

.. code-block::

    apt install libpango1.0-dev pkg-config python3-dev

**Arch Linux:** ``pacman -S pango pkgconf``

**Fedora:** ``dnf install pango-devel pkg-config python3-devel``

Or similar in your system's package manager.

Using ``tar`` archives
~~~~~~~~~~~~~~~~~~~~~~

If you don't want to contribute to this repository, you can use the tar archives published
on PyPi, or just use ``pip`` to install using

.. code-block:: bash

    pip install manimpango --no-binary :all:


**Note**: ``pip`` by default uses wheels, so make sure to pass the ``--no-binary`` parameter.

Using ``git`` clones / Contributing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please remember to do this inside your virtual environment, if you want to use
your **Manimpango** with **Manim**.

.. code-block:: sh

    python -m venv ./venv
    source venv/bin/activate # Linux/macOS
    venv\Scripts\activate # Windows

If you are using a clone of this repository, you will need `Cython <https://cython.org>`_
which can be easily installed using ``pip``:

.. code-block:: sh

    pip install Cython

After that you can use ``pip`` to install the clone with the following command:

.. code-block:: sh


    pip install -e .
    pip install -r requirements-dev.txt .


Next, build the library inplace using:

.. code-block:: sh

    python setup.py build_ext -i


After installation is complete, you should be able to run pytest:

.. code-block:: sh

    pytest


Windows
-------

.. note::

    If you are a normal user, don't read this, you have wheels which you can
    just install directly using pip.

If you want to contribute to **ManimPango** and you are on Windows, this section is
for you.

As Windows does not include a C compiler by default, you will first need to install
one. You have two choices:

1. :ref:`mingw`

2. :ref:`msvc`

.. _mingw:

MinGW/Msys2
~~~~~~~~~~~

1. Download **MSYS2** from the download link provided on their page https://www.msys2.org/#installation and install it according to their instructions.
2. Once you have **MSYS2** installed,  it offers you three different shells: the **MinGW32** shell, the **MinGW64** shell and **MSYS** shell. In order for the following steps to work, you have to open the **MSYS2 MinGW64** shell (you can search for this). Small hint: it has a blue color logo.
3. Run the following commands to install Python, Pango, Cython, Numpy, Scipy, Pillow, Pycairo and ffmpeg

.. code-block::

    pacman -S mingw-w64-x86_64-python
    pacman -S mingw-w64-x86_64-python-pip
    pacman -S mingw-w64-x86_64-pango
    pacman -S mingw-w64-x86_64-cython
    pacman -S mingw-w64-x86_64-python-numpy
    pacman -S mingw-w64-x86_64-python-scipy
    pacman -S mingw-w64-x86_64-python-pillow
    pacman -S mingw-w64-x86_64-python-cairo
    pacman -S mingw-w64-x86_64-ffmpeg

4. Still in the same shell, install **Manim** using ``pip install manim``.
5. Finally, get your clone of **ManimPango**, ``cd`` into that directory and then run ``pip install -e .``.

.. note::

    You can't use it with your regular Python version. It will cause weird errors if you
    do so. For working with **ManimPango**, you must be inside the `MSYS2 MINGW64 shell`.

6. You can then use ``manim`` inside that shell, to run **Manim**.

.. note::
    If you want to try out Python interactively, you can open `idle` using the command
    ``python -m idlelib``  inside that shell.

.. _msvc:

Visual Studio
~~~~~~~~~~~~~

First, install Visual Studio as specified in https://wiki.python.org/moin/WindowsCompilers.
Possibly Visual Studio Build Tools 2022 with Windows11 SDK.

Then run the script at ``packing/download_dlls.py``. This will get a **Pango** build along
with ``pkg-config`` and install it at ``C:\cibw\vendor``. Add ``C:\cibw\vendor\bin`` and
``C:\cibw\vendor\pkg-config\bin`` to PATH.

.. note::

    You can change the install location by editing line 24 of the
    file ``packing/download_dlls.py``.

Then set an environment variable ``PKG_CONFIG_PATH=C:\cibw\vendor\lib\pkgconfig``.

Then you can install Cython using

.. code-block:: sh

    pip install Cython

Finally, you can install your local **ManimPango** clone just like any other python
package by typing:

.. code-block:: sh

    pip install -e .

.. important::

    You have to to use https://docs.python.org/3/library/os.html#os.add_dll_directory
    before running **ManimPango**. This is applicable for Python 3.8 and above.

    .. code-block:: python

        import os
        os.add_dll_directory('C:\cibw\vendor\bin')

    Note that this is done automatically when running test suite.
