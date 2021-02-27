# GitAtom
Developed for Portland State University CS Capstone (Fall 2020 - Winter 2021)
 
 ## Contents
 * Introduction
 * Setup
 * Usage
 * Troubleshooting
 
## Introduction
GitAtom is a git-based static site generator used to create and manage Markdown blog 
content using the Atom XML format.

Upon committing one or more Markdown files, GitAtom will automatically generate a static 
web site and commit all required files for you. You can even configure GitAtom to automatically 
publish your site to a remote repository upon push.

###### Is this drive link publicly accessible?
Detailed information can be found [here](https://docs.google.com/document/d/1eONVONseT0Ex_Z_COYcDEAZJZb3Gb6mCPAmSxwqYNFM/edit?usp=sharing).

 
## Setup 
### Requirements 

`python3` and `pip3` must be installed prior to installing GitAtom.

### Installation 

To begin, clone GitAtom to your local machine.

``` 
HTML: git clone https://github.com/GitAtom-PDX/GitAtom.git
ssh: git clone git@github.com:GitAtom-PDX/GitAtom.git
```

Next, install all required modules using `pip3`.

```
pip3 install -r requirements.txt
```

The following modules will be installed:

* [Jinja2](https://pypi.org/project/Jinja2/) for site generation and formatting.
* [cmark](https://pypi.org/project/cmarkgfm/) to convert Markdown to HTML for site generation.
* [PyYAML](https://pypi.org/project/PyYAML/) for config handling.
* [pygit2](https://pypi.org/project/pygit2/) to implement git commands in Python.
* [paramiko](https://pypi.org/project/paramiko/) to initialize remote server. 

### Configuration 

GitAtom must be configured using `config.yaml` prior to initialization. `sample.config.yaml` is provided as a reference.

#### Fields:  
| Field | Description|
| --- | --- |
| feed_id | A metadata field in Atom, not currently used other then to fill the xml.|
| feed_title | Title of the website/blog.|  
| author | Name of author of the blog.|   
| publish_directory | site -needs to remain site for now.  |
| repo_path | Path to where the remote server bare repository will be located. |   
| work_path | Path to where the website will be hosted on remote server. |
| host | IP address of remote server. |   
| port | SSH port, default used by ssh is 22. |   
| username | Name of the user on the remote system. |  
| keypath | Path to your ssh key. |    
| deploy | true/false, use true if you want to deploy to a remote server.| 

GitAtom can be configured to use automatic remote deployment. You will need access to the 
remote server to which you want to publish the blog.  


### Initialization

Initialize GitAtom using the configuration specified in `config.yaml`.

```
python3 init.py
```

If using GitAtom locally, this will create the required directories and 
install the post-commit hook. 

#### Directories:  
| Directory | Description|
| --- | --- |
| markdowns | Where GitAtom expects to find your Markdown blog posts. |
| atoms | Where GitAtom stores your Atom-formatted blog posts. |  
| site | Where GitAtom stores your static web pages. |   

If using remote depoloyment, a bare repository will be created and the 
post-recieve hook will be installed on the remote server.


## Usage
`git [command] [-flag] (target)`
commands: [add, commit, push]

| Command | Description|
| --- | --- |
| Add | add or update a blog post. Only Markdown files located in the `/markdowns/` will be tracked for xml file creation. |
| Commit | generate and commit XML and HTML from added Markdown files. Resulting files are located in `/atoms/` and `/site/`. |  
| Push | publish to the remote repository. Make sure to push to the 'live' branch. |   
  
```
  git push live
```

  The post-receive hook on the remote repository will checkout the site
  directory to your work_path specified in the configuration file.  

### Example
To publish `somepost.md`:

```
git add ../markdowns/somepost.md
git commit -m 'adding somepost to blog'
git push live main
```


## Troubleshooting

### Permission denied on ssh into remote server

This error occurs when a user has multiple ssh keys. Ceate an alias that indicates use of a specific key.  

###### I thought this was on the local machine?
To fix, create an alias in the ssh config file on the remote repository. 

In `.ssh/config` add the following:  

```
Host `chosen alias name`
 HostName `host IP address`  
 User `your username on host`  
 IDFile `path to your ssh key` 
 IDOnly yes  
``` 

**NOTE** IDFile requires a complete file path.

With the alias specified, the live branch will use `<username>@<alias>`

You need to have permissions to write in the repo and working tree directory on the
remote server. If that directory cannot normally be written to without sudo you
need to connect to remote server and make sure the user has permissions to write 
into the targeted directories.





