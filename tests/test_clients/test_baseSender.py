import urllib

from datetime import datetime, timedelta
from mock import MagicMock, patch
from tornado.httpclient import HTTPClient, HTTPError
from time import sleep

from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime
from tests.fixtures import SenderTestCase, CallableExhausted, ServerTestCase, TimingTestCase


class TestBaseSender(SenderTestCase, ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        SenderTestCase.setUp(self)

    def test_terminate(self):
        sender, connection = self.init_own_sender(manager_server=self)

        sender.terminate()

        self.assertEqual(self, connection.http_client)

        channel_hash = connection.add_channel_to_server()
        channels = self.get_channels()
        self.assertEqual(len(channels), 1)

        sender.channel_hash = channel_hash
        sender.terminate()

        self.assertEqual(sender.channel_hash, None)
        channels = self.get_channels()
        self.assertEqual(len(channels), 0)

    def test_handler_string(self):
        sender, connection = self.init_own_sender()
        sender.connection.host = self.test_host
        self.assertRaises(ValueError, getattr, sender, "handler_string")

        test_handler_port = 54654
        sender.handler_port = test_handler_port

        self.assertEqual(sender.handler_string, "http://" + self.test_host + ":" + str(test_handler_port))

    @patch("sound_sync.clients.base_sender.get_current_date")
    def test_main_loop(self, time_mock):
        mocking_client = MagicMock()

        sender, connection = self.init_own_sender(buffer_server=mocking_client)
        test_handler_port = 547647
        sender.handler_port = test_handler_port

        test_current_time = datetime(2015, 11, 4, 0, 0, 10)
        time_mock.return_value = test_current_time

        # Raise Exception without channel hash
        self.assertRaises(AssertionError, sender.main_loop)

        sender.channel_hash = "345"
        self.assertRaises(CallableExhausted, sender.main_loop)

        expected_time = test_current_time + (self.number_of_stored_buffers - 1) * sender.recorder.get_waiting_time()
        expected_send_buffer = SoundBufferWithTime(sound_buffer=self.test_buffer,
                                                   buffer_number=self.number_of_stored_buffers - 1,
                                                   buffer_time=expected_time)

        expected_parameters = {"buffer": expected_send_buffer.to_string()}
        expected_body = urllib.urlencode(expected_parameters)

        mocking_client.fetch.assert_called_with('http://' + self.test_host + ':' + str(test_handler_port) + '/add',
                                                method="POST", body=expected_body)
        self.assertEqual(mocking_client.fetch.call_count, self.number_of_stored_buffers)

    @patch("sound_sync.clients.base_sender.get_current_date")
    def test_two_sender_full(self, time_mock):
        test_current_time = datetime(2015, 11, 4, 0, 0, 10)
        time_mock.return_value = test_current_time

        self.test_host = "localhost"
        real_http_client = HTTPClient()

        sender1, connection = self.init_own_sender(manager_server=self, buffer_server=real_http_client)
        sender2, connection = self.init_own_sender(manager_server=self, buffer_server=real_http_client)

        sender1.initialize()
        channels = self.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertIn(sender1.channel_hash, channels)
        self.assertEqual(channels[sender1.channel_hash]["description"], self.test_description)
        self.assertEqual(channels[sender1.channel_hash]["name"], self.test_name)

        sender2.initialize()
        channels = self.get_channels()
        self.assertEqual(len(channels), 2)
        self.assertIn(sender2.channel_hash, channels)
        self.assertEqual(channels[sender2.channel_hash]["description"], self.test_description)
        self.assertEqual(channels[sender2.channel_hash]["name"], self.test_name)

        self.assertNotEqual(sender1.channel_hash, sender2.channel_hash)

        sleep(0.1)

        try:
            sender1.main_loop()
        except CallableExhausted:
            pass

        for i in xrange(self.number_of_stored_buffers):
            self.assertEqual(real_http_client.fetch(sender1.handler_string + "/get/" + str(i)).body,
                             "%s<||>%s<||>%d<||>6" % (self.test_buffer, test_current_time + i * sender1.recorder.get_waiting_time(), i))

        self.assertRaisesRegexp(HTTPError, "502: Bad Gateway", real_http_client.fetch,
                                sender1.handler_string + "/get/" + str(self.number_of_stored_buffers + 1))
        self.assertRaisesRegexp(HTTPError, "502: Bad Gateway", real_http_client.fetch,
                                sender2.handler_string + "/get/" + str(0))

        self.assertEqual(real_http_client.fetch(sender1.handler_string + "/start").body, "0")
        self.assertEqual(real_http_client.fetch(sender2.handler_string + "/start").body, "0")

        try:
            sender2.main_loop()
        except CallableExhausted:
            pass

        for i in xrange(self.number_of_stored_buffers):
            self.assertEqual(real_http_client.fetch(sender1.handler_string + "/get/" + str(i)).body,
                             "%s<||>%s<||>%d<||>6" % (self.test_buffer, test_current_time + i * sender1.recorder.get_waiting_time(), i))
            self.assertEqual(real_http_client.fetch(sender2.handler_string + "/get/" + str(i)).body,
                             "%s<||>%s<||>%d<||>6" % (self.test_buffer, test_current_time + i * sender1.recorder.get_waiting_time(), i))

        self.assertRaisesRegexp(HTTPError, "502: Bad Gateway", real_http_client.fetch,
                                sender1.handler_string + "/get/" + str(self.number_of_stored_buffers + 1))
        self.assertRaisesRegexp(HTTPError, "502: Bad Gateway", real_http_client.fetch,
                                sender2.handler_string + "/get/" + str(self.number_of_stored_buffers + 1))

        self.assertEqual(real_http_client.fetch(sender1.handler_string + "/start").body, "0")
        self.assertEqual(real_http_client.fetch(sender2.handler_string + "/start").body, "0")

        sender1.terminate()
        channels = self.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertIn(sender2.channel_hash, channels)

        sender2.terminate()
        channels = self.get_channels()
        self.assertEqual(len(channels), 0)

    def test_get_settings(self):
        sender, connection = self.init_own_sender(manager_server=self)

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
        sender, connection = self.init_own_sender(manager_server=self)

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
