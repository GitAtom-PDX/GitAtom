# given: 'main_templates/nav.html', 
#        'main_templates/blog.html',
#        'main_templates/archive.html',
#        'publish_directory/*.html'
#        'publish_directory/posts/*.html'
#
# build.py: scans publish_directory, atoms/ and publish_directory/posts/
#           renders the nav, blog and archive templates
#
# output:   publish_directory/index.html
from gitatom import config
from pathlib import Path
import cmarkgfm
from shutil import copyfile
import re
from xml.etree import cElementTree as ET
from jinja2 import Environment, FileSystemLoader
import json

# create files with blank pages
def create(publish_directory):
    site_dir = Path(publish_directory)

    with open(site_dir / "index.html", 'w') as f:
        f.write("")
    with open(site_dir / "archive.html", 'w') as f:
        f.write("")
    with open(site_dir / "pageIndex.json", 'w') as f:
        f.write("")
    with open(site_dir / "wordIndex.json", 'w') as f:
        f.write("")

    # copy the stylesheet and search script into the site directory
    copyfile(Path("gitatom/main_templates/style.css"), site_dir / "style.css")
    copyfile(Path("gitatom/main_templates/search.js"), site_dir / "search.js")

# scan, render and write landing page 
def build_it():
    cfg = config.load_into_dict()
    site_dir = Path(cfg['publish_directory'])
    atoms_dir = Path('atoms/')
    site_title = Path(cfg['feed_title'])
    site_author = Path(cfg['author'])

    # scan for atoms and pages
    nav_pages = list(site_dir.glob('*.html'))
    nav_dict = {nav.stem : nav.name for nav in nav_pages}
    nav_dict['home'] = nav_dict.pop('index')
    atoms = list(atoms_dir.glob('*.xml'))

    # create a list of maps of posts
    posts = list()
    archive = list()
    pageIndex = dict()
    wordIndex = dict()
    # create a dictionary for searchable content
    def addWordIndex(title, body, url, wordIndex, pageIndex, pageNum):
        pageIndex[pageNum] = url
        title = title.lower().split(' ')
        body = content.replace('\n', ' ').lower().split(' ')
        words = set(title).union(set(body))
        for word in words:
            if word in wordIndex:
                wordIndex[word] += [pageNum]
            else: wordIndex[word] = [pageNum]

    for i, atom in enumerate(atoms):
        tree = ET.parse(atom)
        root = tree.getroot()
        content = root.find('entry').find('content').text
        content = content.replace('\**', '<').replace('**/', '>')

        title = re.compile(r"#(.+)").findall(content)[0].strip()
        content = re.compile(r"#(.+)").sub('', content, 1)

        post = dict()
        post['updated'] = root.find('entry').find('updated').text
        post['published'] = root.find('entry').find('published').text
        post['original'] = True if post['updated'] == post['published'] else False
        post['title'] = title
        post['body'] = cmarkgfm.markdown_to_html(content)
        post['link'] = 'posts/' + atom.stem + '.html'
        posts.append(post)
        archive.append( { 'title' : post['title'], 'link' : post['link'], 'published': post['published'], 'updated' : post['updated'], 'original' : post['original']} )
        addWordIndex(post['title'], post['body'], post['link'], wordIndex, pageIndex, i)

    sorted_posts = sorted(posts, key=lambda post: post['updated'], reverse=True)
    sorted_archive = sorted(archive, key=lambda item: item['updated'], reverse=True)
    sidebar_len = len(archive) if len(archive) < 5 else 5

    # render blog and archive templates
    file_loader = FileSystemLoader('gitatom/main_templates/')
    env = Environment(loader=file_loader)
    temp1 = env.get_template('blog-a.html')
    rendered_blog = temp1.render(title=site_title, author=site_author, \
                                 nav=nav_dict, posts=sorted_posts, \
                                 sidebar=sorted_archive[0:sidebar_len])
    temp2 = env.get_template('archive-a.html')
    rendered_archive = temp2.render(title=site_title, author=site_author, \
                                    nav=nav_dict, archive=sorted_archive)

    # write the html and json
    with open(site_dir / "index.html", 'w') as f:
        f.write(rendered_blog)
    with open(site_dir / "archive.html", 'w') as f:
        f.write(rendered_archive)
    with open(site_dir / "pageIndex.json", "w") as f:
        json.dump(pageIndex, f, indent=4)
        # { 
        #   "0":"posts/lorem.html", 
        #   "1":"posts/ipsum.html" 
        # }
    with open(site_dir / "wordIndex.json", "w") as f:
        json.dump(wordIndex, f)
        # {  
        #   "wordA":[1,2,5,6], 
        #   "wordB":[3,6], 
        #   "wordC":[2,6,132] 
        # } 	
