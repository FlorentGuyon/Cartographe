# -*- coding: utf-8 -*-

# Lead to the configuration file of the application from the location of this file
from . import logger


CONFIG_PATH = "./config/config.txt"
CONFIG = {}


def load_config():
    """Read the configuration file"""
    global CONFIG
    with open(CONFIG_PATH, 'r') as file:

        for line in file:
            if line == '\n':
                continue
            elif line[0] == "#":
                continue
            else:
                key, value = line.split('=')
                key = key.strip()

                if ',' in value:
                    value = value.split(',')
                    value = list(map(lambda item: item.strip(), value))
                else:
                    value = value.strip()

                if value in ['', '\n']:
                    value = None

                CONFIG[key] = value


def get(key):
    """Return the value corresponding to the given key"""
    if key in CONFIG.keys():
        return CONFIG[key]
    else:
        logger.log.error(f"The key {key} does not exist in the configuration file, or it is not set properly. Please, check the configuration file ({CONFIG_PATH}) and make sure that there is the following line: '{key} = ...'.")
        return None
