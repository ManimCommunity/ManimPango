#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import shutil
import tempfile
from pathlib import Path

from wheel.cli.pack import pack
from wheel.cli.unpack import unpack

parser = argparse.ArgumentParser(
    description="Inject DLLs into a Windows binary wheel",
)
parser.add_argument(
    "wheel",
    type=str,
    help="the source wheel to which DLLs should be added",
)
parser.add_argument(
    "dest_dir",
    type=str,
    help="the directory where to create the repaired wheel",
)
parser.add_argument(
    "dll_dir",
    type=str,
    help="the directory containing the DLLs",
)

args = parser.parse_args()
wheel_name = os.path.basename(args.wheel)
package_name = wheel_name.split("-")[0]
version_number = wheel_name.split("-")[1]
repaired_wheel = os.path.join(args.dest_dir, wheel_name)
temp_dir = Path(tempfile.mkdtemp())

logging.basicConfig(level=logging.DEBUG)
logging.info("Extracting '%s' to '%s'", args.wheel, temp_dir)
unpack(args.wheel, str(temp_dir))

logging.info(
    "Adding DLLs from '%s' to package '%s'",
    args.dll_dir,
    package_name,
)

dll_dir = Path(args.dll_dir)
archive_path = temp_dir / f"{package_name}-{version_number}" / package_name

for local_path in dll_dir.glob("*.dll"):
    logging.info("Copying '%s' to '%s'", local_path, archive_path)
    shutil.copy(local_path, archive_path)
package_directory = temp_dir / f"{package_name}-{version_number}"
pack(str(package_directory), args.dest_dir, None)
