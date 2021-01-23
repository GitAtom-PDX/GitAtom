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
	<title>Blog Post List</title></head><body><header><h1></h1><h2></h2></header><div id=\"archive\"></div></body></html>""", features='html.parser')
    css = "* { box-sizing: 'content-box'; }"

    with open(publish_directory + '/index.html', "w") as index:
        index.write(html.prettify())
    with open(publish_directory + '/style.css', "w") as style:
        style.write(css)


def append(filename):
    print(f"inserting {filename}")

    filename_only = ''.join(filename.split('/')[-1:])

    # get target directory from config file 
    publish_directory = config.options['publish_directory']
    author = config.options['author']
    feed_title = config.options['feed_title']

    # parse publish_directory/index.html
    index_file = publish_directory + '/index.html'
    with open(index_file, 'r') as f:
        index = BeautifulSoup(f, 'html.parser')

    # parse filename (html post) DOM for title and link
    with open(f'{publish_directory}/posts/' + filename_only, 'r') as f:
        post = BeautifulSoup(f, 'html.parser')
    # what it should be: post_title = post.html.head.title.string
    post_title = post.html.body.center.h1.string
    # what it should be: post_date = post.html.h2.string
    post_date = post.html.body.center.next_sibling.next_sibling.h3.string
    post_link = 'posts/' + filename_only

    # insert blog details 
    new_link = index.new_tag('a', href=post_link)
    new_link.string = post_title

    new_p = index.new_tag('p')
    new_p.insert(0, new_link)

    new_p2 = index.new_tag('p')
    new_p2.string = post_date

    new_div = index.new_tag('div')
    new_div.insert(0, new_p)
    new_div.insert(1, new_p2)
    new_div['class'] = 'entry'

    index.find('div', id='archive').insert(0, new_div)

    index.html.head.title.string = feed_title
    index.html.body.header.h1.string = feed_title
    index.html.body.header.h2.string = author

    with open(index_file, 'w') as f:
        f.write(index.prettify())

    return index_file
