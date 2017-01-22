from sound_sync.timing.time_utils import get_current_date, sleep
from threading import Timer


class LowResolutionTimer(Timer):
    """
    Wait until a certain time has occurred in a different process and execute a target function.
    """

    def __init__(self, start_time_to_wait_for, target_function, always_run=False, **kwargs):

        """
        Initialize the timer process
        :param start_time_to_wait_for: the time in seconds after the Epoch
        :param target_function: the function to call. Can not return anything.
        """
        current_time = get_current_date()
        interval = (start_time_to_wait_for - current_time).total_seconds()

        if interval < 0:
            if not always_run:
                raise ValueError("Can not handle a start time in the past.")
            else:
                interval = 0

        super().__init__(interval=interval, function=target_function, kwargs=kwargs)