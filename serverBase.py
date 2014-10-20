__author__ = 'nils'


class ServerBase:
    def __init__(self, request):
        self.start_buffer_size = 1024   # The buffer_size to be used for pre-audio messaging.
        self.buffer_size = 0            # the buffer size of the clients is calculated from teh waiting_time and
                                        # the frame rate. Fo more information see ClientBase.
        self.request = request

    def set_buffer_size(self, waiting_time, frame_rate):
        self.buffer_size = int(4 * waiting_time / 1000.0 * frame_rate)

    def receive_exact(self):
        """
        Receive exact buffer_size bytes from the client. If received less, repeat until the buffer
        is full. If an error occurred, return nothing.

        :rtype: bytearray, None
        """
        pointer = 0
        tmp_buffer = bytearray(self.buffer_size)
        while pointer < self.buffer_size:
            data = self.request.recv(self.buffer_size - pointer)
            if not data:
                return

            tmp_buffer[pointer:pointer + len(data)] = data
            pointer += len(data)

        return tmp_buffer

    def receive_information(self):
        data = self.receive_message()
        self.say_ok()
        return data

    def send_information(self, information):
        self.send_message(str(information).encode())
        self.get_ok()

    def get_ok(self):
        self.receive_message()

    def say_ok(self):
        self.send_message("ok")

    def receive_message(self):
        return self.request.recv(self.start_buffer_size)

    def send_message(self, message):
        self.request.sendall(message)