#!/usr/bin/env python
import socket
import ConfigParser as configparser
import alsaaudio
import math
import wave


class ClientListener:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("settings.conf")

        self.client = 0
        self.device = 0

        try:
            self.port = int(config["DEFAULT"]["Port"])
            self.buffer_size = int(4*(2**math.log(int(config["DEFAULT"]["WaitingTime"])/1000.0 *
                                                int(config["DEFAULT"]["FrameRate"]), 2)))
            self.framerate = int(config["DEFAULT"]["FrameRate"])
        except AttributeError:
            self.port = int(config.get("DEFAULT", "Port"))
            self.buffer_size = int(4*(2**math.log(int(config.get("DEFAULT", "WaitingTime"))/1000.0 *
                                                int(config.get("DEFAULT", "FrameRate")), 2)))
            self.framerate = int(config.get("DEFAULT", "FrameRate"))


    def connect(self):
        self.device = alsaaudio.PCM(card="default")
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(self.framerate)
        self.device.setperiodsize(int(self.buffer_size/4))

        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", self.port))

        # Tell the server we are a receiver
        self.client.sendall(b"receiver")

    def recv_exact(self):
        pointer = 0
        tmp_buffer = bytearray(self.buffer_size)
        while pointer < self.buffer_size:
            data = self.client.recv(self.buffer_size - pointer)
            if not data:
                print("No data!")
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def close(self):
        self.client.close()


if __name__ == "__main__":

    client = ClientListener()
    client.connect()

    try:
        while True:
            data = client.recv_exact()
            #data = bytearray(f.readframes(int(client.buffer_size)))
            client.device.write(bytes(data))
    except KeyboardInterrupt:
        pass
    finally:
        client.close()