# ManimPango

<p align="center">
    <a href="https://pypi.org/project/manimpango/"><img src="https://img.shields.io/pypi/v/manimpango.svg?style=flat&logo=pypi" alt="PyPI Latest Release"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Wheel" src="https://img.shields.io/pypi/wheel/manimpango"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/manimpango"></a>
    <a href="https://choosealicense.com/licenses/mit/"><img alt="PyPI - License" src="https://img.shields.io/pypi/l/manimpango"></a>
    <a href="https://pypi.org/project/manimpango/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/ManimPango.svg?style=flat"></a>
    <a href="https://manimpango.manim.community/"><img src="https://img.shields.io/badge/docs-ManimPango-58C4DC" alt="Documentation"></a>
    <br>
    <img src="https://github.com/ManimCommunity/manimpango/actions/workflows/build.yml/badge.svg" alt="Build status">
</p>

**ManimPango** is a C binding for [Pango](https://pango.gnome.org/) using [Cython](https://cython.org/), which is internally used in [Manim](https://www.manim.community) to render (non-LaTeX) text.



## INSTALL

Installing **ManimPango** is super easy, just use `pip`. It is [`manimpango`](https://pypi.org/project/manimpango/) in PyPi.

```sh
pip install manimpango
```

For **Linux Users**, there are no Wheels. You must have a C compiler as well as **Pango** and its dependencies along with the **Pango** development headers. See [BUILDING](#BUILDING) for more information.

The [quick start](https://manimpango.manim.community/quickstart.html)
and [API reference](https://manimpango.manim.community/reference.html)
cover the complete interface.  A minimal plain-text render is:

```python
import manimpango

result = manimpango.render(
    "Hello, world!",
    size=24,
    spans=(manimpango.TextSpan(0, 5, weight=manimpango.Weight.BOLD),),
)
result.save("hello.svg")
```

## WORKFLOW SETUP / CONTRIBUTING

The repository uses [uv](https://docs.astral.sh/uv/) to manage its locked
development environment. After installing the system dependencies below,
install the development group and the project in editable mode:

```sh
uv sync --locked --group dev --no-install-project
uv pip install --no-build-isolation --editable .
uv run --no-sync pre-commit install
```

Run the test suite with `uv run --no-sync pytest`.

To build the documentation locally, install the `docs` group instead and run
Sphinx:

```sh
uv sync --locked --only-group docs
uv pip install --no-build-isolation --editable .
uv run --no-sync sphinx-build -W --keep-going -b html docs docs/_build/html
```

## BUILDING

### Linux/MacOS

For building **ManimPango**, you need
* a C compiler
* Python's development headers
* [`pkg-config`](https://www.freedesktop.org/wiki/Software/pkg-config/)
* [Pango](https://pango.gnome.org) along with its development headers and its dependencies.

If you are on MacOS, you can use [brew](https://brew.sh) to install those. Using [MacPorts](https://www.macports.org) is also possible.

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

#### Using `tar` archives

If you don't want to contribute to this repository, you can use the tar archives published in PyPi, or just use `pip` to install using

```sh
pip install manimpango --no-binary :all:
```

**Note**: `pip` by default uses wheels, so make sure to pass the `--no-binary` parameter.

#### Using `git` clones / Contributing

Please remember to do this inside your virtual environment, if you want to use your **Manimpango** with **Manim**.

```sh
python -m venv ./venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
```

From a clone, run the uv setup commands in
[WORKFLOW SETUP / CONTRIBUTING](#workflow-setup--contributing). They install
Cython, Meson, and the editable extension build.

### Contributing with Windows

Windows wheels include their native Pango dependencies. For a source build,
use a Visual Studio C toolchain plus Pango, Cairo, and ``pkg-config`` headers
that match the active Python architecture. The CI provisioning script,
``packing/download_dlls.py``, demonstrates the expected vendor layout.
Private font registration on Windows requires Pango 1.56 or newer.

## Code of Conduct

Our full code of conduct, and how we enforce it, can be read on [our website](https://docs.manim.community/en/latest/conduct.html).

## License

This project is licensed under MIT License. The wheels distributed on PyPI contains compiled version of Pango and Cairo subject to terms of the GNU LGPL and other licenses. Consult the licenses of each library for more informations.
