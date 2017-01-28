from datetime import timedelta

from sound_sync.timing.lowres_timer import LowResolutionTimer
from sound_sync.timing.time_utils import get_current_date

import logging
logger = logging.getLogger(__name__)


class TimingClient:
    """
    Base class for a client implementing a time protocol (in whatever way)
    to synchronize the time between each clients of the same type (and connected
    to the same host).

    Calls the virtual function "get_offset" every `interval` and writes back the
    offset and connection_time the function has calculated.

    This offset should be *added* to the clients time, to get the correct time.
    """
    def __init__(self, interval=timedelta(seconds=10)):
        self.offset = timedelta()
        self.connection_time = timedelta()

        self._timer = None
        self._interval = interval

    def terminate(self):
        logger.debug("Terminate the time client")

        if self._timer is not None:
            self._timer.stop()

    def start(self):
        logger.debug("Start the time client")

        self.get_offset_and_restart_timer()

    def get_offset_and_restart_timer(self):
        returned_offset, returned_connection_time = self.get_offset()

        logger.debug("Got new time offset: {offset} and connection time {connection_time}."
                     .format(offset=returned_offset, connection_time=returned_connection_time))

        if returned_offset:
            self.offset = returned_offset

        if returned_connection_time:
            self.connection_time = returned_connection_time

        if self._timer is not None:
            self._timer.cancel()

        next_offset_query = get_current_date() + self._interval

        logger.debug("Will get the offset next on {next_offset_query}"
                     .format(next_offset_query=next_offset_query))

        self._timer = LowResolutionTimer(next_offset_query, self.get_offset_and_restart_timer)
        self._timer.start()

    def get_offset(self):
        raise NotImplementedError
