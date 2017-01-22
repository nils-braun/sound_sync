from datetime import datetime
from mock import MagicMock

from sound_sync.timing.timer import Timer
from tests.fixtures import TimingTestCase


class TestTimer(TimingTestCase):
    def test_not_fail_for_future_values(self):
        self.time_mock.sleep = None

        start_time = datetime(2015, 11, 6, 0, 0, 0)

        self.datetime_mock.datetime.utcnow = MagicMock(return_value=datetime(2015, 11, 4, 0, 0, 0))

        # This should not fail
        Timer(start_time, None)

    def test_fail_for_past_values(self):
        self.time_mock.sleep = None

        start_time = datetime(2015, 11, 6, 0, 0, 0)
        self.datetime_mock.datetime.utcnow = MagicMock(return_value=datetime(2015, 11, 6, 0, 0, 2))

        self.assertRaisesRegexp(ValueError, "Can not handle a start time in the past.", Timer, start_time, None)

    def test_run(self):
        self.datetime_mock.datetime.utcnow = self.time_list_mock_function

        start_time = datetime(2015, 11, 6, 0, 0, 2)

        def sleep_function(time_delta):
            current_time = self.get_current_time()
            self.assertEqual(current_time.second, 1)
            self.assertEqual(time_delta, 0.5)

        self.time_mock.sleep = sleep_function

        def callable_function():
            current_time = self.get_current_time()
            self.assertEqual(current_time.second, 2)

        timer = Timer(start_time, callable_function)

        timer.run()

    def test_stop(self):
        self.datetime_mock.datetime.utcnow = self.time_list_mock_function

        start_time = datetime(2015, 11, 6, 0, 0, 2)
        timer = Timer(start_time, None)

        self.assertEqual(timer._should_run, True)

        timer.cancel()
        self.assertEqual(timer._should_run, False)

    def test_stop_before_function(self):
        self.datetime_mock.datetime.utcnow = self.time_list_mock_function

        start_time = datetime(2015, 11, 6, 0, 0, 2)

        def sleep_function(time_delta):
            timer._should_run = False

        self.time_mock.sleep = sleep_function

        def callable_error():
            raise AssertionError()

        timer = Timer(start_time, callable_error)

        timer.run()
