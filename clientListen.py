#!/usr/bin/env python
# coding=utf-8
"""
This module implements the listener client.
"""

from __future__ import print_function
from pcmHandler import PCMPlay
from listHandler import ClientBufferListHandler
import socket
import time
from threading import Thread, Timer
from clientBase import ClientBase
import xml.etree.ElementTree as ElementTree

__author__ = "nilpferd1991"
__version__ = "2.0.0"


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

    try:
        client.connect()
        handle_correct_start_time(client)
        client.message_loop()
    except KeyboardInterrupt:
        print("stopping")
        if client != 0:
            client.exit_message_loop()
            client.close()

        exit()


def handle_correct_start_time(client):
    thread_to_handle_correct_start_time = HandleCorrectStartTimeThread(client)
    thread_to_handle_correct_start_time.start()

    test_timer = Timer(60*10, handle_correct_start_time, args=[client])
    test_timer.daemon = True
    test_timer.start()


class HandleCorrectStartTimeThread(Thread):
    """
    A class to handle the thread to play the audio from the buffers of the client.
    When running waits for the correct time (time + delta) % waiting_time == 0 and starts playing the correct buffer.
    After that, move all incoming buffers to the sound queue.
    """

    def __init__(self, client):
        self.delta = 0.1        # The delta in ms to correct for wrong timing. Not very useful at the moment?
        assert isinstance(client, ClientListener)
        self.client = client

        Thread.__init__(self)

    def run(self):

        self.clear_audio_queue_and_reset_sound_buffer_list()

        while self.client.is_running and not self.client.is_audio_playing:
            time_stamp = int(time.time() * 1000 + self.delta)
            if self.is_correct_time_and_sound_buffer_is_full(time_stamp):
                self.set_current_playable_buffer_index(time_stamp)
                self.try_filling_audio_queue()

            time.sleep(1/1000.0)

    def clear_audio_queue_and_reset_sound_buffer_list(self):
        if self.client.static_sound_buffer_list.current_buffer_index != -1:
            time_until_audio_queue_is_empty = self.calculate_time_until_audio_queue_is_empty()

            self.client.static_sound_buffer_list.current_buffer_index = -1
            self.client.is_audio_playing = False

            time.sleep(time_until_audio_queue_is_empty / 1000.0)

    def set_current_playable_buffer_index(self, time_stamp):
        real_sound_buffer_index = int((time_stamp - self.client.start_time*1000.0) /
                                      ClientListener.clientInformation.waiting_time)
        current_buffer_index = real_sound_buffer_index - ClientListener.clientInformation.full_sound_buffer_size
        self.client.static_sound_buffer_list.current_buffer_index = current_buffer_index

    def try_filling_audio_queue(self):
        if ClientListener.static_sound_buffer_list.current_buffer_index + 5 < \
                ClientListener.static_sound_buffer_list.end_buffer_index:
            for _ in xrange(ClientListener.static_sound_buffer_list.end_buffer_index -
                    ClientListener.static_sound_buffer_list.current_buffer_index - 5):
                self.client.play_next_playable_buffer()
            self.client.is_audio_playing = True

    def calculate_time_until_audio_queue_is_empty(self):
        time_stamp = int(time.time() * 1000 + self.delta)
        real_sound_buffer_index = int((time_stamp - self.client.start_time * 1000.0) /
                                      ClientListener.clientInformation.waiting_time)
        current_buffer_index = real_sound_buffer_index - ClientListener.clientInformation.full_sound_buffer_size
        current_waiting_time = (self.client.static_sound_buffer_list.current_buffer_index -
                                current_buffer_index) * ClientListener.clientInformation.waiting_time
        return current_waiting_time

    def is_correct_time_and_sound_buffer_is_full(self, time_stamp):
        return len(self.client.static_sound_buffer_list.buffers) > \
               ClientListener.clientInformation.full_sound_buffer_size \
               and time_stamp % ClientListener.clientInformation.waiting_time == 0


