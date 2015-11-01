from mock import MagicMock

from sound_sync.timing.waitForTimeProcess import Timer
from tests.test_fixtures import TimingTestCase


class TestTimer(TimingTestCase):
    def test_fail_or_not_fail_for_past_values(self):
        self.time_mock.sleep = None

        start_time = 1E10
        time_interval = 10
        timer = Timer(start_time, time_interval, None)

        # Call the sleep function, because the time is in the future
        self.datetime_mock.now = MagicMock(return_value=1E8)
        self.assertRaisesRegexp(TypeError, "'NoneType' object is not callable", timer.run)

        # Fail, because the time is in the past
        self.datetime_mock.now = MagicMock(return_value=1E11)
        self.assertRaisesRegexp(ValueError, "Can not handle a start time in the past.", timer.run)

    def test_run(self):
        self.datetime_mock.now = self.time_list_mock_function

        start_time = 2
        time_interval = 4
        timer = Timer(start_time, time_interval, None)

        def callable_function():
            self.assertIn(self.get_current_time(), [2, 6, 10])

            if self.get_current_time() == 10:
                timer.stop()

        timer.target_function = callable_function

        def sleep_function(time_delta):
            current_time = self.get_current_time()
            self.assertIn(current_time, [1, 3, 4, 5, 7, 8, 9, 11])

            if current_time in [1, 5, 9]:
                self.assertEqual(time_delta, 0.5)
            elif current_time in [3, 7, 11]:
                self.assertEqual(time_delta, 1.5)
            elif current_time in [4, 8]:
                self.assertEqual(time_delta, 1)

        self.time_mock.sleep = sleep_function

        timer.run()

    def test_too_long_function(self):

        self.datetime_mock.now = self.time_list_mock_function

        start_time = 4
        time_interval = 2
        timer = Timer(start_time, time_interval, None)

        def callable_function():
            self.assertEqual(self.get_current_time(), 4)
            self.time_list_mock_function.side_effect = [7]

        timer.target_function = callable_function

        def sleep_function(time_delta):
            current_time = self.get_current_time()
            self.assertIn(current_time, [1, 2, 3])

            if current_time in [1]:
                self.assertEqual(time_delta, 1.5)
            elif current_time in [2]:
                self.assertEqual(time_delta, 1)
            elif current_time in [3]:
                self.assertEqual(time_delta, 0.5)

        self.time_mock.sleep = sleep_function

        self.assertRaises(RuntimeError, timer.run)

    def test_stop(self):
        timer = Timer(None, None, None)

        self.assertEqual(timer._should_run, True)

        timer.stop()
        self.assertEqual(timer._should_run, False)



