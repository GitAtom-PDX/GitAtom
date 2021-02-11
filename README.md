# GitAtom
 GitAtom blogging software development repository for CS Capstone

### Install Dependencies
`pip install -r requirements.txt`

### Usage:
`git [command] [-flag] (target)`
commands: [add, commit, push]

-Add: add target files to the /markdowns/ directory.  (same as standard git add command)
-Commit: create formatted .xml files in /atoms/  from .md files in the /markdowns/ directory using atomify.  Create .html files in /site/posts/ directory from .xml files in /atoms/ using jinja template.  Add the new post locations to the site index and archive.
-Push: push site files to remote repository.  Once files are in the remote repository, they are published.



### ex.
Initialize the site directory:
`python3 gitatom init .`

- An empty config.yaml file must exist in the directory otherwise config.py will create one and populate with default values
- config.yaml is populated when `init` is called.


To publish contents of ‘lorem.md’ to the site:

-`git add ../markdowns/lorem.md`
-`git commit -m ‘atomify and render lorem.md’`
-`git push`

To create index.html
`python3 gitatom append lorem.html` 

- Tested with skeleton html


(see: gitatom/\_\_main\_\_.py and gitatom/build.py)

