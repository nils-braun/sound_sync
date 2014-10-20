#!/usr/bin/env python
"""
This module starts the sender.
"""
WAITING_TIME = 10
FRAME_RATE = 44100
CARD_NAME = u'hw:Loopback,1,0'

__author__ = "nilpferd1991"
__version__ = "2.0.0"

import socket

import alsaaudio
from clientBase import ClientBase


class PCMPlayer:
    # The PCM device of the ALSA-Loopback-Adapter. The data coming from the applications
    # is send through this loopback into the program. We need a frame rate of 44100 Hz and collect 10 ms of data
    # at once.

    def __init__(self):
        self.frame_rate = FRAME_RATE
        self.pcm = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, card=CARD_NAME)
        self.waiting_time = WAITING_TIME

        self.search_for_loopback_card()

    def search_for_loopback_card(self):
        card_list = alsaaudio.cards()
        if not "Loopback" in card_list:
            print("There is no Loopback module loaded by ALSA. Loopback is needed by the program. "
                  "Try loading it via modprobe or add it to /etc/modules or to a file in /etc/modules.d/. Aborting.")
            exit()

    def initialize_pcm(self, buffer_size):
        """
        Set the PCM device with the usual parameters.
        """
        self.pcm.setchannels(2)
        self.pcm.setrate(self.frame_rate)
        self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(buffer_size)

    def get_sound_data(self):
        length, buffer = self.pcm.read()
        return buffer, length


class ClientSender(ClientBase, PCMPlayer):
    """
    This class implements the sender to the server. It connects to the server,
    sends the values of the frame rate and the waiting time to the server and
    starts sending sound buffers to the sender.
    """
    def __init__(self):
        self.client = 0
        ClientBase.__init__(self, self.client)
        PCMPlayer.__init__(self)

    def connect(self):
        """
        Connect to the server and send frame rate and waiting time.
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        self.client.sendall(b"sender")
        self.recv()

        self.send_values_to_server()

        self.initialize_pcm(self.buffer_size)

    def message_loop(self):
        """
        Start getting the data from the PCM and sending the sound buffers to the server in a loop.
        Collect factor*waiting_time ms at once and send after that.
        """
        while True:
            sound_buffer_length, sound_buffer = self.collect_sound_data()
            if sound_buffer_length > 0:
                self.send(sound_buffer)

    def collect_sound_data(self):
        tmp_buffer = bytearray()
        tmp_length = 0
        # collect the data...
        for _ in range(self.factor):
            buffer, length = self.get_sound_data()
            tmp_buffer.extend(buffer)
            tmp_length += length
        return tmp_length, tmp_buffer


def main():
    """
    Main function
    Initialize a new instance of the client sender module
    and connect to the server.
    Then start the message loop (get the data from the Alsa-PCM and send it to the server)
    until Ctrl-C is hit.
    """
    client = ClientSender()
    client.connect()

    try:
        client.message_loop()
    except KeyboardInterrupt:
        print("stopped")
    finally:
        client.close()

if __name__ == "__main__":
    main()