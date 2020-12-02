### (sudo apt) install:
`python3-pip`

`python3-venv`

### then run:
`python3 -m venv env`;

`source env/bin/activate`;

`pip install -r requirements.txt`

### finally, run:
`python3 ./build.py`

### when done:
`deactivate`


The directory is structured like Josh's example. If we have...

build.py
- scans site/ as deep as it needs to for html pages
- renders the list_posts template (which inherits from default.html)
- outputs index.html
