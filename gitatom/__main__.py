from gitatom import build
import yaml
from gitatom import config
import shutil
import cmarkgfm  # used to convert markdown to html in mdtohtml()
import pygit2 
import glob
import sys
import re
import string
from os import path
from datetime import datetime 
from pathlib import Path
from xml.etree import cElementTree as ET
from jinja2 import Environment, FileSystemLoader
 
  
# Takes a .md file and pastes its content into an atom xml format
def atomify(md):
    # Check for invalid filetype
    if not md.endswith('.md'): exit("Incorrect input file type (expected .md)")

    # Get title and xml filename	
    entry_title= path.splitext(path.basename(md))[0] # TODO make os-agnostic 
    outname = entry_title + '.xml'

    # Check for a matching xml file 
    atompath = './atoms/'
    exists = glob.glob(atompath + outname) # should only ever return 0-1 matches
    if exists: # overwrite existing file
        s = slice(len(atompath), len(exists[0])) # use path length to slice
        outname = exists[0][s] # slice path from existing file name

    # Grab tags from config
    # Populate tags
    cfg = config.load_into_dict()
    feed_id = cfg['feed_id']
    feed_title = cfg['feed_title']

    entry_id = feed_id + outname[:-4] 

    #atome file already exists so update instead of create new
    if exists: # retain existing publish date
        tree = ET.parse(atompath + outname) 
        root = tree.getroot()
        entry_published = root.find('entry').find('published').text
        entry_updated = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    else: #atom file didnt exist yet 
        entry_published = datetime.now().strftime("%m/%d/%Y %H:%M:%S")	# using current time
        entry_updated = entry_published		
    feed_updated = entry_updated 		

    # Create atom strings
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
    outfile = open('./atoms/' + outname, 'w')
    outfile.write(atom)
    outfile.close()
    return outname
  
#git add the list of files that were created (HTML,XML)
def gitatom_git_add(repo, files):
    index = repo.index
    for f in files:
        index.add(f)
    index.write()
    print('end of gitatom_git_add()')



#get the list of files that have been staged with git
def git_staged_files(repo):
    status = repo.status()
    staged_files = []
    for file_path, flags in status.items():
        if flags == pygit2.GIT_STATUS_INDEX_NEW or flags == pygit2.GIT_STATUS_INDEX_MODIFIED:
            file_only = path.basename(file_path)
            #append the markdown files to list of staged files
            if file_only.endswith('.md') and 'markdowns' in file_path:
                staged_files.append('./markdowns/' + file_only)
    return staged_files


# create a list of files based on newly created files so that they can be git added in gitatom_git_add()
def on_commit(mds):
    files = []
    for md in mds:
        xml = atomify(md)
        files.append('atoms/' + xml)
    html = build.build_it()
    for f in html:
        files.append(f)
    return files
