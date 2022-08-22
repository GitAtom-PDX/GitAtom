from gitatom import build
import yaml
from gitatom import config
import shutil
import cmarkgfm  # used to convert markdown to text in atomify.
from cmarkgfm.cmark import Options as cmarkgfm_options
import pygit2 
import glob
import sys
import string
from os import path
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from gitatom import escape

# Generate an Atom Feed File or Feed File header or Feed File entry.
def atomify(outtype, md=None):
    assert outtype in {"file", "header", "entry"}, \
        f"internal error: unknown atom output type {outtype}"

    # Grab tags from config
    # Populate tags
    cfg = config.load_into_dict()
    feed_id = cfg['feed_id']
    feed_title = cfg['feed_title']
    author_name = cfg['author']
    if 'site_url' in cfg:
        site_url = cfg['site_url']
    else:
        site_url = f"http://{feed_id}"
    now = f"{datetime.utcnow().isoformat(timespec='seconds')}Z"

    # Take care of just generating a header.
    if outtype == "header":
        header = '<?xml version="1.0" encoding="utf-8"?>\n'
        header += '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        header += f'<title>{feed_title}</title>\n'
        header += f'<id>{feed_id}</id>\n'
        header += '<link rel="self" type="application/atom+xml" '
        header += f'href="{site_url}/feed.atom"/>\n'
        header += '<generator uri="https://github.com/GitAtom-PDX/GitAtom">'
        header += 'GitAtom</generator>\n'
        header += f'<updated>{now}</updated>\n'
        return header
    
    # Get title and xml filename	
    entry_filename= path.splitext(path.basename(md))[0] # TODO make os-agnostic 
    outname = entry_filename + '.xml'

    # Check for invalid filetype
    assert md.endswith('.md'), f"Non .md file {md}"

    entry_id = feed_id + '/' + entry_filename

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
        entry_updated = now
    else:
        # atom file didnt exist yet
        # use current time
        entry_published = now
        entry_updated = entry_published		
    feed_updated = entry_updated

    with open (md,'r') as f: 
        raw_content = f.read()
        content = escape.escape(raw_content)
    content_title, content_body = build.split_content(content)

    # Create entry
    entry = '<entry>\n'
    if outtype == "file":
        entry += '<title>' + entry_filename + '</title>\n'
    elif outtype == "entry":
        entry += '<title>' + content_title + '</title>\n'
    else:
        assert False, f"internal error: unknown atom content_type {outtype}"
    entry += '<author><name>' + author_name + '</name></author>\n'
    entry += '<id>' + entry_id + '</id>\n'
    entry += '<published>' + entry_published + '</published>\n'
    entry += '<updated>' + entry_updated + '</updated>\n'
    # https://stackoverflow.com/a/66029848/364875
    if outtype == "file":
        entry += '<content type="text/markdown; charset=UTF-8; variant=GFM">'
        entry += content
        entry += '</content>\n'
    elif outtype == "entry":
        entry += f'<link href="{site_url}/posts/{entry_filename}.html">\n'
        entry += f'<content type="xhtml" xml:base="{site_url}">'
        html_content = cmarkgfm.markdown_to_html(
            content_body,
            options = cmarkgfm_options.CMARK_OPT_UNSAFE,
        )
        entry += html_content
        entry += '</content>\n'
    else:
        assert False, f"internal error: unknown atom content type {outtype}"
    entry += '</entry>\n'

    if outtype == "entry":
        return entry

    if outtype == "file":
        feed = '<?xml version="1.0" encoding="UTF-8"?>\n'
        feed += '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        feed += '<title>' + feed_title + '</title>\n'
        feed += '<updated>' + feed_updated + '</updated>\n'
        feed += '<id>' + feed_id + '</id>\n'
        feed += entry
        feed += '</feed>\n'
        return outname, feed

    assert False, f"internal error: unknown atom type {outtype}"

#git add the list of files that were created (HTML,XML)
def gitatom_git_add(repo, files):
    index = repo.index
    for f in files:
        index.add(f)
    index.write()

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
    with open("./site/feed.xml", 'w') as feed:
        atomheader = atomify("header")
        feed.write(atomheader)
        for md in mds:
            # make feed entry file
            outname, feedfile = atomify("file", md=md)
            outfile = open('./atoms/' + outname, 'w')
            outfile.write(feedfile)
            outfile.close()
            files.append('atoms/' + outname)

            # add entry to feed file
            atomentry = atomify("entry", md=md)
            feed.write(atomentry)
        feed.write('</feed>\n')
    files.append('site/feed.xml')
    html = build.build_it()
    for f in html:
        files.append(f)
    return files
