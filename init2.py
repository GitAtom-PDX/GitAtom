#! /usr/bin/env python3
import subprocess
import os.path
from pathlib import Path
import yaml
from gitatom import build
from gitatom import config
from pathlib import Path
import os
import paramiko
import getpass
import pygit2


# init.py

def remote_setup():

    cfg = config.load_into_dict()    

    host = cfg['host']
    port = cfg['port']
    username = cfg['username']
    repo_path = cfg['repo_path']
    work_path = cfg['work_path']
    shebang = "'#!/bin/sh'"  

    # build init command string
    # init bare repository
    command = "git init --bare " + repo_path + "; " 

    # set up work tree 
    command += f"cd {repo_path}; git symbolic-ref HEAD refs/heads/main; " 
    command += "mkdir " + work_path + "; "

    # generate git hook
    command += "echo '" + shebang + "' > " + repo_path + "/hooks/post-receive; "
    p_rec = f"git --work-tree={work_path} --git-dir={repo_path} checkout HEAD -- site"
    command += "echo '" + p_rec + "' >> " + repo_path + "/hooks/post-receive; "    

    # change permissions
    command += "chmod +x " + repo_path + "/hooks/post-receive" 

    # send commmand string
    subprocess.call(['ssh', '-t', 'gitatom', command]) 


    # Track remote server with git
    current_directory = os.getcwd()
    repo_path2 = pygit2.discover_repository(current_directory)
    repo = pygit2.Repository(repo_path2) # need to fix bad naming
    target = f"{username}@{host}:{repo_path}"
    try:
        repo.remotes.create('live',target)
    except ValueError:
        print("Live remote already tracked")




def init():
    print("initializing")

    cfg = config.load_into_dict()
    posts_path = Path(cfg['publish_directory'] + '/posts')

    cur_dir = os.getcwd()
    
    from_pc = cur_dir+'/gitatom/hooks/pre-commit'
    to_pc = cur_dir+'/.git/hooks/pre-commit'

    with open (from_pc,'r') as f: 
        lines = f.read()
    outfile = open(to_pc,'w')
    outfile.write(lines)
    outfile.close()
    os.chmod(to_pc, 0o755)

    if not posts_path.exists():
        posts_path.mkdir(parents=True)

    atoms_path = Path('./atoms')
    if not atoms_path.exists():
        atoms_path.mkdir()

    markdowns_path = Path('./markdowns')
    if not markdowns_path.exists():
        markdowns_path.mkdir()

    build.create(cfg['publish_directory'])
    # check if deplay set to true before running remote
    if cfg['deploy']: remote_setup()



init()


