#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import re
import shlex
import shutil
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlretrieve as download

PANGO_VERSION = "1.48.4"


def get_platform():
    if (struct.calcsize("P") * 8) == 32:
        return "32"
    else:
        return "64"


logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)


plat = get_platform()
logging.debug(f"Found Platform as {plat}")

download_url = (
    "https://github.com/naveen521kk/pango-build/releases"
    f"/download/v{PANGO_VERSION}/pango-build-win{plat}.zip"
)
final_location = Path(r"C:\cibw\vendor")
download_location = Path(tempfile.mkdtemp())
if final_location.exists():
    logging.info("Final Location already exists clearing it...")
    shutil.rmtree(str(final_location))
os.makedirs(final_location)
download_file = download_location / "build.zip"
logging.info("Downloading Pango and Cairo Binaries for Windows...")
logging.info("Url:%s", download_url)
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

plat_location = download_location
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

logging.info("Building pkg-config")

pkg_config_log = r"C:\cibw\pkg-config"
build_file_loc = str(
    (Path(__file__).parent.resolve() / "build_pkgconfig.ps1").absolute()
)
command = f'powershell -nologo -noexit -file "{build_file_loc}" "{pkg_config_log}"'
print(command)
subprocess.check_call(shlex.split(command), shell=True)
