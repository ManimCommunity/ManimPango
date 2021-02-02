#!#!/bin/bash
# build and install pango
set -e

PANGO_VERSION=1.48.0
GLIB_VERSION=2.66.4
FRIBIDI_VERSION=1.0.10
CAIRO_VERSION=1.17.4
PIXMAN_VERSION=0.40.0
FREETYPE_VERSION=2.10.4
FONTCONFIG_VERSION=2.13.93
EXPANT_VERSION=2.2.10 # TODO: change url to use this version
GPERF_VERSION=3.1
LIBPNG_VERSION=1.6.37
HARFBUZZ_VERSION=2.7.3
ZLIB_VERSION=1.2.11
INTLTOOL_VERSION=0.51.0

FILE_PATH=$PWD

cd $TMP
if [ -d "$PWD/pango" ] ; then
  echo "Skipping Build"
  exit 0
fi

mkdir pango
cd pango
echo "::group::Downloading Files"

python -m pip install requests
python $FILE_PATH/packing/download_and_extract.py "http://download.gnome.org/sources/pango/${PANGO_VERSION%.*}/pango-${PANGO_VERSION}.tar.xz" pango
python $FILE_PATH/packing/download_and_extract.py "http://download.gnome.org/sources/glib/${GLIB_VERSION%.*}/glib-${GLIB_VERSION}.tar.xz" glib
python $FILE_PATH/packing/download_and_extract.py "https://github.com/fribidi/fribidi/releases/download/v${FRIBIDI_VERSION}/fribidi-${FRIBIDI_VERSION}.tar.xz" fribidi
python $FILE_PATH/packing/download_and_extract.py "https://cairographics.org/snapshots/cairo-${CAIRO_VERSION}.tar.xz" cairo
python $FILE_PATH/packing/download_and_extract.py "https://cairographics.org/releases/pixman-${PIXMAN_VERSION}.tar.gz" pixman
python $FILE_PATH/packing/download_and_extract.py "https://www.freedesktop.org/software/fontconfig/release/fontconfig-${FONTCONFIG_VERSION}.tar.xz" fontconfig
python $FILE_PATH/packing/download_and_extract.py "https://download.savannah.gnu.org/releases/freetype/freetype-${FREETYPE_VERSION}.tar.gz" freetype
python $FILE_PATH/packing/download_and_extract.py "https://github.com/libexpat/libexpat/releases/download/R_2_2_10/expat-2.2.10.tar.xz" expat
python $FILE_PATH/packing/download_and_extract.py "https://mirrors.kernel.org/gnu/gperf/gperf-${GPERF_VERSION}.tar.gz" gperf
python $FILE_PATH/packing/download_and_extract.py "https://downloads.sourceforge.net/project/libpng/libpng16/${LIBPNG_VERSION}/libpng-${LIBPNG_VERSION}.tar.xz" libpng
python $FILE_PATH/packing/download_and_extract.py "https://github.com/harfbuzz/harfbuzz/releases/download/${HARFBUZZ_VERSION}/harfbuzz-${HARFBUZZ_VERSION}.tar.xz" harfbuzz
python $FILE_PATH/packing/download_and_extract.py "https://zlib.net/fossils/zlib-${ZLIB_VERSION}.tar.gz" zlib
python $FILE_PATH/packing/download_and_extract.py "https://launchpad.net/intltool/trunk/${INTLTOOL_VERSION}/+download/intltool-${INTLTOOL_VERSION}.tar.gz" intltool
python -m pip uninstall -y requests

echo "::endgroup::"


echo "::group::Install Meson"
echo "Installing Meson and Ninja"
pip3 install -U meson ninja
echo "::endgroup::"


echo "::group::Building and Install IntlTool"
cd intltool
cpan App::cpanminus >> cpan.txt
cpan XML::Parser >> cpan.txt
./configure --disable-silent-rules
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install Zlib"
cd zlib
./configure
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install Glib"
meson setup --buildtype=release -Dselinux=disabled -Dlibmount=enabled glib_builddir glib
meson compile -C glib_builddir
meson install -C glib_builddir
echo "::endgroup::"

echo "::group::Building and Install Fribidi"
meson setup --buildtype=release fribidi_builddir fribidi
meson compile -C fribidi_builddir
meson install -C fribidi_builddir
echo "::endgroup::"

echo "::group::Building and Installing Gperf"
cd gperf
./configure
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Expat"
cd expat
./configure
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Freetype"
cd freetype
./configure --without-harfbuzz
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install Fontconfig"
meson setup --buildtype=release -Ddoc=disabled -Dtests=disabled -Dtools=disabled fontconfig_builddir fontconfig
meson compile -C fontconfig_builddir
meson install -C fontconfig_builddir
echo "::endgroup::"

echo "::group::Building and Install Libpng"
cd libpng
./configure
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Pixman"
cd pixman
./configure
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Cairo"
cd cairo
./configure --enable-fontconfig --enable-freetype
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Harfbuzz"
meson setup --buildtype=release -Dtests=disabled -Ddocs=disabled -Dgobject=disabled harfbuzz_builddir harfbuzz
meson compile -C harfbuzz_builddir
meson install -C harfbuzz_builddir
echo "::endgroup::"

echo "::group::Buildling and Installing Pango"
meson setup --buildtype=release -Dintrospection=disabled pango_builddir pango
meson compile -C pango_builddir
meson install -C pango_builddir
echo "::endgroup::"

cd $FILE_PATH
