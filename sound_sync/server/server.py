from sound_sync.clients.connection import Proxy


class Server:
    def __init__(self, publisher_port, subscriber_port, cache_length=100):
        self.proxy = Proxy(publisher_port, subscriber_port, cache_length=cache_length)

    def main_loop(self):
        while True:
            self.proxy.poll()

    def initialize(self):
        pass

    def terminate(self):
        pass