#!/usr/bin/env python
"""
This module starts the sender.
"""

__author__ = "nilpferd1991"
__version__ = "1.0.0"

import socket
import alsaaudio
from clientBase import ClientBase


class ClientSender(ClientBase):
    """
    This class implements the sender to the server. It connects to the server,
    sends the values of the frame rate and the waiting time to the server and
    starts sending sound buffers to the sender.
    """
    def __init__(self):
        ClientBase.__init__(self)
        self.pcm = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, card=u'hw:Loopback,1,0')
        self.waiting_time = 10
        self.frame_rate = 44100

    def set_pcm(self):
        self.pcm.setchannels(2)
        self.pcm.setrate(self.frame_rate)
        self.pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.pcm.setperiodsize(self.buffer_size)

    def connect(self):
        """
        Connect to the server and send frame rate and waiting time.
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server_ip, self.port))

        # tell the server we are a sender
        self.client.sendall(b"sender")
        self.recv()

        # Send the parameters to the server.
        self.send_values_to_server()

        # initialize the capture pcm
        self.set_pcm()

    def message_loop(self):
        """
        Start sending the sound buffers to the server in a loop. Do factor buffers back-to-back.
        """
        while True:
            tmp_buffer = bytearray()
            for _ in range(self.factor):
                length, buffer = self.pcm.read()
                tmp_buffer.extend(buffer)
            if length > 0:
                self.send(tmp_buffer)


def main():
    """
    Main function
    Initialize a new instance of the client sender module
    and connect to the server.
    Then start the message loop (decode the file to wav and send it to the server)
    until Ctrl-C is hit.
    """
    client = ClientSender()
    client.connect()

    try:
        client.message_loop()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    main()