class ClientListener (ClientBase, PCMPlay):
    """
    A class to handle the listener client. Connects to the server, receives the correct values for frame rate and
    waiting time and starts receiving audio buffers.
    """

    static_sound_buffer_list = ClientBufferListHandler()

    def __init__(self):
        self.is_running = False
        self.is_audio_playing = False
        self.is_closed = False
        ClientBase.__init__(self)
        PCMPlay.__init__(self)

    def message_loop(self):
        while self.is_running:
            self.handle_new_message_loop()

    def connect(self):
        self.connect_to_server()
        self.tell_server_receiver_identity()
        self.get_audio_information()
        self.initialize_pcm(ClientListener.clientInformation.frame_rate,
                            ClientListener.clientInformation.sound_buffer_size)

        self.is_running = True

    def connect_to_server(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ClientListener.addressInformation.server_ip, ClientListener.addressInformation.port))

    def tell_server_receiver_identity(self):
        element = ElementTree.Element("client", {"type": "receiver"})
        self.client.sendall(ElementTree.tostring(element))

    def get_audio_information(self):
        try:
            self.read_values_from_server()
        except ValueError:
            print("[Client] There is no client sending data to the server. Aborting.")
            self.is_running = False
            self.is_closed = True
            exit()

    def handle_new_message_loop(self):
        try:
            #new_sound_buffer_index = int(self.receive_index())
            new_sound_buffer_index_buffer = self.receive(8)
            new_sound_buffer_index = 0

            for i in range(8):
                new_sound_buffer_index = 256*new_sound_buffer_index + ord(new_sound_buffer_index_buffer[7 - i])

            new_sound_buffer = self.receive_buffer_with_exact_length()
            self.handle_new_sound_buffer(new_sound_buffer, new_sound_buffer_index)
        except (ValueError, IndexError):
            print("[Client] There are no buffers loaded into the server. Aborting.")
            self.is_running = False
            self.is_closed = True
            exit()

    def handle_new_sound_buffer(self, sound_buffer, sound_buffer_index):
        if sound_buffer:
            if not self.is_audio_playing:
                self.calibrate_start_index(sound_buffer, sound_buffer_index)
            else:
                self.store_or_play_audio_buffer(sound_buffer, sound_buffer_index)
        else:
            self.exit_message_loop()

    def calibrate_start_index(self, sound_buffer, sound_buffer_index):
        if self.static_sound_buffer_list.start_buffer_index == 0:
            self.static_sound_buffer_list.__init__()
            self.static_sound_buffer_list.start_buffer_index = sound_buffer_index
            self.static_sound_buffer_list.end_buffer_index = sound_buffer_index - 1
            self.static_sound_buffer_list.add_buffer_with_index(sound_buffer, sound_buffer_index)
        else:
            self.add_new_sound_buffer_to_buffer_list(sound_buffer, sound_buffer_index)

    def play_next_playable_buffer(self):
        playable_sound_buffer = self.static_sound_buffer_list.get_current_playable_buffer()
        # the write() gives 0, if the sound queue is full. We have to add this buffer the next time
        if self.play_buffer(playable_sound_buffer) == 0:
            self.static_sound_buffer_list.current_buffer_index -= 1

    def store_or_play_audio_buffer(self, sound_buffer, sound_buffer_index):
        self.add_new_sound_buffer_to_buffer_list(sound_buffer, sound_buffer_index)
        self.play_next_playable_buffer()

    def add_new_sound_buffer_to_buffer_list(self, sound_buffer, sound_buffer_index):
        try:
            self.static_sound_buffer_list.add_buffer_with_index(sound_buffer, sound_buffer_index)
        except IndexError:
            print(sound_buffer_index, self.static_sound_buffer_list.end_buffer_index + 1)
            print(" [Client] Got wrong buffer! What?")
            self.exit_message_loop()

    def exit_message_loop(self):
        print("[Client] Closing!")
        self.is_running = False


if __name__ == "__main__":
    main()
