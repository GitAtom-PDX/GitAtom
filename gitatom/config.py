import yaml

# Add "import config" to any file where you need to access config options.
# Access the options using the names defined in config.yaml:
#       ex.
#           options = config.load_into_dict()
#           blog_title = options["feed_title"]

def generate_default():
        feed_id = 'a-feed-id'
        feed_title = 'yet another blog'
        author = 'Author'
        publish_directory = './site'

        yaml_dict = {
                    'feed_id' : feed_id, \
                    'feed_title' : feed_title, \
                    'author' : author, \
                    'publish_directory' : publish_directory
                    }

        with open('config.yaml', 'w') as f:
            yaml.dump(yaml_dict, f)


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
