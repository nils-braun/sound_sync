import base64
from unittest import TestCase
from sound_sync.entities.buffer_list import BufferList
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import to_datetime


class TestSoundBufferList(TestCase):
    def setUp(self):
        self.max_buffer_size = 5
        self.buffer_list = BufferList(self.max_buffer_size)

    def test_add_buffer(self, start_index=0):

        test_buffer = SoundBufferWithTime(b"", 1, to_datetime("2016-11-27 21:31:00")).to_string()

        self.buffer_list.set_start_index(start_index)
        self.assertEqual(self.buffer_list.get_next_free_index(), start_index)

        first_index = 2
        for i in range(first_index):
            self.buffer_list.add_buffer(test_buffer + str(i))

        for i in range(first_index):
            self.assertEqual(self.buffer_list.get_buffer(str(i + start_index)), test_buffer + str(i))

        self.assertEqual(self.buffer_list.get_start_index(), start_index)
        self.assertEqual(self.buffer_list.get_next_free_index(), first_index + start_index)

        second_index = 8
        for i in range(second_index):
            self.buffer_list.add_buffer(test_buffer + str(i + first_index))

        for i in range(-self.max_buffer_size, 0):
            self.assertEqual(self.buffer_list.get_buffer(str(start_index + first_index + second_index + i)),
                             test_buffer + str(first_index + second_index + i))

        self.assertEqual(self.buffer_list.get_start_index(), self.max_buffer_size + start_index)
        self.assertEqual(self.buffer_list.get_next_free_index(), first_index + second_index + start_index)

        self.assertRaisesRegexp(RuntimeError, "^Wrong buffer index number$", self.buffer_list.get_buffer, "0")

    def test_add_buffer_with_number(self):
        self.test_add_buffer(start_index=148)

    def test_get_buffer(self):
        for i in range(10):
            self.buffer_list.add_buffer(bytes("Test buffer " + str(i), encoding="utf8"))

        self.assertEqual(self.buffer_list.get_buffer("5"), b"Test buffer 5")
        self.assertEqual(self.buffer_list.get_buffer("7"), b"Test buffer 7")
        self.assertEqual(self.buffer_list.get_buffer("9"), b"Test buffer 9")

        self.assertRaises(RuntimeError, self.buffer_list.get_buffer, "4")
        self.assertRaises(RuntimeError, self.buffer_list.get_buffer, "10")

    def test_get_start_index(self):
        self.assertEqual(self.buffer_list.get_start_index(), 0)

        test_start_index = 10
        self.buffer_list.set_start_index(test_start_index)
        self.assertEqual(self.buffer_list.get_start_index(), test_start_index)
