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
import re
from xml.etree import cElementTree as ET
from jinja2 import Environment, FileSystemLoader
import dateutil.parser as dateparser
from dateutil import tz
from datetime import datetime

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

# Convert ISO 8601 string to local timezone.
def dtlocal(iso):
    t = dateparser.isoparse(iso).astimezone(local_zone)
    return t.strftime("%Y-%m-%d %H:%M:%S %Z")

# used for recognizing post titles
TITLE_RE = re.compile(r"#(.+)")

# scan, render and write landing page 
def build_it():
    # get 'Pathlib' paths and blog metadata from config file
    cfg = config.load_into_dict()
    site_dir = Path(cfg['publish_directory'])
    posts_dir = Path(cfg['publish_directory'] + '/posts/')
    atoms_dir = Path('atoms/')
    site_title = Path(cfg['feed_title'])
    site_author = Path(cfg['author'])

    # load jinja template location/environment
    file_loader = FileSystemLoader('./templates/')
    env = Environment(loader=file_loader)
    post_template = env.get_template('post-a.html')
    blog_template = env.get_template('blog-a.html')
    archive_template = env.get_template('archive-a.html')

    atoms = list(atoms_dir.glob('*.xml')) # to be scanned and rendered
    posts = list() # to be sorted and rendered on blog template
    archive = list() # to be sorted and rendered on archive template
    files = list() # to be returned - list of generated html files

    # read atoms and render individual entries, add to lists
    for atom in atoms:
        tree = ET.parse(atom)
        root = tree.getroot()
        entry = root.find('{*}entry')
        content = entry.find('{*}content').text
        content = content.replace('\**', '<').replace('**/', '>')
        title = TITLE_RE.findall(content)[0].strip()
        content = TITLE_RE.sub('', content, 1)
        post = dict()
        post['published'] = dtlocal(entry.find('{*}published').text)
        post['updated'] = post['published']
        original = True
        upd = entry.find('{*}updated')
        if upd is not None:
            upd = upd.text
            if upd != post['published']:
                original = False
                post['updated'] = dtlocal(upd)
        post['original'] = original
        post['title'] = title
        post['body'] = cmarkgfm.markdown_to_html(
            content,
            options = cmarkgfm_options.CMARK_OPT_UNSAFE,
        )
        post['link'] = 'posts/' + atom.stem + '.html'
        posts.append(post)
        archive.append( { 'title' : post['title'], 'link' : post['link'], 'published': post['published'], 'updated' : post['updated'], 'original' : post['original']} )

        # write post html files, add to files list
        html_name = atom.stem + '.html'
        nav_dict = { 'home' : '../index.html', 'archive' : '../archive.html' }
        try:
            with open(posts_dir / html_name, "w") as outfile:
                outfile.write(
                    post_template.render(
                        stylesheet='../style.css',
                        nav=nav_dict,
                        title=post['title'],
                        updated=post['updated'],
                        published=post['published'],
                        original=post['original'],
                        content=post['body']
                    )
                )
            files.append(str(posts_dir / html_name))
        except:
            print("\n No 'posts/' directory found in 'publish_directory' ")
            break

    # sort and render blog and archive templates
    sorted_posts = sorted(posts, key=lambda post: post['updated'], reverse=True)
    sorted_archive = sorted(archive, key=lambda item: item['updated'], reverse=True)
    sidebar_len = len(archive) if len(archive) < 5 else 5
    nav_dict = { 'home' : 'index.html', 'archive' : 'archive.html' }
    rendered_blog = blog_template.render(
        stylesheet='./style.css', 
        title=site_title, 
        author=site_author,
        nav=nav_dict, posts=sorted_posts,
        sidebar=sorted_archive[0:sidebar_len])
    rendered_archive = archive_template.render(
        stylesheet='./style.css', 
        title=site_title,
        author=site_author,
        nav=nav_dict, archive=sorted_archive)

    # write blog and archive html files, add to files list
    try:
        index = site_dir / "index.html"
        with open(index, 'w') as f:
            f.write(rendered_blog)
        archive = site_dir / "archive.html"
        with open(archive, 'w') as f:
            f.write(rendered_archive)
        files.append(str(index))
        files.append(str(archive))
    except:
        print("\n Run init.py before committing to generate site \n")

    return files
