from sys import argv

import yaml
import config

from os import path
from datetime import datetime 

import cmarkgfm
from jinja2 import Environment, FileSystemLoader
from xml.etree import cElementTree as ET

from pathlib import Path
import shutil

import build


# insert definitions and/or `import other-modules`

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

    #get data from xml
    tree = ET.parse(filename)
    root = tree.getroot()

    #get feed and content info from xml file
    title = root.find('entry').find('title').text
    updated = root.find('entry').find('updated').text
    content = root.find('entry').find('content').text
    """
    #can use something like this if we nede to pull template info from xml files with multiple entries
    for page in root.findall('entry'):
        title = root.find('entry').find('title').text
        updated = root.find('entry').find('updated').text
        content = root.find('entry').find('content').text
    """

    # load template html file
    template_env = Environment(
        loader=FileSystemLoader(searchpath='./templates/post_templates/'))
    template = template_env.get_template('default_jinja.html')

    # convert content which should be in md to html
    html_text = cmarkgfm.markdown_to_html(content)
    html_name = title + '.html'

    with open(html_name, "w") as outfile:
        outfile.write(
            template.render(
                title=title,
                date=updated,
                blog=html_text
            )
        )

    return html_name


def publish(filename):
    print(f"calling publish on {filename}")
    # input: string representation of path to source file.
    # returns: ERROR if the source file does not exist.
    # This function copies the source file to TARGET_DIRECTORY.
    # Automatically builds the target directory and sub directories
    # for the posts depending on the hyphens at the beginning of
    # the file. Example: aaa-bbb-ccc-file.html is copied to
    # ./site/posts/aaa/bbb/ccc/file.html

    TARGET_DIRECTORY = config.options['publish_directory']
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
