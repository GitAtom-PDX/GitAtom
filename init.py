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
import pygit2


# init.py

def remote_setup():

    cfg = config.load_into_dict()    

    #pull config options for remote
    host = cfg['host']
    port = cfg['port']
    username = cfg['username']
    password = getpass.getpass("Enter key passphrase: ")
    bare_path = cfg['repo_path']
    work_path = cfg['work_path']
    
    #fstring commands to be run on remote once connection is established for deployment setup
    make_repo = f"git init --bare -b main '{bare_path}'"     #set up bare repo for remote version control
    make_work_tree = f"mkdir -p '{work_path}'"               #make the working tree where site will be deployed
    shabang = "#!/bin/sh"                                    #shabang for remote hook on bare
    #place the hook in remote bare
    make_hook = f"""cat >'{bare_path}/hooks/post-receive' <<'EOF'           
#!/bin/sh
git --work-tree={work_path} --git-dir={bare_path} checkout HEAD -- site
EOF
"""
    change_perm = f"chmod +x '{bare_path}/hooks/post-receive'"      #change the permissions on hook so it will execute properly

    #connect to the remote server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username,password=password)

    #function that will run the fstring commands with some added verbosity 
    def run_command(command):
        print("run", command)
        with ssh.get_transport().open_session() as chan:
            chan.exec_command(command)
            result = chan.recv_exit_status()
            if result != 0:
                print("failed", result)
                message = chan.recv_stderr(1000000)
                print(message.decode('utf-8'))
                exit(result)

    #run the various command strings
    run_command(make_repo)
    run_command(make_work_tree)
    run_command(make_hook)
    run_command(change_perm)

    # Track remote server with git
    current_directory = os.getcwd()
    repo_path = pygit2.discover_repository(current_directory)
    repo = pygit2.Repository(repo_path)
    target = f"{username}@{host}:{bare_path}"
    try:
        repo.remotes.create('live',target)
    except ValueError:
        print("Live remote already tracked")





#set up the local file structure needed for 
def init():
    print("initializing")

    cfg = config.load_into_dict()
    posts_path = Path(cfg['publish_directory'] + '/posts')

    cur_dir = os.getcwd()
    
    from_pc = cur_dir+'/gitatom/hooks/pre-commit'
    to_pc = cur_dir+'/.git/hooks/pre-commit'

    #place the hook in local that will create files and /site
    with open (from_pc,'r') as f: 
        lines = f.read()
    outfile = open(to_pc,'w')
    outfile.write(lines)
    outfile.close()
    os.chmod(to_pc, 0o755)

    #create the initial structure in local for hook and main to work with
    if not posts_path.exists():
        posts_path.mkdir(parents=True)

    atoms_path = Path('./atoms')
    if not atoms_path.exists():
        atoms_path.mkdir()

    markdowns_path = Path('./markdowns')
    if not markdowns_path.exists():
        markdowns_path.mkdir()

    build.create(cfg['publish_directory'])
    # check if deploy set to true before running remote
    if cfg['deploy']: remote_setup()



init()


