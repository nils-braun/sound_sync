__author__ = 'nils'


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
            return ""

    def close(self):
        self.closed = True

    def add_out_message(self, message):
        self.last_out_message.append(message)

    def get_in_message(self):
        return self.last_in_message.pop(0)