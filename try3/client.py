#!/usr/bin/env python3

import socket
import wave
import configparser
import math
import time


class ClientSender:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("settings.conf")
        self.port = int(config["DEFAULT"]["Port"])
        self.buffer_size = int((2**math.log(int(config["DEFAULT"]["WaitingTime"])/1000.0 *
                                            int(config["DEFAULT"]["FrameRate"]), 2)))
        self.start_buffer_size = int(config["DEFAULT"]["BufferSize"])

        self.waiting_time = int(config["DEFAULT"]["WaitingTime"])/1000.0
        self.client = 0

    def connect(self):
        # connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("192.168.178.200", self.port))

        # tell the server we are a sender
        self.client.sendall(b"sender")
        # tell the server the buffer size
        self.client.sendall(str(self.buffer_size).encode())
        # wait for the ok from the server
        self.client.recv(self.start_buffer_size)

    def send(self, message):
        self.client.sendall(message)

    def message_loop(self):
        while True:
            f = wave.open("../test.wav", "rb")
            for i in range(1):
                buffer = bytearray(f.readframes(int(self.buffer_size)))
                self.send(buffer)
                time.sleep(self.waiting_time)
            f.close()

    def close(self):
        self.client.close()

# Main function
# Initialize a new instance of the client sender module
# and connect to the server.
# Then start the message loop (send parts of the file to the server)
# until Ctrl-C is hit.
if __name__ == "__main__":

    client = ClientSender()
    client.connect()

    try:
        client.message_loop()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()