# GitAtom

CS Capstone Winter 2021 ![](RackMultipart20210211-4-bxln3i_html_66b194b54866537f.png)

## Contents

* Goals/General Description
  * What is GitAtom?
  * Goals of this Project
* Usage
  * Configuration
  * Installation
  * Usage with git commands
  * Example
* Pipeline
  * Figure 1: Pipeline Diagram
* Current Implementation
  * HTML to XML Atom - Atomify
  * XML to Formatted HTML- Jinja &amp; XML etree
  * Publish to Web via Git Repository - githooks
* Alternative Implementation Options
  * Markdown to HTML
  * HTML to XML Atom 
  * XML to Formatted HTML
    * Popular Template Languages
    * Python-Based Template Languages
* Publish to Web via Git Repository
## Goals/General Description

### What is GitAtom?

GitAtom is a git-based static site generator used to create and manage blog content. It stores blog content in an Atom XML content.

### Goals of this Project

GitAtom is designed to be an easy to use blog management tool that eliminates problems that are commonly found in other generators.

Because this is a static generator, it is easier to maintain and secure than its dynamic counterparts. It is written primarily in Python, making the code simpler than many other blogging platforms written in Javascript, PHP, etc.

GitAtom does not require the user or a blogging site to host a database of blog content. This means that the user does not have to manage complicated database schema. Content is stored using git. Updates and publishing are handled with git hooks. By using git, GitAtom avoids some of the problems common in static site generators. Revising content is easy and user-friendly, and content is portable.

Blogs and the posts within them are formatted using Atom XML formatting. Atom provides options for a large amount of metadata, which provides information, such as update time and author information, that is useful to authors and readers. Atom also makes it easy to migrate content from a blog to another format, like a book.

## Usage

GitAtom uses githooks to operate behind the scenes when git commands are called. After it is initialized, the user should not need to interact directly with GitAtom to use it.

Install Dependencies

pip install -r requirements.txt

### Configuration

GitAtom can be configured in the config.yaml file. If this file does not exist when GitAtom is initialized, one is created and populated with default values. Blog title, blog id, author name, and file path are specified in this file. (note: style.css will eventually be specified in the config file as well)

### Installation

Initialize the site directory: python3 gitatom init

### Usage with git commands

git [command] [-flag] (target)

commands: [add, commit, push]

- Add: add target files to the /markdowns/ directory. (same as standard git add command)
- Commit: create formatted .xml files in /atoms/ from .md files in the /markdowns/ directory using atomify. Create .html files in /site/posts/ directory from .xml files in /atoms/ using jinja template. Add the new post locations to the site index and archive.
- Push: push site files to remote repository. Once files are in the remote repository, they are published.

### Example

To set up GitAtom:

`pip install gitatom`
`pip install -r requirements.txt`
`python3 gitatom init`

To publish contents of &#39;lorem.md&#39; to the site:

`git add ../markdowns/lorem.md`

`git commit -m 'atomify and render lorem.md'`

`git push`

(see: `gitatom/\_\_main\_\_.py`)

Initialize the site directory: `python3 gitatom init` .

- An empty config.yaml file must exist in the directory otherwise config.py errors
- config.yaml is populated when init is called.

To create index.html python3 gitatom append lorem.html

- Tested with skeleton html

(see: gitatom/\_\_main\_\_.py and gitatom/build.py)

## Pipeline

![](RackMultipart20210211-4-bxln3i_html_443c06fc376ed1b6.jpg)

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

## Alternative Implementation Options

### Markdown to HTML

There are Markdown to HTML conversion tools in pypi. A few examples are [md-to-html](https://pypi.org/project/md-to-html/), [md2html](https://pypi.org/project/md2html/), and [gh-md-to-html](https://pypi.org/project/gh-md-to-html/) which has features to be more user friendly and command-line usable

### HTML to XML Atom

There are several HTML to XML conversion tools for Python. [Lxml](https://lxml.de/parsing.html) and [html5lib](http://code.google.com/p/html5lib/)support HTML to XML parsing. Beautiful Soup sits on top of those and adds extra functionality for parsing and formatting.

### XML to Formatted HTML

#### Popular Template Languages

React

[https://reactjs.org/](https://reactjs.org/)

React is a Javascript library used to build UIs. It is added to HTML pages to make them more interactive. In React, components manage their own state, and they come together to build a UI. Each component has a render() method that handles input data and returns the display. JSX is a syntax similar to XML. It can be used with React, but its use is optional.

Go

[https://golang.org/pkg/html/template/](https://golang.org/pkg/html/template/)

Go&#39;s template package is used mainly to organize and display data for web apps. A notable feature is that it automatically escapes data/input, making web pages more secure against injection. Templates can be parsed from a string or a stored file.

Liquid

[https://shopify.dev/docs/themes/liquid/reference](https://shopify.dev/docs/themes/liquid/reference)

Liquid is a template language written in Ruby. Shopify developed it as a basis for Shopify store design themes, and it is now an open-source tool used for many web pages. The main components of a Liquid template are objects, tags, and filters.

Vue

[https://vuejs.org/v2/guide/syntax.html](https://vuejs.org/v2/guide/syntax.html)

Vue.js uses HTML based syntax, and templates are valid HTML. It compiles templates into Virtual DOM render functions. Alternatively, JSX can be used to directly write render functions. Javascript code is allowed inside Vue bindings, and Javascript can be used as dynamic arguments in templates.

AnyJS

[https://openbase.com/js/anyjs/documentation](https://openbase.com/js/anyjs/documentation)

AnyJS is a Javascript library for UI development. It is relatively lightweight and has TinyUI and BasicUI options.

#### Python-Based Template Languages

Django

[https://docs.djangoproject.com/en/3.1/ref/templates/language/](https://docs.djangoproject.com/en/3.1/ref/templates/language/)

Like Jinia2, Django is a text-based template language written in Python. Templates can be written in any text format. Django templates use variables, tags, and filters. It supports inheritance, so a base template can be used to streamline templates for various pages.

Mako

[https://www.makotemplates.org/](https://www.makotemplates.org/)

Mako is a template language that compiles into Python code. Mako is an embedded Python language, and therefore can be faster than other template languages. Its Syntax is closer to Python than HTML or XML. It supports inheritance and escaping.

Genshi

[https://genshi.edgewall.org/](https://genshi.edgewall.org/)

Genshi is a Python library whose main feature is a template language. It is written to be a more intelligent and less verbose template language. Directives can be attached directly to elements. Features include relatively flexible inheritance, escaping, and stream-based filtering

### Publish to Web via Git Repository
