#!/usr/bin/env python3
# init-content.py - Set up GitAtom content structure.

import os
from pathlib import Path
import sys
import yaml

from gitatom import build
from gitatom.config import publish_directory

# Write a default config file.
def generate_default_config(path):
    yaml_dict = {
        'feed_id' : 'feed id',
        'feed_title' : 'feed title',
        'author' : 'author',
        'repo_path' : 'path to bare git repository',
        'work_path' : 'path to work tree',
        'host' : 'host ip address',
        'port' : 'port number',
        'username' : 'username',
        'keypath' : 'path to ssh key',
        'deploy' : False
    }
    with open(path, 'w') as f:
        yaml.dump(yaml_dict, f, sort_keys=False)


#create the initial structure in local for hook and main to work with
content_path = Path('./content/')
if content_path.exists():
    print("./content: exists, giving up", file=sys.stderr)
    exit(1)
content_path.mkdir()

generate_default_config('./content/config.yaml')

posts_path = Path(f'./content/{publish_directory}/posts')
posts_path.mkdir(parents=True)

atoms_path = Path('./content/atoms')
atoms_path.mkdir()

markdowns_path = Path('./content/markdowns')
markdowns_path.mkdir()

build.create(f"./content/{publish_directory}")

# Set up the content repo.
wstatus = os.system("""sh -c '
cd content &&
git init &&
git add . &&
git commit -m "my blog, by GitAtom"'
""")
code = os.waitstatus_to_exitcode(wstatus)
if code != 0:
    print("content: repo creation failed, giving up.", file=sys.stderr)
    exit(1)
