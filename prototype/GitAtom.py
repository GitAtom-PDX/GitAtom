import sys
import os
import argparse
import datetime
from git import Repo
import cmarkgfm  # used to convert markdown to html in mdtohtml()
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from xml.dom import minidom


"""An atom object contains files and functions used for the GitAtom process

Data memebers in the class help track meta data for each atom feed. 
The files data member is a list and starts with templates for the GitAtom process in each index. 
As each file is parsed replace template with updated file. 
"""


class Atom:
    def __init__(self):
        # Each index is a file along the process. 0: MD 1: CMark HTML 2: Atom XML 3: Jinja HTML]
        self.files = [None] * 4
        self.author = ''
        self.date = datetime.datetime.now()
   
    #Place new md to atom code here ####################


    ####################################################

    def md_to_atom(self, md_filename):

        #use if we want to change to reading in from command arg
        """   
        # Open required files - this is currently designed such 
        # that atomify [file] processes one md file at a time
        if not len(sys.argv) == 2: exit("Usage: python3 atomify.py input.md")
        if not sys.argv[1].endswith('.md'): exit("Incorrect input file type (expected .md)")
        md = sys.argv[1]
        """

        md = md_filename


        # NOTE may not need this if using a separate file for feed tags...
        config_f = open('../gitatom.config')
        config = config_f.readlines()
        config_f.close()

        # Populate required tags 
        feed_id = config[0].strip()
        feed_title = config[1].strip()

        entry_title = os.path.splitext(os.path.basename(md))[0] # TODO make os-agnostic 
        entry_id = feed_id + entry_title # depends on feed id

        # TODO how to check if the given markdown file is a new or existing post...
        # how best to handle updating an existing post? 

        entry_published = datetime.datetime.now()		# using current time
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

        # NOTE https://stackoverflow.com/questions/3411771/best-way-to-replace-multiple-characters-in-a-string
        with open (md,'r') as f: 
            atom += f.read().replace('<', '\<').replace('>', '\>')
            
        atom += '</content>\n'
        atom += '</entry>\n'
        atom += '</feed>\n'

        # Write result to file
        outname = entry_title + '.xml' # TODO need a good naming schema...
        outfile = open(outname, 'w')
        outfile.write(atom)
        outfile.close()
        return outname

    # funtion to convert markdown text into html
    # called by md_to_html(md_text,'filename.xml')
    # either returns a html filename on success or None on failure
    def md_to_html(self, md_text, xml_filename):

        l = len(xml_filename)
        
        # make sure file is a .xml file
        if xml_filename[l - 4:l] == '.xml':
            html_name = xml_filename[:l - 4]
            html_text = cmarkgfm.markdown_to_html(md_text)
            # TODO need to change naming convention of new html files
            html_file = open('{0}.html'.format(html_name), "w")
            html_file.write(html_text)
            html_file.close()
            return html_file.name  # success
        return None  # failure 

    # Jinja - html generator
    #TODO need to add error checking and clean up this function 
    def render_html(self, xml_filename):
        # get data from xml
        #mydoc = minidom.parse('../../atomify/input.xml')
        mydoc = minidom.parse(xml_filename)
        f_title = mydoc.getElementsByTagName('title')[0]
        f_updated = mydoc.getElementsByTagName('updated')[0]
        f_id = mydoc.getElementsByTagName('id')[0]
        entry = mydoc.getElementsByTagName('entry')
        content = mydoc.getElementsByTagName('content')

        html_name = self.md_to_html(content[0].firstChild.nodeValue,xml_filename)
        self.files[2] = html_name

        list1 = []
        
        for i in entry:
            title = i.getElementsByTagName("title")[0]
            id = i.getElementsByTagName("id")[0]
            published = i.getElementsByTagName("published")[0]
            updated = i.getElementsByTagName("updated")[0]

            # save data into list
            list1.append(title.firstChild.data)
            list1.append(id.firstChild.data)
            list1.append(published.firstChild.data)
            list1.append(updated.firstChild.data)

        #TODO this loop breaks the function, need to check indexing or find another way to do this
        """
        # getting data from content
        for i in content:
            blog = i.getElementsByTagName("p")[0]
            list1.append(blog.childNodes)
        """

        # load template html file
        template_env = Environment(
            loader=FileSystemLoader(searchpath='./jinja/templates'))
        template = template_env.get_template('jinja_template.html')

        
        # Open and read the html file for it's content
        html_file = open(html_name, "r")
        html_text = html_file.read()
        html_file.close()
        
        with open('sample.html', 'w') as outfile:
            outfile.write(
                template.render(
                    title=list1[0],
                    date=list1[2],
                    blog=html_text
                )
            )
        
    # input: string representation of path to source file.
    # returns: ERROR if the source file does not exist.
    # This function copies the source file to TARGET_DIRECTORY.
    # Automatically builds the target directory and sub directories
    # for the posts depending on the hyphens at the beginning of
    # the file. Example: aaa-bbb-ccc-file.html is copied to
    # ./site/posts/aaa/bbb/ccc/file.html

    #TODO work on file saving directory structure
    def save_atom(self, path_to_src):

        TARGET_DIRECTORY = "../site/posts/"
        ERROR = -1

        src_path = Path(path_to_src)
        if not src_path.exists():
            return ERROR

        # extract the filename from full path, split filname into pieces
        # based on '-'
        # ex: 2020-12-1-post.html is split into:
        # ['2020', '12', '1', 'post.html']
        src_filename = src_path.name
        name_tokens = src_filename.split("-")

        # build the destination directory based on previous pieces
        dest_path = Path(TARGET_DIRECTORY)
        for i in range(len(name_tokens) - 1):
            dest_path = dest_path / name_tokens[i]

        if not dest_path.exists():
            dest_path.mkdir(parents=True)

        # append filename w/out date info to destination path
        dest_path = dest_path / name_tokens[-1]

        shutil.copy(src_path, dest_path)
        #TODO need to return some metric of success here, maybe just 1
        return True

    def test(self):
        print(self.date)


def main(markdown_file):

    markdown_file = 'BlogPostTest.md'

    # html = '/atomify/lorem.html'

    atom = Atom()
    print("Starting GitAtom on file: " + markdown_file)
    print(atom.date)

    # atom.test()

    atom.files[0] = markdown_file
    print(atom.files[0])
    atom.files[1] = atom.md_to_atom(atom.files[0])   #  ------------new md to atom call goes here with same arg---------------
    print(atom.files[1])
    #atom.files[2] = atom.html_to_atomify(atom.files[1])
    #print(atom.files[2])
    atom.render_html(atom.files[1])

    #files[2] is assigned in th render_html() call after parsing the content out of the xml file
    if not atom.save_atom(atom.files[2]):
        sys.exit('Fail')

    # repo = Repo('/Users/Uwriyel/PycharmProjects/GitAtom')
    # repo = Repo('..')
    # for remote in repo.remotes:
    #     print(f'- {remote.name} {remote.url}')



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='markdown_file',
                        help='Options: valid file name')

    args = parser.parse_args()

    try:
        main(args.markdown_file)        #can be used later to feed md files through command line

    except KeyboardInterrupt:
        print('***** Finished GitAtom *****')
        pass
