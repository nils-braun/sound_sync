from unittest import TestCase
from mock import patch, MagicMock

from sound_sync.timing.waitForTimeProcess import Timer



class TestTimer(TestCase):
    def setUp(self):
        self.time = 0

        patcher = patch("sound_sync.timing.waitForTimeProcess.time")
        self.time = patcher.start()
        self.addCleanup(patcher.stop)

        self.time_mockup = MagicMock(side_effect=xrange(20))

    def get_current_time(self):
        current_time_list = list(self.time_mockup.side_effect)
        current_time = current_time_list[0] - 1
        self.time_mockup.side_effect = current_time_list
        return current_time

    def test_fail_for_past_values(self):
        self.time.time = MagicMock(return_value=1E11)

        start_time = 1E10
        time_interval = 10
        timer = Timer(start_time, time_interval, None)

        self.assertRaises(ValueError, timer.run)

    def test_run(self):
        self.time.time = self.time_mockup

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

        self.time.sleep = sleep_function

        timer.run()

    def test_too_long_function(self):

        self.time.time = self.time_mockup

        start_time = 4
        time_interval = 2
        timer = Timer(start_time, time_interval, None)

        def callable_function():
            self.assertEqual(self.get_current_time(), 4)
            self.time_mockup.side_effect = [7]

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


        self.time.sleep = sleep_function

        self.assertRaises(RuntimeError, timer.run)

    def test_stop(self):
        timer = Timer(None, None, None)

        self.assertEqual(timer._should_run, True)

        timer.stop()
        self.assertEqual(timer._should_run, False)



