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
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
  
def current_time():
    return f"{datetime.utcnow().isoformat(timespec='seconds')}Z"

# Takes a .md file and pastes its content into an atom xml format
def atomify(md):
    # Check for invalid filetype
    assert md.endswith('.md'), f"Non .md file {md}"

    # Get title and xml filename	
    entry_title= path.splitext(path.basename(md))[0] # TODO make os-agnostic 
    outname = entry_title + '.xml'

    # Grab tags from config
    # Populate tags
    cfg = config.load_into_dict()
    feed_id = cfg['feed_id']
    feed_title = cfg['feed_title']
    author_name = cfg['author']

    entry_id = feed_id + '/' + entry_title

    # Check for a matching xml file 
    atompath = './atoms/'
    # should only ever return 0-1 matches
    exists = glob.glob(atompath + outname)
    if exists:
        # atom file already exists so update instead of create new
        # overwrite existing file
        s = slice(len(atompath), len(exists[0])) # use path length to slice
        # check slice path against existing file name
        assert outname == exists[0][s], "weird match fail"
        # retain existing publish date
        tree = ET.parse(atompath + outname) 
        root = tree.getroot()
        entry = root.find('{*}entry')
        assert entry is not None, f"{outname}: no entry: {list(root)}"
        published = entry.find('{*}published')
        assert published is not None, f"{outname}: no published: {list(entry)}"
        entry_published = published.text
        entry_updated = current_time()
    else:
        # atom file didnt exist yet
        # use current time
        entry_published = current_time()
        entry_updated = entry_published		
    feed_updated = entry_updated 		

    # Create entry
    entry = '<entry>\n'
    entry += '<title>' + entry_title + '</title>\n'
    entry += '<author><name>' + author_name + '</name></author>'
    entry += '<id>' + entry_id + '</id>\n'
    entry += '<published>' + entry_published + '</published>\n'
    entry += '<updated>' + entry_updated + '</updated>\n'
    # https://stackoverflow.com/a/66029848/364875
    entry += '<content type="text/markdown; charset=UTF-8; variant=GFM">'

    with open (md,'r') as f: 
        entry += f.read()

    entry += '</content>\n'
    entry += '</entry>\n'

    
    feed = '<?xml version="1.0" encoding="UTF-8"?>\n'
    feed += '<feed xmlns="http://www.w3.org/2005/Atom">\n'
    feed += '<title>' + feed_title + '</title>\n'
    feed += '<updated>' + feed_updated + '</updated>\n'
    feed += '<id>' + feed_id + '</id>\n'
    feed += entry
    feed += '</feed>\n'

    return outname, entry, feed

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


# Generate atom content.  Returns a list of files based
# on newly created files so that they can be git added in
# gitatom_git_add().
def on_commit(mds):
    files = []
    for md in mds:
        outname, entry, feedfile = atomify(md)
        outfile = open('./atoms/' + outname, 'w')
        outfile.write(feedfile)
        outfile.close()
        files.append('atoms/' + outname)
    html = build.build_it()
    for f in html:
        files.append(f)
    return files
