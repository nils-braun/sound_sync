from unittest import TestCase

from clientSender import ClientSender
from test.test_mockingClient import MockingClient, MockingPCM

__author__ = 'nils'


class TestClientSender(TestCase):
    def initialize_socket(self):
        self.client = ClientSender()
        self.mocking_client = MockingClient()
        self.client.client = self.mocking_client

    def initialize_sound_mocking(self):
        ClientSender.clientInformation.set_sound_buffer_size()
        self.mocking_pcm = MockingPCM()
        self.client.pcm = self.mocking_pcm()
        self.mocking_pcm.sound_buffer_size = ClientSender.clientInformation.sound_buffer_size

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

        self.assertEqual(ClientSender.clientInformation.sound_buffer_size, ClientSender.clientInformation.multiple_buffer_factor * len(result_buffer))
        self.assertEqual(self.client.get_attribute("sound_data_size")*result_length, len(result_buffer))

    def test_collect_sound_data(self):
        self.initialize_socket()
        self.initialize_sound()
        ClientSender.clientInformation.multiple_buffer_factor = 2

        test_length, test_buffer = self.client.collect_sound_data()

        self.client.close_sound()

        self.assertEqual(ClientSender.clientInformation.sound_buffer_size, len(test_buffer))
        self.assertEqual(self.client.get_attribute("sound_data_size")*test_length, len(test_buffer))

    def test_collect_and_send_sound_data(self):
        self.initialize_socket()
        self.initialize_sound_mocking()
        # TODO initialize with correct buffer size!
        self.fail()
        test_message = "test message"
        self.mocking_pcm.add_message(test_message)
        self.mocking_pcm.add_message(test_message)
        ClientSender.clientInformation.multiple_buffer_factor = 2
        self.client.set_sound_buffer_size()
        
        self.client.collect_and_send_sound_data()

        self.client.close_sound()
        
        self.assertEqual(ClientSender.clientInformation.sound_buffer_size, len(self.mocking_client.get_in_message())

