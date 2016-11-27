import argparse

from sound_sync.audio.pcm.play import PCMPlay
from sound_sync.clients.base_listener import BaseListener


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
                        help="Port of the management socket on the management server. Default 8888.",
                        dest="manager_port")
    parser.add_argument("-n", "--name",
                        default="Untitled",
                        type=str,
                        help="Name of this channel in the channel list. Default Untitled.",
                        dest="name")
    parser.add_argument("-c", "--channel_hash",
                        default=None,
                        type=str,
                        help="Channel hash to listen to.",
                        dest="channel_hash")
    args = parser.parse_args()

    listener = BaseListener(args.channel_hash, args.hostname, args.manager_port)
    listener.player = PCMPlay()
    listener.name = args.name
    listener.initialize()

    try:
        listener.main_loop()
    finally:
        listener.terminate()


if __name__ == "__main__":
    main()
