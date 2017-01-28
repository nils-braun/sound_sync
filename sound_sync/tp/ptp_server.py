from threading import Thread

from sound_sync.networking.connection import RepSocket
from sound_sync.timing.time_utils import get_current_date


class PTPServer(Thread):
    def __init__(self, port=8889):
        super().__init__()

        self.socket = RepSocket(port)

        self._should_run = True

    def run(self):
        while self._should_run:
            self.socket.receive()
            receive_time = get_current_date()
            self.socket.send(receive_time)

    def cancel(self):
        self._should_run = False

if __name__ == '__main__':
    server = PTPServer()
    server.run()