#!/usr/bin/env python3

import socket
import wave
import configparser
import math
import time

if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("settings.conf")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", int(config["DEFAULT"]["Port"])))

    buffer_size = 2**int(math.log(int(config["DEFAULT"]["WaitingTime"])/1000.0 *
                                  int(config["DEFAULT"]["FrameRate"]), 2))

    client.sendall(b"sender")
    client.sendall(str(buffer_size).encode())

    client.recv(int(config["DEFAULT"]["BufferSize"]))

    # Faktor 4???
    try:
        while True:
            f = wave.open("../test.wav", "rb")
            for i in range(1000):
                data = f.readframes(int(buffer_size/4))
                client.sendall(data)

                time.sleep(int(config["DEFAULT"]["WaitingTime"])/1000.0)

            f.close()
    finally:
        client.close()