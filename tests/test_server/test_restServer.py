import urllib

from tests.fixtures import LowLevelServerTestCase


class TestRestServer(LowLevelServerTestCase):
    def test_main(self):
        response = self.fetch('/')
        self.assertError(response, 501)

    def test_unused_action(self):
        response = self.fetch("/channels/foo")
        self.assertError(response, 501)

        response = self.fetch("/clients/foo")
        self.assertError(response, 501)

        parameter = {"test": "test"}
        body = urllib.parse.urlencode(parameter)

        response = self.fetch("/channels/foo/1", method="POST", body=body)
        self.assertError(response, 501)

        response = self.fetch("/clients/foo/1", method="POST", body=body)
        self.assertError(response, 501)

        response = self.fetch("/buffers/foo/bar", method="POST", body=body)
        self.assertError(response, 501)

        parameter = {"buffer": "test"}
        body = urllib.parse.urlencode(parameter)
        self.fetch("/buffers/1/add", method="POST", body=body)

        response = self.fetch("/buffers/1/bar")
        self.assertError(response, 501)