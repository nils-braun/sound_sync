from unittest import TestCase

from clientBase import ClientBase
from test.test_mockingClient import MockingClient

__author__ = 'nils'


class TestClientBase(TestCase):
    def initialize_socket(self):
        self.client = ClientBase()
        self.mocking_client = MockingClient()
        self.client.client = self.mocking_client

    def initialize_sound_information(self):
        ClientBase.clientInformation.waiting_time = 23
        ClientBase.clientInformation.frame_rate = 65
        ClientBase.clientInformation.set_sound_buffer_size()

    def test_read_values_from_server(self):
        self.initialize_socket()
        test_frame_rate = 15343
        test_waiting_time = 59845
        test_start_time = 59845
        self.mocking_client.add_out_message(test_frame_rate)
        self.mocking_client.add_out_message(test_waiting_time)
        self.mocking_client.add_out_message(test_start_time)

        self.client.read_values_from_server()

        self.assertEqual(ClientBase.clientInformation.frame_rate, test_frame_rate)
        self.assertEqual(ClientBase.clientInformation.waiting_time, test_waiting_time)
        self.assertEqual(self.client.start_time, test_start_time)
        self.assertEqual(0, len(self.mocking_client.last_out_message))
        self.assertEqual("ok", self.mocking_client.get_in_message())
        self.assertEqual("ok", self.mocking_client.get_in_message())
        self.assertEqual("ok", self.mocking_client.get_in_message())
        self.assertRaises(IndexError, self.mocking_client.get_in_message)

    def test_send_values_to_server(self):
        self.initialize_socket()
        self.initialize_sound_information()
        self.mocking_client.add_out_message("ok")
        self.mocking_client.add_out_message("ok")

        self.client.send_values_to_server()

        self.assertEqual(ClientBase.clientInformation.frame_rate, int(self.mocking_client.get_in_message()))
        self.assertEqual(ClientBase.clientInformation.multiple_buffer_factor *
                         ClientBase.clientInformation.waiting_time, int(self.mocking_client.get_in_message()))
        self.assertRaises(IndexError, self.mocking_client.get_in_message)
        self.assertEqual(0, len(self.mocking_client.last_out_message))
        self.assertEqual(ClientBase.clientInformation.information_buffer_size, self.mocking_client.last_buffer_size)