import datetime
import time


def get_current_date():
    """Get the current time in UTC."""
    return datetime.datetime.utcnow()


def to_datetime(date_string):
    """Translate a string form of a datetime to a python datetime"""
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def sleep(sleep_time):
    """Sleep a certain amount of time."""
    time.sleep(sleep_time)
