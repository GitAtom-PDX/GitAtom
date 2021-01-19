import yaml
import config

import build
from sys import argv

from os import path
from datetime import datetime 

from pathlib import Path
import shutil

# insert definitions and/or `import other-modules`

def atomify(filename):
    print(f"calling atomify on {filename}")
    return None


def render(filename):
    print(f"calling render on {filename}")
    return None


def publish(filename):
    print(f"calling publish on {filename}")
    # input: string representation of path to source file.
    # returns: ERROR if the source file does not exist.
    # This function copies the source file to TARGET_DIRECTORY.
    # Automatically builds the target directory and sub directories
    # for the posts depending on the hyphens at the beginning of
    # the file. Example: aaa-bbb-ccc-file.html is copied to
    # ./site/posts/aaa/bbb/ccc/file.html

    TARGET_DIRECTORY = config.options['publish_directory'] + 'posts/'
    ERROR = -1

    src_path = Path(filename)
    if not src_path.exists():
        return ERROR

    # extract the filename from full path, split filname into pieces
    # based on '-'
    # ex: 2020-12-1-post.html is split into:
    # ['2020', '12', '1', 'post.html']
    src_filename = src_path.name
    name_tokens = src_filename.split("-")

    # build the destination directory based on previous pieces
    dest_path = Path(TARGET_DIRECTORY)
    for i in range(len(name_tokens) - 1):
        dest_path = dest_path / name_tokens[i]

    if not dest_path.exists():
        dest_path.mkdir(parents=True)

    # append filename w/out date info to destination path
    dest_path = dest_path / name_tokens[-1]

    shutil.copy(src_path, dest_path)
    #TODO need to return some metric of success here, maybe just 1
    return dest_path.name


def run(filename):
    xml_file = atomify(filename)
    html_file = render(xml_file)
    published_file = publish(html_file)
    build.append(published_file)


def init(target):
    print(f"initializing {target}")

    # save global variables - target is location of 'publish_directory'
    if target.endswith('/'):
        target = target[:-1]
    
    yaml_dict = { 'publish_directory' : f'{target}/site/', \
                'feed_id' : 'https://git.atom/', \
                'feed_title' : 'Git Atom', \
                'author_name' : 'Author', \
                'entry_template' : 'gitatom/templates/blogs.html' }

    with open('config.yaml', 'w') as f:
        yaml.dump(yaml_dict, f)

    # create publish directory 'target/site/'
    target_path = Path(target + '/site')
    if not target_path.exists():
        target_path.mkdir(parents=True)
    else:
        return False

    # make skeleton index.html and style.css
    build.create(target + '/site')

    # insert post-commit script into ./git/hooks here ??


def usage():
    exit("Usage: python3 gitatom [command] (target)")


if __name__ == '__main__':
    if len(argv) == 3:
        if argv[1] == 'init': init(argv[2])
        elif argv[1] == 'atomify': atomify(argv[2])
        elif argv[1] == 'render': render(argv[2])
        elif argv[1] == 'publish': publish(argv[2])
        elif argv[1] == 'append': build.append(argv[2])
        elif argv[1] == 'run': run(argv[2])
        else: usage()
    else: usage()
