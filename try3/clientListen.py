#!/usr/bin/env python
import socket
import alsaaudio
import math
import time
from threading import Thread
import select
import sys
from clientBase import ClientBase


DEBUG = False


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


class ClientListener (ClientBase):
    def __init__(self):
        ClientBase.__init__(self)
        self.device = 0

    def connect(self):
        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        # Tell the server we are a receiver
        self.client.sendall(b"receiver")

        # Get data from Server
        self.read_values_from_server()


        # Set the audio device
        self.device = alsaaudio.PCM(card="default")
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(self.frame_rate)
        self.device.setperiodsize(int(self.buffer_size/4))



def call(buffers):
    # TODO: play the right buffer to the right time...
    if len(buffers) > 0:
        data = buffers.pop(0)
        client.device.write(bytes(data))


def next(buffers):
    buffers.pop(0)


if __name__ == "__main__":

    client = ClientListener()
    client.connect()
    buffers = list()
    thread = UpdateThread(lambda: call(buffers), lambda: next(buffers), client.waiting_time, 0.1)

    print("[Client] Started.")

    try:
        thread.start()
        while True:
            data = client.recv_exact()
            if data:
                buffers.append(data)
            else:
                print("[Client] No new data. Aborting!")
                break
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        thread.stopped = True

        #client.close()