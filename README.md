# GitAtom
 GitAtom blogging software development repository for CS Capstone
 
 ### Contents
 * Introduction
 * Requirements
 * Setup
 * Configuration
 * Usage
 * Troubleshooting
 
### Introduction
GitAtom is a git-based static site generator used to create and manage blog content.  It stores blog content in an Atom XML content.

GitAtom takes a blog post in the form of a Markdown file and commits the file to a local git repository.  On commit, the Markdown file is parsed to find metadata and converted into Atom XML format.  This file goes through a template that adds CSS.  This formatted page is in HTML.  The user can preview the formatted page, then they can use a gitatom command to publish the page to a remote git repository.

More information in GitAtomDocs.md or at <https://docs.google.com/document/d/1eONVONseT0Ex_Z_COYcDEAZJZb3Gb6mCPAmSxwqYNFM/edit?usp=sharing>
 

### Requirements
Python3 and pip need ot be installed to run GitAtom

Install requirements on local repository using `pip install -r requirements.txt`

This application requires the following modules:
* Jinja2 <https://pypi.org/project/Jinja2/>
* cmark <https://pypi.org/project/cmarkgfm/>
* YAML <https://pypi.org/project/PyYAML/>
* Pygit2 <https://pypi.org/project/pygit2/>
* Paramiko <https://pypi.org/project/paramiko/>

### Setup
Before installing GitAtom:
Fork GitAtom from Github and clone to local repository.
Have access to the remote server to which you want to publish the blog.
Create an ssh key
 
Install with `python3 init.py`
 
Modify githook permissions:
You need to have permissions to write in the working tree directory.  If that directory cannot normally be written to without sudo, need to specify the work tree path
`ls .git/hooks`
`chmod u+x .git/hooks/precommit`
 
Connect to remote server
`ssh <user>@<server address>` 
Enter ssh public key if required - See troubleshooting section if ssh key is not accepted
Setup working tree directory and connect remote repository
`python3 init.py`

`mkdir <working tree directory>`
If you already have write permissions where the directory is currently located, creating the working tree directory elsewhere is unnecessary.

 
Connect local repository
In local:
`git remote add live 'username@ipaddress:path-to-bare-directory'`
### Configuration
Configure blog information like title and author in `config.yaml` after initialization.  Fields to configure: author name, feed ID, feed title, desired path to html files.  That path is `/site/` by default

Configure remote server settings using `.ssh config`
(not necessary unless working with multiple ssh keys - see Troubleshooting section)

### Usage:
`git [command] [-flag] (target)`
commands: [add, commit, push]

- Add: add target files to the /markdowns/ directory.  (same as standard git add command)
- Commit: create formatted .xml files in /atoms/  from .md files in the /markdowns/ directory using atomify.  Create .html files in /site/posts/ directory from .xml files in /atoms/ using jinja template.  Add the new post locations to the site index and archive.
- Push: push site files to remote repository.  Once files are in the remote repository, they are published.  Make sure to push to live branch.

### ex.
Initialize the site directory:
`python3 gitatom init .`

- An empty config.yaml file must exist in the directory otherwise config.py will create one and populate with default values
- config.yaml is populated when `init` is called.


To publish contents of ‘lorem.md’ to the site:

- `git add ../markdowns/lorem.md`
- `git commit -m ‘atomify and render lorem.md’`
- `git push live main`

Initialize the site directory: `python3 init.py`
config.yaml is created populated with default values when init is called.

Site index and archive are created at initialization, and they are updated when new entries are added.

###Troubleshooting
Permission denied when ssh into remote server:

This issue comes up when a user has multiple ssh keys to choose from.  To solve, you need to create an alias that indicates use of a specific key.  This is done by updating the config file in the remote repository
In `ssh config`  add/modify the following
`Host <human readable hostname>`
`HostName <host address>`
`User <username>
`IDFile ~/.ssh/key`
`IDOnly` yes

Note IDFile needs a complete file path.

With the alias specified, the live branch will use <username>@<alias>




