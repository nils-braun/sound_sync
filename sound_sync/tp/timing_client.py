from datetime import timedelta

from sound_sync.timing.lowres_timer import LowResolutionTimer
from sound_sync.timing.time_utils import get_current_date


class TimingClient:
    def __init__(self, interval=timedelta(seconds=10)):
        self.offset = timedelta()
        self.connection_time = timedelta()

        self._timer = None
        self._interval = interval

    def terminate(self):
        if self._timer is not None:
            self._timer.stop()

    def start(self):
        self.get_offset_and_restart_timer()

    def get_offset_and_restart_timer(self):
        returned_offset, returned_connection_time = self.get_offset()

        if returned_offset:
            self.offset = returned_offset

        if returned_connection_time:
            self.connection_time = returned_connection_time

        if self._timer is not None:
            self._timer.cancel()

        next_offset_query = get_current_date() + self._interval
        self._timer = LowResolutionTimer(next_offset_query, self.get_offset_and_restart_timer())
        self._timer.start()

    def get_offset(self):
        raise NotImplementedError