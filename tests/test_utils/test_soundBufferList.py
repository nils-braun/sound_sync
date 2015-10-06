from unittest import TestCase

try:
    from sound_sync.buffer_server import BufferList
except ImportError:
    from buffer_server import BufferList


class TestSoundBufferList(TestCase):
    def test_add_buffer(self):
        buffer_list = BufferList(5)

        for i in xrange(2):
            buffer_list.add_buffer("Test buffer " + str(i))

        self.assertEqual(buffer_list.get_buffer("0"), "Test buffer 0")
        self.assertEqual(buffer_list.get_buffer("1"), "Test buffer 1")

        self.assertEqual(buffer_list.get_start_index(), 0)
        #self.assertEqual(buffer_list.next_free_index, 2)

        for i in xrange(8):
            buffer_list.add_buffer("Test buffer " + str(i + 2))

        self.assertEqual(buffer_list.get_buffer("5"), "Test buffer 5")
        self.assertEqual(buffer_list.get_buffer("6"), "Test buffer 6")
        self.assertEqual(buffer_list.get_buffer("7"), "Test buffer 7")
        self.assertEqual(buffer_list.get_buffer("8"), "Test buffer 8")
        self.assertEqual(buffer_list.get_buffer("9"), "Test buffer 9")

        self.assertEqual(buffer_list.get_start_index(), 5)
        self.assertEqual(buffer_list.get_next_free_index(), 10)

    def test_get_buffer(self):
        buffer_list = BufferList(5)
        for i in xrange(10):
            buffer_list.add_buffer("Test buffer " + str(i))

        self.assertEqual(buffer_list.get_buffer("5"), "Test buffer 5")
        self.assertEqual(buffer_list.get_buffer("7"), "Test buffer 7")
        self.assertEqual(buffer_list.get_buffer("9"), "Test buffer 9")

        self.assertRaises(RuntimeError, buffer_list.get_buffer, "4")
        self.assertRaises(RuntimeError, buffer_list.get_buffer, "10")

    def test_get_start_index(self):
        buffer_list = BufferList(5)
        self.assertEqual(buffer_list.get_start_index(), 0)

    def test_add_buffer_with_number(self):
        buffer_list = BufferList(5)

        buffer_list.set_start_index(100)

        buffer_list.add_buffer("Test buffer 100")
        buffer_list.add_buffer("Test buffer 101")

        self.assertEqual(buffer_list.get_buffer("100"), "Test buffer 100")
        self.assertEqual(buffer_list.get_buffer("101"), "Test buffer 101")

        self.assertEqual(buffer_list.get_start_index(), 100)
        self.assertEqual(buffer_list.get_next_free_index(), 102)

        for i in xrange(8):
            buffer_list.add_buffer("Test buffer " + str(i + 102))

        self.assertEqual(buffer_list.get_buffer("105"), "Test buffer 105")
        self.assertEqual(buffer_list.get_buffer("106"), "Test buffer 106")
        self.assertEqual(buffer_list.get_buffer("107"), "Test buffer 107")
        self.assertEqual(buffer_list.get_buffer("108"), "Test buffer 108")
        self.assertEqual(buffer_list.get_buffer("109"), "Test buffer 109")

        self.assertEqual(buffer_list.get_start_index(), 105)
        self.assertEqual(buffer_list.get_next_free_index(), 110)