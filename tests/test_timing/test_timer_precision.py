from datetime import timedelta
from functools import partial
from unittest import TestCase

from sound_sync.timing.lowres_timer import LowResolutionTimer
from sound_sync.timing.time_utils import get_current_date, sleep
from sound_sync.timing.timer import Timer

timer_results = dict()


def target_function(timer_name):
    global timer_results

    timer_results[timer_name] = get_current_date()


def _test_timers(interval):
    current_time = get_current_date()

    wait_time = current_time + interval

    lowres_timer = LowResolutionTimer(start_time_to_wait_for=wait_time,
                                      target_function=partial(target_function, timer_name="lowres"))
    highres_timer = Timer(start_time_to_wait_for=wait_time,
                          target_function=partial(target_function, timer_name="highres"))

    lowres_timer.start()
    highres_timer.start()

    sleep((2 * interval).total_seconds())

    return {key: timer_result - wait_time for key, timer_result in timer_results.items()}


def _test_interval(interval):
    results = {"highres": [], "lowres": []}

    for i in range(10):
        result = _test_timers(interval)
        results["highres"].append(result["highres"])
        results["lowres"].append(result["lowres"])

    for key, result in results.items():
        mean_deviation = sum(result, timedelta()) / len(result)
        yield key, mean_deviation / interval


class TestTimerPrecision(TestCase):
    def test_timer_precision_10(self):
        resolutions = _test_interval(timedelta(milliseconds=10))

        for key, resolution in resolutions:
            if key == "lowres":
                self.assertLess(resolution, 0.05)
            elif key == "highres":
                self.assertLess(resolution, 0.01)

    def test_timer_precision_20(self):
        resolutions = _test_interval(timedelta(milliseconds=20))

        for key, resolution in resolutions:
            if key == "lowres":
                self.assertLess(resolution, 0.05)
            elif key == "highres":
                self.assertLess(resolution, 0.01)
