from tornado.testing import AsyncHTTPTestCase
from sound_sync.rest_server.server import RestServer


class TestRestServer(AsyncHTTPTestCase):
    def get_app(self):
        return RestServer().get_app()

    def assertError(self, response):
        self.assertEqual(response.code, 500)

    def assertResponse(self, response, content=None):
        self.assertEqual(response.code, 200)
        if content is not None:
            self.assertEqual(response.body, content)
        else:
            return response.body

    def test_main(self):
        response = self.fetch('/')
        self.assertError(response)

    def test_get_channels(self):
        response = self.fetch('/channels/get')
        self.assertResponse(response, "{}")

    def test_add_channels(self):
        response = self.fetch('/channels/add')
        hash = self.assertResponse(response)

        response = self.fetch('/channels/get')
        self.assertResponse(response, "")


