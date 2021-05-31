#!/bin/bash

set -e
set -x

PYTHON_VERSION=$(python -c "import sys;print(f'{sys.version_info.major}{sys.version_info.minor}')")
BITNESS=$1

if [[ "$PYTHON_VERSION" == "36" || "$BITNESS" == "32" ]]; then
    # For Python 3.6 and 32-bit architecture use the regular
    # test command (outside of the minimal Docker container)
    pytest
else
    docker container run --rm ManimCommunity/minimal-windows \
                         powershell -Command "pytest"
fi
