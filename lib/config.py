# -*- coding: utf-8 -*-

from sys import argv
from os import path

from . import logger


CONFIG = {"prog_path": path.abspath(path.dirname(argv[0]))}


def load_config():
    """Read the configuration file"""
    global CONFIG
    with open(f'{CONFIG["prog_path"]}/config/config.txt', 'r') as file:

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
