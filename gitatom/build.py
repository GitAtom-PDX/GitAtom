# given: 'main_templates/nav-a.html', 
#        'main_templates/blog-a.html',
#        'main_templates/archive-a.html',
#        'main_templates/post-a.html',
#        'atoms/*.xml'
#
# build.py: scans the 'atoms/' directory and renders the nav, blog, archive and post html pages
#           (blog, archive and post templates extend the nav template)
#
# output: publish_directory/index.html
#         publish_directory/archive.html
#         publish_directory/posts/*.html

from gitatom import config
from pathlib import Path
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfm_options
from shutil import copyfile
from xml.etree import cElementTree as ET
from jinja2 import Environment, FileSystemLoader
import re
import dateutil.parser as dateparser
from dateutil import tz
from datetime import datetime, timezone
from gitatom import escape
import glob
from os import path
  
# used for recognizing post titles
# https://stackoverflow.com/a/3469155/364875
TITLE_RE = re.compile(
    r"[\s\n]*[#][^\S\n]*([^\n]*)\n+(.*)",
    flags=re.M|re.S,
)

# create files with no content 
def create(publish_directory):
    site_dir = Path(publish_directory)

    index = site_dir / "index.html"
    with open(index, 'w') as f:
        f.write("")
    archive = site_dir / "archive.html"
    with open(archive, 'w') as f:
        f.write("")

# https://thispointer.com/convert-utc-datetime-string-to-local-time-in-python/
local_zone = tz.tzlocal()

# convert ISO 8601 string to local timezone datetime
def datetime_local(iso):
    return dateparser.isoparse(iso).astimezone(local_zone)

