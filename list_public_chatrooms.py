#!/usr/bin/env python3

from requests import get
from load_config import load_config
from utils import *

def list_public_chatrooms(cfg):
    url = standard_url(cfg, "chat", "room", "public")
    return get(url).json

if __name__ == "__main__":
    try:
        cfg = load_config()
        for room in list_public_chatrooms(cfg):
            print(room)
    except Exception as ex:
        print(ex)
        exit(-1)