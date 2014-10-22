from unittest import TestCase

from clientSender import ClientSender
from test.test_mockingClient import MockingClient

__author__ = 'nils'


class TestClientSender(TestCase):
    def initialize_socket(self):
        self.client = ClientSender()
        self.mocking_client = MockingClient()
        self.client.client = self.mocking_client

    def initialize_sound(self):
        ClientSender.clientInformation.set_sound_buffer_size()
        self.client.initialize_pcm(ClientSender.clientInformation.frame_rate,
                                   ClientSender.clientInformation.sound_buffer_size)

    def test_tell_server_sender_identity(self):
        self.initialize_socket()
        self.mocking_client.add_out_message("ok")

        self.client.tell_server_sender_identity()
        self.assertEqual(b"sender", self.mocking_client.get_in_message())
        self.assertEqual(0, len(self.mocking_client.last_out_message))

    def test_get_sound_data(self):
        self.initialize_socket()
        self.initialize_sound()

        result_buffer, result_length = self.client.get_sound_data()
        self.client.close_sound()

        self.assertEqual(ClientSender.clientInformation.sound_buffer_size, 4*result_length)
        self.assertEqual(4*result_length, len(result_buffer))

    def test_collect_sound_data(self):
        self.initialize_socket()
        self.initialize_sound()
        ClientSender.clientInformation.multiple_buffer_factor = 2

        test_length, test_buffer = self.client.collect_sound_data()

        self.client.close_sound()

        self.assertEqual(ClientSender.clientInformation.multiple_buffer_factor *
                         ClientSender.clientInformation.sound_buffer_size, 4*test_length)
        self.assertEqual(4*test_length, len(test_buffer))

