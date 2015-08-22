import urllib

from tests.test_server.server_test_case import ServerTestCase


class TestBufferListFromServer(ServerTestCase):
    def add_channel(self):
        response = self.fetch('/channels/add')
        channel_hash = self.assertResponse(response)
        return channel_hash

    def add_buffer_to_channel(self, channel_hash):
        parameters = {"buffer": "This is my test buffer"}
        body = urllib.urlencode(parameters)
        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        return body, response

    def test_get_buffer(self):

        response = self.fetch('/channels/' + "000" + '/buffers/get/' + str(0))
        self.assertError(response, 502)

        channel_hash = self.add_channel()

        response = self.fetch('/channels/' + channel_hash + '/buffers/get/' + str(0))
        self.assertError(response, 503)

        body, response = self.add_buffer_to_channel(channel_hash)
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
        body, response = self.add_buffer_to_channel('000')
        self.assertError(response, 502)

        channel_hash = self.add_channel()
        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "0")

        response = self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)
        self.assertResponse(response, "1")

    def test_len_buffer(self):
        response = self.fetch('/channels/' + str(000) + '/buffers/len')
        self.assertError(response, 502)

        channel_hash = self.add_channel()

        response = self.fetch('/channels/' + channel_hash + '/buffers/len')
        self.assertResponse(response, str(0))

        self.add_buffer_to_channel(channel_hash)
        self.add_buffer_to_channel(channel_hash)

        response = self.fetch('/channels/' + channel_hash + '/buffers/len')
        self.assertResponse(response, str(1))