# atomify.py

# NOTE file handling is not currently OS-agnostic
# NOTE current implementation does NOT allow duplicate titles

# Required <entry> atom tags: 
# <id> unique entry id, generated and contatenated with feed id
# <title> title of post, populated from markdown filename
# <updated> latest update
# <published> creation date, current time (requested by sponsor, not required by atom)
# <content> markdown file contents with escaped characters

# Required <feed> atom tags: 
# <id> site URI, populated from config file 
# <title> title of website, populated from config file
# <updated> latest feed update, populated from entry tag

from xml.etree import cElementTree as ET
from datetime import datetime 
from os import path
import glob
import sys 
import re
import string
import config

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



# Generate xml filename from title and date
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
	str = str[0].upper() + str[1:] # preserve lowercase first words
	return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)



# Takes a .md file and pastes its content into an atom xml format
def atomify(md):

	# Check for invalid filetype
	if not md.endswith('.md'): exit("Incorrect input file type (expected .md)")
	
	# Get title and xml filename	
	filename = path.splitext(path.basename(md))[0] # TODO make os-agnostic 
	entry_title = getTitle(filename)
	outname = getFilename(entry_title) + '.xml'

	# Check for a matching xml file 
	exists = glob.glob('./*' + outname[8:] + '*') # should only ever return 0-1 matches
	if exists: outname = exists[0][2:] # overwrite existing file 

	# Populate tags
        feed_id = config.options['feed_id']
        feed_title = config.options['feed_title']
	entry_id = feed_id + outname[:-4] 
	if exists: # retain existing publish date
		tree = ET.parse(outname) 
		root = tree.getroot()
		entry_published = root.find('entry').find('published').text
		entry_updated = datetime.now()
		entry_updated.replace(microsecond=0)
	else:
		entry_published = datetime.now()	# using current time
		entry_published.replace(microsecond=0) 	# truncate ms
		entry_updated = entry_published		
	feed_updated = entry_updated 		

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
		atom += f.read().replace('<', '\**').replace('>', '**/')
		
	atom += '</content>\n'
	atom += '</entry>\n'
	atom += '</feed>\n'
	
	# Write result to file
	#outname += '.xml' 
	outfile = open(outname, 'w')
	outfile.write(atom)
	outfile.close()
	


# Testing
atomify("../lorem.md")
#atomify("../loremIpsum.md")
