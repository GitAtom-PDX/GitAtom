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
        return filename.capitalize()

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

  
  
# Takes a .md file and pastes its content into an atom xml format
def atomify(md):
    # Check for invalid filetype
    if not md.endswith('.md'): exit("Incorrect input file type (expected .md)")

    # Get title and xml filename	
    filename = path.splitext(path.basename(md))[0] # TODO make os-agnostic 
    entry_title = getTitle(filename)
    outname = getFilename(entry_title) + '.xml'
    #print('outname from atomify: ', outname)

    # Check for a matching xml file 
    exists = glob.glob('./files/xml_files/*' + outname[8:] + '*') # should only ever return 0-1 matches
    if exists: outname = exists[0][2:] # overwrite existing file 

    # Grab tags from config
    config_f = open('./gitatom/gitatom.config')
    config = config_f.readlines()
    config_f.close()

    # Populate tags
    feed_id = config[0].strip()
    feed_title = config[1].strip()
    entry_id = feed_id + outname[:-4] 
    if exists: # retain existing publish date
        tree = ET.parse(outname) 
        root = tree.getroot()
        entry_published = root.find('entry').find('published').text
        entry_updated = datetime.now()
        entry_updated.replace(microsecond=0)
    else:
        entry_published = datetime.now()	# using current time
        entry_published.replace(microsecond=0) 	# truncate ms
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
    outfile = open('files/xml_files/' + outname, 'w')
    outfile.write(atom)
    outfile.close()

    subprocess.call(['git', 'add', 'files/xml_files/' + outname])
    subprocess.call(['git','commit','-m','adding {} to vc'.format(outname)])
    return outname

  
  
def render(filename):

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


    with open('files/html_files/' + html_name, "w") as outfile:
        outfile.write(
            template.render(
                title=title,
                date=updated,
                blog=html_text
            )
        )

    subprocess.call(['git', 'add', 'files/html_files/' + html_name])
    subprocess.call(['git','commit','-m','adding {} to vc'.format(html_name)])
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
    published_file = publish(html_file)
    build.append(published_file)
    gitatom_git_add(filename,xml_file,html_file)


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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        file_out = ''     
       
        elif len(sys.argv) > 2:
            filename = sys.argv[2]
            #print("printing filename from main: ", filename)
            if command == 'atomify':
                subprocess.call(['git', 'add', filename])
                file_out = atomify(filename)
            elif command == 'render': file_out = render(filename)
            elif command == 'publish': file_out = publish(filename)
            elif command == 'run': 
                subprocess.call(['git', 'add', filename])
                file_out = run(filename)
            else: usage()
            gitatom_git_push(file_out)
        else: usage()

    else: usage()
