import sys
import yaml

# Location of site HTML files.
publish_directory = 'site'

# Add "import config" to any file where you need to access config options.
# Access the options using the names defined in config.yaml:
#       ex.
#           options = config.load_into_dict()
#           blog_title = options["feed_title"]

def load_into_dict():
    try:
        config_file = open("./config.yaml", "r")
    except FileNotFoundError:
        config_file = open("./content/config.yaml", "r")
    except FileNotFoundError:
        print("./content/config.yaml: not found, giving up.", file=sys.stderr)
        exit(1)

    options = yaml.load(config_file, yaml.FullLoader)
    config_file.close()
    options['publish_directory'] = publish_directory
    return options
