from datetime import timedelta

import ntplib

from sound_sync.tp.timing_client import TimingClient


class NTPClient(TimingClient):
    def __init__(self, interval=timedelta(seconds=10)):
        super().__init__(interval)

        self._client = ntplib.NTPClient()
        self._url = 'pool.ntp.org'

    def get_offset(self):
        try:
            response = self._client.request(self._url)
            return timedelta(seconds=response.offset), None
        except ntplib.NTPException:
            return None, None
