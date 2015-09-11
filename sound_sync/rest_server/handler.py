import random
from tornado.web import RequestHandler

NOT_SUPPORTED_ERROR_CODE = 501
KEY_ERROR_CODE = 502


class ErrorHandler(RequestHandler):
    def get(self):
        return self.send_error(NOT_SUPPORTED_ERROR_CODE)


class ListHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(ListHandler, self).__init__(application, request, **kwargs)

    # noinspection PyMethodOverriding,PyAttributeOutsideInit
    def initialize(self, item_type, item_list):
        self.item_type = item_type
        self.item_list = item_list

    def get(self, action, list_hash=None):
        if action == "add":
            new_hash = str(random.getrandbits(10))
            self.item_list.update({new_hash: self.item_type(new_hash, self.request)})

            return self.write(str(new_hash))
        elif action == "delete":
            if list_hash in self.item_list:
                self.item_list[list_hash].stop()
                del self.item_list[list_hash]
                return self.write("")
            else:
                return self.send_error(KEY_ERROR_CODE)
        elif action == "get":
            return self.write({item_hash: list_item.encode_json()
                               for item_hash, list_item in self.item_list.iteritems()})

        else:
            return self.send_error(NOT_SUPPORTED_ERROR_CODE)

    def post(self, action, list_hash):
        if action == "set":
            if list_hash in self.item_list:
                list_item = self.item_list[list_hash]

                for parameter_name in self.request.arguments:
                    parameter_value = self.get_argument(parameter_name)

                    setattr(list_item, parameter_name, parameter_value)
            else:
                return self.send_error(KEY_ERROR_CODE)

        else:
            return self.send_error(NOT_SUPPORTED_ERROR_CODE)