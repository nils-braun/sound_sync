import json
import urllib
from tests.server_test_case import ServerTestCase


class TestBufferListFromServer(ServerTestCase):
    def test_get_buffer(self):

        response = self.fetch('/channels/' + "000" + '/buffers/get/' + str(0))
        self.assertError(response, 502)

        response = self.fetch('/channels/add')
        channel_hash = self.assertResponse(response)

        response = self.fetch('/channels/' + channel_hash + '/buffers/get/' + str(0))
        self.assertError(response, 502)

        parameters = {"buffer": "This is my test buffer"}
        body = urllib.urlencode(parameters)
        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "0")

        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "1")

        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "2")

        response = self.fetch('/channels/' + channel_hash + '/buffers/get/' + str(0))
        self.assertResponse(response, "This is my test buffer")

        response = self.fetch('/channels/' + channel_hash + '/buffers/get/' + str(2))
        self.assertResponse(response, "This is my test buffer")

        response = self.fetch('/channels/' + channel_hash + '/buffers/get/' + str(5))
        self.assertError(response, 503)

    def test_add_buffer(self):
        parameters = {"buffer": "This is my test buffer"}
        body = urllib.urlencode(parameters)

        response = self.fetch('/channels/' + '000' + '/buffers/add', method="POST", body=body)
        self.assertError(response, 502)

        response = self.fetch('/channels/add')
        channel_hash = self.assertResponse(response)
        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "0")

        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "1")