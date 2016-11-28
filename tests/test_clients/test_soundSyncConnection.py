from unittest import TestCase

from sound_sync.clients.connection import SoundSyncConnection
from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.timing.time_utils import get_current_date
from tests.fixtures import SoundSyncConnectionTestCase
from tornado.httpclient import HTTPError


class TestSoundSyncConnectionWithoutMock(TestCase):
    def test_manager_string(self):
        test_port = 16347
        test_host = "ThisIsTheHost"

        connection = SoundSyncConnection()
        connection.host = test_host
        connection.manager_port = test_port

        self.assertEqual(connection.manager_string, "http://" + test_host + ":" + str(test_port))


class TestSoundSyncConnection(SoundSyncConnectionTestCase):
    def test_add_channel_to_server(self):
        channel_hash = self.connection.add_channel_to_server()

        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)
        print(channels.keys())
        self.assertEqual(list(channels.keys()), [channel_hash])

    def test_remove_channel_from_server(self):
        channel_hash = self.connection.add_channel_to_server()
        self.connection.remove_channel_from_server(channel_hash)

        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 0)

    def test_set_name_and_description_of_channel(self):
        channel_hash = self.connection.add_channel_to_server()
        test_description = "Test Description"
        test_name = "Test Name"
        self.connection.set_name_and_description_of_channel(test_name, test_description, channel_hash)

        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)
        result_channel = channels[channel_hash]

        self.assertEqual(result_channel["name"], test_name)
        self.assertEqual(result_channel["description"], test_description)

    def test_get_channel_information(self):
        channel_hash = self.connection.add_channel_to_server()
        test_description = "Test Description"
        test_name = "Test Name"
        self.connection.set_name_and_description_of_channel(test_name, test_description, channel_hash)

        channel_information = self.connection.get_channel_information(channel_hash)

        self.assertEqual(channel_information["channel_hash"], channel_hash)
        self.assertEqual(channel_information["name"], test_name)
        self.assertEqual(channel_information["description"], test_description)

    def test_add_client_to_server(self):
        client_hash = self.connection.add_client_to_server()

        clients = self.connection.get_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(list(clients.keys()), [client_hash])

    def test_remove_client_from_server(self):
        client_hash = self.connection.add_client_to_server()
        self.connection.remove_client_from_server(client_hash)

        clients = self.connection.get_clients()
        self.assertEqual(len(clients), 0)

    def test_set_name_of_client(self):
        client_hash = self.connection.add_client_to_server()
        test_name = "Test Name"
        self.connection.set_name_of_client(test_name, client_hash)

        clients = self.connection.get_clients()
        self.assertEqual(len(clients), 1)
        result_client = clients[client_hash]

        self.assertEqual(result_client["name"], test_name)

    def test_add_buffer(self):
        channel_hash = self.connection.add_client_to_server()

        test_buffer = SoundBufferWithTime(sound_buffer=b"\00\01\02", buffer_number=42, buffer_time=get_current_date())

        self.connection.add_buffer(test_buffer, channel_hash)

        self.assertEqual(self.connection.get_start_index(channel_hash), 0)
        self.assertEqual(self.connection.get_end_index(channel_hash), 1)

        self.assertEqual(self.connection.get_buffer(0, channel_hash), test_buffer)

        self.assertRaisesRegex(HTTPError, "502: Bad Gateway", self.connection.get_buffer,
                               2, channel_hash)