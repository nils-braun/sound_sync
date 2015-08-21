from tornado.web import Application, url

from sound_sync.rest_server.handler import ErrorHandler, ListHandler
from sound_sync.rest_server.server_items import Channel, Client

class RestServer:
    def __init__(self):
        self.client_list = dict()
        self.channel_list = dict()

    def get_app(self):
        return Application([
            url(r"/", ErrorHandler),
            url(r"/channels/(\w+)$", ListHandler, {"item_type": Channel, "item_list": self.channel_list}),
            url(r"/channels/(\w+)/(\d+)$", ListHandler, {"item_type": Channel, "item_list": self.channel_list}),
            url(r"/clients/(\w+)$", ListHandler, {"item_type": Client, "item_list": self.client_list}),
            url(r"/clients/(\w+)/(\d+)$", ListHandler, {"item_type": Client, "item_list": self.client_list}),
            #url(r"/buffer/(\d+)/(\w+)$", BufferHandler) #
        ])