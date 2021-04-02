#!/bin/bash
#test wheels in different directory
set -e
package=$1

FILE_PATH="`dirname \"$0\"`"
FILE_PATH="`( cd \"$FILE_PATH\" && pwd )`"
if [ -z "$FILE_PATH" ] ; then
  exit 1
fi
pip install manim --no-deps
pip install colour numpy Pillow progressbar scipy tqdm pydub pygments rich pycairo networkx mapbox-earcut moderngl-window moderngl importlib-metadata
cd $TMP
cp -r $package/tests mtests
pytest -s mtests
rm -r mtests
cd $FILE_PATH
