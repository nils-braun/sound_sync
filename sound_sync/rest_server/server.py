from tornado.web import Application, url

from sound_sync.rest_server.handler import ErrorHandler, ListHandler, BufferHandler
from sound_sync.rest_server.server_items import Channel, Client


class RestServer:
    def __init__(self):
        self.client_list = dict()
        self.channel_list = dict()
        self.buffer_list = dict()

    def get_app(self):

        channel_initializer = {"item_type": Channel, "item_list": self.channel_list}
        client_initializer = {"item_type": Client, "item_list": self.client_list}
        buffer_initializer = {"buffer_list": self.buffer_list, "channel_list": self.channel_list}

        return Application([
            url(r"/", ErrorHandler),
            url(r"/channels/(\w+)$", ListHandler, channel_initializer),
            url(r"/channels/(\w+)/(\d+)$", ListHandler, channel_initializer),
            url(r"/clients/(\w+)$", ListHandler, client_initializer),
            url(r"/clients/(\w+)/(\d+)$", ListHandler, client_initializer),
            url(r"/channels/(\d+)/buffers/(\w+)$", BufferHandler, buffer_initializer),
            url(r"/channels/(\d+)/buffers/(\w+)/(\d+)$", BufferHandler, buffer_initializer)
        ])