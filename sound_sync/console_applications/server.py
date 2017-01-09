import argparse

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
    args = parser.parse_args()
    server = Server(args.publisher_port, args.subscriber_port)

    server.initialize()

    try:
        server.main_loop()
    finally:
        server.terminate()

if __name__ == "__main__":
    main()
