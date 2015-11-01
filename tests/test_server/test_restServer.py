import urllib

from tests.test_fixtures import ServerTestCase


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