from datetime import timedelta
from functools import partial

from sound_sync.timing.lowres_timer import LowResolutionTimer
from sound_sync.timing.time_utils import get_current_date, sleep
from sound_sync.timing.timer import Timer

timer_results = dict()


def target_function(timer_name):
    global timer_results

    timer_results[timer_name] = get_current_date()


def test_timers(interval):
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


def test_interval(interval):
    print(interval)

    results = {"highres": [], "lowres": []}

    for i in range(10):
        result = test_timers(interval)
        results["highres"].append(result["highres"])
        results["lowres"].append(result["lowres"])

    for key, result in results.items():
        mean_deviation = sum(result, timedelta()) / len(result)
        print(key, mean_deviation / interval * 100, "%", mean_deviation)


if __name__ == "__main__":
    test_interval(timedelta(milliseconds=10))
    test_interval(timedelta(milliseconds=20))
    test_interval(timedelta(milliseconds=100))
    test_interval(timedelta(milliseconds=500))
    test_interval(timedelta(milliseconds=184))