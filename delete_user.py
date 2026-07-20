#!/usr/bin/env python3

from requests import delete
from load_config import load_config
from prompts import prompt_for_username
from utils import *

def delete_user(cfg, username):
    url = standard_url(cfg, "user")

    body = {
        "screen_name": username
    }

    return delete(url, json=body).text

if __name__ == "__main__":
    try:
        cfg = load_config()
        username = prompt_for_username()
        print(delete_user(cfg, username))
    except Exception as ex:
        print(ex)
        exit(-1)