import urllib

from tests.server_test_case import ServerTestCase


class TestRestServer(ServerTestCase):
    def test_main(self):
        response = self.fetch('/')
        self.assertError(response, 501)

    def test_unused_action(self):
        response = self.fetch("/channels/foo")
        self.assertError(response, 501)

        parameter = {"test": "test"}
        body = urllib.urlencode(parameter)
        response = self.fetch("/channels/foo/1", method="POST", body=body)
        self.assertError(response, 501)

        response = self.fetch("/clients/foo")
        self.assertError(response, 501)

        parameter = {"test": "test"}
        body = urllib.urlencode(parameter)
        response = self.fetch("/clients/foo/1", method="POST", body=body)
        self.assertError(response, 501)


        response = self.fetch("/channels/add")
        channel_hash = self.assertResponse(response)
        parameters = {"buffer": ""}
        body = urllib.urlencode(parameters)
        self.fetch('/channels/' + channel_hash + '/buffers/add', method="POST", body=body)

        response = self.fetch("/channels/" + channel_hash + "/buffers/foo/0")
        self.assertError(response, 501)

        parameter = {"test": "test"}
        body = urllib.urlencode(parameter)
        response = self.fetch("/channels/" + channel_hash + "/buffers/1", method="POST", body=body)
        self.assertError(response, 501)
