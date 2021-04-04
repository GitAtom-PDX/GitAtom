# GitAtom
Developed for Portland State University CS Capstone (Fall 2020 - Winter 2021)
 
## Introduction

GitAtom is a git-based static site generator used to create
and manage Markdown blog content using the Atom XML format.

Upon committing one or more Markdown files, GitAtom will
automatically generate a static website and commit all
required files for you. You can even configure GitAtom to
automatically publish your site to a remote repository upon
push.
 
## Setup 

The setup of GitAtom is a bit intricate, in spite of some
provided information. We assume a user who is relatively
familiar with the technologies used by GitAtom.

### Requirements 

`python3`, `pip3`, and `git 2.27` or later must be installed
prior to installing GitAtom.  `git` must be up to date on
both local and remote systems to deploy remotely.

### Installation 

To begin, clone GitAtom to your local machine.

``` 
git clone https://github.com/GitAtom-PDX/GitAtom.git
```

Next, install all required modules using `pip3`.

```
pip3 install -r requirements.txt
```

The following modules will be installed:

* [Jinja2](https://pypi.org/project/Jinja2/) for site
  generation and formatting.

* [cmark](https://pypi.org/project/cmarkgfm/) to convert
  Markdown to HTML for site generation.

* [PyYAML](https://pypi.org/project/PyYAML/) for config
  handling.

* [pygit2](https://pypi.org/project/pygit2/) to implement git commands in Python.

* [paramiko](https://pypi.org/project/paramiko/) to
  initialize remote server.

### Set Up Environment Variable

GitAtom needs to be able to find its modules. Set the
`GITATOM_PATH` environment variable to point to the root of
this repository as installed.

### Set Up Blog Content

You will want to have a repo for your blog content, separate
from the GitAtom codebase. Run

```
python3 init-content.py
```

This will make a `content/` subdirectory containing a new
Git repo with a ready-to-edit `config.yaml` in it. It will
populate the `content/` repo with the directories `GitAtom`
needs to operate.

Once you have completed the initialization of `GitAtom` (see
below), you may move `content/` elsewhere: the main
`GitAtom` sourcebase is no longer needed.

### Configuration 

GitAtom must be configured using `config.yaml` prior to
initialization.

#### Fields:  
| Field | Description|
| --- | --- |
| `feed_id` | Website's web address or unique permanent URI|  
| `feed_title` | Title of the website/blog.|  
| `author` | Name of author of the blog.|   
| `repo_path` | Path to where the remote server bare repository will be located. |  
| `work_path` | Path to where the website will be hosted on remote server.|  
| `host` | IP address of remote server. |  
| `port` | SSH port, default used by ssh is 22. |  
| `username` | Name of the user on the remote system. |  
| `keypath` | Path to your ssh key. |  
| `deploy` | `true`/`false`: use `true` if you want to deploy to a remote server.| 

GitAtom can be configured to use automatic remote
deployment. You will need access to the
remote server to which you want to publish the blog.

#### Directories
| Directory | Description|
| --- | --- |
| content/markdowns | Where GitAtom expects to find your Markdown blog posts. |
| content/atoms | Where GitAtom stores your Atom-formatted blog posts. |  
| content/site | Where GitAtom stores your static web pages. |   

### Initialization

Be sure to edit your `content/config.yaml`.  You may then
initialize GitAtom using the configuration specified there.

```
python3 init.py
```

If using GitAtom locally, this will install the `pre-commit`
hook.

If using remote deployment (`deploy = true` in
`./content/config.yaml`), a bare repository will be created
and the `post-receive` hook will be installed on the remote
server.


## Usage

Once GitAtom is set up, you may use normal Git commands to
operate your blog. Three Git commands are set up to work
especially with GitAtom: `add`, `commit`, and `push`.

| Command | Description|
| --- | --- |
| `add` | Add or update one or more blog posts. Only
| Markdown files located in the `markdowns/` directory will be tracked for xml file creation. |  
| `commit` | Generate and commit XML and HTML from added  Markdown file(s). Resulting files are saved in `atoms/` and `site/`. |  
| `push` | Publish to the remote repository. |

If using remote deployment, the `post-receive` hook on the
remote repository will update the site directory at your
`work_path`, as specified in `config.yaml` during
initialization.

### Example
To publish `somepost.md` from your `content/` repo:

```
git add ./markdowns/somepost.md
git commit -m 'adding somepost to blog'
git push -u origin
```

Use `git push -u origin` to publish your first
post. After that, `git push` will default correctly.

### Templating 

To change the blog template, simply modify or replace the
`style.css` file in the `content/site` directory.

## Troubleshooting

### Permission denied on ssh into remote server

This error occurs when a user has multiple ssh keys. Create
an alias that indicates use of a specific key.

To fix, create an alias in the `~/.ssh/config` file on the
local machine and reconfigure the remote branch.

In `~/.ssh/config` add the following:

```
Host alias
    HostName address
    User username
    IdentityFile ~/.ssh/path-to-key
    IdentitiesOnly yes
```

| Field | Description|
| --- | --- |
| `Host` | alias name, chosen by user |  
| `HostName` | IP address of remote server |  
| `User` | username for remote server |   
| `IdentityFile` | path to your ssh key |

**NOTE** `IdentityFile` requires an absolute path.

Next, reconfigure the remote branch. First, display
the list of remote branches.

```
git remote -v
```

Find the branch named `origin` and save the path following the colon.

```
origin user@hostname:/path/to/your/repo.git
```

Reconfigure the `origin` using your alias. 

```
git remote set-url origin alias:/path/to/your/repo.git
```

The remote will now use your alias to connect via ssh.

You need to have permissions to write in the repo and
working tree directory on the remote server. If that
directory cannot normally be written to without sudo you
need to connect to the remote server and make sure the user
has permissions to write into the targeted directories.
