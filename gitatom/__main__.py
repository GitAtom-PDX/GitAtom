import build
import config
import shutil
import cmarkgfm  # used to convert markdown to html in mdtohtml()
import subprocess
import glob
import sys
import re
import string
from os import path
from datetime import datetime 
from pathlib import Path
from xml.etree import cElementTree as ET

def atomify(filename):
    print(f"calling atomify on {filename}")
    # atomify.py
    # Encloses given md in atom xml tags

    # NOTE file handling is not currently OS-agnostic

    # Required <entry> atom tags: 
    # <id> unique entry id, generated and contatenated with feed id
    # <title> title of post, populated from markdown filename
    # <updated> latest update, NOTE see README
    # <published> creation date, current time (requested by sponsor, not required by atom)
    # <content> markdown file contents with escaped characters

    # Required <feed> atom tags: 
    # <id> site URI, populated from config file 
    # <title> title of website, populated from config file
    # <updated> latest feed update, populated from entry tag

    # Open required files - this is currently designed such 
    # that atomify [file] processes one md file at a time
    if not filename.endswith('.md'): exit("Incorrect input file type (expected .md)")
    md = filename

    # Populate required tags 
    feed_id = config.options['feed_id']
    feed_title = config.options['feed_title']

    entry_title = path.splitext(path.basename(md))[0] # TODO make os-agnostic 
    entry_id = feed_id + entry_title # depends on feed id

    # TODO how to check if the given markdown file is a new or existing post...
    # how best to handle updating an existing post? 

    entry_published = datetime.now()		# using current time
    entry_published.replace(microsecond=0) 	# truncate ms
    entry_updated = entry_published			# TODO how to handle updating entries...?
    feed_updated = entry_updated 		# depends on entry updated

    # Create atom string
    atom = '<feed>\n'
    atom += '<title>' + feed_title + '</title>\n'
    atom += '<updated>' + str(feed_updated) + '</updated>\n'
    atom += '<id>' + feed_id + '</id>\n'
    atom += '<entry>\n'
    atom += '<title>' + entry_title + '</title>\n'
    atom += '<id>' + entry_id + '</id>\n'
    atom += '<published>' + str(entry_published) + '</published>\n'
    atom += '<updated>' + str(entry_updated) + '</updated>\n'
    atom += '<content>' 

    # NOTE https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
    with open (md,'r') as f: 
        atom += f.read().replace('<', '\<').replace('>', '\>')

    atom += '</content>\n'
    atom += '</entry>\n'
    atom += '</feed>\n'

    # Write result to file
    outname = entry_title + '.xml' # TODO need a good naming schema...
    outfile = open(outname, 'w')
    outfile.write(atom)
    outfile.close()

    return outfile.name


def render(filename):
    print(f"calling render on {filename}")

    def md_to_html(md_text, filename):
        pass

    # get data from xml
    #mydoc = minidom.parse(filename) - FAILS

    entry_title = path.splitext(path.basename(filename))[0]
    rendered = "<html>see: render()</html>"

    # Write result to file
    outname = entry_title + '.html'
    outfile = open(outname, 'w')
    outfile.write(rendered)
    outfile.close()
    return outfile.name


def publish(filename):
    print(f"calling publish on {filename}")
    # input: string representation of path to source file.
    # returns: ERROR if the source file does not exist.
    # This function copies the source file to TARGET_DIRECTORY.
    # Automatically builds the target directory and sub directories
    # for the posts depending on the hyphens at the beginning of
    # the file. Example: aaa-bbb-ccc-file.html is copied to
    # ./site/posts/aaa/bbb/ccc/file.html

    TARGET_DIRECTORY = config.options["publish_directory"]
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
    return True


def include(filename):
    xml_file = atomify(filename)
    html_file = render(xml_file)
    publish(html_file)


def usage():
    exit("Usage: python3 -m gitatom [command] (filename)")


if __name__ == '__main__':
    if len(argv) > 1:
        command = argv[1]
        if command == 'build': build.build_it('./site')
        elif len(argv) > 2:
            filename = argv[2]
            if command == 'atomify': atomify(filename)
            elif command == 'render': render(filename)
            elif command == 'publish': publish(filename)
            elif command == 'include': include(filename)
            else: usage()
        else: usage()
    else: usage()
