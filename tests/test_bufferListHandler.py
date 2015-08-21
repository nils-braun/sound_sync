from unittest import TestCase

from sound_sync.buffer_list import BufferList


__author__ = 'nils'


class TestBufferListHandler(TestCase):
    def test_add_buffer(self):
        buffer_list_handler = BufferList(max_buffer_length=4)

        buffer_list_handler.add_buffer("test0")
        buffer_list_handler.add_buffer("test1")
        buffer_list_handler.add_buffer("test2")
        buffer_list_handler.add_buffer("test3")

        self.assertEqual(buffer_list_handler.start_buffer_index, 0)
        self.assertEqual(buffer_list_handler.end_buffer_index, 3)
        self.assertEqual(len(buffer_list_handler.buffers), 4)

        buffer_list_handler.add_buffer("test4")

        self.assertEqual(buffer_list_handler.start_buffer_index, 1)
        self.assertEqual(buffer_list_handler.end_buffer_index, 4)
        self.assertEqual(len(buffer_list_handler.buffers), 4)

        buffer_list_handler.add_buffer("test4")

        self.assertEqual(buffer_list_handler.start_buffer_index, 2)
        self.assertEqual(buffer_list_handler.end_buffer_index, 5)
        self.assertEqual(len(buffer_list_handler.buffers), 4)

    def test_is_empty(self):
        buffer_list_handler = BufferList()

        self.assertTrue(buffer_list_handler.is_empty())

        buffer_list_handler.add_buffer("test")

        self.assertFalse(buffer_list_handler.is_empty())

    def test_get_buffer_by_buffer_index(self):
        buffer_list_handler = BufferList(max_buffer_length=4)

        buffer_list_handler.add_buffer("test0")
        buffer_list_handler.add_buffer("test1")
        buffer_list_handler.add_buffer("test2")
        buffer_list_handler.add_buffer("test3")

        self.assertEqual(buffer_list_handler.get_buffer_by_buffer_index(0), "test0")
        self.assertEqual(buffer_list_handler.get_buffer_by_buffer_index(1), "test1")
        self.assertEqual(buffer_list_handler.get_buffer_by_buffer_index(2), "test2")
        self.assertEqual(buffer_list_handler.get_buffer_by_buffer_index(3), "test3")

        buffer_list_handler.add_buffer("test4")
        self.assertEqual(buffer_list_handler.get_buffer_by_buffer_index(4), "test4")

        self.assertRaises(IndexError, buffer_list_handler.get_buffer_by_buffer_index, 0)
        self.assertRaises(IndexError, buffer_list_handler.get_buffer_by_buffer_index, 5)