from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, url

from sound_sync.rest_server.handler import ErrorHandler, ListHandler
from sound_sync.rest_server.server_items import Channel, Client


class RestServer:
    def __init__(self):
        self.client_list = dict()
        self.channel_list = dict()

    def get_app(self):

        channel_initializer = {"item_type": Channel, "item_list": self.channel_list}
        client_initializer = {"item_type": Client, "item_list": self.client_list}

        return Application([
            url(r"/", ErrorHandler),
            url(r"/channels/(\w+)$", ListHandler, channel_initializer),
            url(r"/channels/(\w+)/(\d+)$", ListHandler, channel_initializer),
            url(r"/clients/(\w+)$", ListHandler, client_initializer),
            url(r"/clients/(\w+)/(\d+)$", ListHandler, client_initializer)
        ])

if __name__ == "__main__":
    server = RestServer()
    http_server = HTTPServer(server.get_app())
    http_server.bind(8888)
    http_server.start()
    IOLoop.current().start()