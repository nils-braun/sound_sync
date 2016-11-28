import urllib

from tests.fixtures import LowLevelServerTestCase


class TestRestServer(LowLevelServerTestCase):
    def test_main(self):
        response = self.fetch('/')
        self.assertError(response, 501)

    def test_unused_action(self):
        response = self.fetch("/channels/foo")
        self.assertError(response, 501)

        parameter = {"test": "test"}
        body = urllib.parse.urlencode(parameter)
        response = self.fetch("/channels/foo/1", method="POST", body=body)
        self.assertError(response, 501)

        response = self.fetch("/clients/foo")
        self.assertError(response, 501)

        parameter = {"test": "test"}
        body = urllib.parse.urlencode(parameter)
        response = self.fetch("/clients/foo/1", method="POST", body=body)
        self.assertError(response, 501)