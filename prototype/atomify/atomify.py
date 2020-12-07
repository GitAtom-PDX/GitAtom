# atomify.py
# Encloses given html in atom xml tags

# Required <entry> atom tags: 
# <id> unique entry id, generated and contatenated with feed id
# <title> title of post, populated from markdown filename
# <updated> latest update, NOTE see README
# <published> creation date, current time (requested by sponsor, not required by atom)

# Required <feed> atom tags: 
# <id> site URI, populated from config file 
# <title> title of website, populated from config file
# <updated> latest feed update, populated from entry tag

import sys 
from os import path
from datetime import datetime 

# Open required files
if not len(sys.argv) == 2: exit("Usage: python3 atomify.py input.html")
if not sys.argv[1].endswith('.html'): exit("Incorrect input file type (expected .html)")
html = sys.argv[1]

# NOTE may not need this if using a separate file for feed tags...
config_f = open('gitatom.config')
config = config_f.readlines()
config_f.close()

# Populate required tags 
feed_id = config[0].strip()
feed_title = config[1].strip()

entry_title = path.splitext(path.basename(html))[0]
entry_id = feed_id + entry_title # depends on feed id

entry_published = datetime.now() # using current time
entry_updated = entry_published
feed_updated = entry_updated # depends on entry updated

# Create atom string
atom = '<feed>\n'
atom += '<title>' + feed_title + '</title>\n'
atom += '<updated>' + str(feed_updated) + '</updated>\n'
atom += '<id>' + feed_id + '</id>\n'
atom += '<entry>\n'
atom += '<title>' + entry_title + '</title>\n'
atom += '<id>' + entry_id + '</id>\n'
atom += '<published>' + str(entry_published) + '</published>\n'
atom += '<updated>' + str(entry_updated) + '</updated>\n'
atom += '<content>' 
with open (html,'r') as f: 
	atom += f.read()
atom += '</content>'
atom += '</entry>\n'
atom += '</feed>\n'

# Write result to file
outname = entry_title + '.xml' # NOTE need a good naming schema...
outfile = open(outname, 'w')
outfile.write(atom)
outfile.close()

