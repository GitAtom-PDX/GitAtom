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
