#!/usr/bin/env python3
"""
This module starts the sender.
"""

__author__ = "nilpferd1991"
__version__ = "1.0.0"

import socket
import subprocess
import wave
import time
from clientBase import ClientBase
import tempfile


class ClientSender(ClientBase):
    """
    This class implements the sender to the server. It connects to the server,
    sends the values of the frame rate and the waiting time to the server and
    starts sending sound buffers to the sender.
    """
    def __init__(self):
        ClientBase.__init__(self)
        self.read_values_from_file()

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

    def message_loop(self, filename):
        """
        Start sending the sound buffers to the server in a loop.
        In the moment these sound files come from a mp3 file which is converted to wav before using avconv.
        """
        _, tmp_file = tempfile.mkstemp()

        convert_command = ['avconv', '-y']
        convert_command += ['-i', filename]
        convert_command += ['-vn', '-f', 'wav', tmp_file]

        ret_code = subprocess.call(convert_command, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        assert ret_code == 0

        f = wave.open(tmp_file, "rb")
        max_number = int(f.getnframes()/self.buffer_size*4.0)
        for i in range(max_number):
            buffer = bytearray(f.readframes(int(self.buffer_size/4.0)))
            self.send(buffer)
            time.sleep(self.waiting_time/1000.0)
        f.close()


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

    # TODO: Get data not from file but from the currently playing sound!
    # For this: switch the pulse-audio output to the alsa-loopback and collect this output via
    # pcm = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, card=u'hw:Loopback,1,0')
    # pcm.read()

    try:
        client.message_loop("/media/Daten/Music/In Flames/A Sense Of Purpose/02. Disconnected.mp3")
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    main()