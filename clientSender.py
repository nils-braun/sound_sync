#!/usr/bin/env python

from pcmHandler import PCMCapture
import socket
from clientBase import ClientBase
import xml.etree.ElementTree as ElementTree

__author__ = "nilpferd1991"
__version__ = "2.0.0"


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
        client.close_sound()


class ClientSender(ClientBase, PCMCapture):
    """
    This class implements the sender to the server. It connects to the server,
    sends the values of the frame rate and the waiting time to the server and
    starts sending sound buffers to the sender.
    """
    def __init__(self):
        ClientBase.__init__(self)
        PCMCapture.__init__(self)
        ClientSender.clientInformation.frame_rate = int(self.get_attribute("frame_rate"))
        ClientSender.clientInformation.waiting_time = ClientSender.clientInformation.multiple_buffer_factor * \
                                                      int(self.get_attribute("waiting_time"))

    def tell_server_sender_identity(self):
        element = ElementTree.Element("client", {"type": "sender"})
        ElementTree.SubElement(element, "options", {"waitingTime": str(self.clientInformation.waiting_time),
                                                    "frameRate": str(self.clientInformation.frame_rate)})
        self.client.sendall(ElementTree.tostring(element))

    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ClientSender.addressInformation.server_ip, ClientSender.addressInformation.port))

        self.tell_server_sender_identity()

        self.initialize_pcm(ClientSender.clientInformation.frame_rate,
                            ClientSender.clientInformation.sound_buffer_size /
                            ClientSender.clientInformation.multiple_buffer_factor)

    def message_loop(self):
        while True:
            self.collect_and_send_sound_data()

    def collect_and_send_sound_data(self):
        sound_buffer_length, sound_buffer = self.collect_sound_data()
        if sound_buffer_length > 0:
            self.send(sound_buffer)

    def collect_sound_data(self):
        tmp_buffer = bytearray()
        tmp_length = 0
        for _ in range(ClientSender.clientInformation.multiple_buffer_factor):
            sound_buffer, length = self.get_sound_data()
            tmp_buffer.extend(sound_buffer)
            tmp_length += length
        return tmp_length, tmp_buffer


if __name__ == "__main__":
    main()
