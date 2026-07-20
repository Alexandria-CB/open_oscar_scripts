#!/usr/bin/env python3

from requests import post

from load_config import load_config
from prompts import prompt_for_credentials
from utils import *

def create_user(cfg, username, password):
    url = standard_url(cfg, "user")
        
    body = {
        "screen_name": username,
        "password": password
    }

    return post(url, json=body).text

if __name__ == "__main__":
    try:
        cfg = load_config()
        username, password = prompt_for_credentials()
        print(create_user(cfg, username, password))
    except Exception as ex:
        print(ex)
        exit(-1)
