import sys
import shutil
from pathlib import Path

TARGET_DIRECTORY = "./site/posts/"
ERROR = -1

# input: string representation of path to source file
# returns: ERROR if the source file does not exist
def publish(path_to_src):
    src_path = Path(path_to_src)
    if not src_path.exists():
        return ERROR

    # extract the filename from full path, split filname into pieces
    # based on '-'
    # ex: 2020-12-1-post.html is split into:
    # ['2020', '12', '1', 'post.html']
    src_filename = src_path.name
    name_tokens = src_filename.split("-")

    # build the destination directory based on previous pieces
    dest_path = Path(TARGET_DIRECTORY)
    for i in range(len(name_tokens) - 1):
        dest_path = dest_path / name_tokens[i]

    if not dest_path.exists():
        dest_path.mkdir(parents = True)

    # append filename w/out date info to destination path
    dest_path = dest_path / name_tokens[-1]

    shutil.copy(src_path, dest_path)
    return

# this script just takes in a file name as a command line argument, then publishes it
def main():
    if len(sys.argv) != 2:
        print("file not specified")
        return
    
    if publish(sys.argv[1]) == ERROR:
        print("could not publish file:", sys.argv[1])

    return

if __name__ == "__main__":
    main()
