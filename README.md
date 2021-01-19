# ManimPango

<p align="center">
    <a href="https://pypi.org/project/manimpango/"><img src="https://img.shields.io/pypi/v/manimpango.svg?style=flat&logo=pypi" alt="PyPI Latest Release"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/manimpango"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/manimpango"></a>
    <a href="http://choosealicense.com/licenses/mit/"><img alt="PyPI - License" src="https://img.shields.io/pypi/l/manimpango"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pangocffi.svg?style=flat"></a>
    <a href='https://manimpango.readthedocs.io/en/latest/?badge=latest'><img src='https://readthedocs.org/projects/manimpango/badge/?version=latest' alt='Documentation Status' /></a>
    <br>
    <img src="https://github.com/ManimCommunity/manimpango/workflows/Build%20Wheels/badge.svg">
</p>

**ManimPango** is a C binding for [Pango](https://pango.gnome.org/) using [Cython](https://cython.org/), which is internally used in [Manim](https://www.manim.community) to render (non-LaTeX) text.



## INSTALL

Installing **ManimPango** is super easy, just use `pip`. It is [`manimpango`](https://pypi.org/project/manimpango/) in PyPi.

```sh
pip install manimpango
```

#### Note:

For **Linux Users**, installing the binary wheel provided in PyPi may have unexpected side effects.

For example, a folder named `fontconfig` might be created in the current working directory. That folder would then have a lot of cache files each time you run Manim. In order to avoid this, you will have to install **Manimpango** from source:.

```sh
pip install manimpango --no-binary :all:
```

Please note that for this kind of installation to work, you must have a C compiler as well as **Pango** and its dependencies along with the **Pango** development headers. See [BUILDING](#BUILDING ) for more information.

## BUILDING

### Linux/MacOS

For building **ManimPango**, you need
* a C compiler
* Python's development headers
* [`pkg-config`](https://www.freedesktop.org/wiki/Software/pkg-config/)
* [Pango](https://pango.gnome.org) along with its development headers and its dependencies.

If you are on MacOS, you can use [brew](https://brew.sh) to install those. Using [MacPorts](https://www.macports.org) is also possible, but their version of **Pango** is old and will probably not be updated in the near future.

```sh
brew install pango pkg-config
```

If you are on Linux, you can use a system package manager to do so. For example, if you are on Debian based system, you can use `apt`

```sh
apt install libpango1.0-dev pkg-config python3-dev
```

**Arch Linux:** `pacman -S pango pkgconf`

**Fedora:** `dnf install pango-devel pkg-config python3-devel`

Or similar in your system's package manager.

##### Using `tar` archives

If you don't want to contribute to this repository, you can use the tar archives published in PyPi, or just use `pip` to install using

```sh
pip install manimpango --no-binary :all:
```

**Note**: `pip` by default uses wheels, so make sure to pass the `--no-binary` parameter.

##### Using `git` clones / Contributing

If you are using a clone of this repository, you will need [Cython](https://cython.org) which can be easily installed using `pip`:

```sh
pip install Cython
```

After that you can use `pip` to install the clone with the following command:

```sh
pip install .
```

You will need to this way if you want to *contribute* to **ManimPango**.

Please remember to do this inside your poetry shell, if you want to use your **Manimpango** with **Manim**.

### Contributing with Windows

*If you are a normal user, don't read this, you have wheels which you can just install directly using pip.*

If you want to contribute to **ManimPango** and you are on Windows, this section is for you.

As Windows does not include a C compiler by default, you will first need to install one. You have two choices:

1. MinGW/Msys2

2. Visual Studio

#### MinGW/Msys2

1. Download **MSYS2** from the download link provided on their page https://www.msys2.org/#installation and install it according to their instructions.
2. Once you have **MSYS2** installed,  it offers you three different shells: the **MinGW32** shell, the **MinGW64** shell and **MSYS** shell. In order for the following steps to work, you have to open the **MSYS2 MinGW64** shell (you can search for this). Small hint: it has a blue color logo.
3. Run the following commands to install Python, Pango, Cython, Numpy, Scipy, Pillow, Pycairo and ffmpeg
```sh
pacman -S mingw-w64-x86_64-python
pacman -S mingw-w64-x86_64-python-pip
pacman -S mingw-w64-x86_64-pango
pacman -S mingw-w64-x86_64-cython
pacman -S mingw-w64-x86_64-python-numpy
pacman -S mingw-w64-x86_64-python-scipy
pacman -S mingw-w64-x86_64-python-pillow
pacman -S mingw-w64-x86_64-python-cairo
pacman -S mingw-w64-x86_64-ffmpeg
```
4. Still in the same shell, install **Manim** using `pip install manim`.
5. Finally, get your clone of **ManimPango**, `cd` into that directory and then run `pip install -e .`.
**Note** You can't use it with your regular Python version. It will cause weird errors if you do so. For working with **ManimPango**, you must be inside the `MSYS2 MINGW64 shell`.
6. You can then use `manim` inside that shell, to run **Manim**.
**Hint**: If you want to try out Python interactively, you can open `idle` using the command `python -m idlelib`  inside that shell.

#### Visual Studio

First, install Visual Studio as specified in https://wiki.python.org/moin/WindowsCompilers. Possibly Visual Studio Build Tools 2019 with Windows10 SDK.

Then run the script at `packing/download_dlls.py`. This will get a **Pango** build along with `pkg-config` and install it at `C:\cibw\vendor`. Add `C:\cibw\vendor\bin` and `C:\cibw\vendor\pkg-config\bin` to PATH.

**Note:** You can change the install location by editing line 24 of the file `packing/download_dlls.py`.

Then set an environment variable `PKG_CONFIG_PATH`=`C:\cibw\vendor\lib\pkgconfig`.

Then you can install Cython using

```sh
pip install Cython
```

Finally, you can install your local **ManimPango** clone just like any other python package by typing:

```sh
pip install .
```

**Important**: You have to to use https://docs.python.org/3/library/os.html#os.add_dll_directory before running **ManimPango**. Alternatively, you need to copy the `dll` at `C:\cibw\vendor\bin` to the folder where **ManimPango** is compiled.  This is applicable for Python 3.8 and above.

```python
import os
os.add_dll_directory('C:\cibw\vendor\bin')
```

## Code of Conduct

Our full code of conduct, and how we enforce it, can be read on [our website](https://docs.manim.community/en/latest/conduct.html).
