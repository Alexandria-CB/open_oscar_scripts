#!/usr/bin/env python3

from requests import get
from load_config import load_config
from utils import *

def list_users(cfg):
    url = standard_url(cfg, "user")
    return get(url).json()

if __name__ == "__main__":
    cfg = load_config()
    for user in list_users(cfg):
        print(user)