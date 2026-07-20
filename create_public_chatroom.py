#!/usr/bin/env python3

from requests import post
from load_config import load_config
from prompts import prompt_for_chatroom_name
from utils import *

def create_public_chatroom(cfg, roomname):
    url = standard_url(cfg, "chat", "room", "public")

    body = {
        "name": roomname
    }

    return post(url, json=body).text

if __name__ == "__main__":
    try:
        cfg = load_config()
        roomname = prompt_for_chatroom_name()
        print(create_public_chatroom(cfg, roomname))
    except Exception as ex:
        print(ex)
        exit(-1)
