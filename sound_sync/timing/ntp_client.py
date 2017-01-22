from datetime import timedelta

import ntplib

from sound_sync.timing.lowres_timer import LowResolutionTimer
from sound_sync.timing.time_utils import get_current_date


class NTPClient:
    def __init__(self, interval=timedelta(seconds=10)):
        self._client = ntplib.NTPClient()
        self._interval = interval
        self._url = 'pool.ntp.org'

        self.offset_to_ntp_client = timedelta()
        self._timer = None

        self.get_offset()

    def terminate(self):
        if self._timer is not None:
            self._timer.stop()

    def get_offset(self):
        try:
            response = self._client.request(self._url)
            self.offset_to_ntp_client = timedelta(seconds=response.offset)
        except ntplib.NTPException:
            pass

        if self._timer is not None:
            self._timer.cancel()

        next_offset_query = get_current_date() + self._interval
        self._timer = LowResolutionTimer(next_offset_query, self.get_offset)
        self._timer.start()