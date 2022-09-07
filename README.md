# GitAtom

GitAtom is a "static" website generator used to create and manage
Markdown blog content using [Git](https://git-scm.com) and
the
[Atom feed format](https://www.ibm.com/docs/en/baw/19.x?topic=formats-atom-feed-format).

Upon Git-committing one or more
[Markdown-formatted](https://github.com/github/cmark-gfm)
posts to your blog, GitAtom will automatically regenerate a
static website for you. You can even configure GitAtom to
automatically publish your site to a remote repository upon
Git push.

**This is a work in progress! GitAtom is not yet really
ready for general use. Please see the
[GitAtom Issue Tracker](https://github.com/GitAtom-PDX/GitAtom/issues)
for some of the many GitAtom pitfalls.**
 
## Background

After 20 years of blogging (off and on), Bart Massey got
tired of some of the issues with the various blog
platforms. A CS Capstone Team at
[Portland State University](http://pdx.edu) wrote GitAtom to
Bart's design. Bart has subsequently maintained and updated
GitAtom.

What does GitAtom offer?

* **Maximal data portability:** If you decide to migrate
  your blog content away from GitAtom, you should be able to
  do something reasonable with the combination of per-post
  Atom feed files and Git repo that GitAtom maintains for you.

* **Old-school convenience:** If you are the kind of person
  who wants to just edit a Markdown blog post with emacs,
  git-commit it, push it and have a blog post on the web —
  you are me and you get that. Github Markdown is a good
  markdown engine for blogging purposes.

* **Reasonable flexibility:** GitAtom is only
  medium-opinionated. The use of Jinja2 templating, CSS
  styling on top of simple HTML, and direct access to the
  Git repo via libgit2 means that adapting GitAtom to your
  needs may not be too much of a pull.

What are the downsides?

* **Major features are missing:** Some stuff you'd expect
  from any blog platform isn't there: notably any kind of a
  feed mechanism. Adding missing features is a high
  priority, but let's just say pull requests are welcome.

* **Fragile:** The codebase is tiny but full of
  small issues at this point. Lots of stuff will panic during
  site generation that should be more gracefully handled.
  The process of publishing remotely is a bit convoluted and
  can go wrong in many ways.

* **Bespoke:** This is a boutique project. It has only one
  developer-user currently. You will not have access to help
  or support other than that.

## Setup 

The setup of GitAtom is a bit intricate, in spite of some
provided information. We assume a user who is relatively
familiar with the technologies used by GitAtom.

### Requirements 

`python3.9` and `git 2.27` or later must be installed before
installing GitAtom.  `git` must be up to date on both local
and remote systems to deploy remotely.

### Installation 

To begin, clone GitAtom to your local machine.

``` 
git clone https://github.com/GitAtom-PDX/GitAtom.git
```

Next, install all required modules.

```
python3 -m pip install -r requirements.txt
```

The following modules will be installed:

* [Jinja2](https://pypi.org/project/Jinja2/) for site
  generation and formatting.

* [cmarkgfm](https://pypi.org/project/cmarkgfm/) to convert
  Markdown to HTML for site generation.

* [PyYAML](https://pypi.org/project/PyYAML/) for config
  handling.

* [pygit2](https://pypi.org/project/pygit2/) to implement git commands in Python.

* [paramiko](https://pypi.org/project/paramiko/) to
  initialize remote server.

* [python-dateutil](https://dateutil.readthedocs.io/en/stable/)
  to handle date-time parsing, formatting and conversions.

### Set Up Environment Variable

GitAtom needs to be able to find its modules. Set the
`GITATOM_PATH` environment variable to point to the root of
this repository as installed.

### Set Up Your Blog

You will want to have a repo for your blog content, separate
from the GitAtom codebase. Run

```
python3 init-content.py
```

This will make a `content/` subdirectory containing a new
Git repo with a ready-to-edit `config.yaml` in it. It will
populate the `content/` repo with the directories `GitAtom`
needs to operate.

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

Once you have completed the initialization of `GitAtom`, you
may move `content/` elsewhere: the main `GitAtom` sourcebase
will be referenced using the `GITATOM_PATH` environment
variable (described above).

## Webserver Config

Here's a webserver configuration you can try for Apache2.

```
<VirtualHost *:80>
    ServerName devblog.example.com
    ServerAlias devblog.example.com www.devblog.example.com
    ErrorLog /var/log/apache2/devblog.example.com-error.log
    CustomLog /var/log/apache2/devblog.example.com-access.log common
    ServerAdmin webmaster@devblog.example.com
    DocumentRoot /var/www/devblog/site
</VirtualHost>
```

(If you use `nginx` or something, you'll have to figure that
one out. Let us know how it went.)

The important thing here is to be sure to set `DocumentRoot`
correctly so that the `/site` directory is transparent. This
is a misfeature/bug in Gitatom that
[should be fixed](https://github.com/GitAtom-PDX/GitAtom/issues/28)
but for now here we are.

## Usage

Once GitAtom is set up, you may use normal Git commands to
operate your blog. Three Git commands are set up to work
especially with GitAtom: `add`, `commit`, and `push`.

| Command | Description|
| --- | --- |
| `add` | Add or update one or more blog posts. Only
| Markdown files located in the `markdowns/` directory will
| be tracked for xml file creation. *Note:* `git commit -a`
| does not currently work: you will need to explicitly `git add`. |  
| `commit` | Generate and commit XML and HTML from added
| Markdown file(s). Resulting files are saved in `atoms/` and `site/`. |  
| `push` | Publish to the remote repository. |

If using remote deployment, the `post-receive` hook on the
remote repository will update the site directory at your
`work_path`, as specified in `config.yaml` during
initialization.

### Blogging

To publish `somepost.md` from your `content/` repo:

```
git add ./markdowns/somepost.md
git commit -m 'adding somepost to blog'
git push -u origin
```

(I normally just use `git add .` in the first step.)

Use `git push -u origin` to publish your first
post. After that, `git push` will default correctly.

### Markdown Requirements

Each blog post file should start with a level 1 header that
will be used as the post title. All other blog post
information is extracted from Git at commit time.

### Templating 

To change the blog template, simply modify or replace the
`style.css` file in the `content/site` directory.

## SSH Issues

Perhaps you are seeing "Permission denied on ssh into remote
server."  This error occurs when a user has multiple ssh
keys. Create an alias that indicates use of a specific key.

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

# Authors

GitAtom was developed for the Portland State University CS
Capstone during Fall 2020 - Winter 2021.

Subsequently, Bart Massey <bart@cs.pdx.edu> and Keith
Packard <keithp@keith.com> took over primary responsibility
for the codebase.

# License

This work is made available under the "GPL v3 or later
license." Please see the file `LICENSE` in this distribution
for license terms.
