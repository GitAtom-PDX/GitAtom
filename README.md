# GitAtom
 GitAtom blogging software development repository for CS Capstone

### Install Dependencies
`pip install -r requirements.txt`

### Usage:
`python3 gitatom [command] (target)`

commands: [atomify, render, publish, append, run]


### ex.
Initialize the site directory:
`python3 gitatom init .`

- An empty config.yaml file must exist in the directory otherwise config.py errors
- config.yaml is populated when `init` is called.

To create index.html
`python3 gitatom append lorem.html` 

- Tested with skeleton html


(see: gitatom/\_\_main\_\_.py and gitatom/build.py)

