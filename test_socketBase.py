from unittest import TestCase
from informationBase import SocketBase


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
        self.mocking_client.last_out_message = test_buffer

        result_buffer = self.socket.receive_buffer_with_exact_length()

        self.assertEqual(result_buffer, test_buffer)
        self.assertGreater(len(result_buffer), SocketBase.clientInformation.sound_buffer_size)

    def test_receive_buffer_with_exact_length_no_content(self):
        self.initialize_socket()
        self.initialize_sound_information()
        test_buffer = bytes("a")
        self.mocking_client.last_out_message = test_buffer

        result_buffer = self.socket.receive_buffer_with_exact_length()

        self.assertEqual(result_buffer, None)

    def test_receive_information(self):
        self.initialize_socket()
        test_message = "test message"
        self.mocking_client.last_out_message = test_message

        result_message = self.socket.receive_information()

        self.assertEqual(self.mocking_client.last_in_message, "ok")
        self.assertEqual(self.mocking_client.last_buffer_size, SocketBase.clientInformation.information_buffer_size)
        self.assertEqual(result_message, test_message)

    def test_send_information(self):
        self.initialize_socket()
        test_message = "test message"
        self.socket.send_information(test_message)

        self.assertEqual(self.mocking_client.last_in_message, str(test_message).encode())
        self.assertEqual(self.mocking_client.last_buffer_size, SocketBase.clientInformation.information_buffer_size)

    def test_send_ok(self):
        self.initialize_socket()
        self.socket.send_ok()

        self.assertEqual(self.mocking_client.last_in_message, "ok")

    def test_receive_ok(self):
        self.initialize_socket()
        self.socket.receive_information()
        self.assertEqual(self.mocking_client.last_buffer_size, SocketBase.clientInformation.information_buffer_size)

    def test_send(self):
        self.initialize_socket()

        test_message = "test message"
        self.socket.send(test_message)

        self.assertEqual(self.mocking_client.last_in_message, test_message)

    def test_receive_default_buffer_size(self):
        self.initialize_socket()

        self.socket.receive()
        self.assertEqual(self.mocking_client.last_buffer_size, SocketBase.clientInformation.information_buffer_size)

    def test_receive_non_default_buffer_size(self):
        self.initialize_socket()

        test_buffer_size = 10000

        self.socket.receive(test_buffer_size)
        self.assertEqual(self.mocking_client.last_buffer_size, test_buffer_size)

    def test_receive(self):
        self.initialize_socket()
        test_message = "test message"
        self.mocking_client.last_out_message = test_message

        result_message = self.socket.receive()
        self.assertEqual(result_message, test_message)

    def test_close(self):
        self.initialize_socket()

        self.socket.close()

        self.assertTrue(self.mocking_client.closed)

    def test_not_closed(self):
        self.initialize_socket()

        self.assertFalse(self.mocking_client.closed)


class MockingClient:
    def __init__(self):
        self.last_in_message = ""
        self.last_out_message = ""
        self.last_buffer_size = 0
        self.closed = False

    def sendall(self, message):
        self.last_in_message = message

    def recv(self, buffer_size):
        self.last_buffer_size = buffer_size
        tmp = self.last_out_message
        self.last_out_message = ""
        return tmp

    def close(self):
        self.closed = True