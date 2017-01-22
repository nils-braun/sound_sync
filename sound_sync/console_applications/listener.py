import argparse

import logging

from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.listener.base_listener import BaseListener


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--hostname",
                        default="localhost",
                        type=str,
                        help="Hostname of the management server.",
                        dest="hostname")
    parser.add_argument("-p", "--port",
                        default=8888,
                        type=int,
                        help="Port of the listen to on the server. Default 8888.",
                        dest="port")
    parser.add_argument("-c", "--channel_hash",
                        default="1",
                        type=str,
                        help="Channel hash to listen to.",
                        dest="channel_hash")
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

    listener = BaseListener(args.hostname, args.port, args.channel_hash)
    listener.player = PCMPlay()
    listener.initialize()

    try:
        listener.main_loop()
    finally:
        listener.terminate()


if __name__ == "__main__":
    main()
