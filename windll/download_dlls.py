#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import shutil
import struct
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve as download


def get_platform():
    if (struct.calcsize("P") * 8) == 32:
        return "x86"
    else:
        return "amd64"


download_url = "https://ci.appveyor.com/api/projects/naveen521kk/pango-cairo-build/artifacts/pango-cairo-build.zip?job=image:%20Visual%20Studio%202017"  # noqa: E501
logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)

final_location = Path(r"C:\cibw\vendor")
download_location = Path(tempfile.mkdtemp())
if final_location.exists():
    logging.info("Final Location already exists clearing it...")
    shutil.rmtree(str(final_location))

os.makedirs(final_location)
download_file = download_location / "build.zip"
logging.info("Downloading Pango and Cairo Binaries for Windows...")
download(url=download_url, filename=download_file)
logging.info(f"Download complete. Saved to {download_file}.")
logging.info(f"Extracting {download_file} to {download_location}...")
with zipfile.ZipFile(
    download_file, mode="r", compression=zipfile.ZIP_DEFLATED
) as file:  # noqa :E501
    file.extractall(download_location)
os.remove(download_file)
shutil.move(
    str(download_location / "build" / "pkg-config"), str(final_location)
)  # noqa E501
logging.info("Completed Extracting.")
plat = get_platform()
logging.debug(f"Found Platform as {plat}")
logging.info("Moving Files accordingly.")
plat_location = download_location / "build" / plat
for src_file in plat_location.glob("*"):
    logging.debug(f"Moving {src_file} to {final_location}...")
    shutil.move(str(src_file), str(final_location))
logging.info("Moving files Completed")
logging.info("Fixing .pc files")


rex = re.compile("^prefix=(.*)")


def new_place(some):
    return f"prefix={str(final_location.as_posix())}"


pc_files = final_location / "lib" / "pkgconfig"
for i in pc_files.glob("*.pc"):
    logging.info(f"Writing {i}")
    with open(i) as f:
        content = f.read()
        final = rex.sub(new_place, content)
    with open(i, "w") as f:
        f.write(final)
