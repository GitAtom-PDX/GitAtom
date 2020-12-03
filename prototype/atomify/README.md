
# atomify

## Usage

    $ python3 atomify.py input.html

 - `input.html` is the html file generated from markdown

 - `input.xml` is the outputted atom-format xml file

## Notes 

This script currently generates one atom-format xml file, with both feed and entry tags. It may later be modified to update a file containing only the feed tags, meaning the output file will contain just the entry tags (and encapsulated html). Whether or not this change is made will depend on what is most efficient for our implementation. 

The config file is currently very simple and may be phased out -- if the feed tags are stored in a separate file, there will be no need for the config file in this step. If the config file is ultimately required, the formatting will be improved. 

Also note that the <entry_published> and <entry_updated> tags are the same, because this script does not handle updating an existing blog post. This is something we will need to address in the future: should this module also handle updating an existing blog post? Or should this be handled elsewhere?





