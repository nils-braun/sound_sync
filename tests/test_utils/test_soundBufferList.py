from unittest import TestCase
from sound_sync.entities.buffer_list import OrderedBufferList, RingBufferList

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import get_current_date


class TestOrderedBufferList(TestCase):
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

    def test_buffer_overflow(self):
        self.buffer_list.append(self.buffer_examples[3])

        self.assertRaises(IndexError, self.buffer_list.append, self.buffer_examples[9])


class RingBufferTestCase(TestCase):
    def test_normal_operation(self):
        buffer = RingBufferList(5)

        self.assertRaises(IndexError, lambda: buffer[0])

        buffer.append("1")

        self.assertEqual(buffer[0], "1")

        self.assertRaises(IndexError, lambda: buffer[1])
        self.assertRaises(IndexError, lambda: buffer[11])

    def test_buffer_goes_round(self):
        buffer = RingBufferList(3)

        buffer.append("1")
        buffer.append("2")
        buffer.append("3")
        buffer.append("4")

        self.assertEqual(buffer[0], "2")
        self.assertEqual(buffer[1], "3")
        self.assertEqual(buffer[2], "4")

    def test_buffer_overflow(self):
        buffer = RingBufferList(100)

        for i in range(100):
            buffer.append(i)

        self.assertEqual(buffer[99], 99)

        self.assertRaises(IndexError, lambda: buffer[100])