from multiprocessing import Process


class BufferServerProcess(Process):
    def __init__(self, port_number):
        super(BufferServerProcess, self).__init__()

        self.port_number = port_number

    def run(self):
        try:
            from sound_sync.buffer_server import BufferServer
        except ImportError:
            from buffer_server import BufferServer

        BufferServer(self.port_number).start()