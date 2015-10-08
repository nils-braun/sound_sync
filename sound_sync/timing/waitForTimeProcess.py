from multiprocessing import Process
import time


class Timer(Process):
    """
    Wait until a certain time has occurred in a different process and execute a target function.
    TODO: Handle reoccurring events!
    """
    def __init__(self, start_time_to_wait_for, time_interval, target_function):
        """
        Initialize the timer process
        :param start_time_to_wait_for: the time in seconds after the Epoch
        :param time_interval: the time in seconds to add aftter each call
        :param target_function: the function to call. Can not return anything.
        """
        self.start_time_to_wait_for = start_time_to_wait_for
        self.target_function = target_function
        self.time_interval = time_interval
        self._should_run = True

        super(Timer, self).__init__()

    def run(self):
        start_time_to_wait_for = self.start_time_to_wait_for
        time_interval = self.time_interval

        current_time = time.time()

        if current_time > start_time_to_wait_for:
            raise ValueError("Can not handle a start time in the past.")

        time_to_wait_for = start_time_to_wait_for

        while self._should_run:
            current_time = time.time()
            if current_time >= time_to_wait_for:
                self.target_function()
                time_to_wait_for += time_interval
                current_time = time.time()

                if current_time > time_to_wait_for:
                    raise RuntimeError("Called function lasted longer than a time interval.")

            time_delta = time_to_wait_for - current_time
            time.sleep(time_delta / 2.0)

    def stop(self):
        self._should_run = False

