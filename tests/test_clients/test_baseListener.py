from mock import MagicMock

from sound_sync.clients.base_listener import BaseListener
from tests.fixtures import ListenerTestCase,  ServerTestCase

from contextlib import contextmanager
from io import StringIO
import sys

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class TestBaseListener(ListenerTestCase, ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        ListenerTestCase.setUp(self)

    def test_terminate_with_none(self):
        listener = self.init_own_listener()
        listener.player.terminate = MagicMock()

        # Should not fail, as client hash is None
        self.assertEqual(listener.client_hash, None)
        listener.terminate()

        self.assertEqual(listener.player.terminate.call_count, 0)

    def test_terminate(self):
        listener = self.init_own_listener()
        listener.player.terminate = MagicMock()

        client_hash = self.connection.add_client_to_server()
        listener.client_hash = client_hash

        clients = self.connection.get_clients()
        self.assertEqual(len(clients), 1)

        listener.terminate()

        clients = self.connection.get_clients()
        self.assertEqual(len(clients), 0)

        self.assertEqual(listener.client_hash, None)
        listener.player.terminate.assert_called_once_with()

    def test_get_settings(self):
        listener = self.init_own_listener()

        self.assertRaises(ValueError, listener.get_settings)

        channel_hash = self.connection.add_channel_to_server()
        client_hash = self.connection.add_client_to_server()
        listener.client_hash = client_hash
        listener.channel_hash = channel_hash

        # Change recorder settings and handler port
        body = {"channels": "5", "buffer_size": "34"}
        self.connection.set_parameters_of_channel(body, channel_hash)

        listener.get_settings()

        # Check player settings and handler port
        self.assertEqual(listener._connected_channel.channel_hash, channel_hash)
        self.assertEqual(listener.player.channels, "5")
        self.assertEqual(listener.player.buffer_size, "34")

    def test_print_all_channels(self):
        listener = self.init_own_listener()

        with captured_output() as (out, err):
            listener.print_all_channels()

        self.assertEqual(out.getvalue(), "")

        channel_hash = self.connection.add_channel_to_server()

        with captured_output() as (out, err):
            listener.print_all_channels()

        return_dict = out.getvalue()

        self.assertIn(channel_hash, return_dict)

        second_channel_hash = self.connection.add_channel_to_server()

        with captured_output() as (out, err):
            listener.print_all_channels()

        return_dict = out.getvalue()
        self.assertIn(channel_hash, return_dict)
        self.assertIn(second_channel_hash, return_dict)


    def test_initialize(self):
        listener = self.init_own_listener()

        listener.player.initialize = MagicMock()

        self.assertRaises(ValueError, listener.initialize)

        channel_hash = self.connection.add_channel_to_server()
        listener.channel_hash = channel_hash

        listener.initialize()

        clients = self.connection.get_clients()
        self.assertEqual(len(clients), 1)
        self.assertIn(listener.client_hash, clients)
        result_client = clients[listener.client_hash]
        self.assertEqual(result_client["name"], self.test_name)
        self.assertEqual(listener.player.initialize.call_count, 1)

        # Doing the same twice should not harm
        listener.initialize()
        self.assertEqual(listener.player.initialize.call_count, 1)
        clients = self.connection.get_clients()
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