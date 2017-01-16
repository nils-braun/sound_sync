from unittest import TestCase
from sound_sync.entities.buffer_list import OrderedBufferList

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import get_current_date


class TestSoundBufferList(TestCase):
    def setUp(self):
        self.max_buffer_size = 5
        self.buffer_list = OrderedBufferList(self.max_buffer_size)

        self.buffer_examples = [SoundBufferWithTime(b"test", i, get_current_date()) for i in range(10)]

    def test_normal_store_and_receive(self):
        self.buffer_list.append(self.buffer_examples[0])
        self.buffer_list.append(self.buffer_examples[1])

        self.assertEqual(self.buffer_list.pop().buffer_number, 0)
        self.assertEqual(self.buffer_list.pop().buffer_number, 1)

        self.assertRaises(IndexError, self.buffer_list.pop)

    def test_doubled_store_and_receive(self):
        self.buffer_list.append(self.buffer_examples[0])
        self.buffer_list.append(self.buffer_examples[1])
        self.buffer_list.append(self.buffer_examples[0])
        self.buffer_list.append(self.buffer_examples[1])
        self.buffer_list.append(self.buffer_examples[1])
        self.buffer_list.append(self.buffer_examples[2])

        self.assertEqual(self.buffer_list.pop().buffer_number, 0)
        self.assertEqual(self.buffer_list.pop().buffer_number, 1)
        self.assertEqual(self.buffer_list.pop().buffer_number, 2)

        self.assertRaises(IndexError, self.buffer_list.pop)

    def test_store_and_receive_mixed(self):
        self.buffer_list.append(self.buffer_examples[1])
        self.buffer_list.append(self.buffer_examples[2])

        self.assertEqual(self.buffer_list.pop().buffer_number, 1)

        # will be below first item -> should be dismissed
        self.buffer_list.append(self.buffer_examples[0])
        self.buffer_list.append(self.buffer_examples[2])
        self.buffer_list.append(self.buffer_examples[3])

        self.assertEqual(self.buffer_list.pop().buffer_number, 2)

        self.buffer_list.append(self.buffer_examples[4])

        self.assertEqual(self.buffer_list.pop().buffer_number, 3)
        self.assertEqual(self.buffer_list.pop().buffer_number, 4)

        self.assertRaises(IndexError, self.buffer_list.pop)

    def test_is_continuous(self):
        self.buffer_list.append(self.buffer_examples[2])

        self.assertTrue(self.buffer_list.is_continuous_until(0))
        self.assertFalse(self.buffer_list.is_continuous_until(1))
        self.assertFalse(self.buffer_list.is_continuous_until(10))

        self.buffer_list.append(self.buffer_examples[4])

        self.assertTrue(self.buffer_list.is_continuous_until(0))
        self.assertFalse(self.buffer_list.is_continuous_until(1))
        self.assertFalse(self.buffer_list.is_continuous_until(2))

        self.buffer_list.append(self.buffer_examples[3])

        self.assertTrue(self.buffer_list.is_continuous_until(0))
        self.assertTrue(self.buffer_list.is_continuous_until(1))
        self.assertTrue(self.buffer_list.is_continuous_until(2))
        self.assertFalse(self.buffer_list.is_continuous_until(3))

    def test_buffer_overflow(self):
        self.buffer_list.append(self.buffer_examples[3])

        self.assertRaises(IndexError, self.buffer_list.append, self.buffer_examples[9])