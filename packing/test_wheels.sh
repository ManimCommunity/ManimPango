#!/bin/bash
#test wheels in different directory
set -e
set -x
package=$1

FILE_PATH="`dirname \"$0\"`"
FILE_PATH="`( cd \"$FILE_PATH\" && pwd )`"
if [ -z "$FILE_PATH" ] ; then
  exit 1
fi

cd $TMP
cp -r $package/tests tests
pytest -s tests
rm -r tests
cd $FILE_PATH
