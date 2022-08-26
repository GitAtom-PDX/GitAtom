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
    for md in mds:
        # make feed entry file
        feedfile = build.gen_feedfile(md)
        outname = 'atoms/' + build.filepart(md) + '.xml'
        with open(outname, 'w') as outfile:
            outfile.write(feedfile)
        files.append(outname)

    html = build.build_it()
    for f in html:
        files.append(f)
    return files
