#!/bin/bash

set -e
set -x

PYTHON_VERSION=$(python -c "import sys;print(f'{sys.version_info.major}{sys.version_info.minor}')")
BITNESS=$1
PACKAGE=$2

if [[ "$PYTHON_VERSION" == "36" || "$BITNESS" == "32" ]]; then
    # For Python 3.6 and 32-bit architecture use the regular
    # test command (outside of the minimal Docker container)
    FILE_PATH="`dirname \"$0\"`"
    FILE_PATH="`( cd \"$FILE_PATH\" && pwd )`"
    if [ -z "$FILE_PATH" ] ; then
        exit 1
    fi
    cd $TMP
    cp -r $PACKAGE/tests mtests
    pytest -s mtests
    rm -r mtests
    cd $FILE_PATH
else
    docker container run --rm manimcommunity/minimal-windows \
                         powershell -Command "pytest"
fi
