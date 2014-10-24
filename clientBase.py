"""
This module implements the class ClientBase - a starting point for all client classes.
"""
from informationBase import SocketBase

__author__ = "nilpferd1991"
__version__ = "2.0.0"


class ClientBase(SocketBase):
    """ class ClientBase
    This class is the starting point for a listener and a sender client.
    It introduces the needed variables like the server ip, the port and the client object,
    but also the waiting time and the frame rate. The methods in this class supporting the basic
    messaging between the server and the client.
    """

    def __init__(self):
        self.start_time = 0                     # The time_stamp in s, when the server gets the first buffer
                                                # from the sender
                                                # TODO May be implemented better

        SocketBase.__init__(self)

    def read_values_from_server(self):
        """
        Receive the frame rate, the waiting time and the start time from the server.
        """

        # First is frame rate in Hz
        ClientBase.clientInformation.frame_rate = int(self.receive())
        self.send_ok()

        # Then waiting_time in ms
        ClientBase.clientInformation.waiting_time = int(self.receive())
        self.send_ok()

        # Then start_time in s
        self.start_time = float(self.receive())
        self.send_ok()

        # set the buffer size with the new data
        ClientBase.clientInformation.set_sound_buffer_size()

    def send_values_to_server(self):
        """
        Send the frame rate and the waiting time to the server.
        """

        self.send_information(ClientBase.clientInformation.frame_rate)
        self.send_information(ClientBase.clientInformation.waiting_time)

        ClientBase.clientInformation.set_sound_buffer_size()
