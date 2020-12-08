# given: 'templates/default.html', 
#        'templates/blogs.html',
#        'site/assets/css/style.css',
#        'site/*.html'
#        'site/posts/*.html'
#
# build.py: scans ('site/') and its subdirs, 
#           renders default and/or blogs template
#
# output:   site/index.html
#           site/blog.html
#
# run:      python3 build.py

from jinja2 import Environment, FileSystemLoader
import os, stat, time

# scan for blog html files 
def scan_blog(basepath):
    blogs = list() # blog posts
    for dirpath, dirname, files in os.walk(basepath):
        for f in files:
            if f.endswith('.html'):
                html = dict()
                url = os.path.join(dirpath, f).split('/')[1:]
                urlString = '/'.join(url)
                html['url'] = urlString
                html['filename'] = os.path.splitext(f)[0]
                file_stats = os.stat(os.path.join(dirpath, f))
                modified_time = time.ctime(file_stats[ stat.ST_MTIME ])
                html['modified'] = modified_time
                # assume dir path is year-month-day-etc
                html['dated'] = os.path.join(dirpath).replace(basepath, '').replace('/', '-')
                blogs.append(html)
    # sort on dated (newest first)
    sorted_blogs = sorted(blogs, key=lambda blog: blog['dated'], reverse=True)
    return sorted_blogs

# scan for html files 
def scan_index(basepath):
    nav = list()   # for navbar atop page
    for f in os.listdir(basepath):
        if f.endswith('.html'):
            html = dict()
            url = os.path.join(basepath, f)
            html['url'] = url.replace(basepath, '')
            html['filename'] = os.path.splitext(f)[0]
            nav.append(html)
    return nav

# render blogs template, return html
def blog(nav, blogs):
    file_loader = FileSystemLoader('./templates')
    env = Environment(loader=file_loader)
    template = env.get_template('blogs.html')
    # fill blogs template and inherited default template
    output = template.render(nav=nav, blogs=blogs)
    return output

# render default template, return html
def index(nav):
    file_loader = FileSystemLoader('./templates')
    env = Environment(loader=file_loader)
    template = env.get_template('default.html')
    output = template.render(nav=nav)
    return output

# write html files
def create(basepath, filename, html):
    with open(basepath + filename + '.html', "w") as page:
        page.write(html)
    print(f"\n{basepath + filename} was just rendered.\n")

# scan, render and write landing page and published posts 
def build_it(basepath):
    posts = scan_blog(basepath + 'posts/')
    nav = scan_index(basepath)
    rendered_blog = blog(nav, posts)
    rendered_index = index(nav)
    create(basepath, 'blog', rendered_blog)
    create(basepath, 'index', rendered_index)

build_it('site/')
