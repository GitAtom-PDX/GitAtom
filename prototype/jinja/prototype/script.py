from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom

#get data from xml
mydoc = minidom.parse('test.xml')
home = mydoc.getElementsByTagName('home')[0]
skills = mydoc.getElementsByTagName('skills')
#print(home.firstChild.data)
s = skills[1].getAttribute("name")
print(s)


# load layout html file
template_env = Environment(loader=FileSystemLoader(searchpath='./'))
template = template_env.get_template('layout.html')

with open('sample.html', 'w') as outfile:
    outfile.write(
        template.render(
            title=s,
            date='11/27/2020',
            blog='this is a test blog post.'
        )
    )
