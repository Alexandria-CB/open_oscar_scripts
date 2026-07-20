#!/usr/bin/env python

from requests import get
from load_config import load_config
from utils import *

def list_users(cfg):
    url = standard_url(cfg, "users")
    return get(url).json

if __name__ == "__main__":
    cfg = load_config()
    for user in list_users(cfg):
        print(user)