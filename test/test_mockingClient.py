__author__ = 'nils'


from socket import error as SocketError

class MockingClient:
    def __init__(self):
        self.last_in_message = list()
        self.last_out_message = list()
        self.last_buffer_size = 0
        self.closed = False

    def sendall(self, message):
        self.last_in_message.append(message)

    def recv(self, buffer_size):
        self.last_buffer_size = buffer_size
        if len(self.last_out_message) > 0:
            return self.last_out_message.pop(0)
        else:
            raise SocketError

    def close(self):
        self.closed = True

    def add_out_message(self, message):
        self.last_out_message.append(message)

    def get_in_message(self):
        return self.last_in_message.pop(0)


class MockingPCM:
    def __init__(self):
        self.message_stack = list()
        self.sound_buffer_size = 0

    def read(self):
        if len(self.message_stack) > 0:
            return int(self.sound_buffer_size / 4), self.message_stack.pop(0)
        else:
            raise IndexError

    def write(self, buffer):
        self.message_stack.append(buffer)
        return len(buffer)

    def add_buffer(self, buffer):
        self.message_stack.append(buffer)
