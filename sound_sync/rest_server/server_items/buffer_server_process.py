from multiprocessing import Process

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


class BufferServerProcess(Process):
    def __init__(self, port_number):
        super(BufferServerProcess, self).__init__()

        self.port_number = port_number

    def run(self):
        pass