#!/usr/bin/env python3
# init.py - Set up GitAtom.

import getpass
import os
import paramiko
import pygit2
import sys
import shutil
from pathlib import Path

from gitatom import config

# Set up GitAtom on remote host.
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
    #change the permissions on hook so it will execute properly
    change_perm = f"chmod +x '{bare_path}/hooks/post-receive'"

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
    repo_path = pygit2.discover_repository("./content")
    repo = pygit2.Repository(repo_path)
    target = f"{username}@{host}:{bare_path}"
    try:
        repo.remotes.create('origin', target)
    except ValueError:
        print("origin: could not add remote", file=sys.stderr)

# Set up GitAtom.
print("initializing")

cfg = config.load_into_dict()

# Place the hook in local that will create files and /site.
from_pc = Path('./gitatom/hooks/pre-commit')
to_pc = Path('./content/.git/hooks/pre-commit')
shutil.copyfile(from_pc, to_pc)
os.chmod(to_pc, 0o755)

# check if deploy set to true before running remote
if cfg['deploy']: remote_setup()
