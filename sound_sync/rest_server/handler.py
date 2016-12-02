import random

from sound_sync.entities.buffer_list import BufferList
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
            if list_hash:
                if list_hash in self.item_list:
                    return self.write(self.item_list[list_hash].encode_json())
                else:
                    return self.send_error(KEY_ERROR_CODE)
            else:
                return self.write({item_hash: list_item.encode_json()
                                   for item_hash, list_item in self.item_list.items()})
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


class BufferHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BufferHandler, self).__init__(application, request, **kwargs)

    # noinspection PyMethodOverriding,PyAttributeOutsideInit
    def initialize(self, buffer_list):
        self.buffer_list = buffer_list

    def get(self, channel_hash, action, index=None):
        if channel_hash not in self.buffer_list:
            print(channel_hash, self.buffer_list)
            return self.send_error(KEY_ERROR_CODE)
        else:
            buffer_list = self.buffer_list[channel_hash]

        if action == "start":
            return self.write(str(buffer_list.get_start_index()))
        elif action == "end":
            return self.write(str(buffer_list.get_next_free_index()))
        elif action == "get":
            try:
                return self.write(str(buffer_list.get_buffer(str(index))))
            except RuntimeError:
                self.send_error(KEY_ERROR_CODE)
        else:
            return self.send_error(NOT_SUPPORTED_ERROR_CODE)

    def post(self, channel_hash, action):
        if channel_hash not in self.buffer_list:
            self.buffer_list[channel_hash] = BufferList(100)

        if action == "add":
            self.buffer_list[channel_hash].add_buffer(self.get_argument("buffer"))

        else:
            return self.send_error(NOT_SUPPORTED_ERROR_CODE)
