#!/usr/bin/env bash
# build and install pango
set -e

PANGO_VERSION=1.48.4
GLIB_VERSION=2.67.6
FRIBIDI_VERSION=1.0.10
CAIRO_VERSION=1.17.4
HARFBUZZ_VERSION=2.7.4

FILE_PATH=$PWD
PREFIX="$HOME/pangoprefix"

cd $TMP
cd $TEMPDIR

mkdir pango
cd pango
echo "::group::Downloading Files"

python -m pip install requests
python $FILE_PATH/scripts/download_and_extract.py "http://download.gnome.org/sources/pango/${PANGO_VERSION%.*}/pango-${PANGO_VERSION}.tar.xz" pango
python $FILE_PATH/scripts/download_and_extract.py "http://download.gnome.org/sources/glib/${GLIB_VERSION%.*}/glib-${GLIB_VERSION}.tar.xz" glib
python $FILE_PATH/scripts/download_and_extract.py "https://github.com/fribidi/fribidi/releases/download/v${FRIBIDI_VERSION}/fribidi-${FRIBIDI_VERSION}.tar.xz" fribidi
python $FILE_PATH/scripts/download_and_extract.py "https://gitlab.freedesktop.org/cairo/cairo/-/archive/${CAIRO_VERSION}/cairo-${CAIRO_VERSION}.tar.gz" cairo
python $FILE_PATH/scripts/download_and_extract.py "https://github.com/harfbuzz/harfbuzz/releases/download/${HARFBUZZ_VERSION}/harfbuzz-${HARFBUZZ_VERSION}.tar.xz" harfbuzz

python -m pip uninstall -y requests

echo "::endgroup::"

export CMAKE_PREFIX_PATH=$PKG_CONFIG_PATH
LIB_INSTALL_PREFIX=$PREFIX

echo "::group::Install Meson"
echo "Installing Meson and Ninja"
pip3 install -U meson ninja
echo "::endgroup::"

echo "::group::Building and Install Glib"
meson setup --prefix=$PREFIX --buildtype=release -Dselinux=disabled -Dlibmount=disabled glib_builddir glib
meson compile -C glib_builddir
meson install -C glib_builddir
echo "::endgroup::"

echo "::group::Building and Install Fribidi"
meson setup --prefix=$PREFIX --buildtype=release fribidi_builddir fribidi
meson compile -C fribidi_builddir
meson install -C fribidi_builddir
echo "::endgroup::"

echo "::group::Building and Installing Cairo"
echo "Getting patch"
curl -L https://gitlab.freedesktop.org/cairo/cairo/-/merge_requests/101.diff -o 101.diff
cd cairo
patch -Nbp1 -i "$PWD/../101.diff" || true
# it is fine to fail because the CI config is missing.
cd ..
meson setup --prefix=$PREFIX --default-library=shared --buildtype=release -Dfontconfig=enabled -Dfreetype=enabled -Dglib=enabled -Dzlib=enabled -Dtee=enabled cairo_builddir cairo
meson compile -C cairo_builddir
meson install --no-rebuild -C cairo_builddir
echo "::endgroup::"

echo "::group::Building and Installing Harfbuzz"
meson setup --prefix=$PREFIX -Dcoretext=enabled --buildtype=release -Dtests=disabled -Ddocs=disabled harfbuzz_builddir harfbuzz
meson compile -C harfbuzz_builddir
meson install -C harfbuzz_builddir
echo "::endgroup::"

echo "::group::Buildling and Installing Pango"
meson setup --prefix=$PREFIX --buildtype=release -Dintrospection=disabled pango_builddir pango
meson compile -C pango_builddir
meson install -C pango_builddir
echo "::endgroup::"
