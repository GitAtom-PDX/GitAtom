import yaml

# Add "import config" to any file where you need to access config options.
# Access the options using the names defined in config.yaml:
#       ex.
#           blog_title = config.options["feed_title"]

options = {}

def load():
    try:
        config_file = open("config.yaml", "r")

    except FileNotFoundError:
        yaml_dict = {
            'feed_id' : '', \
            'feed_title' : '', \
            'author' : '', \
            'publish_directory' : '' 
            }

        with open('config.yaml', 'w') as f:
            yaml.dump(yaml_dict, f)

        config_file = open("config.yaml", "r")

    global options
    options = yaml.load(config_file, yaml.FullLoader)
    config_file.close()


# this is called when config is imported
load()
