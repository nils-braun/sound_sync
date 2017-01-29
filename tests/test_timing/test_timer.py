from datetime import datetime
from mock import MagicMock
from sound_sync.timing.lowres_timer import LowResolutionTimer

from sound_sync.timing.timer import Timer
from tests.fixtures import TimingTestCase


def case_factory(timer_class):
    class TestTimer(TimingTestCase):
        def test_not_fail_for_future_values(self):
            self.time_mock.sleep = None

            start_time = datetime(2015, 11, 6, 0, 0, 0)

            self.datetime_mock.datetime.utcnow = MagicMock(return_value=datetime(2015, 11, 4, 0, 0, 0))

            # This should not fail
            timer_class(start_time, None)

        def test_fail_for_past_values(self):
            self.time_mock.sleep = None

            start_time = datetime(2015, 11, 6, 0, 0, 0)
            self.datetime_mock.datetime.utcnow = MagicMock(return_value=datetime(2015, 11, 6, 0, 0, 2))

            self.assertRaisesRegexp(ValueError, "Can not handle a start time in the past.", timer_class, start_time, None)

        def test_stop_before_run(self):
            self.datetime_mock.datetime.utcnow = self.time_list_mock_function

            start_time = datetime(2015, 11, 6, 0, 0, 2)
            timer = timer_class(start_time, None)

            self.assertEqual(timer.is_finished(), False)

            timer.cancel()
            self.assertEqual(timer.is_finished(), True)

        def test_stop_while_run(self):
            self.datetime_mock.datetime.utcnow = self.time_list_mock_function

            start_time = datetime(2015, 11, 6, 0, 0, 2)
            timer = timer_class(start_time, None)

            timer.start()

            self.assertEqual(timer.is_finished(), False)

            timer.cancel()
            self.assertEqual(timer.is_finished(), True)

        def test_always_run(self):
            self.datetime_mock.datetime.utcnow = self.time_list_mock_function
            
            start_time = datetime(2014, 1, 1, 0, 0, 1)

            target_function = MagicMock()

            timer = timer_class(start_time, target_function, always_run=True)
            timer.start()

            target_function.assert_called()

    return TestTimer

TestHighResTimer = case_factory(Timer)
TestLowResTimer = case_factory(LowResolutionTimer)
