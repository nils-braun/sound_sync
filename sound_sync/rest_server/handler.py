import random
from tornado.web import RequestHandler

__author__ = 'nils'


class ErrorHandler(RequestHandler):
    def get(self):
        self.send_error()


class ListHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(ListHandler, self).__init__(application, request, **kwargs)

    def initialize(self, item_type, item_list):
        self.item_type = item_type
        self.item_list = item_list

    def get(self, action, list_hash=None):
        if action == "add":
            new_hash = int(random.getrandbits(10))
            self.item_list.update({new_hash: self.item_type(new_hash)})

            self.write(str(new_hash))
        elif action == "delete":
            list_hash = int(list_hash)

            if list_hash in self.item_list:
                del self.item_list[list_hash]
                self.write("")
            else:
                self.send_error()
        elif action == "get":
            self.write({item_hash: list_item.encode_json() for item_hash, list_item in self.item_list.iteritems()})

        else:
            self.send_error()

    def post(self, action, list_hash):
        if action == "set":
            list_hash = int(list_hash)

            if list_hash in self.item_list:
                list_item = self.item_list[list_hash]

                for parameter_name in self.request.arguments:
                    parameter_value = self.get_argument(parameter_name)

                    setattr(list_item, parameter_name, parameter_value)
            else:
                self.send_error()

        else:
            self.send_error()