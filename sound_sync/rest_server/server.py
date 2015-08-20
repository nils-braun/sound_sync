from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
import random


class Client:
    def __init__(self):
        pass

class Channel:
    def __init__(self):
        pass


class ListHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(ListHandler, self).__init__(application, request, **kwargs)

        self.list = dict()

    def initialize(self, type):
        self.type = type

    def get(self, action, list_hash=None):
        if action == "add":
            new_hash = random.getrandbits(20)
            self.list.update({new_hash: self.type()})

            print self.list

            self.write(str(new_hash))
        elif action == "delete":
            if list_hash in self.list:
                del self.list[list_hash]
            else:
                self.send_error()
        elif action == "get":
            self.write(self.list)

        else:
            self.send_error()

    def post(self, action, list_hash):
        if action == "set":
            pass

        else:
            self.send_error()


class ErrorHandler(RequestHandler):
    def get(self):
        self.send_error()


class RestServer:
    def __init__(self):
        pass

    def get_app(self):
        return Application([
            url(r"/", ErrorHandler),
            url(r"/channels/(\w+)$", ListHandler, {"type": Channel}), # get, add, delete
            url(r"/clients/(\w+)$", ListHandler, {"type": Client}), # get, add, delete
            #url(r"/buffer/(\d+)/(\w+)$", BufferHandler) #
        ])