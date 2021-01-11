from gitatom import build
from sys import argv

# insert definitions and/or `from gitatom import other-modules`

def atomify(filename):
    print(f"calling atomify on {filename}")
    return "xml"

def render(filename):
    print(f"calling render on {filename}")
    return "html"

def publish(filename):
    print(f"calling publish on {filename}")
    return True

def update(filename):
    xml = atomify(filename)
    if xml == "xml": 
        html = render(filename)
        if html == "html": 
            publish(filename)

def usage():
    exit("Usage: python3 -m gitatom [command] (filename)")

if __name__ == '__main__':
    if len(argv) > 1:
        command = argv[1]
        if command == 'build': build.build_it('./site')
        elif len(argv) > 2:
            filename = argv[2]
            if command == 'atomify': atomify(filename)
            elif command == 'render': render(filename)
            elif command == 'publish': publish(filename)
            elif command == 'update': update(filename)
            else: usage()
        else: usage()
    else: usage()
