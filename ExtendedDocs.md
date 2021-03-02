# GitAtom

CS Capstone Winter 2021 ![](RackMultipart20210211-4-bxln3i_html_66b194b54866537f.png)

## Contents

* Introduction
  * What is GitAtom?
  * Goals of this Application
* Usage
  * Installation
  * Configuration
  * Setup
  * Usage with git commands
  * Example
* Pipeline
* Current Implementation
  * HTML to XML Atom - Atomify
  * XML to Formatted HTML- Jinja &amp; XML etree
  * Publish to Web via Git Repository - githooks

## Introduction

### What is GitAtom?

GitAtom is a git-based static site generator used to create and manage Markdown blog content using the Atom XML format.  Upon committing one or more Markdown files, GitAtom will automatically generate a static website. 

### Goals of this Project

GitAtom is designed to be an easy to use blog management tool that eliminates problems that are commonly found in other generators.

Because this is a static generator, it is easier to maintain and secure than its dynamic counterparts. It is written primarily in Python, making the code simpler than many other blogging platforms written in Javascript, PHP, etc.

GitAtom does not require the user or a blogging site to host a database of blog content. This means that the user does not have to manage complicated database schema. Content is stored using git. Updates and publishing are handled with git hooks. By using git, GitAtom avoids some of the problems common in static site generators. Revising content is easy and user-friendly, and content is portable.

Blogs and the posts within them are formatted using Atom XML formatting. Atom provides options for a large amount of metadata, which provides information, such as update time and author information, that is useful to authors and readers. Atom also makes it easy to migrate content from a blog to another format, like a book.

## Usage

GitAtom uses githooks to operate behind the scenes when git commands are called. After it is initialized, the user should not need to interact directly with GitAtom to use it.

### Installation

`python3` and `pip3` must be installed prior to installing GitAtom.
Install by cloning GitAtom to the local repository, then install requirements using pip:

`pip3 install -r requirements.txt`

### Configuration

GitAtom must be configured using `config.yaml` prior to initialization. `sample.config.yaml` is provided as a reference.  
#### `config.yaml` Fields:  
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

GitAtom can be configured to use automatic remote deployment. You will need access to the remote server to which you want to publish the blog.

### Setup

Initialize GitAtom: `python3 init.py`  

If using GitAtom locally, this will create the required directories and install the post-commit hook.  
#### Directories
| Directory | Description|
| --- | --- |
| markdowns | Where GitAtom expects to find your Markdown blog posts. |
| atoms | Where GitAtom stores your Atom-formatted blog posts. |  
| site | Where GitAtom stores your static web pages. |   

If using remote depoloyment, a bare repository will be created and the 
post-recieve hook will be installed on the remote server.

### Usage with git commands

`git [command] [-flag] (target)`

commands: [add, commit, push]

- Add: add target files to the `/markdowns/` directory. (same as standard git add command)
- Commit: create formatted .xml files in `/atoms/` from Markdown files in the `/markdowns/` directory using atomify. Create HTML files in /site/posts/ directory from XML files in `/atoms/` using jinja template. Add the new post locations to the site index and archive.
- Push: push site files to remote repository. Once files are in the remote repository, they are published.

### Example

To publish contents of `lorem.md` to the site:  
`git add ../markdowns/lorem.md`  
`git commit -m 'atomify and render lorem.md'`  
`git push`  
(see: `gitatom/\_\_main\_\_.py`)  

## Troubleshooting

### Permission denied when ssh into remote server
This error occurs when a user has multiple ssh keys to choose from.  To solve, create an alias that indicates use of a specific key.  Update the config file in the remote repository with the following:
In `.ssh/config`  add/modify the following:  
`Host alias`  
`HostName <address>`  
`User <username>`  
`IDFile ~/.ssh/<path to key>`  
`IDOnly yes`  

#### `.ssh/config` fields

| Field | Description|
| --- | --- |
| Host | alias name, chosen by user |
| HostName | IP address of remote server |  
| User | username for remote server |   
| IDFile | path to your ssh key |   

Note: IDFile needs a complete file path.  

With the alias specified, the live branch will use `<username>@<alias>`  

You need to have permissions to write in the repo and working tree directory on the remote server. If that directory cannot normally be written to without sudo you need to connect to remote server and make sure the user has permissions to write into the targeted directories.  

## Pipeline

See pipeline diagram at [https://docs.google.com/drawings/d/1fY9yvk1XWXno47KaTcl7GqXHPoirk4SK26p59zirCmI/edit?usp=sharing](https://docs.google.com/drawings/d/1fY9yvk1XWXno47KaTcl7GqXHPoirk4SK26p59zirCmI/edit?usp=sharing)

The linked diagram shows the pipeline used by GitAtom. The process takes a Markdown file from the user, converts it into formatted HTML, and publishes a git repository.

To begin the process, a user creates a blog post in a Markdown (.md) file and commits the file to a local git repository. On commit, the Markdown file is parsed to find metadata and converted into Atom XML format. This file goes through a template that adds CSS. This formatted page is in HTML. The user can preview the formatted page, then they can use a gitatom command to publish the page to a remote git repository.

## Current Implementation

Currently, GitAtom is implemented using primarily Python 3 with some HTML and CSS.

### HTML to XML Atom - Atomify

The atomify() function is located in the GitAtom class. It checks that the named Markdown file exists and that it is in the correct format. Auxiliary functions getTitle() and getFilename() help to parse the Markdown file to find required tags like title, date, and author. This information is used to build the text of the Atom file. Then, that text is written to an XML file.

### XML to Formatted HTML- Jinja &amp; XML etree

Located in the GitAtom class - render\_html(). Imports [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html).

The XML file is parsed using minidom. Then, tags, blog content, and other information are sorted out and appended to a list. The function then loads a Jinja template and renders a formatted HTML page using the list of blog information.

Jinja template is located at jinja/templates/jinja\_template.html

### Publish to Web via Git Repository - githooks

Hooks are located in gitatom/hooks directory. These githooks call functions that are located in the gitAtom class&#39; main file.

The pre-commit hook calls atomify() and render(), and it stores the resulting .xml and .html files in their respective directories. The functions that are called directly by this hook are git\_staged\_files() and gitatom\_git\_add().

The on-push hook (note: this has not been implemented yet) publishes the .html files in /site/ to a remote repository.
