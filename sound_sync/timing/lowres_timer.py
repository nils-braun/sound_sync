from sound_sync.timing.time_utils import get_current_date
from threading import Timer

import logging
logger = logging.getLogger(__name__)


class LowResolutionTimer(Timer):
    """
    Wait until a certain time has occurred in a different thread and execute a target function.
    Uses sleep for this which does not have a good resolution.
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
                logger.debug("The requested time of {start_time_to_wait_for} is "
                             "in the past (currently: {current_time}). Will not run."
                             .format(start_time_to_wait_for=start_time_to_wait_for,
                                     current_time=current_time))
                raise ValueError("Can not handle a start time in the past.")
            else:
                interval = 0

        super().__init__(interval=interval, function=target_function, kwargs=kwargs)