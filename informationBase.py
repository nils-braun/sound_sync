import ConfigParser

__author__ = 'nils'


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
        self.multiple_buffer_factor = int(self.get_attribute("multiple_buffer_factor"))

    def set_sound_buffer_size(self):
        """
        Set the buffer_size to the number of bytes used for the sound snippet of length
        waiting_time (now in seconds!) * frame_rate.

        :rtype: None
        """

        self.sound_buffer_size = int(float(self.get_attribute("sound_data_size")) *
                                     self.waiting_time / 1000.0 * self.frame_rate)


class SocketBase():

    clientInformation = ClientInformationBase()
    addressInformation = AddressInformationBase()

    def __init__(self):
        self.client = 0

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
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def receive_information(self):
        data = self.receive()
        self.send_ok()
        return data

    def send_information(self, information):
        self.send(str(information).encode())
        self.receive_ok()

    def send_ok(self):
        """
        Send the message "ok" to the server of any.
        """
        self.send("ok")

    def receive_ok(self):
        """
        Receive a message without saving the message.
        """
        self.receive(SocketBase.clientInformation.information_buffer_size)

    def send(self, message):
        """
        Send the message message to the server if any.
        """
        if self.client != 0:
            self.client.sendall(message)

    def receive(self, buffer_size=None):
        """
        Receive a new message from the server of maximum length buffer_size. If not buffer_size is given,
        the start_buffer_size is used.
        """
        if buffer_size is None:
            buffer_size = SocketBase.clientInformation.information_buffer_size
        if self.client != 0:
            return self.client.recv(buffer_size)

    def close(self):
        """
        Close the connection to the server if any.
        """
        if self.client != 0:
            self.client.close()