#!/bin/bash
# Test installed wheel by running the test suite from a temporary directory.
# This ensures tests import the installed package, not the source tree.
#
# Usage: bash packing/test_wheels.sh /path/to/project
set -euo pipefail

project="$1"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

cp -r "$project/tests" "$tmpdir/tests"
cd "$tmpdir"
pytest -s tests
