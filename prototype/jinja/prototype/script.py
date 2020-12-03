from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom

# get data from xml
mydoc = minidom.parse('input.xml')
f_title = mydoc.getElementsByTagName('title')[0]
f_updated = mydoc.getElementsByTagName('updated')[0]
f_id = mydoc.getElementsByTagName('id')[0]
entry = mydoc.getElementsByTagName('entry')
# print(home.firstChild.data)

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

print(list)

# load layout html file
template_env = Environment(loader=FileSystemLoader(searchpath='./'))
template = template_env.get_template('layout.html')

with open('sample.html', 'w') as outfile:
    outfile.write(
        template.render(
            title=list[0],
            date='11/27/2020',
            blog='this is a test blog post.'
        )
    )
