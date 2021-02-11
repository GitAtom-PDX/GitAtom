#! /usr/bin/env python3

import os.path
from pathlib import Path
import yaml
from gitatom import build
from gitatom import config



# init.py


def init():
    print("initializing")

    cfg = config.load_into_dict()

    posts_path = Path(cfg['publish_directory'] + '/posts')
    if not posts_path.exists():
        posts_path.mkdir(parents=True)

    atoms_path = Path('./atoms')
    if not atoms_path.exists():
        atoms_path.mkdir()

    build.create(cfg['publish_directory'])



init()


