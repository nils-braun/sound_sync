from unittest import TestCase
from mock import patch, MagicMock
from tornado.testing import AsyncHTTPTestCase
from sound_sync.rest_server.server import RestServer

__author__ = 'nils'


class TimingTestCase(TestCase):
    def setUp(self):
        self.time_mock = 0

        patcher = patch("sound_sync.timing.time_utils.datetime")
        self.datetime_mock = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = patch("sound_sync.timing.time_utils.time")
        self.time_mock = patcher.start()
        self.addCleanup(patcher.stop)

        self.time_list_mock_function = MagicMock(side_effect=xrange(20))

    def get_current_time(self):
        current_time_list = list(self.time_list_mock_function.side_effect)
        current_time = current_time_list[0] - 1
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