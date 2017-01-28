from threading import Thread, Event

from sound_sync.timing.time_utils import get_current_date, sleep


import logging
logger = logging.getLogger(__name__)


class Timer(Thread):
    """
    Wait until a certain time has occurred in a different thread and execute a target function.
    Uses an iterative sleep-approach, which should have most of the time a much better
    resolution than the LowResTimer.
    """
    def __init__(self, start_time_to_wait_for, target_function, always_run=False, **kwargs):
        """
        Initialize the timer process
        :param start_time_to_wait_for: the time in seconds after the Epoch
        :param target_function: the function to call. Can not return anything.
        """
        self.start_time_to_wait_for = start_time_to_wait_for
        self.target_function = target_function
        self._should_run = Event()
        self.kwargs = kwargs

        current_time = get_current_date()

        if current_time > start_time_to_wait_for and not always_run:
            logger.debug("The requested time of {start_time_to_wait_for} is "
                         "in the past (currently: {current_time}). Will not run."
                         .format(start_time_to_wait_for=start_time_to_wait_for,
                                 current_time=current_time))
            raise ValueError("Can not handle a start time in the past.")

        super(Timer, self).__init__()

    def run(self):
        start_time_to_wait_for = self.start_time_to_wait_for

        time_to_wait_for = start_time_to_wait_for

        while not self.is_finished():
            current_time = get_current_date()
            if current_time >= time_to_wait_for:
                self.target_function(**self.kwargs)
                self._should_run.set()
                return

            time_delta = time_to_wait_for - current_time
            self._should_run.wait(time_delta.total_seconds() / 2.0)

    def cancel(self):
        self._should_run.set()

    def is_finished(self):
        return self._should_run.is_set()
