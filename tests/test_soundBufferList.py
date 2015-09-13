from unittest import TestCase
from sound_sync.sound_buffer_list import SoundBufferList


class TestSoundBufferList(TestCase):
    def test_add_buffer(self):
        buffer_list = SoundBufferList(5)

        for i in xrange(2):
            buffer_list.add_buffer("Test buffer " + str(i))

        self.assertEqual(len(buffer_list.deque), 2)
        self.assertEqual(buffer_list.deque[0], (0, "Test buffer 0"))
        self.assertEqual(buffer_list.deque[1], (1, "Test buffer 1"))

        self.assertEqual(buffer_list.start_index, 0)
        self.assertEqual(buffer_list.next_free_index, 2)

        for i in xrange(8):
            buffer_list.add_buffer("Test buffer " + str(i + 2))

        self.assertEqual(len(buffer_list.deque), 5)
        self.assertEqual(buffer_list.deque[0][1], "Test buffer 5")
        self.assertEqual(buffer_list.deque[1][1], "Test buffer 6")
        self.assertEqual(buffer_list.deque[2][1], "Test buffer 7")
        self.assertEqual(buffer_list.deque[3][1], "Test buffer 8")
        self.assertEqual(buffer_list.deque[4], (9, "Test buffer 9"))

        self.assertEqual(buffer_list.start_index, 5)
        self.assertEqual(buffer_list.next_free_index, 10)

    def test_get_buffer(self):
        buffer_list = SoundBufferList(5)
        for i in xrange(10):
            buffer_list.add_buffer("Test buffer " + str(i))

        self.assertEqual(buffer_list.get_buffer(5), "Test buffer 5")
        self.assertEqual(buffer_list.get_buffer(7), "Test buffer 7")
        self.assertEqual(buffer_list.get_buffer(9), "Test buffer 9")

        self.assertRaises(KeyError, buffer_list.get_buffer, 4)
        self.assertRaises(KeyError, buffer_list.get_buffer, 10)

    def test_get_start_index(self):
        buffer_list = SoundBufferList(5)
        self.assertEqual(buffer_list.start_index, 0)