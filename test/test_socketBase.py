from unittest import TestCase

from informationBase import SocketBase
from test.test_mockingClient import MockingClient
from socket import error as SocketError

__author__ = 'nils'


class TestSocketBase(TestCase):
    def initialize_socket(self):
        self.socket = SocketBase()
        self.mocking_client = MockingClient()
        self.socket.client = self.mocking_client

    def test_connect(self):
        socket = SocketBase()
        pass

    def initialize_sound_information(self):
        SocketBase.clientInformation.waiting_time = 23
        SocketBase.clientInformation.frame_rate = 65
        SocketBase.clientInformation.set_sound_buffer_size()

    def test_receive_buffer_with_exact_length_content(self):
        self.initialize_socket()
        self.initialize_sound_information()
        test_buffer = bytes(xrange(SocketBase.clientInformation.sound_buffer_size))
        self.mocking_client.add_out_message(test_buffer)

        result_buffer = self.socket.receive_buffer_with_exact_length()

        self.assertEqual(test_buffer, result_buffer)
        self.assertLess(SocketBase.clientInformation.sound_buffer_size, len(result_buffer))

    def test_receive_buffer_with_exact_length_no_content(self):
        self.initialize_socket()
        self.initialize_sound_information()
        test_buffer = bytes("a")
        self.mocking_client.add_out_message(test_buffer)

        self.assertRaises(SocketError, self.socket.receive_buffer_with_exact_length)

    def test_receive_buffer_with_exact_length_too_much_content(self):
        self.initialize_socket()
        self.initialize_sound_information()
        test_buffer = bytes("a")
        for i in xrange(SocketBase.clientInformation.sound_buffer_size + 20):
            self.mocking_client.add_out_message(test_buffer)

        result_buffer = self.socket.receive_buffer_with_exact_length()

        self.assertEqual(SocketBase.clientInformation.sound_buffer_size, len(result_buffer))

    def test_receive_information(self):
        self.initialize_socket()
        test_message = "test message"
        self.mocking_client.add_out_message(test_message)

        result_message = self.socket.receive_information()

        self.assertEqual("ok", self.mocking_client.get_in_message())
        self.assertEqual(SocketBase.clientInformation.information_buffer_size, self.mocking_client.last_buffer_size)
        self.assertEqual(test_message, result_message)

    def test_send_information(self):
        self.initialize_socket()

        self.mocking_client.add_out_message("ok")
        test_message = "test message"
        self.socket.send_information(test_message)

        self.assertEqual(str(test_message).encode(), self.mocking_client.get_in_message())
        self.assertEqual(SocketBase.clientInformation.information_buffer_size, self.mocking_client.last_buffer_size)
        self.assertRaises(IndexError, self.mocking_client.get_in_message)

    def test_send_ok(self):
        self.initialize_socket()
        self.socket.send_ok()

        self.assertEqual("ok", self.mocking_client.get_in_message())
        self.assertRaises(IndexError, self.mocking_client.get_in_message)

    def test_receive_ok(self):
        self.initialize_socket()

        test_message = "test message"
        self.mocking_client.add_out_message(test_message)

        self.socket.receive_information()
        self.assertEqual(SocketBase.clientInformation.information_buffer_size, self.mocking_client.last_buffer_size)

    def test_send(self):
        self.initialize_socket()

        test_message = "test message"
        test_message2 = "test message2"
        self.socket.send(test_message)
        self.socket.send(test_message2)

        self.assertEqual(test_message, self.mocking_client.get_in_message())
        self.assertEqual(test_message2, self.mocking_client.get_in_message())
        self.assertRaises(IndexError, self.mocking_client.get_in_message)

    def test_receive_default_buffer_size(self):
        self.initialize_socket()

        test_message = "test message"
        self.mocking_client.add_out_message(test_message)

        self.socket.receive()
        self.assertEqual(SocketBase.clientInformation.information_buffer_size, self.mocking_client.last_buffer_size)

    def test_receive_non_default_buffer_size(self):
        self.initialize_socket()

        test_buffer_size = 10000
        test_message = "test message"
        self.mocking_client.add_out_message(test_message)

        self.socket.receive(test_buffer_size)
        self.assertEqual(test_buffer_size, self.mocking_client.last_buffer_size)

    def test_receive(self):
        self.initialize_socket()
        test_message = "test message"
        test_message2 = "test message2"
        self.mocking_client.add_out_message(test_message)
        self.mocking_client.add_out_message(test_message2)

        result_message = self.socket.receive()
        self.assertEqual(test_message, result_message)

        result_message = self.socket.receive()
        self.assertEqual(test_message2, result_message)

    def test_close(self):
        self.initialize_socket()

        self.socket.close()

        self.assertTrue(self.mocking_client.closed)

    def test_not_closed(self):
        self.initialize_socket()

        self.assertFalse(self.mocking_client.closed)