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
Before installing GitAtom:  
Python3 and pip need ot be installed to run GitAtom.    
clone to local repository.   
Have access to the remote server to which you want to publish the blog.  
Create an ssh key.  

Install requirements on local repository using `pip install -r requirements.txt`  

This application requires the following modules:
* Jinja2 <https://pypi.org/project/Jinja2/>
* cmark <https://pypi.org/project/cmarkgfm/>
* YAML <https://pypi.org/project/PyYAML/>
* Pygit2 <https://pypi.org/project/pygit2/>
* Paramiko <https://pypi.org/project/paramiko/>

### Configuration
Edit the configuration file: `config.yaml` before initialization.  
Fields:   
feed_id: A metadata field in Atom, not currently used other then to fill the
xml.  
feed_title: Title of the website/blog.  
author: Name of author of the blog.   
publish_directory: site -needs to remain site for now.  
repo_path: path to where the remote server bare repository will be located.   
work_path: path to where the website will be hosted.  
host: ip adddress of remote server.   
port: ssh port used default is 22.   
username: name of the user on the remote system.  
keypath: Path to your ssh key.    
deploy: true/false use true if you want to deploy to a remote server.  

Configure remote server settings using `.ssh config`
(not necessary unless working with multiple ssh keys - see Troubleshooting section)

To change blog appearance, add a CSS file to the `gitatom/main_templates` directory.  To choose which template to use, specify the file name in the 'stylesheet' reference in `gitatom/post_templates/default_jinja.html`.  To use a different Jinja template, add the new template as an HTML file to the `gitatom/post_templates` directory.

### Setup
 
Install with `python3 init.py`  
This will install git hooks and initialize a bare repository on the remote
server
 
You need to have permissions to write in the repo and working tree directory on the
remote server.  If that directory cannot normally be written to without sudo you
need to  connect to remote server
`ssh <user>@<server address>` 
and make sure the user has permions to write into the targeted directories.

### Usage:
`git [command] [-flag] (target)`
commands: [add, commit, push]

- Add: add target files to the /markdowns/ directory.  (same as standard git add
  command) Only markdown files located in the `/markdowns/` and added to the
  repository will be tracked for xml file creation. 
- Commit: create formatted .xml files in /atoms/  from .md files in the /markdowns/ directory using atomify.  Creates .html files in /site/posts/ directory from .xml files in /atoms/ using jinja template.  Add the new post locations to the site index and archive.
- Push: push site files to remote repository.  Once files are in the remote
  repository, they are published.  Make sure to push to live branch. 
  `git push live`  
  The post-recieve hook on the remote repository will checkout the site
  directory to your work_path specified in the configuration file.  

### ex. --CURRENTLY UNDER CONSTRUCTION
Initialize the site directory:
`python3 init.py`

- An config.yaml file must exist in the directory otherwise config.py will create one and populate with default values
- The config.yaml file is read in on when init.py is ran. Taking in the users
  input to setup the remote repository if deploy is set to true.  


To publish contents of ‘lorem.md’ to the site:

- `git add ../markdowns/lorem.md`
- `git commit -m ‘atomify and render lorem.md’`
- `git push live main`

Initialize the site directory: `python3 init.py`
config.yaml is created populated with default values when init is called.

Site index and archive are created at initialization, and they are updated when new entries are added.

### Troubleshooting
Permission denied when ssh into remote server:

This issue comes up when a user has multiple ssh keys to choose from.  To solve, you need to create an alias that indicates use of a specific key.  This is done by updating the config file in the remote repository.  
In `ssh config`  add/modify the following:  
`Host <human readable hostname>`  
`HostName <host address>`  
`User <username>`  
`IDFile ~/.ssh/key`  
`IDOnly yes`  

Note IDFile needs a complete file path.

With the alias specified, the live branch will use `<username>@<alias>`




