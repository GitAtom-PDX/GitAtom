#! /usr/bin/env python3

import yaml
from gitatom import build
from pathlib import Path



# init.py


def init():
    print("initializing")
    
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

    posts_path = Path(publish_directory + '/posts')
    if not posts_path.exists():
        posts_path.mkdir(parents=True)

    atoms_path = Path('./atoms')
    if not atoms_path.exists():
        atoms_path.mkdir()

    build.create(publish_directory)



init()


