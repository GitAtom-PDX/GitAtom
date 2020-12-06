### install jinja2
`pip install -r requirements.txt`

### run:
`python3 gitatom.py (module)

or

`python3 -m gitatom (module)`

modules: [md, atomify, preview, publish, build]



The directory is structured like Josh's example. 

build.py
- scans site/ assuming dirs are year/month/day/etc for html pages
- renders the blogs template (which inherits from default.html) and outputs blog.html
- renders the default template and outputs index.html
