from tornado.testing import AsyncHTTPTestCase
from sound_sync.rest_server.server import RestServer

__author__ = 'nils'


class ServerTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return RestServer().get_app()

    def assertError(self, response, error_code=500):
        self.assertEqual(response.code, error_code)

    def assertResponse(self, response, content=None):
        self.assertEqual(response.code, 200)
        if content is not None:
            self.assertEqual(response.body, content)
        else:
            return response.body