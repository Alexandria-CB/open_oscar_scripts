#!/usr/bin/env python3

from getpass import getpass

AFFIRMITIVE = ["y", "yes"]

def prompt_for_credentials():
    username = input("Enter a username: ")
    password = getpass("Enter a password: ")

    if password != getpass("Enter it again: "):
        raise ValueError("Passwords don't match.")
    
    return (username, password)

def prompt_for_username(confirm=True):
    global AFFIRMITIVE
    username = input("Enter a username: ")
    if confirm:
        confirmation = input(f"Is {username} correct? [Y/n]: ")
        if confirmation.lower() not in AFFIRMITIVE:
            raise ValueError("Username incorrect.")
    return username