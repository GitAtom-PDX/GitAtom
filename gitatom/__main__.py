import build
import yaml
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
from jinja2 import Environment, FileSystemLoader


#Functions not being used in current iteration, together do some modification of title to capitilize and append date to front
"""
# Generate blog post title from .md filename
def getTitle(filename):
    # Determine filename style
    if '-' in filename: 
        words = filename.replace('-',' ').split(' ')

    elif '_' in filename:
        words = filename.replace('_',' ').split(' ')

    elif ' ' in filename:
        words = filename.split(' ')	

        # Check for single-word titles
        # https://www.geeksforgeeks.org/python-test-if-string-contains-any-uppercase-character/
    elif not bool(re.match(r'\w*[A-Z]\w*', filename)):
        return filename

    else: # assume camelCase
        words = camelCaseSplit(filename)

    words = [word.capitalize() for word in words]
    title = ' '.join(words)
    return title
 # Generate xml filename from title and date
def getFilename(title):
    # Generate date in YYYYMMDD	
    filename = datetime.today().strftime('%Y%m%d')

    # Append title to date 
    if ' ' not in title: # check for single-word title
        filename += title
    else: 
        words = title.split(' ')
        for word in words: filename += word

    return filename 

# camelCase splitter 
# https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
def camelCaseSplit(str):
    str = str[0].upper() + str[1:] # preserve lowercase first words
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)
"""
  
  
# Takes a .md file and pastes its content into an atom xml format
def atomify(md):
    # Check for invalid filetype
    if not md.endswith('.md'): exit("Incorrect input file type (expected .md)")

    # Get title and xml filename	
    entry_title= path.splitext(path.basename(md))[0] # TODO make os-agnostic 
    outname = entry_title + '.xml'
    #print('outname from atomify: ', outname)

    # Check for a matching xml file 
    atompath = './atoms/'
    exists = glob.glob(atompath + '*' + outname + '*') # should only ever return 0-1 matches
    if exists: # overwrite existing file
        s = slice(len(atompath), len(exists[0])) # use path length to slice
        outname = exists[0][s] # slice path from existing file name

    # Grab tags from config
    # Populate tags
    feed_id = config.options['feed_id']
    feed_title = config.options['feed_title']

    entry_id = feed_id + outname[:-4] 
    if exists: # retain existing publish date
        tree = ET.parse(atompath + outname) 
        root = tree.getroot()
        entry_published = root.find('entry').find('published').text
        entry_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    else:
        entry_published = datetime.now().strftime("%d/%m/%Y %H:%M:%S")	# using current time
        entry_updated = entry_published		
    feed_updated = entry_updated 		

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

    # https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
    with open (md,'r') as f: 
        #embedded html brackets replaced with *** on either side, can be replaced later using opposite operation
        atom += f.read().replace('<', '\**').replace('>', '**/')

    atom += '</content>\n'
    atom += '</entry>\n'
    atom += '</feed>\n'

    # Write result to file
    #outname += '.xml' 
    outfile = open('./atoms/' + outname, 'w')
    outfile.write(atom)
    outfile.close()
    #subprocess.call(['git', 'add', 'atoms/' + outname])
    #subprocess.call(['git','commit','-m','adding {} to vc'.format(outname)])
    return outfile.name

  
  
def render(filename):

    #get data from xml
    tree = ET.parse(filename)
    root = tree.getroot()

    #get feed and content info from xml file
    title = root.find('entry').find('title').text
    updated = root.find('entry').find('updated').text
    content = root.find('entry').find('content').text
   
    # load template html file
    template_env = Environment(
        loader=FileSystemLoader(searchpath='gitatom/post_templates/'))
    template = template_env.get_template('default_jinja.html')

    # convert content which should be in md to html
    html_text = cmarkgfm.markdown_to_html(content)
    html_name = title + '.html'

    posts_directory = config.options['publish_directory'] + '/posts/'

    with open(posts_directory + html_name, "w") as outfile:
        outfile.write(
            template.render(
                title=title,
                date=updated,
                blog=html_text
            )
        )

    #subprocess.call(['git', 'add', posts_directory + html_name])
    #subprocess.call(['git','commit','-m','adding {} to vc'.format(html_name)])
    return html_name


def gitatom_git_add(md_file,xml_file,html_file):
    subprocess.call(['git', 'add', md_file])
    subprocess.call(['git', 'add', 'files/xml_files/' + xml_file])
    subprocess.call(['git', 'add', 'files/html_files/' + html_file])
    subprocess.call(['git', 'commit', '-m', 'Adding {}, {}, {} files to git.'.format(md_file, xml_file, html_file)])


def gitatom_git_push(filename):
    print('New files add to vc, push when ready.')
    #print('Push called with file: {}'.format(filename))
    #subprocess.call(['git', 'push', 'origin', 'git_hook'])


def run(filename):
    xml_file = atomify(filename)
    html_file = render(xml_file)
    #published_file = publish(html_file)
    #build.append(published_file)
    build.build_it()
    #gitatom_git_add(filename,xml_file,html_file)


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


def usage():
    exit("Usage: python3 gitatom [command] (filename)")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init': init()
        elif command == 'build': build.build_it()
        elif len(sys.argv) > 2:
            file_out = ''     
            filename = sys.argv[2]
            #print("printing filename from main: ", filename)
            if command == 'atomify':
                #subprocess.call(['git', 'add', filename])
                file_out = atomify(filename)
            elif command == 'render': file_out = render(filename)
            elif command == 'run': 
                #subprocess.call(['git', 'add', filename])
                file_out = run(filename)
            else: usage()
            #gitatom_git_push(file_out)
        else: usage()
    else: usage()
