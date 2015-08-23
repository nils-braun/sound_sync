import random
from tornado.web import RequestHandler
from sound_sync.buffer_list import BufferList

NOT_SUPPORTED_ERROR_CODE = 501
KEY_ERROR_CODE = 502
BUFFER_ERROR_CODE = 503

class ErrorHandler(RequestHandler):
    def get(self):
        return self.send_error(NOT_SUPPORTED_ERROR_CODE)


class BufferHandler(RequestHandler):
    # noinspection PyMethodOverriding,PyAttributeOutsideInit
    def initialize(self, buffer_list, channel_list):
        self.buffer_list = buffer_list
        self.channel_list = channel_list

    def get(self, channel_hash, action, buffer_number=None):
        if channel_hash not in self.channel_list:
            return self.send_error(KEY_ERROR_CODE)
        if action == "get":
            buffer_number = int(buffer_number)
            try:
                correct_buffer_list = self.buffer_list[channel_hash]

                buffer_content = correct_buffer_list.get_buffer_by_buffer_index(buffer_number)
                return self.write(buffer_content)
            except (IndexError, KeyError):
                return self.send_error(BUFFER_ERROR_CODE)

        elif action == "len":
            try:
                correct_buffer_list = self.buffer_list[channel_hash]
                return self.write(str(len(correct_buffer_list)))
            except (IndexError, KeyError):
                return self.write(str(0))

        else:
            return self.send_error(NOT_SUPPORTED_ERROR_CODE)

    def post(self, channel_hash, action):
        if channel_hash not in self.channel_list:
            return self.send_error(KEY_ERROR_CODE)

        if action == "add":

            if channel_hash not in self.buffer_list:
                self.buffer_list.update({channel_hash: BufferList()})

            buffer_content = self.request.arguments.get("buffer")
            next_buffer_number = self.buffer_list[channel_hash].add_buffer(buffer_content)
            return self.write(str(next_buffer_number))

        else:
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
            self.item_list.update({new_hash: self.item_type(new_hash)})

            return self.write(str(new_hash))
        elif action == "delete":
            if list_hash in self.item_list:
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