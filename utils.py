#!/usr/bin/env python3

def standard_url(cfg, *args):
    return "/".join([f"http://{cfg['hostname']}:{cfg['port']}"] + list(args))