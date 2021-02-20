#! /usr/bin/env python3

import os.path
from pathlib import Path
import yaml
from gitatom import build
from gitatom import config
from pathlib import Path
import os
import paramiko
import getpass


# init.py

def remote_setup():
    
    cfg = config.load_into_dict()    

    host = cfg['host']
    port = cfg['port']
    username = cfg['username']
    password = getpass.getpass("Enter ssh key passphrase: ")

    #absolute path from root
    bare_path = cfg['repo_path']
    command = "git init --bare " + bare_path
    #absolute path from root
    symbolic_command = f"cd {bare_path}; git symbolic-ref HEAD refs/heads/main"
    work_path = cfg['work_path']
    work_tree = "mkdir " + work_path

    shabang = "'#!/bin/sh'"
    p_rec = f"git --work-tree={work_path} --git-dir={bare_path} checkout HEAD -- site"
    change_perm = "chmod +x " + bare_path + "/hooks/post-receive"
    make_hook = "echo '" + shabang + "' > " + bare_path + "/hooks/post-receive"
    make_hook2 = "echo '" + p_rec + "' >> " + bare_path + "/hooks/post-receive"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(cfg['keypath'])
    ssh.connect(host, port, username, password, key_filename=cfg['keypath'])

    #should prob catch these
    ssh.exec_command(command)
    ssh.exec_command(symbolic_command)
    ssh.exec_command(work_tree)
    stdin, stdout, stderr =  ssh.exec_command(make_hook)
    ssh.exec_command(make_hook2)
    ssh.exec_command(change_perm)
    lines = stdout.readlines()
    print(lines)


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

    if not posts_path.exists():
        posts_path.mkdir(parents=True)

    atoms_path = Path('./atoms')
    if not atoms_path.exists():
        atoms_path.mkdir()

    build.create(cfg['publish_directory'])
    # check if deplay set to true before running remote
    if cfg['deploy']: remote_setup()



init()


