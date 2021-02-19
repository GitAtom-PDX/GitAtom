import yaml

# Add "import config" to any file where you need to access config options.
# Access the options using the names defined in config.yaml:
#       ex.
#           options = config.load_into_dict()
#           blog_title = options["feed_title"]

def generate_default():
        yaml_dict = {
            'feed_id' : 'feed id',
            'feed_title' : 'feed title',
            'author' : 'author',
            'publish_directory' : 'site',
            'repo_path' : 'path to bare git repository',
            'work_path' : 'path to work tree',
            'host' : 'host ip address',
            'port' : 'port number',
            'username' : 'username',
            'keypath' : 'path to ssh key',
            'deploy' : False
        }

        with open('config.yaml', 'w') as f:
            yaml.dump(yaml_dict, f, sort_keys=False)


def load_into_dict():
    try:
        config_file = open("config.yaml", "r")

    except FileNotFoundError:
        print("config file not found, generating default config \"config.yaml\"")
        print("this file needs to be filled out!")
        generate_default()
        config_file = open("config.yaml", "r")

    options = yaml.load(config_file, yaml.FullLoader)
    config_file.close()
    return options
