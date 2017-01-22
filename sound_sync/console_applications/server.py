import argparse

import logging

from sound_sync.server.server import Server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--subscriber-port",
                        default=8888,
                        type=int,
                        help="Port number where the clients are listening on. Default 8888.",
                        dest="subscriber_port")
    parser.add_argument("--publisher-port",
                        default=8887,
                        type=int,
                        help="Port number where the clients are sending to. Default 8887.",
                        dest="publisher_port")
    parser.add_argument("-l", "--log",
                        default="INFO",
                        type=str,
                        help="Log level of the application",
                        dest="loglevel")
    args = parser.parse_args()

    numeric_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    logging.basicConfig(level=numeric_level)

    server = Server(args.publisher_port, args.subscriber_port)

    server.initialize()

    try:
        server.main_loop()
    finally:
        server.terminate()

if __name__ == "__main__":
    main()
