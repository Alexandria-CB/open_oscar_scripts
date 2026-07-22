#!/usr/bin/env python3

import json
import os

DEFAULT_CONFIG_FILE = os.path.join(os.path.split(__file__)[0], "open_oscar.json")

def load_config(filename=DEFAULT_CONFIG_FILE):
    with open(filename, 'r') as cfg_file:
        return json.load(cfg_file)