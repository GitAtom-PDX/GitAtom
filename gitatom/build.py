# build.py: Using the 'pubish_directory' config option ...
#           Creates publish_directory/index.html and publish_directory/style.css
#           Appends a blog post link to index
# output:   publish_directory/index.html
#           publish_directory/style.css

import config
from bs4 import BeautifulSoup

def create(publish_directory):

    print(f"creating {publish_directory}/index.html and {publish_directory}/style.css")

    html = BeautifulSoup(f"""<html lang="en"><head><link rel=stylesheet type=text/css href="{publish_directory}/style.css">
	<title>Blog Post List</title></head><body><div id=main></div></body></html>""", features='html.parser')
    css = "* { box-sizing: 'content-box'; }"

    with open(publish_directory + '/index.html', "w") as index:
        index.write(html.prettify())
    with open(publish_directory + '/style.css', "w") as style:
        style.write(css)


def append(filename):
    print(f"inserting {filename}")

    # get target directory from config file 
    publish_directory = config.options['publish_directory']

    # parse publish_directory/index.html
    index_file = publish_directory + '/index.html'
    with open(index_file, 'r') as f:
        index = BeautifulSoup(f, 'html.parser')

    # parse filename (html post) DOM for title and link
    with open(f'{publish_directory}/posts/' + filename, 'r') as f:
        post = BeautifulSoup(f, 'html.parser')
    post_link = 'posts/' + ''.join(filename.split('/')[-1:])
    post_title = ''.join(filename.split('.')[-2:-1])
    site_title = post.title.string

    # insert blog details 
    new_link = index.new_tag('a', href=post_link)
    new_link.string = post_title
    new_div = index.new_tag('div')
    new_div['class'] = 'entry'
    new_div.insert(0, new_link)

    index.html.body.insert(0, new_div)
    with open(index_file, 'w') as f:
        f.write(index.prettify())

    return index_file
