from unittest import TestCase

from listHandler import ClientListHandler, EmptyException, IndexToLowException, IndexToHighException

__author__ = 'nilpferd'


class TestClientListHandler(TestCase):

    def initialize_list(self):
        self.client_list = ClientListHandler()
        self.test_socket = "test socket"
        self.test_socket_2 = "test socket 2"
        self.test_buffer = "test buffer"

    def initialize_listener(self):
        self.client_list.add_listener(self.test_socket)

    def initialize_sender(self):
        self.client_list.add_sender(self.test_socket)

    def test_add_sender(self):
        self.initialize_list()
        self.initialize_sender()

        self.assertTrue(self.client_list.is_sender(self.test_socket))
        self.assertFalse(self.client_list.no_sender())
        self.assertFalse(self.client_list.is_listener(self.test_socket))

    def test_add_listener(self):
        self.initialize_list()
        self.initialize_listener()

        self.client_list.add_buffer("test")

        self.assertTrue(self.client_list.is_listener(self.test_socket))
        self.assertEqual(0, self.client_list.get_buffer_index(self.test_socket))
        self.assertFalse(self.client_list.is_sender(self.test_socket))
        self.assertTrue(self.client_list.no_sender())

    def test_add_buffer(self):
        self.initialize_list()

        self.assertTrue(self.client_list.is_empty())

        self.client_list.add_buffer(self.test_buffer)
        self.assertFalse(self.client_list.is_empty())
        self.assertTrue(self.test_buffer in self.client_list.buffers)
        self.assertEqual(1, len(self.client_list.buffers))
        self.assertEqual(0, self.client_list.start_buffer_index)
        self.assertEqual(0, self.client_list.end_buffer_index)

        for _ in xrange(8):
            self.client_list.add_buffer(self.test_buffer)

        self.assertEqual(9, len(self.client_list.buffers))
        self.assertEqual(0, self.client_list.start_buffer_index)
        self.assertEqual(8, self.client_list.end_buffer_index)

        for _ in xrange(101):
            self.client_list.add_buffer(self.test_buffer)

        self.assertFalse(self.client_list.is_empty())
        self.assertEqual(50, len(self.client_list.buffers))
        self.assertEqual(60, self.client_list.start_buffer_index)
        self.assertEqual(109, self.client_list.end_buffer_index)

    def test_get_buffer_index(self):
        self.initialize_list()
        self.initialize_listener()

        self.client_list.add_buffer("test")

        self.assertEqual(0, self.client_list.get_buffer_index(self.test_socket))

    def test_get_buffer_by_buffer_index(self):
        self.initialize_list()

        self.assertRaises(EmptyException, self.client_list.get_buffer_by_buffer_index, 20)

        for i in xrange(200):
            self.client_list.add_buffer(i)

        self.assertRaises(IndexToLowException, self.client_list.get_buffer_by_buffer_index, 10)
        self.assertRaises(IndexToHighException, self.client_list.get_buffer_by_buffer_index, 200)
        self.assertRaises(IndexToLowException, self.client_list.get_buffer_by_buffer_index, 149)

        self.assertEqual(199, self.client_list.get_buffer_by_buffer_index(199))
        self.assertEqual(190, self.client_list.get_buffer_by_buffer_index(190))

    def test_remove_sender(self):
        self.initialize_list()
        self.initialize_sender()

        self.client_list.remove_sender()

        self.assertTrue(self.client_list.no_sender())
        self.assertFalse(self.client_list.is_sender(self.test_socket))

    def test_remove_listener(self):
        self.initialize_list()
        self.initialize_listener()

        self.client_list.remove_listener(self.test_socket)
        self.assertFalse(self.client_list.is_listener(self.test_socket))

        self.client_list.remove_listener(self.test_socket_2)
        self.assertFalse(self.client_list.is_listener(self.test_socket_2))