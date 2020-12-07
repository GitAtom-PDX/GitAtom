# given: 'gitatom/templates/default.html', 
#        'gitatom/templates/blogs.html',
#        'site/assets/css/style.css',
#        'site/*.html'
#
# build.py: scans source ('site/') and its subdirs, 
#           renders default and/or blogs template
#
# output:   site/index.html
#           site/blog.html
#
# run:      python3 build.py

from jinja2 import Environment, FileSystemLoader
import os, stat, time

class Builder(object):
    def __init__(self, basepath):
        self.basepath = basepath

    # scan for blog html files 
    def scan_blog(self):
        blogs = list() # blog posts
        nav = list()   # for navbar atop page
        for dirpath, dirname, files in os.walk(self.basepath):
            for f in files:
                if f.endswith('.html'):

                    html = dict()
                    url = os.path.join(dirpath, f)
                    html['url'] = url.replace(self.basepath, '')
                    html['filename'] = os.path.splitext(f)[0]

                    # one of assumed pages that will always exist
                    if f in {'index.html', 'about.html', 'blog.html'}:
                        nav.append(html)
                    
                    else: # a page parsed from Atom
                        file_stats = os.stat(url)
                        modified_time = time.ctime(file_stats[ stat.ST_MTIME ])
                        html['modified'] = modified_time
                        # assume dir path is year-month-day-etc
                        html['dated'] = os.path.join(dirpath).replace(self.basepath, '').replace('/', '-')
                        blogs.append(html)

        # sort on dated (newest first)
        sorted_blogs = sorted(blogs, key=lambda blog: blog['dated'], reverse=True)
        return sorted_blogs, nav


    # scan for other html files 
    def scan_index(self):
        nav = list()   # for navbar atop page
        for dirpath, dirname, files in os.walk(self.basepath):
            for f in files:
                # one of assumed pages that will always exist
                if f in {'index.html', 'about.html', 'blog.html'}:

                    html = dict()
                    url = os.path.join(dirpath, f)
                    html['url'] = url.replace(self.basepath, '')
                    html['filename'] = os.path.splitext(f)[0]
                    nav.append(html)

        return nav


    # render blogs template, return html
    def blog(self, blogs, nav):

        file_loader = FileSystemLoader('./gitatom/templates')
        env = Environment(loader=file_loader)
        template = env.get_template('blogs.html')
        # fill blogs template and inherited default template
        output = template.render(nav=nav, blogs=blogs)

        return output


    # render default template, return html
    def index(self, nav):

        file_loader = FileSystemLoader('./gitatom/templates')
        env = Environment(loader=file_loader)
        template = env.get_template('default.html')
        # fill default template
        output = template.render(nav=nav)

        return output


    # write html
    def create(self, filename, html):
        with open(self.basepath + filename + '.html', "w") as page:
            page.write(html)
        print(f"\n{self.basepath + filename} was just rendered.\n")
    

    # scan, render and write published posts
    def build_blog(self):
        posts, nav = self.scan_blog()
        rendered_blog = self.blog(posts, nav)
        self.create('blog', rendered_blog)


    # scan, render and write home page
    def build_index(self):
        nav = self.scan_index()
        rendered_index = self.index(nav)
        self.create('index', rendered_index)


if __name__ == '__main__':
    # scan 'site/' for html files 
    site = build.Builder('site/')
    site.build_blog()
    site.build_index()
