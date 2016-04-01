import argparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from sound_sync.rest_server.server import RestServer


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
