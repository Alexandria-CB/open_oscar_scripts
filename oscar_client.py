#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from ctypes import c_byte, c_uint16, c_uint32
import struct
from threading import Thread, Lock
from argparse import Namespace
from typing import Type
from time import sleep

class OscarClient(object):

    def __init__(self, buffer_size=1024):
        self.buffer_size = buffer_size
        
        self.exit = Namespace()
        self.exit.running = False
        self.exit.lock = Lock()
        
        self.inet = Namespace()
        self.inet.socket = None
        self.inet.connected = False
        self.inet.lock = Lock()

        self.input = Namespace()
        self.input.buffer = ""
        self.input.lock = Lock()
        self.input.thread = Thread(target=OscarClient.read_socket, args=[self])

        self.output = Namespace()
        self.output.buffer = ""
        self.output.lock = Lock()
        self.output.thread = Thread(target=OscarClient.write_socket, args=[self])

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

    def connect(self, host, port):
        with self.inet.lock:
            if not self.isConnected():
                self.inet.socket = socket(AF_INET, SOCK_STREAM)
                self.inet.socket.connect((host, port))
                self.inet.socket.setblocking(False)
                self.inet.connected = True

    def isConnected(self): # Should only be called after acquiring the inet lock
        return self.inet.socket != None and self.inet.connected

    def disconnect(self):
        with self.inet.lock:
            if self.isConnected():
                self.inet.socket.shutdown(SHUT_RDWR)
                self.inet.socket.close()
                self.inet.socket = None
                self.inet.connected = False
    
    def running(self):
        with self.exit.lock:
            return self.exit.running

    def stop(self):
        with self.exit.lock():
            self.exit.running = False
        self.input.thread.wait()
        self.output.thread.wait()

    def start(self):
        with self.inet.lock:
            if self.isConnected():
                with self.exit.lock():
                    self.exit.running = True
                self.input.thread.run()
                self.output.thread.run()

    def read_socket(self):
        while self.running():
            with self.inet.lock:
                with self.input.lock:
                    self.input.buffer += self.inet.socket.recv(self.buffer_size)
            sleep(0)
        
    def write_socket(self):
        while self.running():
            with self.inet.lock:
                with self.output.lock:
                    n_sent = self.inet.socket.send(self.output.buffer)
                    self.output.buffer = self.output.buffer[:n_sent]
            sleep(0)

    def read_n_bytes(self, n: int):
        data = b""
        while len(data) != n:
            with self.input.lock:
                data = self.input.buffer[:n]
            sleep(0)
        
        with self.input.lock:
            self.input.buffer = self.input.buffer[n:]
        
        return data
    
    def write_data(self, data: bytes):
        with self.output.lock:
            self.output.buffer += data

    def __call__(self, host: str, port: int):
        self.connect(host, port)
        self.start()

        # DO STUFF HERE

        self.stop()
        self.disconnect()