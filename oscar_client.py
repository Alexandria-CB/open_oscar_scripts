#!/usr/bin/env python3

from socket import *
from ctypes import *
import struct

class OscarClient(object):
    def __init__(self):
        self.connected = False

    @staticmethod
    def flap_wrap(channel: c_byte, sequence: c_uint16, data: bytes) -> bytes:
        data_size = len(data)
        return struct.pack(f"!BBHH{data_size}s", 0x2A, channel.value, sequence.value, c_uint16(data_size).value, data)
    
    @staticmethod
    def snac_wrap(family: c_uint16, family_subtype: c_uint16, flags: c_uint16, request_id: c_uint32, data: bytes) -> bytes:
        return struct.pack(f"!HHHL{len(data)}s", family.value, family_subtype.value, flags.value, data)
    
    @staticmethod
    def tlv_wrap(type: c_uint16, data: bytes) -> bytes:
        data_size = len(data)
        return struct.pack(f"HH{data_size}s", type.value, c_uint16(data_size).value, data)