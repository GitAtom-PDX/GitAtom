#! /usr/bin/env python3

import yaml
import os.path
from gitatom import build
from pathlib import Path



# init.py


def init():
    print("initializing")

    # check if config file exists
    if not os.path.isfile('config.yaml'):
        print("config file not found, generating default config \"config.yaml\"")
        print("this file needs to be filled out!")
        feed_id = 'a-feed-id'
        feed_title = 'yet another blog'
        author = 'Author'
        publish_directory = './site'

        yaml_dict = {
                    'feed_id' : feed_id, \
                    'feed_title' : feed_title, \
                    'author' : author, \
                    'publish_directory' : publish_directory
                    }

        with open('config.yaml', 'w') as f:
            yaml.dump(yaml_dict, f)

    posts_path = Path('./site' + '/posts')
    if not posts_path.exists():
        posts_path.mkdir(parents=True)

    atoms_path = Path('./atoms')
    if not atoms_path.exists():
        atoms_path.mkdir()

    build.create('./site')



init()


