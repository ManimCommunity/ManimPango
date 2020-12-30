# ManimPango

<p align="center">
    <a href="https://pypi.org/project/manimpango/"><img src="https://img.shields.io/pypi/v/manimpango.svg?style=flat&logo=pypi" alt="PyPI Latest Release"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/manimpango"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/manimpango"></a>
    <a href="http://choosealicense.com/licenses/mit/"><img alt="PyPI - License" src="https://img.shields.io/pypi/l/manimpango"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/pangocffi.svg?style=flat"></a>
    <br>
    <img src="https://github.com/ManimCommunity/manimpango/workflows/Build%20Wheels/badge.svg">
</p>

**ManimPango** is a C binding for [Pango](https://pango.gnome.org/) using [Cython](https://cython.org/), which is internally used in [Manim](https://www.manim.community) to render **Text**. 



## INSTALL

Installing **ManimPango** is super easy, just use pip to install it. It is [`manimpango`](https://pypi.org/project/manimpango/) in PyPi.

```sh
pip install manimpango
```

#### Note:

For **Linux Users**, installing the binary wheel provided in PyPi could cause some weird things happen to your system.

For example, you would get a folder named `fontconfig`, in your directory, and it will have a lot of cache files each time you run Manim. To avoid those kind of weird things from happening, you would have to install it from source using the below command.

```sh
pip install manimpango --no-binary :all:
```

For installing that this way you would need a C compiler as well as Pango and its dependencies along with it's Development headers. See [BUILDING](#BUILDING ) for more information.

## BUILDING

### Linux/MacOS

For building **ManimPango**, you would need a C compiler,python's development headers,[`pkg-config`](https://www.freedesktop.org/wiki/Software/pkg-config/),[Pango](https://pango.gnome.org) along with its development headers and its dependencies.

If you are on macOS, you can use [brew](https://brew.sh) to install those

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

If you don't want to contribute to this Repository, you can use the tar archives published in PyPi, or just use pip to install using 

```sh
pip install manimpango --no-binary :all:
```

**Note**: `pip` by default uses wheels, so make sure to pass `--no-binary` parameter.

##### Using `git` clones

If you are using a clone of this repository, then you would need [Cython](https://cython.org) which can be easily installed using pip

```sh
pip install Cython
```

After that you can use pip to install the clone using

```sh
pip install .
```

You would need to this way if you want to *Contribute* to **ManimPango**.

You should do these inside your poetry shell, if you want to use it with **Manim**.

### Windows

*If you are a normal user, don't read this, you have wheels which you can just install directly using pip.*

If you want to contribute to **ManimPango** and you are on Windows, this section is for you.

First you would need a C compiler, as windows doesn't have one by default, you have two choices

1. MinGW/Msys2

2. Visual Studio

#### MinGW/Msys2

1. Download Msys2 from as specified in their page https://www.msys2.org/#installation
2. Open, a `MSYS2 MINGW64 shell`, and not anything else. Small hint, it has a blue color logo.
3. Run the following commands to install Python, Pango, Cython, Numpy, Scipy, Pillow, Pycairo, ffmpeg
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
4. Install Manim using pip inside the same shell.
5. Finally, get your clone of **ManimPango** and `cd` into that directory and then run `pip install -e .`.
**Note** You can't use it with Python provided on `python.org`. It will cause weird errors if you do so. For working with **ManimPango**, you would need to be inside the `MSYS2 MINGW64 shell`. 
6. You can then use `manim` inside that shell, to run manim.
**TIP**: If you want to try around python interactively, you can open `idle` using `python -m idlelib` command inside that shell.

#### Visual Studio

First, install Visual Studio as specified in https://wiki.python.org/moin/WindowsCompilers. Possibly Visual Studio Build Tools 2019 with Windows10 SDK.

Then run the script at `packing/download_dlls.py`, that will get a Pango build along with `pkg-config`, and install it at `C:\cibw\vendor`. Add `C:\cibw\vendor\bin` and `C:\cibw\vendor\pkg-config\bin`  to PATH. 

**Note:** You can change the install location by editing line 24 on `packing/download_dlls.py`, to where you want to.

Then set an environment variable `PKG_CONFIG_PATH`=`C:\cibw\vendor\lib\pkgconfig`. 

Then you can install Cython using

```sh
pip install Cython
```

Finally, you can install it as any other python package **ManimPango**,

```sh
pip install .
```

**Important**: You would to use https://docs.python.org/3/library/os.html#os.add_dll_directory before running **ManimPango** or you would need to copy the `dll` at `C:\cibw\vendor\bin`to the folder where it is compiled.  This is applicable for python 3.8+.

```python
import os
os.add_dll_directory('C:\cibw\vendor\bin')
```

