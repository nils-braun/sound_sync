#!/usr/bin/env python3

import socket
import wave
import configparser
import math


if __name__ == "__main__":

    config = configparser.ConfigParser()
    config.read("settings.conf")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", int(config["DEFAULT"]["Port"])))

    buffer_size = 2**int(math.log(int(config["DEFAULT"]["WaitingTime"])/1000.0 *
                                  int(config["DEFAULT"]["FrameRate"]), 2))

    client.sendall(b"receiver")

    data = client.recv(buffer_size)
    print(data)
    client.close()