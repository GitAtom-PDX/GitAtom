from build import Builder
from sys import argv


def build_it():
    # scan 'site/' for html files 
    site = Builder('site/')
    site.build_blog()
    site.build_index()

if len(argv) == 2:
    if argv[1] == 'md':
        print("calling a module: md -> html")
    elif argv[1] == 'atomify':
        print("calling a module: html -> atomify")
    elif argv[1] == 'preview':
        print("calling a module: Atom -> preview html")
    elif argv[1] == 'publish':
        print("calling a module: Atom -> publish html")
    elif argv[1] == 'build':
        build_it()
else:
    print("correct invocation: gitatom (module)")
    print("modules: [md, atomify, preview, publish, build]")
