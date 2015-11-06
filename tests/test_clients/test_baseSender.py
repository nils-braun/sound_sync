import urllib

from mock import MagicMock

from sound_sync.clients.sender import Sender
from tests.fixtures import SenderTestCase, CallableExhausted, ServerTestCase


class TestBaseSender(SenderTestCase, ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        SenderTestCase.setUp(self)

    def test_terminate(self):
        sender, connection = self.init_own_sender()

        sender.terminate()

        channel_hash = connection.add_channel_to_server()
        sender.channel_hash = channel_hash
        sender.terminate()

        self.assertEqual(sender.channel_hash, None)
        clients = self.get_clients()
        self.assertEqual(len(clients), 0)

    def test_handler_string(self):
        sender = Sender()
        sender.connection.host = self.test_host
        self.assertRaises(ValueError, getattr, sender, "handler_string")

        test_handler_port = 54654
        sender.handler_port = test_handler_port

        self.assertEqual(sender.handler_string, "http://" + self.test_host + ":" + str(test_handler_port))

    def test_main_loop(self):
        sender = self.init_sender()
        test_handler_port = 547647
        sender.handler_port = test_handler_port

        mocking_client = MagicMock()
        sender.connection.http_client = mocking_client

        # Raise Exception without channel hash
        self.assertRaises(AssertionError, sender.main_loop)

        sender.channel_hash = "345"
        self.assertRaises(CallableExhausted, sender.main_loop)

        mocking_client.fetch.assert_called_with('http://' + self.test_host + ':' + str(test_handler_port) + '/add',
                                                method="POST", body="buffer=" + self.test_buffer)
        self.assertEqual(mocking_client.fetch.call_count, self.number_of_stored_buffers)

    def test_get_settings(self):
        sender, connection = self.init_own_sender()

        channel_hash = connection.add_channel_to_server()
        sender.channel_hash = channel_hash

        # Change recorder settings and handler port
        body = urllib.urlencode({"handler_port": "64567", "channels": "5", "buffer_size": "34"})
        self.set_channel_html(body, channel_hash)

        sender.get_settings()

        # Check recorder settings and handler port
        self.assertEqual(sender.handler_port, "64567")
        self.assertEqual(sender.recorder.channels, "5")
        self.assertEqual(sender.recorder.buffer_size, "34")

    def test_initialize(self):
        sender, connection = self.init_own_sender()
        sender.recorder.initialize = MagicMock()

        sender.initialize()

        channels = self.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertIn(sender.channel_hash, channels)
        result_channel = channels[sender.channel_hash]
        self.assertEqual(result_channel["name"], self.test_name)
        self.assertEqual(result_channel["description"], self.test_description)
        self.assertEqual(sender.recorder.initialize.call_count, 1)

        # Doing the same twice should not harm
        sender.initialize()
        self.assertEqual(sender.recorder.initialize.call_count, 1)
        channels = self.get_channels()
        self.assertEqual(len(channels), 1)

