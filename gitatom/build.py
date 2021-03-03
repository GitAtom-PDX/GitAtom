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

# create files with blank pages
def create(publish_directory):
    site_dir = Path(publish_directory)

    index = site_dir / "index.html"
    with open(index, 'w') as f:
        f.write("")
    archive = site_dir / "archive.html"
    with open(archive, 'w') as f:
        f.write("")

    # copy the stylesheet we create into the site directory
    style_src = Path("gitatom/main_templates/style.css")
    style_dst = site_dir / "style.css"
    copyfile(style_src, style_dst)

# scan, render and write landing page 
def build_it():
    # create 'Pathlib' paths from publish_directory config option
    cfg = config.load_into_dict()
    site_dir = Path(cfg['publish_directory'])
    posts_dir = Path(cfg['publish_directory'] + '/posts/')
    atoms_dir = Path('atoms/')

    site_title = Path(cfg['feed_title'])
    site_author = Path(cfg['author'])

    atoms = list(atoms_dir.glob('*.xml'))
    files = list()
    try : 
        # to render post template in loop below
        file_loader = FileSystemLoader('gitatom/main_templates/')
        env = Environment(loader=file_loader)
        post_template = env.get_template('post-a.html')

        # create a list of maps of posts
        posts = list()
        archive = list()
        for atom in atoms:
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

            # write post html files
            html_name = atom.stem + '.html'
            nav_dict = { 'home' : '../index.html', 'archive' : '../archive.html' }
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

        sorted_posts = sorted(posts, key=lambda post: post['updated'], reverse=True)
        sorted_archive = sorted(archive, key=lambda item: item['updated'], reverse=True)
        sidebar_len = len(archive) if len(archive) < 5 else 5

        # render blog and archive templates
        nav_dict = { 'home' : 'index.html', 'archive' : 'archive.html' }
        file_loader = FileSystemLoader('gitatom/main_templates/')
        env = Environment(loader=file_loader)
        blog_template = env.get_template('blog-a.html')
        rendered_blog = blog_template.render(
            stylesheet='./style.css', 
            title=site_title, 
            author=site_author,
            nav=nav_dict, posts=sorted_posts,
            sidebar=sorted_archive[0:sidebar_len])
        archive_template = env.get_template('archive-a.html')
        rendered_archive = archive_template.render(
            stylesheet='./style.css', 
            title=site_title,
            author=site_author,
            nav=nav_dict, archive=sorted_archive)

        # write the html
        index = site_dir / "index.html"
        with open(index, 'w') as f:
            f.write(rendered_blog)
        archive = site_dir / "archive.html"
        with open(archive, 'w') as f:
            f.write(rendered_archive)

        files.append(str(index))
        files.append(str(archive))

        return files

    except:
        print("\n Run init.py before committing to generate site \n")
        return files