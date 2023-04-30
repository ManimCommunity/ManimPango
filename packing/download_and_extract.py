#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import logging
import shutil
import tarfile
import tempfile
from pathlib import Path

import requests

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
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, tmpdirname)
    logging.info(
        f"Moving {str(tmpdirname / Path(Path(args.url).stem).stem)} "
        f"to {str(args.folder)}"
    )
    shutil.move(
        str(tmpdirname / Path(Path(args.url).stem).stem),
        str(args.folder),
    )
