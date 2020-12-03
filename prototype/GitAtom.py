import sys, os
import argparse
import datetime
from git import Repo

"""An atom object contains files and functions used for the GitAtom process

Data memebers in the class help track meta data for each atom feed. 
The files data member is a list and starts with templates for the GitAtom process in each index. 
As each file is parsed replace template with updated file. 
"""

class Atom:
    files = [] # Each index is a file along the process. 1: MD 2: CMark HTML 3: Atom XML 4: Jinja HTML]
    author = ''
    date = datetime.datetime.now()

def main(markdown_file):

    atom = Atom

    print("Starting GitAtom on file: " + markdown_file)
    print(atom.date)



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store', dest='markdown_file',
                        help='Options: valid file name')

    args = parser.parse_args()

    try:
        main(args.markdown_file)

    except KeyboardInterrupt:
        print('***** Finished GitAtom *****')
        pass
