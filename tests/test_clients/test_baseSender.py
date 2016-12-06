import urllib
from datetime import datetime
from time import sleep

from mock import MagicMock, patch
from tornado.httpclient import HTTPClient, HTTPError

from sound_sync.entities.sound_buffer_with_time import SoundBufferWithTime
from tests.fixtures import SenderTestCase, CallableExhausted, ServerTestCase


class TestBaseSender(SenderTestCase, ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        SenderTestCase.setUp(self)

    def test_terminate(self):
        sender = self.init_own_sender()

        sender.terminate()

        channel_hash = self.connection.add_channel_to_server()
        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)

        sender.channel_hash = channel_hash
        sender.terminate()

        self.assertEqual(sender.channel_hash, None)
        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 0)

    @patch("sound_sync.clients.base_sender.get_current_date")
    def test_main_loop(self, time_mock):
        sender = self.init_own_sender()

        test_current_time = datetime(2015, 11, 4, 0, 0, 10)
        time_mock.return_value = test_current_time

        # Raise Exception without channel hash
        self.assertRaises(AssertionError, sender.main_loop)

        sender.initialize()
        self.assertRaises(CallableExhausted, sender.main_loop)

        for i in range(self.number_of_stored_buffers):
            resulting_sound_buffer = self.connection.get_buffer(i, sender.channel_hash)

            expected_time = test_current_time
            expected_send_buffer = SoundBufferWithTime(sound_buffer=self.test_buffer,
                                                       buffer_number=i,
                                                       buffer_time=expected_time)

            self.assertEqual(expected_send_buffer, resulting_sound_buffer)

        self.assertEqual(self.connection.get_start_index(sender.channel_hash), 0)
        self.assertEqual(self.connection.get_end_index(sender.channel_hash), self.number_of_stored_buffers)

        self.assertRaisesRegex(HTTPError, "502: Bad Gateway", self.connection.get_buffer,
                               self.number_of_stored_buffers + 1, sender.channel_hash)

    @patch("sound_sync.clients.base_sender.get_current_date")
    def test_two_sender_full(self, time_mock):
        test_current_time = datetime(2015, 11, 4, 0, 0, 10)
        time_mock.return_value = test_current_time

        sender1 = self.init_own_sender()
        sender2 = self.init_own_sender()

        sender1.initialize()
        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertIn(sender1.channel_hash, channels)
        self.assertEqual(channels[sender1.channel_hash]["description"], self.test_description)
        self.assertEqual(channels[sender1.channel_hash]["name"], self.test_name)

        sender2.initialize()
        channels = self.connection.get_channels()
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

        self.assertRaisesRegex(HTTPError, "502: Bad Gateway", self.connection.get_buffer, 0, sender2.channel_hash)
        self.assertRaisesRegex(HTTPError, "502: Bad Gateway", self.connection.get_start_index, sender2.channel_hash)

        try:
            sender2.main_loop()
        except CallableExhausted:
            pass

        for i in range(self.number_of_stored_buffers):
            resulting_sound_buffer = self.connection.get_buffer(i, sender1.channel_hash)

            expected_time = test_current_time
            expected_send_buffer = SoundBufferWithTime(sound_buffer=self.test_buffer,
                                                       buffer_number=i,
                                                       buffer_time=expected_time)

            self.assertEqual(expected_send_buffer, resulting_sound_buffer)

            resulting_sound_buffer = self.connection.get_buffer(i, sender2.channel_hash)

            expected_time = test_current_time
            expected_send_buffer = SoundBufferWithTime(sound_buffer=self.test_buffer,
                                                       buffer_number=i,
                                                       buffer_time=expected_time)

            self.assertEqual(expected_send_buffer, resulting_sound_buffer)

        self.assertRaisesRegex(HTTPError, "502: Bad Gateway", self.connection.get_buffer,
                               self.number_of_stored_buffers + 1, sender1.channel_hash)
        self.assertRaisesRegex(HTTPError, "502: Bad Gateway", self.connection.get_buffer,
                               self.number_of_stored_buffers + 1, sender2.channel_hash)

        self.assertEqual(self.connection.get_start_index(sender1.channel_hash), 0)
        self.assertEqual(self.connection.get_end_index(sender1.channel_hash), self.number_of_stored_buffers)
        self.assertEqual(self.connection.get_start_index(sender2.channel_hash), 0)
        self.assertEqual(self.connection.get_end_index(sender2.channel_hash), self.number_of_stored_buffers)

        sender1.terminate()
        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertIn(sender2.channel_hash, channels)

        sender2.terminate()
        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 0)

    def test_get_settings(self):
        sender = self.init_own_sender()

        channel_hash = self.connection.add_channel_to_server()
        sender.channel_hash = channel_hash

        # Change recorder settings and handler port
        parameters = {"channels": "5", "buffer_size": "34"}
        self.connection.set_parameters_of_channel(parameters, channel_hash)

        sender.get_settings()

        # Check recorder settings and handler port
        self.assertEqual(sender.recorder.channels, "5")
        self.assertEqual(sender.recorder.buffer_size, "34")

    def test_initialize(self):
        sender = self.init_own_sender()

        sender.recorder.initialize = MagicMock()

        sender.initialize()

        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)
        self.assertIn(sender.channel_hash, channels)
        result_channel = channels[sender.channel_hash]
        self.assertEqual(result_channel["name"], self.test_name)
        self.assertEqual(result_channel["description"], self.test_description)
        self.assertEqual(sender.recorder.initialize.call_count, 1)

        # Doing the same twice should not harm
        sender.initialize()
        self.assertEqual(sender.recorder.initialize.call_count, 1)
        channels = self.connection.get_channels()
        self.assertEqual(len(channels), 1)
