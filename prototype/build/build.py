#!/usr/bin/python3
# given: 'gitatom/templates/default.html', 
#        'gitatom/templates/list_posts.html',
#        'site/assets/css/style.css',
#        'site/about.html', and 'site/blog.html'
#
# build.py: scans 'site/' and its subdirs, 
#           renders list_posts template (which inherits from default.html)
#
# output:   'index.html' in working directory
# run:      ./build.py (in 'site/')

from jinja2 import Environment, FileSystemLoader
import os, stat, time


# scan 'site/' for html files 
def scan():

    posts = list()
    nav = list()
    basepath = 'site/'

    for dirpath, dirname, files in os.walk(basepath):
        for f in files:
            if f.endswith('.html'):

                html = dict()
                url = os.path.join(dirpath, f)
                html['filename'] = f
                html['url'] = url.replace(basepath, '')

                if f not in {'index.html', 'about.html', 'blog.html'}:
                    file_stats = os.stat(url)
                    modified_time = time.ctime(file_stats[ stat.ST_MTIME ])
                    html['modified'] = modified_time
                    posts.append(html)
                else:
                    nav.append(html)

    sorted_posts = sorted(posts, key=lambda post: post['modified'])
    return sorted_posts, nav


# fill list_posts template, return rendered html
def index(posts, nav):

    file_loader = FileSystemLoader('./gitatom/templates')
    env = Environment(loader=file_loader)

    template = env.get_template('list_posts.html')
    output = template.render(nav=nav, posts=posts)

    return output


# write out to site/index.html
def render(html):
        with open("site/index.html", "w") as index:
            index.write(html)
        print("\nsite/index.html was just rendered.\n")


posts, nav = scan()
generated = index(posts, nav)
render(generated)
