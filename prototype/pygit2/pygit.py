#! /usr/bin/env python3
# source: https://gist.github.com/lig/dc1ede7e09488a62116fe90aa31617d9
import pygit2
import sys
import os 
import time

message = "This is the demonstratoin commit"

# can use this info to add it to the commit
# not really used in this example
# user_name = "Author"
# user_mail = "author@test.edu"
# author = pygit2.Signature(user_name, user_mail)
# commiter = pygit2.Signature(user_name, user_mail)





print('show nothing in git status as added')
os.system('git status')

time.sleep(5)

os.system('echo "test" >> htmltoadd.html')
print('echo "test" >> htmltoadd.html')

time.sleep(5)
print('show modified in git status')
os.system('git status')
time.sleep(5)


# location of .git dir
repo = pygit2.Repository('/home/kellywho/dev/pygit2')

# can use this to shorten code
# index = repo.index
# index.add("htmltoadd.html")
# index.write()




# adds one specific file
repo.index.add('htmltoadd.html')

# Alternativly you can add all files with: 
# repo.index.add_all()






# not fully sure what this is doing
repo.index.write()
print('show htmltoadd queued to be commited')
os.system('git status')
tree = repo.index.write_tree()
parent, ref = repo.resolve_refish(refish=repo.head.name)
time.sleep(5)





# this will throw an error if the directory hasn't already had a commit before
# as /.git/refs/head/master won't exist
repo.create_commit( ref.name, repo.default_signature, repo.default_signature,
        message, tree, [parent.oid],)
print('show it has been commited')
os.system('git status')
time.sleep(5)
os.system('git log')
