from sound_sync.clients.connection import SoundSyncConnection
from tests.fixtures import ServerTestCase


class TestSoundSyncConnection(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)

        self.test_port = 16347
        self.test_host = "ThisIsTheHost"

        self.connection = SoundSyncConnection()
        self.connection.host = self.test_host
        self.connection.manager_port = self.test_port

    def setUpForOwnServer(self):
        self.connection.http_client = self
        self.connection.manager_string = ""

    def test_manager_string(self):
        self.assertEqual(self.connection.manager_string, "http://" + self.test_host + ":" + str(self.test_port))

    def test_add_channel_to_server(self):
        self.setUpForOwnServer()
        channel_hash = self.connection.add_channel_to_server()

        channels = self.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels.keys()[0], channel_hash)

    def test_remove_channel_from_server(self):
        self.setUpForOwnServer()

        channel_hash = self.connection.add_channel_to_server()
        self.connection.remove_channel_from_server(channel_hash)

        channels = self.get_channels()
        self.assertEqual(len(channels), 0)

    def test_set_name_and_description_of_channel(self):
        self.setUpForOwnServer()

        channel_hash = self.connection.add_channel_to_server()
        test_description = "Test Description"
        test_name = "Test Name"
        self.connection.set_name_and_description_of_channel(test_name, test_description, channel_hash)

        channels = self.get_channels()
        self.assertEqual(len(channels), 1)
        result_channel = channels[channel_hash]

        self.assertEqual(result_channel["name"], test_name)
        self.assertEqual(result_channel["description"], test_description)

    def test_get_channel_information(self):
        self.setUpForOwnServer()

        channel_hash = self.connection.add_channel_to_server()
        test_description = "Test Description"
        test_name = "Test Name"
        self.connection.set_name_and_description_of_channel(test_name, test_description, channel_hash)

        channel_information = self.connection.get_channel_information(channel_hash)

        self.assertEqual(channel_information["channel_hash"], channel_hash)
        self.assertEqual(channel_information["name"], test_name)
        self.assertEqual(channel_information["description"], test_description)

    def test_add_client_to_server(self):
        self.setUpForOwnServer()
        client_hash = self.connection.add_client_to_server()

        clients = self.get_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients.keys()[0], client_hash)

    def test_remove_client_from_server(self):
        self.setUpForOwnServer()

        client_hash = self.connection.add_client_to_server()
        self.connection.remove_client_from_server(client_hash)

        clients = self.get_clients()
        self.assertEqual(len(clients), 0)

    def test_set_name_of_client(self):
        self.setUpForOwnServer()

        client_hash = self.connection.add_client_to_server()
        test_name = "Test Name"
        self.connection.set_name_of_client(test_name, client_hash)

        clients = self.get_clients()
        self.assertEqual(len(clients), 1)
        result_client = clients[client_hash]

        self.assertEqual(result_client["name"], test_name)
