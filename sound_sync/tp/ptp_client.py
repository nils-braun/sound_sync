from datetime import timedelta

from sound_sync.networking.connection import ReqSocket
from sound_sync.timing.time_utils import get_current_date, to_datetime
from sound_sync.tp.timing_client import TimingClient


def mean(listable_item):
    return sum(listable_item, timedelta()) / len(listable_item)


class PTPClient(TimingClient):
    def __init__(self, host, port=8889, interval=timedelta(seconds=20)):
        super().__init__(interval)

        self._socket = ReqSocket(host, port)

        self.number_of_calls = 20

    def get_offset(self):
        connection_times = []
        offsets = []

        for i in range(self.number_of_calls):
            self._socket.send("get_time")
            send_time = get_current_date()

            server_time = self._socket.receive()
            receive_time = get_current_date()

            server_time = to_datetime(str(server_time, encoding="utf8"))
            connection_time = 0.5 * (receive_time - send_time)
            offset = server_time - send_time - connection_time

            connection_times.append(connection_time)
            offsets.append(offset)

        return mean(offsets), mean(connection_times)