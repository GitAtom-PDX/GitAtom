### (sudo apt) install
`python3-pip`
`python3-venv`

### first
`python3 -m venv env`
`source env/bin/activate'
`pip install -r requirements.txt`

### run
`python3 ./build.py`

### done?
`deactivate`


The directory is structured like Josh's example. If we have...

gitatom/templates/default.html
gitatom/templates/list_posts.html
site/assets/css/style.css
site/about.html, and site/blog.html

build.py
- scans site/ as deep as it needs to
- renders the list_posts template (which inherits from default.html)
- outputs index.html
