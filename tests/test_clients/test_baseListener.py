import urllib

from mock import MagicMock

from sound_sync.clients.base_listener import BaseListener
from sound_sync.rest_server.server_items.server_items import Channel
from tests.fixtures import ListenerTestCase,  ServerTestCase


class TestBaseListener(ListenerTestCase, ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        ListenerTestCase.setUp(self)

    def test_terminate_with_none(self):
        listener, connection = self.init_own_listener(manager_server=self)
        self.assertEqual(self, connection.http_client)

        listener.player.terminate = MagicMock()

        # Should not fail, as client hash is None
        self.assertEqual(listener.client_hash, None)
        listener.terminate()

        self.assertEqual(listener.player.terminate.call_count, 0)

    def test_terminate(self):
        listener, connection = self.init_own_listener(manager_server=self)
        self.assertEqual(self, connection.http_client)

        listener.player.terminate = MagicMock()

        client_hash = connection.add_client_to_server()
        listener.client_hash = client_hash

        clients = self.get_clients()
        self.assertEqual(len(clients), 1)

        listener.terminate()

        clients = self.get_clients()
        self.assertEqual(len(clients), 0)

        self.assertEqual(listener.client_hash, None)
        listener.player.terminate.assert_called_once_with()

    def test_handler_string(self):
        listener, connection = self.init_own_listener()
        listener.connection.host = self.test_host
        self.assertRaises(ValueError, getattr, listener, "handler_string")

        test_handler_port = 54654
        listener._connected_channel = Channel()
        listener._connected_channel.handler_port = test_handler_port

        self.assertEqual(listener.handler_string, "http://" + self.test_host + ":" + str(test_handler_port))

    def test_get_settings(self):
        listener, connection = self.init_own_listener(manager_server=self)

        self.assertRaises(ValueError, listener.get_settings)

        channel_hash = connection.add_channel_to_server()
        client_hash = connection.add_client_to_server()
        listener.client_hash = client_hash
        listener.channel_hash = channel_hash

        # Change recorder settings and handler port
        body = urllib.parse.urlencode({"handler_port": "64567", "channels": "5", "buffer_size": "34"})
        self.set_channel_html(body, channel_hash)

        listener.get_settings()

        # Check player settings and handler port
        self.assertEqual(listener._connected_channel.handler_port, "64567")
        self.assertEqual(listener._connected_channel.channel_hash, channel_hash)
        self.assertEqual(listener.player.channels, "5")
        self.assertEqual(listener.player.buffer_size, "34")

    def test_initialize(self):
        listener, connection = self.init_own_listener(manager_server=self)

        listener.player.initialize = MagicMock()

        self.assertRaises(ValueError, listener.initialize)

        channel_hash = connection.add_channel_to_server()
        listener.channel_hash = channel_hash

        listener.initialize()

        clients = self.get_clients()
        self.assertEqual(len(clients), 1)
        self.assertIn(listener.client_hash, clients)
        result_client = clients[listener.client_hash]
        self.assertEqual(result_client["name"], self.test_name)
        self.assertEqual(listener.player.initialize.call_count, 1)

        # Doing the same twice should not harm
        listener.initialize()
        self.assertEqual(listener.player.initialize.call_count, 1)
        clients = self.get_clients()
        self.assertEqual(len(clients), 1)

    def test_mainloop(self):
        listener = BaseListener()
        self.assertRaises(AssertionError, listener.main_loop)

        listener.client_hash = "123"
        listener.player_thread = MagicMock()
        listener.downloader_thread = MagicMock()

        listener.main_loop()

        self.assertTrue(listener.player_thread.run.called_only_once_with())
        self.assertTrue(listener.player_thread.run.called_only_once_with())