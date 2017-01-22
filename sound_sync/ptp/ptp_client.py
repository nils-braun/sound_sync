from sound_sync.networking.connection import ReqSocket
from sound_sync.timing.time_utils import get_current_date, sleep


class PTPClient:
    def __init__(self, host="localhost", port=9999):
        self.socket = ReqSocket(host, port)

    def main_loop(self):
        while True:
            self.socket.send("get_time")
            send_time = get_current_date()

            server_time = self.socket.receive()
            receive_time = get_current_date()

            print(send_time, server_time, receive_time)
            sleep(1)

if __name__ == '__main__':
    client = PTPClient()
    client.main_loop()