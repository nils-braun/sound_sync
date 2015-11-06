from datetime import datetime, timedelta
from mock import MagicMock

from sound_sync.timing.waitForTimeProcess import Timer
from tests.fixtures import TimingTestCase


class TestTimer(TimingTestCase):
    def test_fail_or_not_fail_for_past_values(self):
        self.time_mock.sleep = None

        start_time = datetime(2015, 11, 6, 0, 0, 0)
        time_interval = timedelta(10)
        timer = Timer(start_time, time_interval, None)

        # Call the sleep function, because the time is in the future
        self.datetime_mock.datetime.now = MagicMock(return_value=datetime(2015, 11, 4, 0, 0, 0))
        self.assertRaisesRegexp(TypeError, "'NoneType' object is not callable", timer.run)

        # Fail, because the time is in the past
        self.datetime_mock.datetime.now = MagicMock(return_value=datetime(2015, 11, 6, 0, 0, 2))
        self.assertRaisesRegexp(ValueError, "Can not handle a start time in the past.", timer.run)

    def test_run(self):
        self.datetime_mock.datetime.now = self.time_list_mock_function

        start_time = datetime(2015, 11, 6, 0, 0, 2)
        time_interval = timedelta(seconds=4)
        timer = Timer(start_time, time_interval, None)

        def callable_function():
            current_time = self.get_current_time()
            self.assertIn(current_time.second, [2, 6, 10])

            if current_time.second == 10:
                timer.stop()

        timer.target_function = callable_function

        def sleep_function(time_delta):
            current_time = self.get_current_time()
            self.assertIn(current_time.second, [1, 3, 4, 5, 7, 8, 9, 11])

            if current_time.second in [1, 5, 9]:
                self.assertEqual(time_delta, 0.5)
            elif current_time.second in [3, 7, 11]:
                self.assertEqual(time_delta, 1.5)
            elif current_time.second in [4, 8]:
                self.assertEqual(time_delta, 1)

        self.time_mock.sleep = sleep_function

        timer.run()

    def test_too_long_function(self):

        self.datetime_mock.datetime.now = self.time_list_mock_function

        start_time = datetime(2015, 11, 6, 0, 0, 4)
        time_interval = timedelta(seconds=2)
        timer = Timer(start_time, time_interval, None)

        def callable_function():
            self.assertEqual(self.get_current_time().second, 4)
            self.time_list_mock_function.side_effect = [datetime(2015, 11, 6, 0, 0, 7)]

        timer.target_function = callable_function

        def sleep_function(time_delta):
            current_time = self.get_current_time()
            self.assertIn(current_time.second, [1, 2, 3])

            if current_time.second in [1]:
                self.assertEqual(time_delta, 1.5)
            elif current_time.second in [2]:
                self.assertEqual(time_delta, 1)
            elif current_time.second in [3]:
                self.assertEqual(time_delta, 0.5)

        self.time_mock.sleep = sleep_function

        self.assertRaises(RuntimeError, timer.run)

    def test_stop(self):
        timer = Timer(None, None, None)

        self.assertEqual(timer._should_run, True)

        timer.stop()
        self.assertEqual(timer._should_run, False)



