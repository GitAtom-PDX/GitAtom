import sys
import shutil
from pathlib import Path

TARGET_DIRECTORY = "./site/posts/"
ERROR = -1

def publish(path_to_src):
    src_path = Path(path_to_src)
    if not src_path.exists():
        return ERROR

    src_filename = src_path.name
    name_tokens = src_filename.split("-")

    dest_path = Path(TARGET_DIRECTORY)
    for i in range(len(name_tokens) - 1):
        dest_path = dest_path / name_tokens[i]

    if not dest_path.exists():
        dest_path.mkdir(parents = True)

    dest_path = dest_path / name_tokens[-1]

    shutil.copy(src_path, dest_path)
    return

def main():
    if len(sys.argv) != 2:
        print("file not specified")
        return
    
    if publish(sys.argv[1]) == ERROR:
        print("could not publish file:", sys.argv[1])

    return

if __name__ == "__main__":
    main()