# render datetime in a user-friendly detail format
def datetime_render(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

# render datetime as date
def datetime_date(dt):
    return dt.strftime("%Y-%m-%d")

# split content into title and body
def split_content(content):
    fields = TITLE_RE.fullmatch(content)
    assert fields is not None, "content split failure"
    title = fields[1].rstrip()
    body = fields[2]
    return title, body

RAW_TEXT_RE = re.compile("<[^>]*>([^<]*)<[^>]*>\n", flags=re.M)

# extract text from ElementTree leaf preserving entities.
# XXX This is the grossest hack I've done in a long time.
# Suggestions welcome. --Bart
def raw_text(node):
    text = ET.tostring(node, encoding="unicode", method="html")
    match = RAW_TEXT_RE.fullmatch(text)
    assert match is not None, f"internal error: failed match on '{text}'"
    return match[1]


# Set up a from-scratch configuration from the config data.
def get_atom_config():
    cfg = config.load_into_dict()
    if 'site_url' not in cfg:
        cfg['site_url'] = f"http://{feed_id}"
    cfg['now'] = f"{datetime.utcnow().isoformat(timespec='seconds')}Z"
    return cfg

def cfg_from_atom(cfg, md):
    cfg['entry_id'] = cfg['feed_id'] + '/' + cfg['entry_filename']

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


# generate a feed header
def feed_header(cfg):
    header = '<?xml version="1.0" encoding="utf-8"?>\n'
    header += '<feed xmlns="http://www.w3.org/2005/Atom">\n'
    header += f'<title>{cfg["feed_title"]}</title>\n'
    header += f'<id>{cfg["feed_id"]}</id>\n'
    header += '<link rel="self" type="application/atom+xml" '
    header += f'href="{cfg["site_url"]}/feed.atom"/>\n'
    header += '<generator uri="https://github.com/GitAtom-PDX/GitAtom">'
    header += 'GitAtom</generator>\n'
    header += f'<updated>{cfg["now"]}</updated>\n'
    return header

# Generate an Atom Feed File or Feed File header or Feed File entry.
def xatomify(outtype, md=None):
    assert outtype in {"file", "header", "entry"}, \
        f"internal error: unknown atom output type {outtype}"

    

    content_title, content_body = split_content(content)

    # Create entry
    entry = '<entry>\n'
    if outtype == "file":
        entry += '<title>' + entry_filename + '</title>\n'
    elif outtype == "entry":
        entry += '<title>' + content_title + '</title>\n'
    else:
        assert False, f"internal error: unknown atom content_type {outtype}"
    entry += '<author><name>' + author + '</name></author>\n'
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

    assert False, f"internal error: unknown atom type {outtype}"

# HERE

def gen_feed_file(cfg):
    feed = '<?xml version="1.0" encoding="UTF-8"?>\n'
    feed += '<feed xmlns="http://www.w3.org/2005/Atom">\n'
    feed += '<title>' + cfg['feed_title'] + '</title>\n'
    feed += '<updated>' + cfg['feed_updated'] + '</updated>\n'
    feed += '<id>' + cfg['feed_id'] + '</id>\n'
    feed += entry
    feed += '</feed>\n'
    return outname, feed

def atomify(md):
    # Check for invalid filetype
    assert md.endswith('.md'), f"Non .md file {md}"

    # Read and escape content.
    with open (md,'r') as f: 
        raw_content = f.read()
        content = escape.escape(raw_content)

    cfg = get_atom_config()
    cfg['content'] = content

    # Get path info.
    # TODO make os-agnostic 
    cfg['entry_filename'] = path.splitext(path.basename(md))[0]
    cfg['outname'] = cfg['entry_filename'] + '.xml'
    outname, feed = gen_feed_file(cfg)
    return outname, feed

# scan, render and write blog content
def build_it():
    # get 'Pathlib' paths and blog metadata from config file
    cfg = config.load_into_dict()
    site_dir = Path(cfg['publish_directory'])
    posts_dir = Path(cfg['publish_directory']) / 'posts'
    atoms_dir = Path('atoms')
    site_title = Path(cfg['feed_title'])
    site_author = Path(cfg['author'])

    # basic sanity check
    if not site_dir.is_dir():
        print("cannot build site")
        print("run init.py before committing to generate site")
        exit(1)

    # load jinja template location/environment
    file_loader = FileSystemLoader('./templates/')
    env = Environment(loader=file_loader)
    post_template = env.get_template('post-a.html')
    blog_template = env.get_template('blog-a.html')
    archive_template = env.get_template('archive-a.html')

    # set up state to be accumulated
    # atoms to be scanned and rendered
    atoms = list(atoms_dir.glob('*.xml'))
    # posts to be sorted and rendered on blog template
    posts = list()
    # posts to be sorted and rendered on archive template
    archives = list()
    # generated html files to be returned
    files = list()
    # markdown bodies to be added to feed.
    contents = list()

    # read atoms and render individual entries, add to lists
    for atom in atoms:
        # extract relevant information from atom feed file
        tree = ET.parse(atom)
        root = tree.getroot()
        entry = root.find('{*}entry')
        atom_content_raw = raw_text(entry.find('{*}content'))
        atom_content = escape.unescape(atom_content_raw)
        atom_updated = entry.find('{*}updated')
        atom_published = entry.find('{*}published')

        contents.append(atom_content)

        post_title, post_markdown = split_content(atom_content)
        post_body = cmarkgfm.markdown_to_html(
            post_markdown,
            options = cmarkgfm_options.CMARK_OPT_UNSAFE,
        )

        # get a post link
        post_link = (Path("posts") / atom.name).with_suffix('.html')

        # deal with updates
        # XXX non-updated posts by default have an `updated`
        # entry in their atom feed file that is the same as
        # their `published` entry
        post_published = datetime_local(atom_published.text)
        post_updated = post_published
        post_original = True
        if atom_updated is not None:
            upd = datetime_local(atom_updated.text)
            if upd != post_published:
                post_original = False
                post_updated = upd

        # queue the post
        post = {
            'published' : datetime_render(post_published),
            'updated' : datetime_render(post_updated),
            'original' : post_original,
            'title' : post_title,
            'body' : post_body,
            'link' : post_link,
        }
        posts.append(post)

        # queue the archive entry
        archive = dict(post)
        archive['published'] = datetime_date(post_published)
        archive['updated'] = datetime_date(post_updated)
        archives.append(archive)

        # write post html files, add to files list
        nav_dict = {
            'home' : '../index.html',
            'archive' : '../archive.html'
        }
        # XXX ugh there must be a better way to build this
        html_name = atom.stem + '.html'
        post_path = posts_dir / html_name
        with open(post_path, "w") as outfile:
            outfile.write(
                post_template.render(
                    stylesheet='../style.css',
                    nav=nav_dict,
                    **post,
                )
            )
            files.append(post_path)

    # sort and render blog and archive templates
    # XXX should sort on datetime not string
    sorted_posts = sorted(
        posts,
        key=lambda post: post['published'],
        reverse=True,
    )
    sorted_archives = sorted(
        archives,
        key=lambda item: item['published'],
        reverse=True,
    )
    nav_dict = {
        'home' : 'index.html',
        'archive' : 'archive.html',
    }
    basic_fields = {
        'stylesheet' : './style.css', 
        'title' : site_title, 
        'author' : site_author,
        'nav' : nav_dict,
    }
    # XXX should be configurable somehow
    sidebar_len = min(len(archives), 5)
    rendered_blog = blog_template.render(
        posts=sorted_posts,
        sidebar=sorted_archives[:sidebar_len],
        **basic_fields,
    )
    rendered_archive = archive_template.render(
        archive=sorted_archives,
        **basic_fields,
    )

    # write feed.xml
    with open("./site/feed.xml", 'w') as feed:
        atomheader = atomify("header")
        feed.write(atomheader)
        for md in contents:
            # add entry to feed file
            atomentry = atomify("entry", md=md)
            feed.write(atomentry)
        feed.write('</feed>\n')
    files.append('site/feed.xml')

    # write blog and archive html files, build files list
    index_path = site_dir / "index.html"
    with open(index_path, 'w') as f:
        f.write(rendered_blog)
    archive_path = site_dir / "archive.html"
    with open(archive_path, 'w') as f:
        f.write(rendered_archive)
    files.append(index_path)
    files.append(archive_path)
    return files
