#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR
from ctypes import c_byte, c_uint16, c_uint32
import struct
from threading import Thread, Lock
from argparse import Namespace
from typing import Type
from time import sleep
from select import select
from copy import copy
from enum import Enum

def socket_ready(sock: socket):
    readable, _, _ = select([sock], [], [], 0)
    return readable == sock

class OscarClient(object):

    class FLAP_Channel(Enum):
        LOGIN = 1
        SNAC = 2
        ERROR = 3
        DISCONNECT = 4
        KEEPALIVE = 5

    class FoodGroup(Enum):
        OSERVICE = 0x01
        LOCATE = 0x02
        BUDDY = 0x03
        ICBM = 0x04
        CHATNAV = 0x0D
        CHAT = 0x0E
        FEEDBACK = 0x13
        ICQ = 0x15

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
        self.input.buffer = b""
        self.input.lock = Lock()
        self.input.thread = Thread(target=OscarClient.read_socket, args=[self])

        self.output = Namespace()
        self.output.buffer = b""
        self.output.lock = Lock()
        self.output.thread = Thread(target=OscarClient.write_socket, args=[self])

    @staticmethod
    def flap_wrap(channel: c_byte, sequence: c_uint16, data: bytes) -> bytes:
        data_size = len(data)
        return struct.pack(f"!BBHH{data_size}s", 0x2A, channel.value, sequence.value, c_uint16(data_size).value, data)
    
    @staticmethod
    def snac_wrap(family: c_uint16, family_subtype: c_uint16, flags: c_uint16, request_id: c_uint32, data: bytes) -> bytes:
        return struct.pack(f"!HHHL{len(data)}s", family.value, family_subtype.value, flags.value, request_id.value, data)
    
    @staticmethod
    def tlv_wrap(type: c_uint16, data: bytes) -> bytes:
        data_size = len(data)
        return struct.pack(f"HH{data_size}s", type.value, c_uint16(data_size).value, data)

    def connect(self, host, port):
        with self.inet.lock:
            if not self.isConnected():
                self.inet.socket = socket(AF_INET, SOCK_STREAM)
                self.inet.socket.connect((host, int(port)))
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
        with self.exit.lock:
            self.exit.running = False
        self.input.thread.join()
        self.output.thread.join()

    def start(self):
        with self.inet.lock:
            if self.isConnected():
                with self.exit.lock:
                    self.exit.running = True
                self.input.thread.start()
                self.output.thread.start()

    def read_socket(self):
        while self.running():
            with self.inet.lock:
                with self.input.lock:
                    try:
                        self.input.buffer += self.inet.socket.recv(self.buffer_size)
                    except BlockingIOError:
                        pass
            sleep(0)
        
    def write_socket(self):
        while self.running():
            with self.inet.lock:
                with self.output.lock:
                    n_sent = self.inet.socket.send(self.output.buffer)
                    self.output.buffer = self.output.buffer[n_sent:]
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
    
    def read_data(self) -> bytes:
        with self.input.lock:
            data = self.input.buffer
            self.input.buffer = b""
            return data

    def write_data(self, data: bytes):
        with self.output.lock:
            self.output.buffer += data

    def read_flap_packet(self):
        # Parse header
        _, channel, sequence, data_size = struct.unpack("!BBHH", self.read_n_bytes(6))
        data = struct.unpack(f"!{data_size}", self.read_n_bytes(data_size))[0]
        if channel == self.FLAP_Channel.LOGIN:
            pass
        elif channel == self.FLAP_Channel.SNAC:
            foodgroup, type, flags, request_id, snac_data = struct.unpack(f"!HHHL{len(data) - 8}s", data)
        elif channel == self.FLAP_Channel.ERROR:
            pass
        elif channel == self.FLAP_Channel.DISCONNECT:
            pass
        else:
            raise ValueError(f"Unexpected FLAP Channel {channel} from packet {sequence}")

    def mainloop(self):
        self.start()
        while self.running():
            data = input("data: ").encode()
            if len(data) == 0:
                self.stop()
            self.write_data(data)
            new_data = self.read_data()
            print(new_data.decode())

    def bufferPeek(self):
        input = b""
        output = b""

        with self.input.lock:
            input = copy(self.input.buffer)
        
        with self.output.lock:
            output = copy(self.output.buffer)

        return (input, output)

    def __call__(self, host: str, port: int):
        self.connect(host, port)
        self.mainloop()
        self.disconnect()


if __name__ == "__main__":
    OC = OscarClient(1)
    OC('localhost', 5190)