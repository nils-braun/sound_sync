from sound_sync.networking.connection import RepSocket
from sound_sync.timing.time_utils import get_current_date


class PTPServer:
    def __init__(self, port=9999):
        self.socket = RepSocket(port)

    def main_loop(self):
        while True:
            self.socket.receive()
            receive_time = get_current_date()
            self.socket.send(receive_time)

if __name__ == '__main__':
    server = PTPServer()
    server.main_loop()