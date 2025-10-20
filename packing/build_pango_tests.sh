#!/usr/bin/env bash
# build and install pango
set -e

PANGO_VERSION=1.56.4

FILE_PATH=$PWD
PREFIX="$HOME/pangoprefix"

cd $TMP
cd $TEMPDIR

mkdir pango
cd pango
echo "::group::Downloading Files"

python $FILE_PATH/packing/download_and_extract.py "http://download.gnome.org/sources/pango/${PANGO_VERSION%.*}/pango-${PANGO_VERSION}.tar.xz" pango

echo "::endgroup::"

export CMAKE_PREFIX_PATH=$PKG_CONFIG_PATH
LIB_INSTALL_PREFIX=$PREFIX

echo "::group::Install Meson"
echo "Installing Meson and Ninja"
pip3 install -U meson ninja
echo "::endgroup::"

echo "::group::Buildling and Installing Pango"
meson setup --prefix=$PREFIX --buildtype=release \
    -Dintrospection=disabled \
    -Dfontconfig=enabled \
    --force-fallback-for=fontconfig \
    pango_builddir pango
meson compile -C pango_builddir
meson install -C pango_builddir
echo "::endgroup::"
