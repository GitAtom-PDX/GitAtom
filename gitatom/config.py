import yaml

options = {}

def load():
    config_file = open("gitatom/config.yaml", "r")
    global options
    options = yaml.load(config_file, yaml.FullLoader)
    config_file.close()

load()
