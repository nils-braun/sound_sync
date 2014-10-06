#!/usr/bin/env python
# coding=utf-8
"""
This module implements the listener client.
"""

__author__ = "nilpferd1991"
__version__ = "1.0.0"

import socket
import alsaaudio
import time
from threading import Thread
import select
import sys
from clientBase import ClientBase


class PlayThread(Thread):
    """
    A class to handle the thread to play the audio from the buffers of the client.
    When running waits for the correct time (time + delta) % waiting_time == 0 and plays one buffer.
    Skips one buffer if it is "too late".
    """

    def _call(self):
        self.client.device.pause(0)

    def _next(self):
        # The function to call when we skip a buffer
        if len(self.client.buffers) > 0:
            self.client.buffers.pop(0)

    def __init__(self, client):
        self.stopped = False
        self.delta = 0.1
        self.counter = 0
        self.client = client
        self.started = False    # Fill in some buffers before running

        Thread.__init__(self)

    def run(self):
        """
        This function is called everytime the thread is executed. It waits for the correct time and starts playing.
        If playing is started, the buffers from the incoming data are automatically moved to the sound device.
        The waiting for the "correct" start time is crucial. We check every cycle
        (when time + delta % waiting_time == 0) if the number of saved frames is bigger than 10 (arbitrary)
        Then we calculate the number of cycles between the beginning of the client (the server
        told us this time) and now and start the corresponding frame minus 5 (arbitrary).
        """

        while not self.stopped:

            if not self.started:
                time_stamp = int(time.time() * 1000 + self.delta)
                if len(self.client.buffers) > 10 and time_stamp % self.client.waiting_time == 0:
                    real_index = int((time_stamp - self.client.start_time*1000.0)/self.client.waiting_time)
                    del self.client.buffers[:real_index - self.client.start_counter - 5]
                    self.started = True

            else:
                while len(self.client.buffers) > 0:
                    data = self.client.buffers.pop(0)
                    if self.client.device.write(bytes(data)) == 0:
                        self.client.buffers.insert(0, data)
                        break

            time.sleep(1/1000.0)

    def start(self):
        """
        Start the thread.
        """
        Thread.start(self)

    def stop(self):
        """
        Stop the thread.
        """
        self.stopped = True


class ClientListener (ClientBase):
    """
    A class to handle the listener client. Connects to the server, receives the correct values for frame rate and
    waiting time and starts receiving audio buffers.
    """
    def __init__(self):
        ClientBase.__init__(self)
        self.device = 0
        self.buffers = list()
        self.running = False

    def connect(self):
        """
        Connect to the server and get frame rate and waiting time. Then start the playing device.
        """
        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        # Tell the server we are a receiver
        self.client.sendall(b"receiver")

        # Get data from Server
        self.read_values_from_server()

        # Set the audio device
        self.device = alsaaudio.PCM(card="default", type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NONBLOCK)
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(self.frame_rate)
        self.device.setperiodsize(int(self.buffer_size/4.0))

        self.running = True

    def set_buffer_size(self):
        ClientBase.set_buffer_size(self)
        self.buffer_size *= 4

    def message_loop(self):
        """
        The message loop where the data is received from the server. Blocking!
        """
        while self.running:
            index = self.client.recv(self.start_buffer_size)
            self.send_ok()
            data = self.recv_exact()
            if data:
                self.buffers.append(data)
                if self.start_counter == 0:
                    self.start_counter = int(index)
            else:
                print("[Client] No new data. Aborting!")
                self.running = False
                break


def main():
    """
    Main function
    Initialize a new instance of the client listener module
    and connect to the server.
    Then start the message loop (receive the data from the server).
    Also initialize a new thread to play the audio. Start waiting for the correct time.
    Repeat until Ctrl-C is hit and the sound buffer is empty.
    """
    client = ClientListener()
    client.connect()

    thread = PlayThread(client)

    try:
        thread.start()
        client.message_loop()
    except KeyboardInterrupt:
        # ATTENTION: Stops only if the sound buffer is empty!
        client.running = False
        client.close()
        thread.stop()


if __name__ == "__main__":
    main()
