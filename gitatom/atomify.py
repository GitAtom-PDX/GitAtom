# atomify.py
# Encloses given md in atom xml tags

# NOTE file handling is not currently OS-agnostic

# Required <entry> atom tags: 
# <id> unique entry id, generated and contatenated with feed id
# <title> title of post, populated from markdown filename
# <updated> latest update, NOTE see README
# <published> creation date, current time (requested by sponsor, not required by atom)
# <content> markdown file contents with escaped characters

# Required <feed> atom tags: 
# <id> site URI, populated from config file 
# <title> title of website, populated from config file
# <updated> latest feed update, populated from entry tag

import sys 
from os import path
from datetime import datetime 
import re


# Generate blog post title from .md filename
def getTitle(filename):

	# Determine filename style
	if '-' in filename: 
		words = filename.replace('-',' ').split(' ')

	elif '_' in filename:
		words = filename.replace('_',' ').split(' ')

	elif ' ' in filename:
		words = filename.split(' ')	

	# Check for single-word titles
	# https://www.geeksforgeeks.org/python-test-if-string-contains-any-uppercase-character/
	elif not bool(re.match(r'\w*[A-Z]\w*', filename)):
		return filename.capitalize()

	else: # assume camelCase
		words = camelCaseSplit(filename)

	words = [word.capitalize() for word in words]
	title = ' '.join(words)
	return title



# Generate blog post filename from title and date
def getFilename(title):
	
	# Generate date in YYYYMMDD	
	filename = datetime.today().strftime('%Y%m%d')
	
	# Append title to date 
	if ' ' not in title: # check for single-word title
		filename += title
	else: 
		words = title.split(' ')
		for word in words: filename += word

	return filename
	


# camelCase splitter 
# https://www.geeksforgeeks.org/python-split-camelcase-string-to-individual-strings/
def camelCaseSplit(str):
	return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)



# Open required files - this is currently designed such 
# that atomify [file] processes one md file at a time
if not len(sys.argv) == 2: exit("Usage: python3 atomify.py input.md")
if not sys.argv[1].endswith('.md'): exit("Incorrect input file type (expected .md)")
md = sys.argv[1]

# NOTE may not need this if using a separate file for feed tags...
config_f = open('gitatom.config')
config = config_f.readlines()
config_f.close()

# Populate required tags 
feed_id = config[0].strip()
feed_title = config[1].strip()

filename = path.splitext(path.basename(md))[0] # TODO make os-agnostic 
entry_title = getTitle(filename)
outname = getFilename(entry_title)
entry_id = feed_id + outname # depends on feed id


# TODO how to check if the given markdown file is a new or existing post...
# how best to handle updating an existing post? 

entry_published = datetime.now()		# using current time
entry_published.replace(microsecond=0) 	# truncate ms
entry_updated = entry_published			# TODO how to handle updating entries...?
feed_updated = entry_updated 		# depends on entry updated

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

# https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
with open (md,'r') as f: 
	atom += f.read().replace('<', '\<').replace('>', '\>')
	
atom += '</content>\n'
atom += '</entry>\n'
atom += '</feed>\n'

# Write result to file
outname += '.xml' 
outfile = open(outname, 'w')
outfile.write(atom)
outfile.close()
