from threading import Thread

from sound_sync.timing.time_utils import get_current_date, sleep


class Timer(Thread):
    """
    Wait until a certain time has occurred in a different process and execute a target function.
    TODO: Handle reoccurring events!
    """

    def __init__(self, start_time_to_wait_for, target_function):
        """
        Initialize the timer process
        :param start_time_to_wait_for: the time in seconds after the Epoch
        :param target_function: the function to call. Can not return anything.
        """
        self.start_time_to_wait_for = start_time_to_wait_for
        self.target_function = target_function
        self._should_run = True

        current_time = get_current_date()

        if current_time > start_time_to_wait_for:
            raise ValueError("Can not handle a start time in the past.")

        super(Timer, self).__init__()

    def run(self):
        start_time_to_wait_for = self.start_time_to_wait_for

        time_to_wait_for = start_time_to_wait_for

        while self._should_run:
            current_time = get_current_date()
            if current_time >= time_to_wait_for:
                self.target_function()
                self._should_run = False
                return

            time_delta = time_to_wait_for - current_time
            sleep(time_delta.total_seconds() / 2.0)

    def stop(self):
        self._should_run = False
