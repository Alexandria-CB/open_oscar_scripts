#!/usr/bin/env python3

import requests
import sys
from getpass import getpass
import json
import os

DEFAULT_CONFIG_FILE = os.path.join(os.path.split(__file__)[0], "open_oscar.json")

with open(DEFAULT_CONFIG_FILE, 'r') as cfg_file:
    cfg = json.load(cfg_file)

username = input("Enter a username: ")
password = getpass("Enter a password: ")

if password != getpass("Enter it again: "):
    print("Passwords don't match.", file=sys.stderr)
    exit(-1)

url = f"http://{cfg['hostname']}:{cfg['port']}/user"
    
body = {
    "screen_name": username,
    "password": password
}

print(requests.post(url, json=body).text)
