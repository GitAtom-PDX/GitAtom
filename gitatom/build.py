# build.py: Using the 'target' config option ...
#           Creates 'target/index.html' and 'target/style.css'
#           Adds a blog post link to the index
# output:   target/index.html
#           target/blog.html

from bs4 import BeautifulSoup

def create(target):
    print(f"creating {target}/index.html and {target}/style.css")

    html = BeautifulSoup(f"""<html lang="en"><head><link rel=stylesheet type=text/css href="{target}/style.css">
	<title>Blog Post List</title></head><body><div id=main></div></body></html>""", features='html.parser')

    css = "* { box-sizing: 'content-box'; }"

    with open(target + '/index.html', "w") as index:
        index.write(html.prettify())
    with open(target + '/style.css', "w") as style:
        style.write(css)


def append(filename):
    print(f"inserting {filename}")

    # get target directory from config file 
    with open('gitatom.config', "r") as config_f:
        config = config_f.readlines()
        target = config[0].strip()

    # parse filename (html post) DOM for title and link
    with open(filename, 'r') as f:
        post = BeautifulSoup(f, 'html.parser')
    post_title = post.head.title.string
    post_link = '/posts/' + filename

    # parse target/site/index.html
    index_file = target + '/site/index.html'
    with open(index_file, 'r') as f:
        index = BeautifulSoup(f, 'html.parser')

    # insert blog details 
    new_link = index.new_tag('a', href=post_link)
    new_link.string = post_title
    new_div = index.new_tag('div')
    new_div['class'] = 'entry'
    new_div.insert(0, new_link)

    index.html.body.insert(0, new_div)
    with open(index_file, 'w') as f:
        f.write(index.prettify())
