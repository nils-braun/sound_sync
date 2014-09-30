#!/usr/bin/env python
import socket
import ConfigParser as configparser
import alsaaudio
import math
import time
from threading import Thread
import select, sys


DEBUG = True

class UpdateThread(Thread):

    def __init__(self, call, next, waiting_time, delta):
        self.stopped = False
        self.call = call
        self.next = next
        self.delta = delta
        self.waiting_time = waiting_time

        if DEBUG:
            self._dev = 0.0
            self._counter = 0

        # Call the super constructor
        Thread.__init__(self)

    def run(self):
        while not self.stopped:
            # in ms
            time_stamp = time.time() * 1000
            #print(int(time_stamp) % self.waiting_time)
            if int(time_stamp + self.delta) % self.waiting_time == 0:

                self.call()
                if int(time_stamp + self.delta) % self.waiting_time == 0:
                    time.sleep(1/1000.0)

                if DEBUG:
                    deviation = time_stamp - int(time_stamp / self.waiting_time) * self.waiting_time
                    if deviation > 1:
                        deviation -= self.waiting_time
                    self._dev += deviation
                    print(deviation)

                    self._counter += 1

                    if self._counter == 10:
                        print(self._dev/10.0)
                        self._dev = 0
                        self._counter = 0

            i, _, _ = select.select([sys.stdin], [], [], 1/10000.0)
            for s in i:
                if s == sys.stdin:
                    test = sys.stdin.readline()
                    if test == "n\n":
                        print("next")
                        self.next()

    def start(self):
        Thread.start(self)


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
            self.waiting_time = int(config["DEFAULT"]["WaitingTime"])
            self.framerate = int(config["DEFAULT"]["FrameRate"])
        except AttributeError:
            self.port = int(config.get("DEFAULT", "Port"))
            self.buffer_size = int(4*(2**math.log(int(config.get("DEFAULT", "WaitingTime"))/1000.0 *
                                                  int(config.get("DEFAULT", "FrameRate")), 2)))
            self.waiting_time = int(config.get("DEFAULT", "WaitingTime"))
            self.framerate = int(config.get("DEFAULT", "FrameRate"))

    # TODO: get buffer_size and frame_rate from server!
    def connect(self):
        self.device = alsaaudio.PCM(card="default")
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(self.framerate)
        self.device.setperiodsize(int(self.buffer_size/4))

        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("192.168.178.200", self.port))

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


def call(buffers):
    #pass
    data = buffers.pop(0)
    client.device.write(bytes(data))


def next(buffers):
    buffers.pop(0)


if __name__ == "__main__":

    client = ClientListener()
    client.connect()
    buffers = list()
    thread = UpdateThread(lambda: call(buffers), lambda: next(buffers), client.waiting_time, 0.1)

    try:
        thread.start()
        while True:
            data = client.recv_exact()
            if data:
                buffers.append(data)
            else:
                print("Aborting!")
                break
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        thread.stopped = True

        #client.close()