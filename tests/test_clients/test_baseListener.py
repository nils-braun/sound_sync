import urllib
from datetime import datetime, timedelta

from mock import MagicMock

from sound_sync.rest_server.server_items.server_items import Channel
from tests.fixtures import ListenerTestCase,  ServerTestCase, TimingTestCase


class TestBaseListener(ListenerTestCase, ServerTestCase, TimingTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)
        ListenerTestCase.setUp(self)
        TimingTestCase.setUp(self)

    def test_terminate(self):
        listener, connection = self.init_own_listener(manager_server=self)

        listener.terminate()

        self.assertEqual(self, connection.http_client)

        client_hash = connection.add_client_to_server()
        clients = self.get_clients()
        self.assertEqual(len(clients), 1)

        listener.client_hash = client_hash
        listener.terminate()

        self.assertEqual(listener.client_hash, None)
        clients = self.get_clients()
        self.assertEqual(len(clients), 0)

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
        body = urllib.urlencode({"handler_port": "64567", "channels": "5", "buffer_size": "34"})
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

    def test_receive_and_add_next_buffer(self):
        listener, connection = self.init_own_listener()

        listener.get_buffer = MagicMock(return_value=self.test_buffer)

        listener.receive_and_add_next_buffer()
        listener.get_buffer.assert_called_once_with(0)

        result_buffer = listener.buffer_list.get_buffer("0")
        self.assertEqual(result_buffer, self.test_buffer)

        self.assertEqual(listener.buffer_list.get_next_free_index(), 1)

    def test_receive_and_add_next_buffer_real(self):
        listener, connection, real_http_client = self.init_typical_setup()

        buffer_numbers = 10
        for i in xrange(buffer_numbers):
            parameters = {"buffer": self.test_buffer + str(i)}
            body = urllib.urlencode(parameters)
            real_http_client.fetch(listener.handler_string + '/add',
                                   method="POST", body=body)

        for i in xrange(buffer_numbers):
            listener.receive_and_add_next_buffer()

        for i in xrange(buffer_numbers):
            result_buffer = listener.buffer_list.get_buffer(str(i))
            self.assertEqual(result_buffer, self.test_buffer + str(i))

        self.assertEqual(listener.buffer_list.get_next_free_index(), 10)

    def test_play_next_buffer(self):
        listener, connection = self.init_own_listener()

        listener.last_played_buffer_number = 0
        listener.player.put = MagicMock()

        for i in xrange(10):
            listener.buffer_list.add_buffer(self.test_buffer + str(i))

        for i in xrange(9):
            listener.play_next_buffer()
            self.assertEqual(listener.last_played_buffer_number, i + 1)
            listener.player.put.assert_called_with(self.test_buffer + str(i + 1))

        self.assertRaises(RuntimeError, listener.play_next_buffer)

        listener.buffer_list.add_buffer(self.test_buffer + "10")
        listener.play_next_buffer()
        listener.player.put.assert_called_with(self.test_buffer + str(10))

    def test_calculate_next_starting_time_and_buffer(self):
        listener, connection = self.init_own_listener()

        self.datetime_mock.datetime.now = MagicMock(return_value=datetime(2015, 11, 4, 0, 0, 10))
        self.datetime_mock.timedelta = timedelta
        listener.player.start_time = datetime(2015, 11, 4, 0, 0, 11)

        self.assertRaises(ValueError, listener.calculate_next_starting_time_and_buffer)

        listener.player.start_time = datetime(2015, 11, 4, 0, 0, 0)

        listener.player.get_waiting_time = lambda: 10
        next_time, number_of_next_clock = listener.calculate_next_starting_time_and_buffer()
        self.assertEqual(next_time, datetime(2015, 11, 4, 0, 0, 20))
        self.assertEqual(number_of_next_clock, 2)

        listener.player.get_waiting_time = lambda: 11
        next_time, number_of_next_clock = listener.calculate_next_starting_time_and_buffer()
        self.assertEqual(next_time, datetime(2015, 11, 4, 0, 0, 11))
        self.assertEqual(number_of_next_clock, 1)

        listener.player.get_waiting_time = lambda: 3
        next_time, number_of_next_clock = listener.calculate_next_starting_time_and_buffer()
        self.assertEqual(next_time, datetime(2015, 11, 4, 0, 0, 12))
        self.assertEqual(number_of_next_clock, 4)

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
        body = urllib.urlencode(parameters)

        for i in xrange(101):
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
        body = urllib.urlencode(parameters)

        for i in xrange(11):
            real_http_client.fetch(listener.handler_string + '/add',
                                   method="POST", body=body)

        end_index = listener.get_current_buffer_end_index()
        self.assertEqual(end_index, 10)

    def test_initial_fill_buffer_list(self):
        listener, connection = self.init_own_listener()

        test_buffer_start_index = 100
        listener.get_current_buffer_start_index = MagicMock(return_value=test_buffer_start_index)
        listener.get_buffer = MagicMock(return_value=self.test_buffer)

        next_buffer_number = 101
        listener.get_current_buffer_end_index = MagicMock(return_value=next_buffer_number)

        self.assertRaisesRegexp(ValueError, "^Too few buffers loaded into the server.$",
                                listener.initial_fill_buffer_list)

        next_buffer_number = 120
        listener.get_current_buffer_end_index = MagicMock(return_value=next_buffer_number)
        listener.initial_fill_buffer_list()

        self.assertEqual(listener.buffer_list.get_start_index(), 100)
        self.assertEqual(listener.buffer_list.get_next_free_index(), 121)
        self.assertEqual(listener.get_buffer.call_count, 21)

        for i in xrange(100, 120):
            self.assertEqual(listener.buffer_list.get_buffer(str(i)), self.test_buffer)

        self.assertRaises(RuntimeError, listener.buffer_list.get_buffer, str(121))

    def test_initial_fill_buffer_list_real(self):
        pass

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

        failed_response = Response(502)

        good_response = Response(200, "45")

        mocking_client.fetch = MagicMock(return_value=failed_response)
        self.assertRaises(RuntimeError, listener.get_buffer, 245)

        mocking_client.fetch = MagicMock(return_value=good_response)
        buffer = listener.get_buffer(245)
        mocking_client.fetch.assert_called_once_with("http://" + self.test_host + ":" +
                                                     str(handler_test_port) + "/get/245", raise_error=False)
        self.assertEqual(buffer, "45")

    def test_get_buffer_real(self):
        listener, connection, real_http_client = self.init_typical_setup()

        buffer_numbers = 10
        for i in xrange(buffer_numbers):
            parameters = {"buffer": self.test_buffer + str(i)}
            body = urllib.urlencode(parameters)
            real_http_client.fetch(listener.handler_string + '/add',
                                   method="POST", body=body)

        for i in xrange(buffer_numbers):
            buffer = listener.get_buffer(i)
            self.assertEqual(buffer, self.test_buffer + str(i))

        self.assertRaises(RuntimeError, listener.get_buffer, 11)
        self.assertRaises(RuntimeError, listener.get_buffer, -1)
        self.assertRaises(RuntimeError, listener.get_buffer, 4897458)

    def test_main_loop(self):
        pass

    def test_start_play_thread(self):
        pass
