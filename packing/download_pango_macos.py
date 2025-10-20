#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve as download

PANGO_VERSION = "1.56.4-v1"

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


rex = re.compile("^prefix=(.*)")


def new_place(_) -> str:
    return f"prefix={str(final_location.as_posix())}"


pc_files = final_location / "lib" / "pkgconfig"
for i in pc_files.glob("*.pc"):
    logging.info(f"Writing {i}")
    with open(i) as f:
        content = f.read()
        final = rex.sub(new_place, content)
    with open(i, "w") as f:
        f.write(final)
