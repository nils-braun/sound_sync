"""
This module implements the class ClientBase - a starting point for all client classes.
"""

__author__ = "nilpferd1991"
__version__ = "1.0.0"

import math


class ClientBase:
    """ class ClientBase
    This class is the starting point for a listener and a sender client.
    It introduces the needed variables like the server ip, the port and the client object,
    but also the waiting time and the frame rate. The methods in this class supporting the crucial
    messaging between the server and the client.
    """

    def __init__(self):
        self.client = 0
        self.waiting_time = 0
        self.frame_rate = 0
        self.buffer_size = 0
        self.start_buffer_size = 1024
        self.server_ip = "192.168.178.200"
        self.port = 50007

    def read_values_from_server(self):
        """
        Receive the frame rate and the waiting time from the server.

        :rtype: None
        """

        # First is frame rate in Hz
        self.frame_rate = int(self.recv())
        self.send_ok()

        # Then waiting_time in ms
        self.waiting_time = int(self.recv())
        self.send_ok()

        # set the buffer size with the new data
        self.set_buffer_size()

    def send_values_to_server(self):
        """
        Send the frame rate and the waiting time to the server.

        :rtype : None
        """

        # tell the server the frame rate in Hz
        self.send(str(self.frame_rate).encode())
        # get ok
        self.recv_ok()
        # tell the server the waiting time in ms
        self.send(str(self.waiting_time).encode())
        # get ok
        self.recv_ok()

        # set the buffer size with the data
        self.set_buffer_size()

    def set_buffer_size(self):
        """
        Set the buffer_size to the number of bytes used for the sound snippet of length
        waiting_time (now in seconds!) * frame_rate. Multiplication by 4 is used because of
        format SE_16.

        :rtype: None
        """

        self.buffer_size = int(4*(2**math.log(self.waiting_time / 1000.0 * self.frame_rate, 2)))

    def recv_exact(self):
        """
        Receive exact buffer_size bytes from the server. If received less, repeat until the buffer
        is full. If an error occurred, return nothing.

        :rtype: bytearray
        """

        pointer = 0
        tmp_buffer = bytearray(self.buffer_size)
        while pointer < self.buffer_size:
            data = self.client.recv(self.buffer_size - pointer)
            if not data:
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def connect(self):
        """
        A function to connect to the server. Must be overwritten!
        """
        pass

    def close(self):
        """
        Close the connection to the server if any.
        """
        if self.client != 0:
            self.client.close()

    def send(self, message):
        """
        Send the message message to the server if any.
        """
        if self.client != 0:
            self.client.sendall(message)

    def send_ok(self):
        """
        Send the message "ok" to the server of any.
        """
        self.send("ok")

    def recv(self, buffer_size=None):
        """
        Receive a new message from the server of maximum length buffer_size. If not buffer_size is given,
        the start_buffer_size is used.
        """
        if buffer_size is None:
            buffer_size = self.start_buffer_size
        if self.client != 0:
            return self.client.recv(buffer_size)

    def recv_ok(self):
        """
        Receive a message without saving the message.
        """
        self.recv(self.start_buffer_size)