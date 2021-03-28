#!/bin/bash
# build and install pango
set -e

PANGO_VERSION=1.48.4
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
BROTLI_VERSION=1.0.9
PCRE_VERSION=8.44

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
python $FILE_PATH/packing/download_and_extract.py "https://github.com/fribidi/fribidi/releases/download/v${FRIBIDI_VERSION}/fribidi-${FRIBIDI_VERSION}.tar.xz" fribidi
python $FILE_PATH/packing/download_and_extract.py "https://cairographics.org/snapshots/cairo-${CAIRO_VERSION}.tar.xz" cairo
python $FILE_PATH/packing/download_and_extract.py "https://cairographics.org/releases/pixman-${PIXMAN_VERSION}.tar.gz" pixman
python $FILE_PATH/packing/download_and_extract.py "https://www.freedesktop.org/software/fontconfig/release/fontconfig-${FONTCONFIG_VERSION}.tar.xz" fontconfig
python $FILE_PATH/packing/download_and_extract.py "https://downloads.sourceforge.net/project/freetype/freetype2/${FREETYPE_VERSION}/freetype-${FREETYPE_VERSION}.tar.gz" freetype
#python $FILE_PATH/packing/download_and_extract.py "https://download.savannah.gnu.org/releases/freetype/freetype-${FREETYPE_VERSION}.tar.gz" freetype
python $FILE_PATH/packing/download_and_extract.py "https://github.com/libexpat/libexpat/releases/download/R_2_2_10/expat-2.2.10.tar.xz" expat
python $FILE_PATH/packing/download_and_extract.py "https://mirrors.kernel.org/gnu/gperf/gperf-${GPERF_VERSION}.tar.gz" gperf
python $FILE_PATH/packing/download_and_extract.py "https://downloads.sourceforge.net/project/libpng/libpng16/${LIBPNG_VERSION}/libpng-${LIBPNG_VERSION}.tar.xz" libpng
python $FILE_PATH/packing/download_and_extract.py "https://github.com/harfbuzz/harfbuzz/releases/download/${HARFBUZZ_VERSION}/harfbuzz-${HARFBUZZ_VERSION}.tar.xz" harfbuzz
python $FILE_PATH/packing/download_and_extract.py "https://zlib.net/fossils/zlib-${ZLIB_VERSION}.tar.gz" zlib
python $FILE_PATH/packing/download_and_extract.py "https://ftp.pcre.org/pub/pcre/pcre-${PCRE_VERSION}.tar.bz2" pcre
curl -L "https://github.com/frida/proxy-libintl/archive/0.1.tar.gz" -o 0.1.tar.gz
tar -xf 0.1.tar.gz
mv proxy-libintl-0.1 proxy-libintl
python -m pip uninstall -y requests

echo "::endgroup::"

export PKG_CONFIG_PATH=$PREFIX/lib/pkgconfig
export CMAKE_PREFIX_PATH=$PKG_CONFIG_PATH
LIB_INSTALL_PREFIX=$PREFIX
echo "::group::Install Meson"
echo "Installing Meson and Ninja"
pip3 install -U meson ninja
echo "::endgroup::"

echo "::group::Removing the things from brew"
brew uninstall --ignore-dependencies brotli
brew uninstall --ignore-dependencies pcre
brew uninstall --ignore-dependencies libpng
echo "::endgroup::"

echo "::group::Building and Install PCRE"
cd pcre
./configure \
      --prefix=$PREFIX \
      --enable-utf8 \
      --enable-pcre8  \
      --enable-pcre16 \
      --enable-pcre32 \
      --enable-unicode-properties \
      --enable-pcregrep-libz \
      --enable-pcregrep-libbz2
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install proxy-libintl"
meson setup --buildtype=release libintlbuilddir proxy-libintl
meson compile -C libintlbuilddir
meson install -C libintlbuilddir
echo "::endgroup::"

echo "::group::Building and Install Zlib"
cd zlib
./configure --prefix=$PREFIX
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install Glib"
meson setup --prefix=$PREFIX --buildtype=release -Dselinux=disabled -Dlibmount=enabled glib_builddir glib
meson compile -C glib_builddir
meson install -C glib_builddir
echo "::endgroup::"

echo "::group::Building and Install Fribidi"
meson setup --prefix=$PREFIX --buildtype=release fribidi_builddir fribidi
meson compile -C fribidi_builddir
meson install -C fribidi_builddir
echo "::endgroup::"

echo "::group::Building and Installing Gperf"
cd gperf
./configure --prefix=$PREFIX
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Expat"
cd expat
./configure --prefix=$PREFIX
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install Libpng"
cd libpng
./configure --prefix=$PREFIX
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Freetype"
cd freetype
./configure --without-harfbuzz --prefix=$PREFIX
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Install Fontconfig"
rm -rf /usr/local/share/fontconfig/conf.avail
meson setup --buildtype=release --prefix=$PREFIX --sysconfdir=$HOME -Ddoc=disabled -Dtests=disabled -Dtools=disabled fontconfig_builddir fontconfig
meson compile -C fontconfig_builddir
meson install -C fontconfig_builddir
echo "::endgroup::"


echo "::group::Building and Installing Pixman"
cd pixman
./configure --prefix=$PREFIX
make
make install
cd ..
echo "::endgroup::"

echo "::group::Building and Installing Cairo"
cd cairo
./configure --prefix=$PREFIX --enable-fontconfig --enable-freetype
make
make install
cd ..

#try using meson to see if things are fixed.
# meson setup --prefix=$PREFIX --buildtype=release -Dfontconfig=enabled -Dfreetype=enabled -Dtests=disabled cairo_builddir cairo
# meson compile -C cairo_builddir
# meson install -C cairo_builddir
echo "::endgroup::"

echo "::group::Building and Installing Harfbuzz"
meson setup --prefix=$PREFIX --buildtype=release -Dtests=disabled -Ddocs=disabled -Dgobject=disabled -Dcoretext=enabled -Dfreetype=enabled -Dglib=enabled harfbuzz_builddir harfbuzz
meson compile -C harfbuzz_builddir
meson install -C harfbuzz_builddir
echo "::endgroup::"

echo "::group::Buildling and Installing Pango"
meson setup --prefix=$PREFIX --buildtype=release -Dintrospection=disabled pango_builddir pango
meson compile -C pango_builddir
meson install -C pango_builddir
echo "::endgroup::"

cd $FILE_PATH
