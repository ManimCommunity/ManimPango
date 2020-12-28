 #!/usr/bin/python

import requests
import argparse
import tempfile
import tarfile
import shutil
from pathlib import Path
import logging

logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.INFO)
parser = argparse.ArgumentParser(description="Download things.")
parser.add_argument("url", help="the url to download")
parser.add_argument("folder", help="folder name to extract")
args = parser.parse_args()

a = requests.get(args.url)
logging.info("Download Complete Extracting")
assert a.status_code != 404, "Does not exist."
with tempfile.TemporaryDirectory() as tmpdirname:
    tmpdirname = Path(tmpdirname)
    fname = Path(args.url).name
    for i in tmpdirname.iterdir():
        print(i)
    with open(tmpdirname / fname, "wb") as f:
        logging.info(f"Saving to {tmpdirname / fname}")
        f.write(a.content)
    with tarfile.open(tmpdirname / fname, "r") as tar:
        logging.info(f"Extracting {tmpdirname / fname} to {tmpdirname}")
        tar.extractall(tmpdirname)
    logging.info(
        f"Moving {str(tmpdirname / Path(Path(args.url).stem).stem)} to {str(args.folder)}"
    )
    shutil.move(str(tmpdirname / Path(Path(args.url).stem).stem), str(args.folder))
