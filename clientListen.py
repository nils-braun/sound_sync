#!/usr/bin/env python
# coding=utf-8
"""
This module implements the listener client.
"""

from __future__ import print_function

FULL_BUFFER_SIZE = 10
STOPPED = False

__author__ = "nilpferd1991"
__version__ = "2.0.0"

import socket
import alsaaudio
import time
from threading import Thread, Timer
from clientBase import ClientBase


class PlayThread(Thread):
    """
    A class to handle the thread to play the audio from the buffers of the client.
    When running waits for the correct time (time + delta) % waiting_time == 0 and starts playing the correct buffer.
    After that, move all incoming buffers to the sound queue.
    """

    def __init__(self, client):
        self.delta = 0.1        # The delta in ms to correct for wrong timing. Not very useful at the moment?
        self.client = client    # The listener we will use

        Thread.__init__(self)

    def run(self):
        """
        This function is called every time the thread is executed. It waits for the correct time and starts playing.
        If playing is started, the buffers from the incoming data are automatically moved to the sound device.
        The waiting for the "correct" start time is crucial. We check every beginning of the cycle
        (when time + delta % waiting_time == 0) if the number of saved frames is bigger than 10 (TODO: arbitrary)
        Then we calculate the number of cycles between the beginning of the client (the server
        told us this time) and the time now and start the corresponding frame minus 5 (TODO: arbitrary).
        """

        while not STOPPED:

            # no audio playing now:
            if not self.client.started:
                # calculate the delta-corrected current time in ms.
                time_stamp = int(time.time() * 1000 + self.delta)
                # if we have filled the buffer list long enough and the time is correct:
                if len(self.client.buffers) > FULL_BUFFER_SIZE and time_stamp % self.client.waiting_time == 0:
                    # calculate the index of the buffer that should come next by using the start_time from the server
                    real_index = int((time_stamp - self.client.start_time*1000.0)/self.client.waiting_time)
                    # delete all packages before this correct time minus 5 packages
                    del self.client.buffers[:real_index - self.client.start_counter - 5]
                    # start the audio playing
                    for _ in xrange(len(self.client.buffers) - 4):
                        self.client.device.write(bytes(self.client.buffers.pop(0)))
                    self.client.started = True
                    print("..started")
                    return

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
        global STOPPED
        STOPPED = True


class ClientListener (ClientBase):
    """
    A class to handle the listener client. Connects to the server, receives the correct values for frame rate and
    waiting time and starts receiving audio buffers.
    """
    def __init__(self):
        ClientBase.__init__(self)
        self.device = 0         # The PCM device we play to
        self.buffers = list()   # The buffers we fill in the beginning
        self.running = False    # Set to false to stop running
        self.started = False    # Fill in some buffers before running, then start the movement of buffers

    def connect(self):
        """
        Connect to the server and get frame rate and waiting time. Then start the playing device.
        """
        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        # Tell the server we are a receiver
        self.client.sendall(b"receiver")
        self.recv_ok()

        # Get data from Server
        try:
            self.read_values_from_server()
        except ValueError:
            print("There is no client sending data to the server. Aborting.")
            exit()

        # Set the audio device
        self.device = alsaaudio.PCM(card="default", type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NONBLOCK)
        self.device.setchannels(2)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.device.setrate(self.frame_rate)
        self.device.setperiodsize(int(self.buffer_size/4.0))

        self.running = True

    def set_buffer_size(self):
        """
        Now we set the buffer_size to buffer_size*4 - so it corresponds to the real buffer size.
        Attention: For all PCM devices we will now need buffer_size/4.
        :rtype: None
        """
        ClientBase.set_buffer_size(self)
        self.buffer_size *= 4

    def message_loop(self):
        """
        The message loop where the data and the corresponding index (in the list on the server)
        is received from the server. Play a new buffer only if a new buffer is coming fom the server!
        """
        while self.running:
            # Receive the index of the buffer in the server list
            index = self.client.recv(self.start_buffer_size)
            self.send_ok()
            # Receive the data
            data = self.recv_exact()
            if data:
                # we are in pre-filling mode
                if not self.started:
                    self.buffers.append(data)
                    # "Calibrate" to the start_point to have the same list with the same index as the server
                    # To calculate which package is needed to which time, just use int(T/waiting_time) - start_counter
                    # were T is time - start_time.
                    if self.start_counter == 0:
                        self.start_counter = int(index)
                # play audio
                else:
                    self.buffers.append(data)
                    # only play audio if there are buffers in the buffer list
                    if len(self.buffers) > 0:
                        data = self.buffers.pop(0)
                        # the write() gives 0, if the sound queue is full. We have to add this buffer the next time
                        if self.device.write(bytes(data)) == 0:
                            self.buffers.insert(0, data)
            else:
                # This should not happen. The server is dead.
                print("[Client] No new data. Aborting!")
                self.running = False
                break


def reset_thread(client):
    """
    (Re)starts the thread to catch the first buffers from the server. Is executed every 10 minutes and in the beginning.
    :param client: the client to handle
    :return: None
    """
    print("Starting (new)..")
    client.start_counter = 0
    client.started = False
    client.buffers = list()
    thread_tmp = PlayThread(client)
    thread_tmp.start()
    timer = Timer(600.0, reset_thread, args=[client])
    timer.daemon = True
    timer.start()


def main():
    """
    Main function
    Initialize a new instance of the client listener module
    and connect to the server.
    Then start the message loop (receive the data from the server).
    Also initialize a new thread to play the audio. Start waiting for the correct time.
    Repeat until Ctrl-C is hit and the sound buffer is empty.
    """

    try:
        client = ClientListener()
        client.connect()

        reset_thread(client)

        client.message_loop()
    except KeyboardInterrupt:
        print("stopping")
        if client != 0:
            client.running = False
            client.close()

        global STOPPED
        STOPPED = True

        exit()

if __name__ == "__main__":
    main()
