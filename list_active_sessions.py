#!/usr/bin/env python3

from requests import get
from load_config import load_config
from utils import *

def list_active_sessions(cfg):
    url = standard_url(cfg, "session")
    return get(url).json()

if __name__ == "__main__":
    try:
        cfg = load_config()
        for session in list_active_sessions(cfg):
            print(session)
    except Exception as ex:
        print(ex)
        exit(-1)
