# -*- coding: utf-8 -*-

import json
from types import SimpleNamespace

# Lead to the configuration file of the application from the location of this file
CONFIG_PATH = ".\\config\\config.json"
config = {}


def load_config():
    """Import the configuration file as a global object"""
    global config
    with open(CONFIG_PATH, 'r') as config_file:
        config = json.load(
            config_file, object_hook=lambda d: SimpleNamespace(**d))


def get_config():
    if config == {}:
        load_config()
        print("Configuration loaded.")
    return config
