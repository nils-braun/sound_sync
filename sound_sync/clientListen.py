#!/usr/bin/env python
# coding=utf-8
"""
This module implements the listener client.
"""

from __future__ import print_function
import socket
import time
from threading import Thread, Timer
import xml.etree.ElementTree as ElementTree

from pcmHandler import PCMPlay
from listHandler import ClientBufferListHandler
from clientBase import ClientBase


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



if __name__ == "__main__":
    main()
