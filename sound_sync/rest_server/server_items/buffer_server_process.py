from multiprocessing import Process
import time


class BufferServerProcess(Process):
    def __init__(self, port_number):
        super(BufferServerProcess, self).__init__()

        self.port_number = port_number

    def run(self):
        try:
            from sound_sync.buffer_server import BufferServer
        except ImportError:
            from buffer_server import BufferServer
        self.buffer_server = BufferServer(self.port_number)
        self.buffer_server.start()