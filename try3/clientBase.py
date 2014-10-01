#!/usr/bin/env python3
try: import configparser
except ImportError:
    import ConfigParser as configparser
import math


class ClientBase:
    def __init__(self):
        self.client = 0
        self.waiting_time = 0
        self.frame_rate = 0
        self.buffer_size = 0
        self.start_buffer_size = 1024
        self.server_ip = "192.168.178.200"

        self.config = configparser.ConfigParser()
        self.config.read("settings.conf")
        self.port = 50007

    def read_values_from_file(self):
        # in ms
        self.waiting_time = int(self.config["DEFAULT"]["WaitingTime"])
        # in Hz
        self.frame_rate = int(self.config["DEFAULT"]["FrameRate"])

    def read_values_from_server(self):
        # First is frame rate in Hz
        self.frame_rate = int(self.recv())
        self.send_ok()

        # Then waiting_time in ms
        self.waiting_time = int(self.recv())
        self.send_ok()

        # set the buffer size with the new data
        self.set_buffer_size()

    def send_values_to_server(self):
        # tell the server the frame rate in Hz
        self.send(str(self.frame_rate).encode())
        # get ok
        self.recv_ok()
        # tell the server the waiting time in ms
        self.send(str(self.waiting_time).encode())
        # get ok
        self.recv_ok()

        self.set_buffer_size()

    def set_buffer_size(self):
        # set the buffer_size correctly
        self.buffer_size = int(4*(2**math.log(self.waiting_time / 1000.0 * self.frame_rate, 2)))

    def recv_exact(self):
        pointer = 0
        tmp_buffer = bytearray(self.buffer_size)
        while pointer < self.buffer_size:
            data = self.client.recv(self.buffer_size - pointer)
            if not data:
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def connect(self):
        pass

    def close(self):
        if self.client != 0:
            self.client.close()

    def send(self, message):
        if self.client != 0:
            self.client.sendall(message)

    def send_ok(self):
        self.send("ok")

    def recv(self, buffer_size=None):
        if buffer_size is None:
            buffer_size = self.start_buffer_size
        if self.client != 0:
            return self.client.recv(buffer_size)

    def recv_ok(self):
        self.recv(self.start_buffer_size)