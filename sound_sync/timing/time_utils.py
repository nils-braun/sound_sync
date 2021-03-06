import datetime
import time


def get_current_date():
    return datetime.datetime.utcnow()


def to_datetime(date_string):
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def waiting_time_to_datetime(waiting_time):
    return datetime.timedelta(seconds=waiting_time)


def sleep(sleep_time):
    time.sleep(sleep_time)
