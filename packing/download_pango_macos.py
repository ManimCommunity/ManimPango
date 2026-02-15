#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve as download

PANGO_VERSION = "1.56.4-v2"

logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)


plat = sys.argv[1]
logging.debug(f"Platform is {plat}")

download_url = (
    "https://github.com/naveen521kk/pango-build/releases"
    f"/download/v{PANGO_VERSION}/pango-v{PANGO_VERSION}-mac-{plat}.zip"
)
final_location = Path(r"~/pangobuild").expanduser()
download_location = Path(tempfile.mkdtemp())
if final_location.exists():
    logging.info("Final Location already exists clearing it...")
    shutil.rmtree(str(final_location))
os.makedirs(final_location)
download_file = download_location / "build.zip"
logging.info("Downloading Pango and Cairo Binaries for macOS...")
logging.info("Url: %s", download_url)
download(url=download_url, filename=download_file)
logging.info(f"Download complete. Saved to {download_file}.")
logging.info(f"Extracting {download_file} to {download_location}...")
with zipfile.ZipFile(
    download_file, mode="r", compression=zipfile.ZIP_DEFLATED
) as file:  # noqa: E501
    file.extractall(download_location)
os.remove(download_file)
logging.info("Completed Extracting.")
logging.info("Moving Files accordingly.")

plat_location = download_location / f"mac-pango-{plat}"
for src_file in plat_location.glob("*"):
    logging.debug(f"Moving {src_file} to {final_location}...")
    shutil.move(str(src_file), str(final_location))
logging.info("Moving files Completed")
logging.info("Fixing .pc files")


# Get the current macOS SDK path — the pre-built binaries may reference
# an Xcode version that isn't installed on this runner.
current_sdk = subprocess.check_output(
    ["xcrun", "--sdk", "macosx", "--show-sdk-path"],
).decode().strip()
logging.info(f"Current macOS SDK: {current_sdk}")

# Matches any Xcode SDK path, e.g.
# /Applications/Xcode_15.4.app/.../SDKs/MacOSX.sdk
sdk_pattern = re.compile(
    r"/Applications/Xcode[^/]*/Contents/Developer/Platforms"
    r"/MacOSX\.platform/Developer/SDKs/MacOSX\.sdk"
)

rex = re.compile("^prefix=(.*)")


def new_place(_) -> str:
    return f"prefix={str(final_location.as_posix())}"


pc_files = final_location / "lib" / "pkgconfig"
for i in pc_files.glob("*.pc"):
    logging.info(f"Fixing {i}")
    with open(i) as f:
        content = f.read()
    content = rex.sub(new_place, content)
    content = sdk_pattern.sub(current_sdk, content)
    with open(i, "w") as f:
        f.write(content)
