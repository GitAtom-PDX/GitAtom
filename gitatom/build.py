# given: 'main_templates/base.html', 
#        'main_templates/default.html',
#        'publish_directory/*.html'
#        'publish_directory/posts/*.html'
#
# build.py: scans publish_directory and publish_directory/posts/
#           renders the base and default templates
#
# output:   publish_directory/index.html

import config
from pathlib import Path
import cmarkgfm
from xml.etree import cElementTree as ET
from jinja2 import Environment, FileSystemLoader

# create files with blank pages
def create(publish_directory):
    site_dir = Path(publish_directory)

    index = site_dir / "index.html"
    with open(index, 'w') as f:
        f.write("")
    archive = site_dir / "archive.html"
    with open(archive, 'w') as f:
        f.write("")

# scan, render and write landing page 
def build_it():
    # create 'Pathlib' paths from publish_directory config option
    site_dir = Path(config.options['publish_directory'])
    posts_dir = Path(config.options['publish_directory'] + '/posts/')
    atoms_dir = Path('atoms/')

    # scan for atoms and pages
    nav_pages = list(site_dir.glob('*.html'))
    nav_dict = {nav.stem : nav.name for nav in nav_pages}
    nav_dict['home'] = nav_dict.pop('index')
    atoms = list(atoms_dir.glob('*.xml'))

    # create a list of maps of posts
    posts = list()
    archive = list()
    for atom in atoms:
        tree = ET.parse(atom)
        root = tree.getroot()
        post = dict()
        post['title'] = root.find('entry').find('title').text
        post['updated'] = root.find('entry').find('updated').text
        content = root.find('entry').find('content').text
        post['body'] = cmarkgfm.markdown_to_html(content)
        post['link'] = 'posts/' + atom.stem[8:] + '.html'
        posts.append(post)
        archive.append( { 'title' : post['title'], 'link' : post['link'], 'updated' : post['updated'] } )

    # render blog template with found entries and other pages
    file_loader = FileSystemLoader('gitatom/main_templates/')
    env = Environment(loader=file_loader)
    template = env.get_template('blog-a.html')
    rendered_blog = template.render(nav=nav_dict, posts=posts, sidebar=archive)
    index = site_dir / "index.html"

    # render archive template with found entries and other pages
    file_loader = FileSystemLoader('gitatom/main_templates/')
    env = Environment(loader=file_loader)
    template = env.get_template('archive-a.html')
    rendered_archive = template.render(nav=nav_dict, archive=archive)
    archive = site_dir / "archive.html"

    # write the html
    with open(index, 'w') as f:
        f.write(rendered_blog)
    with open(archive, 'w') as f:
        f.write(rendered_archive)

    return index
