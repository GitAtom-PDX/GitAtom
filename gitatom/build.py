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

# get the non-extension part of the basename of p
def filepart(p):
    return path.splitext(path.basename(p))[0]

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
# Provides: site_url, now
def new_config():
    cfg = config.load_into_dict()
    if 'site_url' not in cfg:
        cfg['site_url'] = f"http://{cfg['feed_id']}"
    cfg['now'] = f"{datetime.utcnow().isoformat(timespec='seconds')}Z"
    return cfg

# Update a config from an atom file if possible; otherwise
# from the source md file.
# Requires: feed_id, entry_filename, now
# Provides: entry_id, entry_published, entry_updated
def update_cfg_from_atom(cfg):
    cfg['entry_id'] = cfg['feed_id'] + '/' + cfg['entry_filename']

    # Check for a matching xml file 
    atom_filename = './atoms/' + cfg['entry_filename'] + '.xml'
    # should only ever return 0-1 matches
    exists = Path(atom_filename).is_file()
    if exists:
        # atom file already exists so retain existing
        # publish date
        tree = ET.parse(atom_filename) 
        root = tree.getroot()
        entry = root.find('{*}entry')
        assert entry is not None, f"{outname}: no entry: {list(root)}"
        published = entry.find('{*}published')
        assert published is not None, f"{outname}: no published: {list(entry)}"
        cfg['entry_published'] = published.text
    else:
        # atom file didnt exist yet
        # use current time
        cfg['entry_published'] = cfg['now']
    cfg['entry_updated'] = cfg['now']
    return cfg

# Generate an Atom Feed Entry
# Requires: entry_title, entry_author, entry_id,
#   entry_published, entry_updated, entry_link,
#   entry_content_tag, entry_content
def gen_entry(cfg):
    # Create entry
    entry = '<entry>\n'
    entry += '<title>' + cfg['entry_title'] + '</title>\n'
    entry += '<author><name>' + cfg['entry_author'] + '</name></author>\n'
    entry += '<id>' + cfg['entry_id'] + '</id>\n'
    entry += '<published>' + cfg['entry_published'] + '</published>\n'
    entry += '<updated>' + cfg['entry_updated'] + '</updated>\n'
    entry_filename = cfg['entry_filename']
    site_url = cfg['site_url']
    entry_link = f'{site_url}/posts/{entry_filename}.html'
    entry += f'<link href="{entry_link}"/>\n'
    entry += cfg['entry_content_tag'] + '\n'
    entry += cfg['entry_content']
    entry += '</content>\n'
    entry += '</entry>\n'
    return entry

# generate atom feed header
# Requires: feed_title, feed_id, now
def gen_atom_header(cfg):
    header = '<?xml version="1.0" encoding="utf-8"?>\n'
    header += '<feed xmlns="http://www.w3.org/2005/Atom">\n'
    header += '<title>' + cfg["feed_title"] + '</title>\n'
    header += '<id>' + cfg["feed_id"] + '</id>\n'
    header += '<updated>' + cfg["now"] + '</updated>\n'
    header += '<generator uri="https://github.com/GitAtom-PDX/GitAtom">'
    header += 'GitAtom</generator>\n'
    return header

def gen_atom_footer(cfg):
    return "</feed>\n"

# generate Atom Feed content string
def gen_feedfile(md):
    # Check for invalid filetype
    assert md.endswith('.md'), f"Non .md file {md}"

    # Get a base config
    cfg = new_config()

    # Read and escape content.
    cfg['entry_filename'] = filepart(md)
    with open(md, 'r') as f: 
        raw_content = f.read()
        content = escape.escape(raw_content)
    cfg['entry_content'] = content

    # Update cfg for entry.
    cfg = update_cfg_from_atom(cfg)
    cfg['entry_title'] = cfg['entry_filename']
    cfg['entry_author'] = cfg['author']
    site_url = cfg['site_url']
    cfg['entry_content_tag'] = \
        '<content type="text/markdown; charset=UTF-8; variant=GFM">'

    # Generate feed file contents.
    feed = gen_atom_header(cfg)
    feed += gen_entry(cfg)
    feed += gen_atom_footer(cfg)

    return feed

# generate Atom feed header
# Requires: gen_atom_header(), site_url
def gen_feed_header(cfg):
    header = gen_atom_header(cfg)
    header += '<link rel="self" type="application/atom+xml" '
    header += f'href="{cfg["site_url"]}/feed.xml"/>\n'
    return header

def gen_feed_footer(cfg):
    return gen_atom_footer(cfg)

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
    # and in Atom feed
    posts = list()
    # posts to be sorted and rendered on archive template
    archives = list()
    # generated html files to be returned
    files = list()

    # read atoms and render individual entries, add to lists
    for atom in atoms:
        # extract relevant information from atom feed file
        tree = ET.parse(atom)
        root = tree.getroot()
        entry = root.find('{*}entry')
        atom_id = entry.find('{*}id')
        atom_content_raw = raw_text(entry.find('{*}content'))
        atom_content = escape.unescape(atom_content_raw)
        atom_updated = entry.find('{*}updated')
        atom_published = entry.find('{*}published')
        atom_filename = filepart(atom)

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
            'id' : atom_id.text,
            'filename' : atom_filename,
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

    # sort templates
    def sorted_cfgs(cfgs):
        # XXX should sort on datetime not string
        def sort_key(cfg):
            return (cfg['published'], cfg['updated'], cfg['id'])

        return sorted(cfgs, key=sort_key, reverse=True)

    sorted_posts = sorted_cfgs(posts)
    sorted_archives = sorted_cfgs(archives)

    # render posts and archives
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
        cfg = new_config()
        feed_header = gen_feed_header(cfg)
        feed.write(feed_header)
        for post in sorted_posts:
            cfg['entry_title'] = post['title']
            cfg['entry_author'] = cfg['author']
            cfg['entry_id'] = post['id']
            cfg['entry_published'] = post['published']
            cfg['entry_updated'] = post['updated']
            cfg['entry_filename'] = post['filename']
            cfg['entry_content'] = post['body']
            site_url = cfg['site_url']
            cfg['entry_content_tag'] = \
                f'<content type="xhtml" xml:base="{site_url}">'
            feed_entry = gen_entry(cfg)
            feed.write(feed_entry)
        feed_footer = gen_feed_footer(cfg)
        feed.write(feed_footer)
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
