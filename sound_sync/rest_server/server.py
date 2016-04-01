from tornado.web import Application, url

from sound_sync.rest_server.handler import ErrorHandler, ListHandler
from sound_sync.rest_server.server_items.server_items import ClientItem, ChannelItem


# TODO: Add a heartbeat

class RestServer:
    def __init__(self):
        self.client_list = dict()
        self.channel_list = dict()

    def get_app(self):
        channel_initializer = {"item_type": ChannelItem, "item_list": self.channel_list}
        client_initializer = {"item_type": ClientItem, "item_list": self.client_list}

        return Application([
            url(r"/", ErrorHandler),
            url(r"/channels/(\w+)$", ListHandler, channel_initializer),
            url(r"/channels/(\w+)/(\d+)$", ListHandler, channel_initializer),
            url(r"/clients/(\w+)$", ListHandler, client_initializer),
            url(r"/clients/(\w+)/(\d+)$", ListHandler, client_initializer)
        ])