from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import argparse
from sound_sync.rest_server.handler import ErrorHandler, ListHandler
from sound_sync.rest_server.server_items import Channel, Client
from tornado.web import Application, url


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",
                        default=8888,
                        type=int,
                        help="Port number the management server is listening on. Default 8888.",
                        dest="port")
    args = parser.parse_args()
    server = RestServer()
    http_server = HTTPServer(server.get_app())
    http_server.bind(args.port)
    http_server.start()
    IOLoop.current().start()


if __name__ == "__main__":
    main()