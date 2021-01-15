# GitAtom
 GitAtom blogging software development repository for CS Capstone

### Install Dependencies
`pip install -r requirements.txt`

### Usage:
`python3 gitatom [command] (filename)`

commands: [atomify, render, publish, include, build]


### ex.
To create 'lorem.xml':
`python3 gitatom atomify lorem.md` 

To create 'lorem.xml', 'lorem.html' and 'site/posts/lorem.html':
`python3 gitatom include lorem.md` 


(see: gitatom/\_\_main\_\_.py)
