import json
import urllib
from datetime import datetime, timedelta
from time import sleep
from unittest import TestCase

from mock import patch, MagicMock
from tornado.testing import AsyncHTTPTestCase

from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.audio.pcm.record import PCMRecorder
from sound_sync.clients.base_listener import BaseListener
from sound_sync.clients.base_sender import BaseSender
from sound_sync.clients.connection import SoundSyncConnection
from sound_sync.rest_server.server import RestServer


class TimingTestCase(TestCase):
    def setUp(self):
        self.time_mock = 0

        patcher = patch("sound_sync.timing.time_utils.datetime")
        self.datetime_mock = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch("sound_sync.timing.time_utils.time")
        self.time_mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.datelist = [datetime(2015, 11, 6, 0, 0, i) for i in range(20)]

        self.time_list_mock_function = MagicMock(side_effect=self.datelist)

    def get_current_time(self):
        current_time_list = list(self.time_list_mock_function.side_effect)
        current_time = current_time_list[0] + timedelta(seconds=-1)
        self.time_list_mock_function.side_effect = current_time_list
        return current_time


class ServerTestCase(AsyncHTTPTestCase):
    def get_app(self):
        self.restServer = RestServer()
        return self.restServer.get_app()


class LowLevelServerTestCase(ServerTestCase):

    def assertError(self, response, error_code=500):
        self.assertEqual(response.code, error_code)

    def assertResponse(self, response, content=None):
        self.assertEqual(response.code, 200)
        body = str(response.body, encoding="utf8")

        if content is not None:
            self.assertEqual(body, content)
        else:
            return body

    def get_channels_html(self):
        response = self.fetch('/channels/get')
        return response

    def get_channels(self):
        response = self.get_channels_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        return response_dict

    def add_channel_html(self):
        response = self.fetch('/channels/add')
        return response

    def set_channel_html(self, body, item_hash):
        response = self.fetch('/channels/set/' + str(item_hash), method="POST", body=body)
        return response

    def delete_channel_html(self, item_hash):
        response = self.fetch('/channels/delete/' + str(item_hash))
        return response

    def get_clients_html(self):
        response = self.fetch('/clients/get')
        return response

    def get_clients(self):
        response = self.get_clients_html()
        response = self.assertResponse(response)
        response_dict = json.loads(response)
        return response_dict

    def set_client_html(self, body, item_hash):
        response = self.fetch('/clients/set/' + str(item_hash), method="POST", body=body)
        return response

    def add_client_html(self):
        response = self.fetch('/clients/add')
        return response

    def delete_client_html(self, item_hash):
        response = self.fetch('/clients/delete/' + item_hash)
        return response


class SoundTestCase(TestCase):
    def setUp(self):
        self.PCM_CAPTURE = 372435
        self.PCM_NONBLOCK = 21354
        self.PCM_PLAYBACK = 372435
        self.PCM_FORMAT_S16_LE = 21654

        patcher = patch("sound_sync.audio.pcm.device.alsaaudio")
        self.alsaaudio = patcher.start()
        self.addCleanup(patcher.stop)

    def init_sound_player(self):
        player = PCMPlay()
        self.alsaaudio.PCM_PLAYBACK = self.PCM_PLAYBACK
        self.alsaaudio.PCM_FORMAT_S16_LE = self.PCM_FORMAT_S16_LE
        self.alsaaudio.PCM_NONBLOCK = self.PCM_NONBLOCK
        player.buffer_size = 2
        player.frame_rate = 3
        player.channels = 4
        player.factor = 5
        player.initialize()
        return player

    def init_sound_recorder(self):
        recorder = PCMRecorder()
        self.alsaaudio.cards = lambda: ["TestCard", "Loopback", "Bla"]
        self.alsaaudio.PCM_CAPTURE = self.PCM_CAPTURE
        self.alsaaudio.PCM_FORMAT_S16_LE = self.PCM_FORMAT_S16_LE
        recorder.buffer_size = 2
        recorder.frame_rate = 3
        recorder.channels = 4
        recorder.factor = 5
        recorder.initialize()
        return recorder


class SoundSyncConnectionTestCase(ServerTestCase):
    def setUp(self):
        ServerTestCase.setUp(self)

        self.connection = SoundSyncConnection()
        self.connection.http_client = self
        self.connection.manager_string = ""


class SenderTestCase(SoundSyncConnectionTestCase):
    def setUp(self):
        SoundSyncConnectionTestCase.setUp(self)
        self.number_of_stored_buffers = 5
        self.test_name = "TheName"
        self.test_description = "TheDescription"
        self.test_buffer = bytes("Buffer", encoding="utf8")
        self.test_buffer_length = 100

    def init_own_sender(self):
        sender = BaseSender()
        sender.connection = self.connection
        sender.name = self.test_name
        sender.description = self.test_description

        # Ensure we will not run into an infinite loop
        sender.recorder = PCMRecorder()
        sender.recorder.get = ErrorAfter(self.number_of_stored_buffers, (self.test_buffer, self.test_buffer_length))
        sender.recorder.initialize = lambda: None

        return sender


class ListenerTestCase(SoundSyncConnectionTestCase):
    def setUp(self):
        SoundSyncConnectionTestCase.setUp(self)

        self.number_of_stored_buffers = 5
        self.test_name = "TheName"
        self.test_description = "TheDescription"
        self.test_buffer = "Buffer"
        self.test_buffer_length = 100

    def init_own_listener(self):
        listener = BaseListener()
        listener.connection = self.connection
        listener.name = self.test_name
        listener.description = self.test_description

        # Ensure we will not run into an infinite loop
        listener.player = PCMPlay()
        listener.player.initialize = lambda: None

        return listener

    def init_typical_setup(self):
        listener = self.init_own_listener()
        channel_hash = self.connection.add_channel_to_server()
        listener.channel_hash = channel_hash
        listener.initialize()
        sleep(0.1)
        return listener


class ErrorAfter:
    def __init__(self, limit, return_before=None):
        self.limit = limit
        self.calls = 0
        self.return_before = return_before

    def __call__(self):
        self.calls += 1
        if self.calls > self.limit:
            raise CallableExhausted

        return self.return_before


class CallableExhausted(Exception):
    pass