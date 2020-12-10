from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom

# get data from xml
#mydoc = minidom.parse('../../atomify/input.xml')
mydoc = minidom.parse('input.xml')
f_title = mydoc.getElementsByTagName('title')[0]
f_updated = mydoc.getElementsByTagName('updated')[0]
f_id = mydoc.getElementsByTagName('id')[0]
entry = mydoc.getElementsByTagName('entry')
content = mydoc.getElementsByTagName('content')

list = []

for i in entry:
    title = i.getElementsByTagName("title")[0]
    id = i.getElementsByTagName("id")[0]
    published = i.getElementsByTagName("published")[0]
    updated = i.getElementsByTagName("updated")[0]

    # save data into list
    list.append(title.firstChild.data)
    list.append(id.firstChild.data)
    list.append(published.firstChild.data)
    list.append(updated.firstChild.data)

# getting data from content
for i in content:
    blog = i.getElementsByTagName("p")[0]
    list.append(blog.firstChild.data)


# load template html file
template_env = Environment(loader=FileSystemLoader(searchpath='../templates'))
template = template_env.get_template('jinja_template.html')

with open('sample.html', 'w') as outfile:
    outfile.write(
        template.render(
            title=list[0],
            date=list[2],
            blog=list[4]
        )
    )
