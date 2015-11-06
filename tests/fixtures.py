from datetime import datetime, timedelta
from unittest import TestCase
from mock import patch, MagicMock
from tornado.testing import AsyncHTTPTestCase
from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.audio.pcm.record import PCMRecorder
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

        self.datelist = [datetime(2015, 11, 6, 0, 0, i) for i in xrange(20)]

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

    def assertError(self, response, error_code=500):
        self.assertEqual(response.code, error_code)

    def assertResponse(self, response, content=None):
        self.assertEqual(response.code, 200)
        if content is not None:
            self.assertEqual(response.body, content)
        else:
            return response.body


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