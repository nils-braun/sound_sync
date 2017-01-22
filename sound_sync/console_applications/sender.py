import argparse

import logging

from sound_sync.audio.pcm.record import PCMRecorder
from sound_sync.sender.base_sender import BaseSender


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--hostname",
                        default="localhost",
                        type=str,
                        help="Hostname of the management server.",
                        dest="hostname")
    parser.add_argument("-p", "--port",
                        default=8887,
                        type=int,
                        help="Port to send to on the server. Default 8887.",
                        dest="port")
    parser.add_argument("--hash",
                        default="1",
                        type=str,
                        help="Hash value. TODO",
                        dest="hash")
    parser.add_argument("-n", "--name",
                        default="Untitled",
                        type=str,
                        help="Name of this channel in the channel list. Default Untitled.",
                        dest="name")
    parser.add_argument("-d", "--description",
                        default="No Description",
                        type=str,
                        help="Description of this channel in the channel list. Default No Description.",
                        dest="description")
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

    sender = BaseSender(args.hostname, args.port, args.hash)
    sender.recorder = PCMRecorder()
    sender.name = args.name
    sender.description = args.description
    sender.initialize()
    try:
        sender.main_loop()
    finally:
        sender.terminate()


if __name__ == "__main__":
    main()
