#!/bin/bash
# build and install pango
set -e

PANGO_VERSION=1.50.11
GLIB_VERSION=2.74.0
CAIRO_VERSION=1.17.4
FONTCONFIG_VERSION=2.14.0
HARFBUZZ_VERSION=5.3.1

FILE_PATH=$PWD
PREFIX=$HOME/pangobuild

cd $TMPDIR
if [ -d $PREFIX ] ; then
  echo "Skipping Build"
  exit 0
fi

mkdir pango
cd pango
echo "::group::Downloading Files"

python -m pip install requests
python $FILE_PATH/packing/download_and_extract.py "http://download.gnome.org/sources/pango/${PANGO_VERSION%.*}/pango-${PANGO_VERSION}.tar.xz" pango
python $FILE_PATH/packing/download_and_extract.py "http://download.gnome.org/sources/glib/${GLIB_VERSION%.*}/glib-${GLIB_VERSION}.tar.xz" glib
python $FILE_PATH/packing/download_and_extract.py "https://gitlab.freedesktop.org/cairo/cairo/-/archive/${CAIRO_VERSION}/cairo-${CAIRO_VERSION}.tar.gz" cairo
python $FILE_PATH/packing/download_and_extract.py "https://www.freedesktop.org/software/fontconfig/release/fontconfig-${FONTCONFIG_VERSION}.tar.xz" fontconfig
python $FILE_PATH/packing/download_and_extract.py "https://github.com/harfbuzz/harfbuzz/releases/download/${HARFBUZZ_VERSION}/harfbuzz-${HARFBUZZ_VERSION}.tar.xz" harfbuzz

curl -L "https://github.com/frida/proxy-libintl/archive/0.2.tar.gz" -o 0.2.tar.gz
tar -xf 0.2.tar.gz
mv proxy-libintl-0.2 proxy-libintl

python -m pip uninstall -y requests

echo "::endgroup::"

export PKG_CONFIG_PATH=$PREFIX/lib/pkgconfig
export CMAKE_PREFIX_PATH=$PKG_CONFIG_PATH
export LIB_INSTALL_PREFIX=$PREFIX
export PATH="$PATH:$PREFIX/bin"

echo "::group::Install Meson"
echo "Installing Meson and Ninja"
pip3 install -U meson==0.63.3 ninja
echo "::endgroup::"

echo "::group::Removing the things from brew"
brew uninstall --ignore-dependencies brotli
brew uninstall --ignore-dependencies pcre
brew uninstall --ignore-dependencies libpng
brew uninstall --ignore-dependencies freetype
brew uninstall --ignore-dependencies libxdmcp
brew uninstall --ignore-dependencies libxcb
brew uninstall --ignore-dependencies xorgproto
brew uninstall --ignore-dependencies libxau
echo "::endgroup::"

export CFLAGS=" -w" # warning are just noise. Ignore it.

echo "::group::Building and installing proxy-libintl"
meson setup --buildtype=release libintlbuilddir proxy-libintl
meson compile -C libintlbuilddir
meson install -C libintlbuilddir
echo "::endgroup::"

echo "::group::Building and installing Fontconfig"
rm -rf /usr/local/share/fontconfig/conf.avail
meson setup \
  --buildtype=release \
  --prefix=$PREFIX \
  --sysconfdir=$HOME \
  -Ddoc=disabled \
  -Dtests=disabled \
  -Dtools=disabled \
  --default-library=shared \
  fontconfig_builddir fontconfig
meson compile -C fontconfig_builddir
meson install -C fontconfig_builddir
echo "::endgroup::"


echo "::group::Building and installing Glib"
meson setup \
  --prefix=$PREFIX \
  --buildtype=release \
  -Dselinux=disabled \
  -Dlibmount=disabled \
  -Dtests=false \
  --force-fallback-for=pcre,libffi,proxy-libintl,zlib \
  --default-library=shared \
  glib_builddir glib
meson compile -C glib_builddir
meson install -C glib_builddir
echo "::endgroup::"

echo "::group::Building and installing Cairo"
meson setup \
  --prefix=$PREFIX \
  --buildtype=release \
  -Dfontconfig=enabled \
  -Dfreetype=enabled \
  -Dtests=disabled \
  -Dxlib=disabled \
  --force-fallback-for=expat,libpng,pixman \
  --default-library=shared \
  cairo_builddir cairo
meson compile -C cairo_builddir
meson install -C cairo_builddir
echo "::endgroup::"

echo "::group::Building and installing Harfbuzz"
meson setup \
  --prefix=$PREFIX \
  --buildtype=release \
  -Dtests=disabled \
  -Ddocs=disabled \
  -Dgobject=disabled \
  -Dcoretext=enabled \
  -Dfreetype=enabled \
  -Dintrospection=disabled \
  -Dglib=enabled \
  --default-library=shared \
  harfbuzz_builddir harfbuzz
meson compile -C harfbuzz_builddir
meson install -C harfbuzz_builddir
echo "::endgroup::"


echo "::group::Building and installing Pango"
export LDFLAGS=" -framework Foundation "
meson setup \
  --prefix=$PREFIX \
  --buildtype=release \
  -Dintrospection=disabled \
  -Dxft=disabled \
  --default-library=shared \
  pango_builddir pango
meson compile -C pango_builddir
meson install -C pango_builddir
echo "::endgroup::"

cd $FILE_PATH
