#!/usr/bin/env python3

import socket
import wave
import math
import time
from clientBase import ClientBase


class ClientSender(ClientBase):
    def __init__(self):
        ClientBase.__init__(self)
        self.read_values_from_file()

    def connect(self):
        # connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        # tell the server we are a sender
        self.client.sendall(b"sender")
        self.recv()

        self.send_values_to_server()

    def message_loop(self):
        while True:
            f = wave.open("../test.wav", "rb")
            for i in range(200):
                buffer = bytearray(f.readframes(int(self.buffer_size/4.0)))
                self.send(buffer)
                time.sleep(self.waiting_time/1000.0)
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