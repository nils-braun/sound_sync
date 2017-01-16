from unittest import TestCase
from sound_sync.timing import time_utils
from tests.fixtures import TimingTestCase


class TestUtils(TimingTestCase):
    def test_get_current_date(self):
        time_utils.get_current_date()
        self.datetime_mock.datetime.utcnow.assert_called_with()

    def test_sleep(self):
        test_sleep_time = 343
        time_utils.sleep(test_sleep_time)
        self.time_mock.sleep.assert_called_with(test_sleep_time)


class TestUtilsNoPatch(TestCase):
    def test_to_datetime(self):
        test_date_string_one = "2015-11-06 21:35:25"
        result_datetime = time_utils.to_datetime(test_date_string_one)

        self.assertEqual(result_datetime.year, 2015)
        self.assertEqual(result_datetime.month, 11)
        self.assertEqual(result_datetime.day, 6)
        self.assertEqual(result_datetime.hour, 21)
        self.assertEqual(result_datetime.minute, 35)
        self.assertEqual(result_datetime.second, 25)
        self.assertEqual(result_datetime.microsecond, 0)

        test_date_string_one = "2015-11-06 21:35:25.123456"
        result_datetime = time_utils.to_datetime(test_date_string_one)

        self.assertEqual(result_datetime.year, 2015)
        self.assertEqual(result_datetime.month, 11)
        self.assertEqual(result_datetime.day, 6)
        self.assertEqual(result_datetime.hour, 21)
        self.assertEqual(result_datetime.minute, 35)
        self.assertEqual(result_datetime.second, 25)
        self.assertEqual(result_datetime.microsecond, 123456)