import ConfigParser
from socket import error as SocketError

__author__ = 'nilpferd'


class ReadFromConfig:
    def __init__(self):
        self.configParser = ConfigParser.RawConfigParser()
        self.configParser.read("/etc/sound-sync.conf")

    def get_attribute(self, attribute):
        return self.configParser.get("defaults", attribute)


class AddressInformationBase(ReadFromConfig):
    def __init__(self):
        ReadFromConfig.__init__(self)
        self.server_ip = str(self.get_attribute("ip"))
        self.port = int(self.get_attribute("port"))


class ClientInformationBase(ReadFromConfig):
    def __init__(self):
        ReadFromConfig.__init__(self)
        self.waiting_time = 0
        self.frame_rate = 0
        self.sound_buffer_size = 0
        self.information_buffer_size = 1024
        self.multiple_buffer_factor = 50
        self.full_sound_buffer_size = 10
        self.sound_data_size = 0

    def set_sound_buffer_size(self):
        """
        Set the buffer_size to the number of bytes used for the sound snippet of length
        waiting_time (now in seconds!) * frame_rate.

        :rtype: None
        """

        self.sound_buffer_size = int(float(self.sound_data_size) *
                                     self.waiting_time / 1000.0 * self.frame_rate)


class SocketBase():

    clientInformation = ClientInformationBase()
    addressInformation = AddressInformationBase()

    def __init__(self):
        self.client = None

    def connect(self):
        """
        A function to connect to the server. Must be overwritten!
        """
        pass

    def receive_buffer_with_exact_length(self):
        """
        Receive exact buffer_size bytes from the server. If received less, repeat until the buffer
        is full. If an error occurred, return nothing.
        """

        pointer = 0
        tmp_buffer = bytearray(SocketBase.clientInformation.sound_buffer_size)
        while pointer < SocketBase.clientInformation.sound_buffer_size:
            data = self.receive(SocketBase.clientInformation.sound_buffer_size - pointer)
            if not data:
                raise SocketError

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def send(self, message):
        """
        Send the message message to the server if any.
        """
        if self.client is not None:
            self.client.sendall(message)

    def receive(self, buffer_size=None):
        """
        Receive a new message from the server of maximum length buffer_size. If not buffer_size is given,
        the start_buffer_size is used.
        """
        if buffer_size is None:
            buffer_size = SocketBase.clientInformation.information_buffer_size
        if self.client is not None:
            return self.client.recv(buffer_size)

    def close(self):
        """
        Close the connection to the server if any.
        """
        if self.client is not None:
            self.client.close()