import urllib
from datetime import datetime, timedelta

from mock import MagicMock, patch, call

from sound_sync.clients.sound_buffer_with_time import SoundBufferWithTime
from sound_sync.rest_server.server_items.server_items import Channel
from sound_sync.timing.time_utils import sleep
from tests.fixtures import ListenerTestCase,  ServerTestCase, TimingTestCase


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

    def test_receive_and_play_next_buffer(self):
        listener, connection = self.init_own_listener()

        test_buffer_with_time = SoundBufferWithTime(sound_buffer=self.test_buffer, buffer_number=0, buffer_time=datetime(2015, 11, 3, 0, 0, 10))
        listener.get_buffer = MagicMock(return_value=test_buffer_with_time.to_string())
        listener.start_play_timer = MagicMock()

        listener.next_expected_buffer_number = 0

        listener.receive_and_play_next_buffer()

        listener.get_buffer.assert_called_once_with(0)
        self.assertEqual(listener.start_play_timer.call_count, 1)
        self.assertEqual(listener.start_play_timer.call_args, ((test_buffer_with_time,),))
        self.assertEqual(listener.next_expected_buffer_number, 1)

        listener.next_expected_buffer_number = 10
        self.assertRaises(AssertionError, listener.receive_and_play_next_buffer)

        test_buffer_with_time = SoundBufferWithTime(sound_buffer=self.test_buffer, buffer_number=10, buffer_time=datetime(2015, 11, 3, 0, 0, 10))
        listener.get_buffer = MagicMock(return_value=test_buffer_with_time.to_string())

        listener.next_expected_buffer_number = 10
        listener.receive_and_play_next_buffer()
        listener.get_buffer.assert_called_once_with(10)
        self.assertEqual(listener.next_expected_buffer_number, 11)

    def test_receive_and_play_next_buffer_real(self):
        listener, connection, real_http_client = self.init_typical_setup()

        listener.start_play_timer = MagicMock()
        listener.next_expected_buffer_number = 0

        test_buffer_with_time = SoundBufferWithTime(sound_buffer=self.test_buffer, buffer_number=0, buffer_time=datetime(2015, 11, 3, 0, 0, 10))

        buffer_numbers = 10
        for i in range(buffer_numbers):
            test_buffer_with_time.buffer_number = i
            self.send_buffer(test_buffer_with_time.to_string(), listener, real_http_client)

        for i in range(buffer_numbers):
            listener.receive_and_play_next_buffer()

        self.assertEqual(listener.start_play_timer.call_count, 10)
        for i, call_arg in enumerate(listener.start_play_timer.call_args_list):
            test_buffer_with_time.buffer_number = i
            self.assertEqual(call_arg, call(test_buffer_with_time))

    def test_get_current_buffer_start_index(self):
        mocking_client = MagicMock()
        listener, connection = self.init_own_listener(buffer_server=mocking_client)
        handler_test_port = 1111
        listener._connected_channel = Channel()
        listener._connected_channel.handler_port = handler_test_port

        class Response:
            def __init__(self, code, body=None):
                self.code = code
                self.body = body

        good_response = Response(200, "45")

        mocking_client.fetch = MagicMock(return_value=good_response)
        start_index = listener.get_current_buffer_start_index()
        mocking_client.fetch.assert_called_once_with("http://" + self.test_host + ":" + str(handler_test_port) + "/start")
        self.assertEqual(start_index, 45)

    def test_get_current_buffer_start_index_real(self):
        listener, connection, real_http_client = self.init_typical_setup()

        start_index = listener.get_current_buffer_start_index()
        self.assertEqual(start_index, 0)

        parameters = {"buffer": self.test_buffer}
        body = urllib.parse.urlencode(parameters)

        for i in range(101):
            real_http_client.fetch(listener.handler_string + '/add',
                                   method="POST", body=body)

        start_index = listener.get_current_buffer_start_index()
        self.assertEqual(start_index, 1)

    def test_get_current_buffer_end_index(self):
        mocking_client = MagicMock()
        listener, connection = self.init_own_listener(buffer_server=mocking_client)
        handler_test_port = 1111
        listener._connected_channel = Channel()
        listener._connected_channel.handler_port = handler_test_port

        class Response:
            def __init__(self, code, body=None):
                self.code = code
                self.body = body

        good_response = Response(200, "45")

        mocking_client.fetch = MagicMock(return_value=good_response)
        end_index = listener.get_current_buffer_end_index()
        mocking_client.fetch.assert_called_once_with("http://" + self.test_host + ":" + str(handler_test_port) + "/end")
        self.assertEqual(end_index, 45)

    def test_get_current_buffer_end_index_real(self):
        listener, connection, real_http_client = self.init_typical_setup()

        end_index = listener.get_current_buffer_end_index()
        self.assertEqual(end_index, 0)

        parameters = {"buffer": self.test_buffer}
        body = urllib.parse.urlencode(parameters)

        for i in range(11):
            real_http_client.fetch(listener.handler_string + '/add',
                                   method="POST", body=body)

        end_index = listener.get_current_buffer_end_index()
        self.assertEqual(end_index, 10)

    def test_get_buffer_fail(self):
        mocking_client = MagicMock()
        listener, connection = self.init_own_listener(buffer_server=mocking_client)
        handler_test_port = 1111
        listener._connected_channel = Channel()
        listener._connected_channel.handler_port = handler_test_port

        class Response:
            def __init__(self, code, body=None):
                self.code = code
                self.body = body

        failed_response = Response(502)

        mocking_client.fetch = MagicMock(return_value=failed_response)
        self.assertRaises(RuntimeError, listener.get_buffer, 245)

    def test_get_buffer(self):
        mocking_client = MagicMock()
        listener, connection = self.init_own_listener(buffer_server=mocking_client)
        handler_test_port = 1111
        listener._connected_channel = Channel()
        listener._connected_channel.handler_port = handler_test_port

        class Response:
            def __init__(self, code, body=None):
                self.code = code
                self.body = body

        good_response = Response(200, "45")

        mocking_client.fetch = MagicMock(return_value=good_response)
        buffer = listener.get_buffer(245)
        mocking_client.fetch.assert_called_once_with("http://" + self.test_host + ":" +
                                                     str(handler_test_port) + "/get/245", raise_error=False)
        self.assertEqual(buffer, "45")

    def test_get_buffer_real(self):
        listener, connection, real_http_client = self.init_typical_setup()

        buffer_numbers = 10
        for i in range(buffer_numbers):
            self.send_buffer(self.test_buffer + str(i), listener, real_http_client)

        sleep(0.05)

        for i in range(buffer_numbers):
            buffer = listener.get_buffer(i)
            self.assertEqual(buffer, self.test_buffer + str(i))

        self.assertRaises(RuntimeError, listener.get_buffer, 11)
        self.assertRaises(RuntimeError, listener.get_buffer, -1)
        self.assertRaises(RuntimeError, listener.get_buffer, 4897458)

    def send_buffer(self, buffer_content, listener, real_http_client):
        parameters = {"buffer": buffer_content}
        body = urllib.parse.urlencode(parameters)
        real_http_client.fetch(listener.handler_string + '/add',
                               method="POST", body=body)