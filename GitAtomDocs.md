##
# GitAtom

CS Capstone Winter 2021 ![](RackMultipart20210115-4-76adbx_html_66b194b54866537f.png)

**Table of Contents**

[Goals/General Description 2](#_Toc61537779)

[What is GitAtom? 2](#_Toc61537780)

[Goals of this Project 2](#_Toc61537781)

[Usage 2](#_Toc61537782)

[Example 2](#_Toc61537783)

[Install Dependencies 3](#_Toc61537784)

[Pipeline 3](#_Toc61537785)

[Figure 1: Pipeline Diagram 3](#_Toc61537786)

[Current Implementation 4](#_Toc61537787)

[Markdown to HTML - CMark 4](#_Toc61537788)

[HTML to XML Atom - Atomify 4](#_Toc61537789)

[XML to Formatted HTML- Jinja &amp; Minidom 4](#_Toc61537790)

[Publish to Web via Git Repository 4](#_Toc61537791)

[Alternative Implementation Options 5](#_Toc61537792)

[Markdown to HTML 5](#_Toc61537793)

[HTML to XML Atom 5](#_Toc61537794)

[XML to Formatted HTML 5](#_Toc61537795)

[Publish to Web via Git Repository 5](#_Toc61537796)

### Goals/General Description

## What is GitAtom?

GitAtom is a git-based static site generator used to create and manage blog content. It stores blog content in an Atom XML content.

## Goals of this Project

GitAtom is designed to be an easy to use blog management tool that eliminates problems that are commonly found in other generators.

Because this is a static generator, it is easier to maintain and secure than its dynamic counterparts. It is written primarily in Python, making the code simpler than many other blogging platforms written in Javascript, PHP, etc.

GitAtom does not require the user or a blogging site to host a database of blog content. This means that the user does not have to manage complicated database schema. Content is stored using git. Updates and publishing are handled with git hooks. By using git, GitAtom avoids some of the problems common in static site generators. Revising content is easy and user-friendly, and content is portable.

Blogs and the posts within them are formatted using Atom XML formatting. Atom provides options for a large amount of metadata, which provides information, such as update time and author information, that is useful to authors and readers. Atom also makes it easy to migrate content from a blog to another format, like a book.

### Usage

python3 -m gitatom [command] (filename)

commands: [atomify, render, publish, include, build]

## Example

To create &#39;lorem.xml&#39;: python3 -m gitatom atomify lorem.md

To create &#39;lorem.xml&#39;, &#39;lorem.html&#39; and &#39;site/posts/lorem.html&#39;: python3 -m gitatom include lorem.md

(see: gitatom/\_\_main\_\_.py)

## Install Dependencies

pip install -r requirements.txt

### Pipeline

![](RackMultipart20210115-4-76adbx_html_443c06fc376ed1b6.jpg)

### Figure 1: Pipeline Diagram

The [linked diagram](https://docs.google.com/drawings/d/1vogONGyVG5FVBg1XpAbyG_FnPneU2iwRE61v5BCrI_A/edit?usp=sharing) shows the pipeline used by GitAtom. The process takes a Markdown file from the user, converts it into formatted HTML, and publishes a git repository.

To begin the process, a user creates a blog post in a Markdown (.md) file and commits the file to a local git repository. On commit, the Markdown file is converted to HTML. Then, the HTML file is parsed to find metadata and converted into Atom XML format. This file goes through a template that adds CSS. This formatted page is in HTML. The user can preview the formatted page, then they can use a gitatom command to publish the page to a remote git repository.

### Current Implementation

Currently, GitAtom is written implemented using primarily Python 3 with some HTML and CSS.

## Markdown to HTML - CMark

Located in GitAtom class - mdtohtml(). Uses [CMark](https://github.com/commonmark/cmark). Imports [cmarkgfm](https://pypi.org/project/cmarkgfm/).

The function checks that the named Markdown file exists and that it is in the correct format. cmarkgfm is used to convert the Markdown text to HTML text, and the text is written to an HTML file.

## HTML to XML Atom - Atomify

The atomify() function is located in the GitAtom class. It parses the file to find required tags like title, date, and author. This information is used to build the text of the Atom file. Then, that text is written to an XML file.

## XML to Formatted HTML- Jinja &amp; Minidom

Located in the GitAtom class - render\_html(). Imports [xml.dom.minidom](https://docs.python.org/3/library/xml.dom.minidom.html).

The XML file is parsed using minidom. Then, tags, blog content, and other information are sorted out and appended a list. The function then loads a Jinja template and renders a formatted HTML page using the list of blog information.

Jinja template is located at jinja/templates/jinja\_template.html

## Publish to Web via Git Repository

publish() in GitAtom class Githooks. Dependency: [shutil](https://docs.python.org/3/library/shutil.html)

This function checks that the source HTML file exists and copies it to a target directory in a remote git repository. If necessary, it builds the target directory.

### Alternative Implementation Options

## Markdown to HTML

There are Markdown to HTML conversion tools in pypi. A few examples are [md-to-html](https://pypi.org/project/md-to-html/), [md2html](https://pypi.org/project/md2html/), and [gh-md-to-html](https://pypi.org/project/gh-md-to-html/) which has features to be more user friendly and command-line usable

## HTML to XML Atom

There are several HTML to XML conversion tools for Python. [Lxml](https://lxml.de/parsing.html) and [html5lib](http://code.google.com/p/html5lib/)support HTML to XML parsing. Beautiful Soup sits on top of those and adds extra functionality for parsing and formatting.

## XML to Formatted HTML

Some alternative Python-friendly templating languages are [Django](https://docs.djangoproject.com/en/3.1/ref/templates/), [Mako](http://www.makotemplates.org/), and [Genshi](https://genshi.edgewall.org/).

## Publish to Web via Git Repository

Alternatives?