from unittest import TestCase

try:
    from sound_sync.buffer_server import BufferList
except ImportError:
    from buffer_server import BufferList


class TestSoundBufferList(TestCase):
    def setUp(self):
        self.max_buffer_size = 5
        self.buffer_list = BufferList(self.max_buffer_size)

    def test_add_buffer(self, start_index=0):

        test_buffer = "Test buffer"

        self.buffer_list.set_start_index(start_index)

        first_index = 2
        for i in xrange(first_index):
            self.buffer_list.add_buffer(test_buffer + str(i))

        for i in xrange(first_index):
            self.assertEqual(self.buffer_list.get_buffer(str(i + start_index)), test_buffer + str(i))

        self.assertEqual(self.buffer_list.get_start_index(), start_index)
        self.assertEqual(self.buffer_list.get_next_free_index(), first_index + start_index)

        second_index = 8
        for i in xrange(second_index):
            self.buffer_list.add_buffer(test_buffer + str(i + first_index))

        for i in xrange(-self.max_buffer_size, 0):
            self.assertEqual(self.buffer_list.get_buffer(str(start_index + first_index + second_index + i)),
                             test_buffer + str(first_index + second_index + i))

        self.assertEqual(self.buffer_list.get_start_index(), self.max_buffer_size + start_index)
        self.assertEqual(self.buffer_list.get_next_free_index(), first_index + second_index + start_index)

        self.assertRaisesRegexp(RuntimeError, "^Wrong buffer index number$", self.buffer_list.get_buffer, "0")

    def test_add_buffer_with_number(self):
        self.test_add_buffer(start_index=148)

    def test_get_buffer(self):
        for i in xrange(10):
            self.buffer_list.add_buffer("Test buffer " + str(i))

        self.assertEqual(self.buffer_list.get_buffer("5"), "Test buffer 5")
        self.assertEqual(self.buffer_list.get_buffer("7"), "Test buffer 7")
        self.assertEqual(self.buffer_list.get_buffer("9"), "Test buffer 9")

        self.assertRaises(RuntimeError, self.buffer_list.get_buffer, "4")
        self.assertRaises(RuntimeError, self.buffer_list.get_buffer, "10")

    def test_get_start_index(self):
        self.assertEqual(self.buffer_list.get_start_index(), 0)
