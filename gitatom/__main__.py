from gitatom import build
import yaml
import pygit2 
from os import path

#git add the list of files that were created (HTML,XML)
def gitatom_git_add(repo, files):
    index = repo.index
    for f in files:
        index.add(f)
    index.write()

#get the list of files that have been staged with git
def git_staged_files(repo):
    status = repo.status()
    staged_files = []
    for file_path, flags in status.items():
        if flags == pygit2.GIT_STATUS_INDEX_NEW or flags == pygit2.GIT_STATUS_INDEX_MODIFIED:
            file_only = path.basename(file_path)
            #append the markdown files to list of staged files
            if file_only.endswith('.md') and 'markdowns' in file_path:
                staged_files.append('./markdowns/' + file_only)
    return staged_files


# Generate atom content.  Returns a list of files based
# on newly created files so that they can be git added in
# gitatom_git_add().
def on_commit(mds):
    files = []
    with open("./site/feed.xml", 'w') as feed:
        atomheader = build.atomify("header")
        feed.write(atomheader)
        for md in mds:
            # make feed entry file
            outname, feedfile = build.atomify("file", md=md)
            outfile = open('./atoms/' + outname, 'w')
            outfile.write(feedfile)
            outfile.close()
            files.append('atoms/' + outname)

            # add entry to feed file
            atomentry = build.atomify("entry", md=md)
            feed.write(atomentry)
        feed.write('</feed>\n')
    files.append('site/feed.xml')
    html = build.build_it()
    for f in html:
        files.append(f)
    return files
